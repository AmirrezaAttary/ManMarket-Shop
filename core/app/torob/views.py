import json
import math

from django.http import JsonResponse
from rest_framework.views import APIView

from .auth import TorobAuthError, verify_request
from .feed import (
    PAGE_SIZE,
    SORT_ID,
    SORTS,
    build_item,
    items_by_uniques,
    items_by_urls,
    order_queryset,
    variant_queryset,
)

API_VERSION = "torob_api_v3"


class BadRequest(Exception):
    pass


def _error(message, status):
    return JsonResponse({"error": message}, status=status, json_dumps_params={"ensure_ascii": False})


def _string_list(body, key):
    value = body.get(key)
    if not isinstance(value, list) or not value:
        raise BadRequest(f"{key} must be a non-empty list of strings")
    if not all(isinstance(v, str) and v for v in value):
        raise BadRequest(f"{key} must be a non-empty list of strings")
    return value


def parse_body(raw):
    """Torob's rule: no defaults at all. Exactly one of the four documented shapes, nothing else."""
    if not raw or not raw.strip():
        raise BadRequest("request body is empty")
    try:
        body = json.loads(raw)
    except ValueError:
        raise BadRequest("request body is not valid JSON")
    if not isinstance(body, dict):
        raise BadRequest("request body must be a JSON object")
    if not body:
        raise BadRequest("no parameters provided")

    keys = set(body)
    for mode in ("page_urls", "page_uniques"):
        if mode in keys:
            if keys != {mode}:
                raise BadRequest(f"{mode} cannot be combined with other parameters")
            return mode, _string_list(body, mode)

    unknown = keys - {"page", "sort", "cursor"}
    if unknown:
        raise BadRequest(f"unknown parameter(s): {', '.join(sorted(unknown))}")
    if "sort" not in body:
        raise BadRequest("sort parameter is not provided")
    sort = body["sort"]
    if sort not in SORTS:
        raise BadRequest(f"sort must be one of: {', '.join(SORTS)}")

    if sort == SORT_ID:
        if "page" in body:
            raise BadRequest("page is not supported with sort=product_id_desc (use cursor)")
        cursor = body.get("cursor")
        if "cursor" in body and (not isinstance(cursor, str) or not cursor.isdigit()):
            raise BadRequest("cursor must be the next_cursor string of the previous response")
        return "cursor", {"cursor": int(cursor) if cursor is not None else None}

    if "cursor" in body:
        raise BadRequest("cursor is only supported with sort=product_id_desc")
    if "page" not in body:
        raise BadRequest("page parameter is not provided")
    page = body["page"]
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise BadRequest("page must be an integer >= 1")
    return "page", {"page": page, "sort": sort}


class TorobProductsView(APIView):
    """POST /torob_api/v3/products"""

    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    http_method_names = ["post", "options"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return _error("method not allowed, use POST", 405)

    def post(self, request):
        try:
            verify_request(request)
        except TorobAuthError as exc:
            return _error(str(exc), 401)

        try:
            mode, params = parse_body(request.body)
        except BadRequest as exc:
            return _error(str(exc), 400)

        if mode in ("page_urls", "page_uniques"):
            items = items_by_urls(params) if mode == "page_urls" else items_by_uniques(params)
            payload = {
                "api_version": API_VERSION,
                "current_page": 1,
                "total": len(items),
                "max_pages": 1,
                "next_cursor": None,
                "products": items,
            }
        elif mode == "page":
            qs = order_queryset(variant_queryset(), params["sort"])
            total = qs.count()
            start = (params["page"] - 1) * PAGE_SIZE
            payload = {
                "api_version": API_VERSION,
                "current_page": params["page"],
                "total": total,
                "max_pages": max(1, math.ceil(total / PAGE_SIZE)),
                "next_cursor": None,
                "products": [build_item(inv) for inv in qs[start : start + PAGE_SIZE]],
            }
        else:  # cursor
            qs = order_queryset(variant_queryset(), SORT_ID)
            if params["cursor"] is not None:
                qs = qs.filter(pk__lt=params["cursor"])
            rows = list(qs[: PAGE_SIZE + 1])
            page_rows, has_more = rows[:PAGE_SIZE], len(rows) > PAGE_SIZE
            payload = {
                "api_version": API_VERSION,
                "total": None,
                "max_pages": None,
                "next_cursor": str(page_rows[-1].pk) if has_more else None,
                "products": [build_item(inv) for inv in page_rows],
            }
        return JsonResponse(payload, json_dumps_params={"ensure_ascii": False})
