from datetime import datetime, timezone as dt_tz

from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import DigifyFeedPermission
from .feed import build_product, feed_queryset


def _int_param(request, name, default, minimum=0, maximum=None):
    raw = request.query_params.get(name)
    if raw in (None, ""):
        return default, None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None, f"'{name}' must be an integer."
    if value < minimum:
        return None, f"'{name}' must be >= {minimum}."
    if maximum is not None:
        value = min(value, maximum)
    return value, None


class _FeedView(APIView):
    authentication_classes = []  # key / IP check only; no session, no CSRF, no JWT
    permission_classes = [DigifyFeedPermission]
    throttle_classes = []


class ProductListFeedView(_FeedView):
    """GET /digify/v1/products/?limit=&offset=&updated_after=<unix seconds, UTC>  (PLP)"""

    def get(self, request):
        max_limit = getattr(settings, "DIGIFY_FEED_MAX_LIMIT", 200)
        default_limit = min(getattr(settings, "DIGIFY_FEED_DEFAULT_LIMIT", 100), max_limit)

        limit, error = _int_param(request, "limit", default_limit, minimum=1, maximum=max_limit)
        if error:
            return Response({"detail": error}, status=400)
        offset, error = _int_param(request, "offset", 0, minimum=0)
        if error:
            return Response({"detail": error}, status=400)
        updated_after, error = _int_param(request, "updated_after", None, minimum=0)
        if error:
            return Response({"detail": error}, status=400)

        qs = feed_queryset()
        if updated_after is None:
            qs = qs.order_by("created_date", "id")
        else:
            try:
                since = datetime.fromtimestamp(updated_after, tz=dt_tz.utc)
            except (OverflowError, OSError, ValueError):
                return Response({"detail": "'updated_after' is out of range."}, status=400)
            qs = qs.filter(feed_updated_at__gte=since).order_by("feed_updated_at", "created_date", "id")

        total = qs.count()
        page = qs[offset : offset + limit]
        return Response({"total": total, "results": [build_product(p) for p in page]})


class ProductDetailFeedView(_FeedView):
    """GET /digify/v1/products/<id>/  (PDP, with variants)"""

    def get(self, request, pk):
        product = feed_queryset().filter(pk=pk).first()
        if product is None:
            raise Http404
        return Response(build_product(product, detail=True))
