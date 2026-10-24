
import requests
import re
from requests.exceptions import RequestException, Timeout


GRAPHQL_URL = "https://core-api.hamrahtel.com/graphql/"


def normalize_variants(variants):
    result = []

    for variant in variants or []:
        try:
            pricing = variant.get("pricing") or {}
            price_obj = pricing.get("price") or {}
            gross = price_obj.get("gross") or {}
            amount = gross.get("amount")

            if amount is None:
                continue

            color_name = None
            color_code = None

            for attr in variant.get("attributes", []):
                attribute = attr.get("attribute") or {}

                if attribute.get("slug") == "color":
                    values = attr.get("values") or []

                    if values:
                        color_name = values[0].get("name")
                        color_code = values[0].get("value")
                    break

            result.append({
                "color": color_name or variant.get("name"),
                "color_code": color_code,
                "price": int(amount),
                "quantity": variant.get("quantityAvailable") or 0,
            })

        except (TypeError, ValueError, AttributeError):
            continue

    return result or None


def extract_product_data(url):
    match = re.search(r"/products/([^/?#]+)", url)

    if not match:
        return None

    slug = match.group(1)

    query = """
    query ProductDetailV2(
        $slug: String!,
        $channel: String = "customer"
    ) {
        publicProductV2(slug: $slug, channel: $channel) {
            id
            name
            slug
            isAvailable
            isAvailableForPurchase
            variants {
                id
                name
                quantityAvailable
                attributes {
                    attribute {
                        name
                        slug
                    }
                    values {
                        name
                        value
                    }
                }
                pricing {
                    price {
                        gross {
                            amount
                        }
                    }
                }
            }
        }
    }
    """

    payload = {
        "operationName": "ProductDetailV2",
        "variables": {
            "channel": "customer",
            "slug": slug,
        },
        "query": query,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://hamrahtel.com/",
    }

    try:
        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

    except (Timeout, RequestException, ValueError) as exc:
        print(f"Request error: {exc}")
        return None

    if data.get("errors"):
        print("GraphQL errors:", data["errors"])
        return None

    product = (data.get("data") or {}).get("publicProductV2")

    if not product:
        print("Product not found:", data)
        return None

    variants = product.get("variants") or []
    normalized = normalize_variants(variants)

    return normalized


# if __name__ == "__main__":
#     url = (
#         "https://hamrahtel.com/products/"
#         "xiaomi-15t-5g-512gb-ram-12gb"
#     )

#     print(extract_product_data(url))
