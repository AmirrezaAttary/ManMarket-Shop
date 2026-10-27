import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _presented_key(request):
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header.lower().startswith("api-key "):
        return header[8:].strip()
    return request.META.get("HTTP_X_API_KEY", "").strip()


class DigifyFeedPermission(BasePermission):
    """Optional protection of the catalog feed.

    * DIGIFY_FEED_API_KEY empty  -> the feed is public (the Digify doc allows that).
    * DIGIFY_FEED_API_KEY set    -> `Authorization: Api-Key <key>` or `X-Api-Key: <key>` is required.
    * DIGIFY_FEED_ALLOWED_IPS    -> if not empty, only these IPs may read the feed.
    """

    message = "Invalid or missing API key."

    def has_permission(self, request, view):
        allowed_ips = getattr(settings, "DIGIFY_FEED_ALLOWED_IPS", [])
        if allowed_ips and _client_ip(request) not in allowed_ips:
            self.message = "IP address is not allowed."
            return False

        expected = getattr(settings, "DIGIFY_FEED_API_KEY", "")
        if not expected:
            return True
        return hmac.compare_digest(_presented_key(request).encode(), expected.encode())
