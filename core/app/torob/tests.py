import base64
import json
import time

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from django.test import TestCase, override_settings

from app.shop.models import (
    Brand,
    Color,
    ProductCategoryModel,
    ProductColorInventory,
    ProductImageModel,
    ProductModel,
    ProductSpecification,
)
from app.shop.models.products import ProductStatusType

PRIVATE = Ed25519PrivateKey.generate()
PUBLIC_B64 = base64.b64encode(
    PRIVATE.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
).decode()
AUD = "api.manmarket.ir"
URL = "/torob_api/v3/products"


def token(aud=AUD, exp_in=300, key=PRIVATE):
    now = int(time.time())
    return jwt.encode({"aud": aud, "exp": now + exp_in, "nbf": now - 10}, key, algorithm="EdDSA", headers={"v": 1})


def make_product(title, slug, colors=(), **extra):
    brand, _ = Brand.objects.get_or_create(title="سامسونگ", slug="samsung")
    cat, _ = ProductCategoryModel.objects.get_or_create(title="موبایل", slug="mobile")
    product = ProductModel.objects.create(
        title=title, slug=slug, description="<p>x</p>", brand=brand, category=cat, **extra
    )
    for title_, price, final, stock in colors:
        color, _ = Color.objects.get_or_create(title=title_, defaults={"hex_color": "#000000"})
        ProductColorInventory.objects.create(
            product=product, color=color, price=price, final_price=final, stock=stock
        )
    return product


