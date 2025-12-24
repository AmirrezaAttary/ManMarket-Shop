import requests
from requests.exceptions import Timeout, RequestException
import re


def normalize_variants(variants):
    result = []

    for variant in variants:
        try:
            pricing = variant.get("pricing") or {}
            price_obj = pricing.get("price") or {}
            gross = price_obj.get("gross") or {}
            amount = gross.get("amount")

            if amount is None:
                continue  # ⬅️ این variant رو رد کن

            color_name = None
            color_code = None

            for attr in variant.get("attributes", []):
                if attr.get("attribute", {}).get("slug") == "color":
                    values = attr.get("values") or []
                    if values:
                        color_name = values[0].get("name")
                        color_code = values[0].get("value")

            result.append({
                "color": color_name or variant.get("name"),
                "color_code": color_code,
                "price": int(amount),
                "quantity": variant.get("quantityAvailable") or 0,
            })

        except Exception:
            # ⬅️ اگر یک variant خراب بود، کل محصول خراب نشه
            continue

    return result if result else None



def extract_product_data(url):
    graphql_url = "https://core-api.hamrahtel.com/graphql/"
    
    query = """
    query productDetail($slug: String!) {
      publicProduct(slug: $slug) {
        variants {
          name
          quantityAvailable
          pricing {
            price {
              gross {
                amount
              }
            }
          }
          attributes {
            attribute {
              slug
              name
            }
            values {
              name
              value
            }
          }
        }
      }
    }
    """

    match = re.search(r'/products/([^/]+)', url)
    if not match:
        return None

    slug = match.group(1)

    payload = {
        "query": query,
        "variables": {"slug": slug}
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            graphql_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    except Timeout:
        return None
    except RequestException as e:
        return None
    except requests.exceptions.RequestException:
        return None
    if response.status_code != 200:
        return None

    data = response.json()

    # ✅ بررسی مرحله‌به‌مرحله
    product = data.get("data", {}).get("publicProduct")

    if not product:
        return None

    variants = product.get("variants")

    if not variants:
        return None
    normal_var = normalize_variants(variants)
    return normal_var



# variants = extract_product_data(
#     "https://hamrahtel.com/products/blackview-color-6-128gb-ram-8gb"
# )
# print(variants)
