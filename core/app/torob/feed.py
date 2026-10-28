"""Builds the Torob API v3 product objects.

Torob works on *pages*: every colour of a product is its own page (`page_unique`), all colours of one
product share `product_group_id`.

    page_unique        = "<product id>_<inventory id>"
    product_group_id   = "<product id>"
    page_url           = <site>/product/<slug>?variant=<inventory id>     (the storefront preselects it)
"""
import html
from datetime import datetime
from urllib.parse import parse_qs, quote, unquote, urlparse

from django.conf import settings
from django.db.models import DateTimeField
from django.db.models.functions import Greatest
from django.utils import timezone
from django.utils.html import strip_tags

from app.shop.models import ProductColorInventory
from app.shop.models.products import ProductStatusType

PAGE_SIZE = 100
DEFAULT_IMAGE_NAME = "default/product-image.png"
SORT_ADDED = "date_added_desc"
SORT_UPDATED = "date_updated_desc"
SORT_ID = "product_id_desc"
SORTS = (SORT_ADDED, SORT_UPDATED, SORT_ID)


def _site_url():
    return getattr(settings, "TOROB_SITE_URL", "https://manmarket.ir").rstrip("/")


def _media_url(name):
    base = getattr(settings, "TOROB_MEDIA_BASE_URL", "https://api.manmarket.ir").rstrip("/")
    prefix = str(settings.MEDIA_URL).strip("/")
    path = f"{prefix}/{name.lstrip('/')}" if prefix else name.lstrip("/")
    return f"{base}/{path}"


def _iso(value):
    """Timezone-aware ISO 8601 in the project's timezone (e.g. 2026-10-27T10:15:12+03:30)."""
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
    return timezone.localtime(value).isoformat(timespec="seconds")


def _text(value, limit):
    value = html.unescape(strip_tags(value or "")).strip()
    value = " ".join(value.split())
    return value[:limit] or None


def variant_queryset():
    """One row per sellable colour of every *published* product. Rows are the unit Torob lists."""
    return (
        ProductColorInventory.objects.filter(
            product__status=ProductStatusType.publish.value,
            price__gt=0,  # no price at all -> nothing to show on Torob
        )
        .select_related("product", "product__category", "color")
        .prefetch_related("product__product_images", "product__specifications")
        .annotate(
            _changed_at=Greatest("product__updated_date", "updated_date", output_field=DateTimeField())
        )
    )


def order_queryset(qs, sort):
    if sort == SORT_ADDED:
        return qs.order_by("-product__created_date", "-id")
    if sort == SORT_UPDATED:
        return qs.order_by("-_changed_at", "-id")
    return qs.order_by("-id")


def _images(inv):
    product = inv.product
    main = []
    if product.image and product.image.name and product.image.name != DEFAULT_IMAGE_NAME:
        main.append(product.image.name)
    extras = [i for i in product.product_images.all() if i.file and i.file.name]
    own = [i.file.name for i in extras if i.color_id == inv.color_id]
    names = own or (main + [i.file.name for i in extras])  # option's own photos win (Torob rule)
    seen, result = set(), []
    for name in names:
        if name not in seen:
            seen.add(name)
            result.append(_media_url(name))
    return result


def build_item(inv):
    product = inv.product
    price = int(inv.get_price())
    regular = int(inv.get_price_product())

    spec = {}
    for s in product.specifications.all():
        if s.status and s.name and s.value:  # same rule the storefront uses (only active specs)
            spec[s.name.strip()[:200]] = s.value.strip()
    spec.setdefault("رنگ", inv.color.title)

    added = product.created_date
    changed = max(product.updated_date, inv.updated_date, added)
    return {
        "page_unique": f"{product.pk}_{inv.pk}",
        "page_url": f"{_site_url()}/product/{quote(product.slug, safe='')}?variant={inv.pk}",
        "product_group_id": str(product.pk),
        "title": product.title[:500],
        "subtitle": None,
        "current_price": price,
        "old_price": regular if regular > price else None,
        "availability": inv.stock > 0 and price > 0,
        "category_name": product.category.title[:200] if product.category_id else None,
        "image_links": _images(inv),
        "spec": spec,
        "guarantee": (product.warranty or "").strip()[:200] or None,
        "short_desc": _text(product.brief_description, 500),
        "date_added": _iso(added),
        "date_updated": _iso(changed),
    }


# ---- lookups -------------------------------------------------------------------------------------

def items_by_uniques(uniques):
    wanted = {}
    for value in uniques:
        left, sep, right = str(value).partition("_")
        if sep and left.isdigit() and right.isdigit():
            wanted[value] = (int(left), int(right))
    rows = {inv.pk: inv for inv in variant_queryset().filter(pk__in={i for _, i in wanted.values()})}
    result, seen = [], set()
    for value in uniques:
        pid_iid = wanted.get(value)
        inv = rows.get(pid_iid[1]) if pid_iid else None
        if inv and inv.product_id == pid_iid[0] and inv.pk not in seen:
            seen.add(inv.pk)
            result.append(build_item(inv))
    return result


def _default_variant(variants):
    """Mirror of the storefront: lowest list price among priced colours, ties -> first one."""
    best = None
    for inv in variants:
        if inv.price > 0 and (best is None or inv.price < best.price):
            best = inv
    return best


def _parse_page_url(url):
    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")
    if not path.startswith("product/"):
        return None, None
    slug = path[len("product/"):].strip("/")
    variant = parse_qs(parsed.query).get("variant", [None])[0]
    return slug or None, (int(variant) if variant and variant.isdigit() else None)


def items_by_urls(urls):
    parsed = [_parse_page_url(u) for u in urls]
    slugs = {slug for slug, _ in parsed if slug}
    by_slug = {}
    for inv in variant_queryset().filter(product__slug__in=slugs).order_by("id"):
        by_slug.setdefault(inv.product.slug, []).append(inv)

    result, seen = [], set()
    for slug, variant_id in parsed:
        variants = by_slug.get(slug or "", [])
        inv = next((v for v in variants if v.pk == variant_id), None) if variant_id else None
        inv = inv or _default_variant(variants)  # no/unknown ?variant -> what the page shows by default
        if inv and inv.pk not in seen:
            seen.add(inv.pk)
            result.append(build_item(inv))
    return result
