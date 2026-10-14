import requests
from django.conf import settings

BASE_URLS = {
    "sandbox": "https://bwdk-backend-sandbox.digify.shop",
    "production": "https://bwdk-backend.digify.shop",
}


class BWDKError(Exception):
    """Raised for network problems and for HTTP >= 400 answers of the BWDK API."""

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}

    @property
    def detail(self):
        if isinstance(self.payload, dict):
            for key in ("detail", "message", "error"):
                if self.payload.get(key):
                    return str(self.payload[key])
        return str(self)


def get_base_url():
    override = getattr(settings, "BWDK_BASE_URL", "")
    if override:
        return override.rstrip("/")
    env = getattr(settings, "BWDK_ENV", "sandbox")
    return BASE_URLS.get(env, BASE_URLS["sandbox"])


class BWDKClient:
    """HTTP client for Digikala Buy With Digikala (BWDK). Methods return the JSON body
    and raise BWDKError on network errors / HTTP errors."""

    def __init__(self, api_key=None):

        self.api_key = (api_key or getattr(settings, "BWDK_API_KEY", "")).strip()

        if self.api_key.lower().startswith("api-key "):
            self.api_key = self.api_key.split(None, 1)[1].strip()

        if not self.api_key:
            raise RuntimeError("BWDK_API_KEY is not configured.")

        self.base_url = get_base_url()

    @property
    def headers(self):
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(
                method, url, headers=self.headers, timeout=(5, 25), **kwargs
            )
        except requests.RequestException as exc:
            raise BWDKError(f"BWDK network error: {exc}") from exc

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text[:500]}

        if response.status_code >= 400:
            raise BWDKError(
                f"BWDK {method} {path} -> HTTP {response.status_code}",
                status_code=response.status_code,
                payload=data,
            )
        return data

    def create_order(self, payload):
        return self._request("POST", "/orders/api/v1/create-order/", json=payload)

    def get_order(self, order_uuid):
        return self._request("GET", f"/orders/api/v1/manager/{order_uuid}/")

    def verify_order(self, order_uuid, merchant_unique_id):
        # the doc requires merchant_unique_id in the body
        return self._request(
            "POST",
            f"/orders/api/v1/manager/{order_uuid}/verify/",
            json={"merchant_unique_id": str(merchant_unique_id)},
        )

    def refund_order(self, order_uuid, reason, amount):
        return self._request(
            "POST",
            f"/orders/api/v1/manager/{order_uuid}/refund/",
            json={"reason": reason, "amount": int(amount)},
        )