@override_settings(TOROB_PUBLIC_KEY=PUBLIC_B64, TOROB_ALLOWED_AUDIENCES=[AUD])
class TorobApiTests(TestCase):
    def post(self, body, tok=None, raw=None):
        headers = {"HTTP_X_TOROB_TOKEN": tok if tok is not None else token()}
        data = raw if raw is not None else json.dumps(body)
        return self.client.post(URL, data=data, content_type="application/json", **headers)

    def setUp(self):
        self.p1 = make_product(
            "گوشی A", "a", [("مشکی", 1000000, 900000, 5), ("سفید", 1100000, 1100000, 0)],
            warranty="گارانتی ۱۸ ماه", brief_description="<b>توضیح</b> کوتاه",
        )
        ProductSpecification.objects.create(product=self.p1, name="حافظه", value="128GB", status=True)
        ProductSpecification.objects.create(product=self.p1, name="مخفی", value="x", status=False)
        self.p2 = make_product("گوشی B", "b", [("آبی", 500000, 500000, 3)])
        self.black, self.white = self.p1.color_inventories.order_by("id")

    # ---- auth ----
    def test_token_required_and_validated(self):
        self.assertEqual(self.client.post(URL, "{}", content_type="application/json").status_code, 401)
        self.assertEqual(self.post({"page": 1, "sort": "date_added_desc"}, tok="garbage").status_code, 401)
        self.assertEqual(self.post({"page": 1, "sort": "date_added_desc"}, tok=token(aud="other.com")).status_code, 401)
        self.assertEqual(self.post({"page": 1, "sort": "date_added_desc"}, tok=token(exp_in=-3600)).status_code, 401)
        self.assertEqual(
            self.post({"page": 1, "sort": "date_added_desc"}, tok=token(key=Ed25519PrivateKey.generate())).status_code, 401
        )
        self.assertEqual(self.post({"page": 1, "sort": "date_added_desc"}).status_code, 200)

    @override_settings(ALLOWED_HOSTS=["other.com", "testserver", "api.manmarket.ir"])
    def test_forged_host_header_cannot_replay_other_shops_token(self):
        r = self.client.post(
            URL, json.dumps({"page": 1, "sort": "date_added_desc"}), content_type="application/json",
            HTTP_X_TOROB_TOKEN=token(aud="other.com"), HTTP_HOST="other.com",
        )
        self.assertEqual(r.status_code, 401)

    def test_trailing_slash_and_get(self):
        r = self.client.post(URL + "/", json.dumps({"page": 1, "sort": "date_added_desc"}),
                             content_type="application/json", HTTP_X_TOROB_TOKEN=token())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get(URL).status_code, 405)

    # ---- validation (every error is 400 + {"error": ...}) ----
    def test_bad_requests(self):
        cases = [
            ({}, "no parameters"),
            ({"page": 1}, "sort parameter is not provided"),
            ({"sort": "date_added_desc"}, "page parameter is not provided"),
            ({"page": 0, "sort": "date_added_desc"}, "page must be"),
            ({"page": "1", "sort": "date_added_desc"}, "page must be"),
            ({"page": True, "sort": "date_added_desc"}, "page must be"),
            ({"page": 1, "sort": "nope"}, "sort must be"),
            ({"page": 1, "sort": "product_id_desc"}, "use cursor"),
            ({"sort": "product_id_desc", "cursor": 5}, "cursor must be"),
            ({"sort": "product_id_desc", "limit": 10}, "unknown parameter"),
            ({"page": 1, "sort": "date_added_desc", "cursor": "1"}, "cursor is only"),
            ({"page_urls": []}, "non-empty list"),
            ({"page_uniques": "1_1"}, "non-empty list"),
            ({"page_uniques": ["1_1"], "page": 1}, "cannot be combined"),
        ]
        for body, fragment in cases:
            r = self.post(body)
            self.assertEqual(r.status_code, 400, body)
            self.assertIn(fragment, r.json()["error"], body)
        self.assertEqual(self.post(None, raw="").status_code, 400)
        self.assertEqual(self.post(None, raw="{bad").status_code, 400)
        self.assertEqual(self.post(None, raw="[1]").status_code, 400)

    # ---- page mode ----
    def test_page_mode_shape(self):
        data = self.post({"page": 1, "sort": "date_added_desc"}).json()
        self.assertEqual(data["api_version"], "torob_api_v3")
        self.assertEqual((data["current_page"], data["total"], data["max_pages"]), (1, 3, 1))
        by_unique = {p["page_unique"]: p for p in data["products"]}
        self.assertEqual(len(by_unique), 3)
        black = by_unique[f"{self.p1.pk}_{self.black.pk}"]
        self.assertEqual(black["product_group_id"], str(self.p1.pk))
        self.assertEqual(black["title"], "گوشی A")
        self.assertEqual((black["current_price"], black["old_price"], black["availability"]), (900000, 1000000, True))
        self.assertEqual(black["category_name"], "موبایل")
        self.assertEqual(black["spec"], {"حافظه": "128GB", "رنگ": "مشکی"})  # inactive spec hidden
        self.assertEqual(black["guarantee"], "گارانتی ۱۸ ماه")
        self.assertEqual(black["short_desc"], "توضیح کوتاه")
        self.assertEqual(black["page_url"], f"https://manmarket.ir/product/a?variant={self.black.pk}")
        self.assertRegex(black["date_added"], r"\+03:30$")
        self.assertRegex(black["date_updated"], r"\+03:30$")
        white = by_unique[f"{self.p1.pk}_{self.white.pk}"]
        self.assertFalse(white["availability"])
        self.assertIsNone(white["old_price"])
        for p in data["products"]:
            self.assertIsInstance(p["current_price"], int)

    def test_hundred_per_page(self):
        for i in range(120):
            make_product(f"P{i}", f"p{i}", [("مشکی", 1000, 1000, 1)])
        page1 = self.post({"page": 1, "sort": "date_added_desc"}).json()
        page2 = self.post({"page": 2, "sort": "date_added_desc"}).json()
        page3 = self.post({"page": 3, "sort": "date_added_desc"}).json()
        self.assertEqual((page1["total"], page1["max_pages"]), (123, 2))
        self.assertEqual((len(page1["products"]), len(page2["products"]), len(page3["products"])), (100, 23, 0))
        ids = [p["page_unique"] for p in page1["products"] + page2["products"]]
        self.assertEqual(len(set(ids)), 123)

    def test_date_updated_desc_puts_recent_stock_change_first(self):
        ProductColorInventory.objects.filter(pk=self.p2.color_inventories.first().pk).update(stock=9)
        first = self.post({"page": 1, "sort": "date_updated_desc"}).json()["products"][0]
        self.assertEqual(first["product_group_id"], str(self.p2.pk))

    # ---- cursor mode ----
    def test_cursor_walk_covers_everything_once(self):
        for i in range(250):
            make_product(f"P{i}", f"p{i}", [("مشکی", 1000, 1000, 1)])
        seen, body, pages = [], {"sort": "product_id_desc"}, 0
        while True:
            data = self.post(body).json()
            pages += 1
            self.assertIsNone(data["total"])
            seen += [p["page_unique"] for p in data["products"]]
            if data["next_cursor"] is None:
                break
            self.assertEqual(len(data["products"]), 100)
            body = {"sort": "product_id_desc", "cursor": data["next_cursor"]}
        self.assertEqual((pages, len(seen), len(set(seen))), (3, 253, 253))

    # ---- single lookups ----
    def test_page_uniques_and_urls_return_the_same_variant(self):
        unique = f"{self.p1.pk}_{self.white.pk}"
        by_unique = self.post({"page_uniques": [unique]}).json()
        by_url = self.post({"page_urls": [f"https://manmarket.ir/product/a?variant={self.white.pk}"]}).json()
        self.assertEqual(by_unique["total"], 1)
        self.assertEqual(by_unique["products"], by_url["products"])
        self.assertEqual(by_unique["products"][0]["page_unique"], unique)

    def test_url_without_variant_returns_storefront_default(self):
        data = self.post({"page_urls": ["https://manmarket.ir/product/a"]}).json()
        self.assertEqual(data["products"][0]["page_unique"], f"{self.p1.pk}_{self.black.pk}")  # lowest list price

    def test_unknown_removed_and_draft_are_omitted(self):
        self.p2.status = ProductStatusType.draft.value
        self.p2.save()
        gone = f"{self.p2.pk}_{self.p2.color_inventories.first().pk}"
        data = self.post({"page_uniques": [gone, "999_999", "junk", f"{self.p1.pk}_{self.black.pk}"]}).json()
        self.assertEqual((data["total"], len(data["products"])), (1, 1))
        listing = self.post({"page": 1, "sort": "date_added_desc"}).json()
        self.assertEqual(listing["total"], 2)
        empty = self.post({"page_uniques": [gone]}).json()
        self.assertEqual((empty["total"], empty["max_pages"], empty["products"]), (0, 1, []))

    def test_wrong_product_id_in_unique_is_not_found(self):
        data = self.post({"page_uniques": [f"{self.p2.pk}_{self.black.pk}"]}).json()
        self.assertEqual(data["products"], [])

    def test_option_images_win(self):
        ProductImageModel.objects.create(product=self.p1, color=self.black.color, file="product/extra-img/black.jpg")
        ProductImageModel.objects.create(product=self.p1, color=self.white.color, file="product/extra-img/white.jpg")
        data = self.post({"page_uniques": [f"{self.p1.pk}_{self.black.pk}", f"{self.p1.pk}_{self.white.pk}"]}).json()
        black, white = data["products"]
        self.assertEqual(black["image_links"], ["https://api.manmarket.ir/media/product/extra-img/black.jpg"])
        self.assertEqual(white["image_links"], ["https://api.manmarket.ir/media/product/extra-img/white.jpg"])
