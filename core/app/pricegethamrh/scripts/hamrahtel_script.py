import requests
from requests.exceptions import Timeout, RequestException
import re


def normalize_variants(variants):
    result = []

    for variant in variants:
        color_name = None
        color_code = None

        # پیدا کردن attribute رنگ
        for attr in variant.get("attributes", []):
            if attr["attribute"]["slug"] == "color" and attr["values"]:
                color_name = attr["values"][0]["name"].strip()
                color_code = attr["values"][0]["value"]

        item = {
            "color": color_name or variant.get("name"),
            "color_code": color_code,
            "price": int(
                variant["pricing"]["price"]["gross"]["amount"]
            ),
            "quantity": variant.get("quantityAvailable", 0)
        }

        result.append(item)

    return result


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
        return f"HTTP Error: {response.status_code}"

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
