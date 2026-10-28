"""Validation of the JWT that Torob sends in `X-Torob-Token` (EdDSA / ed25519, signed by Torob).

Checks: signature (Torob public key), `exp`, and `aud` == the API's own host.
"""
import jwt
from django.conf import settings


class TorobAuthError(Exception):
    pass


def _public_key_pem():
    raw = getattr(settings, "TOROB_PUBLIC_KEY", "").strip()
    if raw.startswith("-----BEGIN"):
        return raw
    # a bare base64 DER body (as printed in Torob's guide) -> PEM
    return f"-----BEGIN PUBLIC KEY-----\n{raw}\n-----END PUBLIC KEY-----"


def _expected_audiences(request):
    configured = list(getattr(settings, "TOROB_ALLOWED_AUDIENCES", []))
    if configured:
        return configured
    # Fallback: the Host header. Prefer configuring TOROB_ALLOWED_AUDIENCES: the Host header is
    # chosen by the caller, so a token issued to another shop could be replayed with a forged Host.
    return [request.META.get("HTTP_HOST", "")]


def verify_request(request):
    token = request.META.get("HTTP_X_TOROB_TOKEN", "").strip()
    if not token:
        raise TorobAuthError("X-Torob-Token header is missing")
    try:
        jwt.decode(
            token,
            key=_public_key_pem(),
            algorithms=["EdDSA"],
            audience=_expected_audiences(request),
            options={"require": ["exp", "aud"]},
            leeway=int(getattr(settings, "TOROB_TOKEN_LEEWAY_SECONDS", 30)),
        )
    except jwt.PyJWTError as exc:
        raise TorobAuthError(f"invalid token: {exc}") from exc
