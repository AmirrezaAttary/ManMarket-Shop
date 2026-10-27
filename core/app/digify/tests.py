import time
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from django.db.models import F
from rest_framework.test import APIClient

from app.shop.models import Brand, Color, ProductCategoryModel, ProductColorInventory, ProductModel
from app.shop.models.products import ProductStatusType


def make_product(title, slug, color_specs=(), **extra):
    brand, _ = Brand.objects.get_or_create(title="سامسونگ", slug="samsung")
    cat, _ = ProductCategoryModel.objects.get_or_create(title="موبایل", slug="mobile")
    product = ProductModel.objects.create(
        title=title, slug=slug, description="<p>شرح</p>", brand=brand, category=cat, **extra
    )
    for color_title, hex_color, price, final_price, stock in color_specs:
        color, _ = Color.objects.get_or_create(title=color_title, defaults={"hex_color": hex_color})
        ProductColorInventory.objects.create(
            product=product, color=color, hex_color=hex_color, price=price, final_price=final_price, stock=stock
        )
    return product


class DigifyFeedTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.p1 = make_product(
            "گوشی A", "a", [("مشکی", "#000000", 1000000, 900000, 5), ("سفید", "#fff", 1000000, 1000000, 0)]
        )
        self.p2 = make_product("گوشی B", "b", [("آبی", "#0000ff", 500000, 500000, 3)])

    def test_plp_shape_and_total(self):
        data = self.api.get("/digify/v1/products/").json()
        self.assertEqual(data["total"], 2)
        item = data["results"][0]
        self.assertEqual(item["id"], str(self.p1.pk))  # created_date asc
        self.assertEqual(item["price"], 900000)
        self.assertEqual(item["original_price"], 1000000)
        self.assertTrue(item["is_available"])
        self.assertEqual(item["category_path"], ["موبایل"])
        self.assertEqual(item["brand"], "سامسونگ")
        self.assertTrue(item["updated_at"].endswith("Z"))
        self.assertNotIn("variants", item)

    def test_pdp_variants(self):
        data = self.api.get(f"/digify/v1/products/{self.p1.pk}/").json()
        self.assertEqual(len(data["variants"]), 2)
        black, white = data["variants"]
        self.assertEqual(black["stock"], 5)
        self.assertTrue(black["is_available"])
        self.assertEqual(black["attributes"][0], {"name": "رنگ", "value": "مشکی", "is_color": True, "color_code": "#000000"})
        self.assertFalse(white["is_available"])
        self.assertEqual(white["attributes"][0]["color_code"], "#FFFFFF")  # #fff expanded
        self.assertIsNone(white["original_price"])

    def test_pdp_always_has_a_variant(self):
        bare = make_product("بدون تنوع", "bare")
        data = self.api.get(f"/digify/v1/products/{bare.pk}/").json()
        self.assertEqual(len(data["variants"]), 1)
        self.assertFalse(data["is_available"])

    def test_pagination_is_limit_offset_and_stable(self):
        page1 = self.api.get("/digify/v1/products/?limit=1&offset=0").json()
        page2 = self.api.get("/digify/v1/products/?limit=1&offset=1").json()
        self.assertEqual(page1["total"], 2)
        self.assertEqual([page1["results"][0]["id"], page2["results"][0]["id"]], [str(self.p1.pk), str(self.p2.pk)])

    def test_bad_params(self):
        for qs in ("limit=abc", "limit=0", "offset=-1", "updated_after=yesterday"):
            self.assertEqual(self.api.get(f"/digify/v1/products/?{qs}").status_code, 400, qs)

    def test_updated_after_filters_and_total_matches_filter(self):
        future = int(time.time()) + 3600
        data = self.api.get(f"/digify/v1/products/?updated_after={future}").json()
        self.assertEqual((data["total"], data["results"]), (0, []))
        past = int(time.time()) - 3600
        self.assertEqual(self.api.get(f"/digify/v1/products/?updated_after={past}").json()["total"], 2)

    def test_bulk_stock_update_is_seen_as_a_change(self):
        old = timezone.now() - timedelta(days=1)
        ProductModel.objects.update(updated_date=old)
        ProductColorInventory.objects.update(updated_date=old)
        since = int(time.time()) - 60
        self.assertEqual(self.api.get(f"/digify/v1/products/?updated_after={since}").json()["total"], 0)

        # same kind of write the BWDK stock reservation does (queryset.update, no save())
        ProductColorInventory.objects.filter(product=self.p2).update(stock=F("stock") - 1)

        data = self.api.get(f"/digify/v1/products/?updated_after={since}").json()
        self.assertEqual([r["id"] for r in data["results"]], [str(self.p2.pk)])

    def test_deleting_a_variant_is_seen_as_a_change(self):
        old = timezone.now() - timedelta(days=1)
        ProductModel.objects.update(updated_date=old)
        ProductColorInventory.objects.update(updated_date=old)
        ProductColorInventory.objects.filter(product=self.p1, color__title="سفید").first().delete()
        since = int(time.time()) - 60
        data = self.api.get(f"/digify/v1/products/?updated_after={since}").json()
        self.assertEqual([r["id"] for r in data["results"]], [str(self.p1.pk)])

    def test_draft_product_is_reported_unavailable(self):
        self.p2.status = ProductStatusType.draft.value
        self.p2.save()
        data = self.api.get(f"/digify/v1/products/{self.p2.pk}/").json()
        self.assertFalse(data["is_available"])
        self.assertFalse(data["variants"][0]["is_available"])
        self.assertEqual(data["variants"][0]["stock"], 0)

    def test_unknown_product_is_404(self):
        self.assertEqual(self.api.get("/digify/v1/products/999999/").status_code, 404)

    @override_settings(DIGIFY_FEED_API_KEY="s3cret")
    def test_api_key(self):
        self.assertEqual(self.api.get("/digify/v1/products/").status_code, 403)
        self.assertEqual(self.api.get("/digify/v1/products/", HTTP_AUTHORIZATION="Api-Key nope").status_code, 403)
        self.assertEqual(self.api.get("/digify/v1/products/", HTTP_AUTHORIZATION="Api-Key s3cret").status_code, 200)
        self.assertEqual(self.api.get("/digify/v1/products/", HTTP_X_API_KEY="s3cret").status_code, 200)

    @override_settings(DIGIFY_FEED_ALLOWED_IPS=["1.2.3.4"])
    def test_ip_allowlist(self):
        self.assertEqual(self.api.get("/digify/v1/products/").status_code, 403)
        self.assertEqual(self.api.get("/digify/v1/products/", REMOTE_ADDR="1.2.3.4").status_code, 200)
