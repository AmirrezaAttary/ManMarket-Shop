"""Builds the JSON shapes that the Digify (Bazaar) catalog document asks for.

Mapping of our model -> the document:
    ProductModel                -> product
    ProductColorInventory       -> variant (one variant per colour of a product)
    Color                       -> variant attribute "رنگ"
    ProductImageModel(color)    -> variant images (same colour) / product images
Prices are in Toman, integers (that is what the shop stores).
"""
import re
from urllib.parse import quote

from django.conf import settings
from django.db.models import DateTimeField, Max, Prefetch
from django.db.models.functions import Coalesce, Greatest
from django.utils import timezone as dj_tz
from datetime import timezone as dt_tz

from app.shop.models import ProductColorInventory, ProductImageModel, ProductModel
from app.shop.models.products import ProductStatusType

DEFAULT_IMAGE_NAME = "default/product-image.png"
DEFAULT_CATEGORY = "سایر"
_HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _site_url():
    return getattr(settings, "DIGIFY_SITE_URL", "https://manmarket.ir").rstrip("/")


def _media_url(name):
    base = getattr(settings, "DIGIFY_MEDIA_BASE_URL", "https://api.manmarket.ir").rstrip("/")
    prefix = str(settings.MEDIA_URL).strip("/")
    path = f"{prefix}/{name.lstrip('/')}" if prefix else name.lstrip("/")
    return f"{base}/{path}"


def _iso_utc(value):
    if dj_tz.is_naive(value):
        value = dj_tz.make_aware(value, dt_tz.utc)
    return value.astimezone(dt_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hex(value):
    value = (value or "").strip()
    if not _HEX.match(value):
        return None
    if len(value) == 4:  # #abc -> #aabbcc
        value = "#" + "".join(ch * 2 for ch in value[1:])
    return value.upper()


def feed_queryset():
    """Products + the real "last change" time = newest of the product row and its stock/price rows."""
    return (
        ProductModel.objects.select_related("brand", "category")
        .prefetch_related(
            Prefetch(
                "color_inventories",
                queryset=ProductColorInventory.objects.select_related("color").order_by("id"),
            ),
            Prefetch("product_images", queryset=ProductImageModel.objects.order_by("created_date", "id")),
        )
        .annotate(
            _inventory_updated=Max("color_inventories__updated_date"),
        )
        .annotate(
            feed_updated_at=Greatest(
                "updated_date",
                Coalesce("_inventory_updated", "updated_date"),
                output_field=DateTimeField(),
            )
        )
    )


def _product_images(product):
    names = []
    if product.image and product.image.name and product.image.name != DEFAULT_IMAGE_NAME:
        names.append(product.image.name)
    for extra in product.product_images.all():
        if extra.file and extra.file.name and extra.file.name not in names:
            names.append(extra.file.name)
    return [_media_url(n) for n in names]


def _variants(product):
    published = product.status == ProductStatusType.publish.value
    extra_by_color = {}
    for extra in product.product_images.all():
        if extra.color_id and extra.file and extra.file.name:
            extra_by_color.setdefault(extra.color_id, []).append(_media_url(extra.file.name))

    variants = []
    for inv in product.color_inventories.all():
        price = int(inv.get_price())
        regular = int(inv.get_price_product())
        stock = int(inv.stock)
        sellable = published and price > 0 and stock > 0
        attribute = {"name": "رنگ", "value": inv.color.title, "is_color": True}
        color_code = _hex(inv.hex_color) or _hex(inv.color.hex_color)
        if color_code:
            attribute["color_code"] = color_code
        variants.append(
            {
                "id": str(inv.pk),
                "name": inv.color.title,
                "images": extra_by_color.get(inv.color_id, []),
                "price": price,
                "original_price": regular if regular > price > 0 else None,
                "is_available": sellable,
                "stock": stock if published else 0,
                "is_unlimited": False,
                "attributes": [attribute],
            }
        )
    return variants


def _placeholder_variant(product):
    # the doc: "variants" must never be empty, even for a product without real variants
    return {
        "id": f"{product.pk}-default",
        "name": product.title,
        "images": [],
        "price": 0,
        "original_price": None,
        "is_available": False,
        "stock": 0,
        "is_unlimited": False,
        "attributes": [],
    }


def _base_price(variants):
    """price / original_price / is_available of the product level (PLP), taken from its variants."""
    sellable = [v for v in variants if v["is_available"]]
    pool = sellable or [v for v in variants if v["price"] > 0] or variants
    best = min(pool, key=lambda v: v["price"])
    return best["price"], best["original_price"], bool(sellable)


def build_product(product, detail=False):
    variants = _variants(product) or [_placeholder_variant(product)]
    price, original_price, is_available = _base_price(variants)

    data = {
        "id": str(product.pk),
        "name": product.title,
        "brand": product.brand.title if product.brand_id else None,
        "source_url": f"{_site_url()}/product/{quote(product.slug, safe='')}",
        "images": _product_images(product),
        "price": price,
        "original_price": original_price,
        "is_available": is_available,
        "category_path": [product.category.title] if product.category_id else [DEFAULT_CATEGORY],
        "updated_at": _iso_utc(product.feed_updated_at),
    }
    prep_days = getattr(settings, "BWDK_DEFAULT_PREPARATION_TIME", None)
    if prep_days is not None:
        data["preparation_time_in_days"] = int(prep_days)

    if detail:
        data["description"] = product.description or ""
        data["variants"] = variants
    return data
