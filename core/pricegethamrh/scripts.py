import requests
import re

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
        return "Slug not found in URL."

    slug = match.group(1)

    payload = {
        "query": query,
        "variables": {"slug": slug}
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(graphql_url, json=payload, headers=headers)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    data = response.json()
    variants = data.get('data', {}).get('publicProduct', {}).get('variants', [])

    result = {}

    for variant in variants:
        color_name = None
        color_code = None
        for attr in variant.get('attributes', []):
            if attr.get('attribute', {}).get('slug') == 'color':
                values = attr.get('values', [])
                if values:
                    color_name = values[0].get('name')
                    color_code = values[0].get('value')

        quantity = variant.get("quantityAvailable", 0)

        pricing = variant.get('pricing')
        price = 0

        if pricing and pricing.get('price') and pricing['price'].get('gross'):
            price = pricing['price']['gross'].get('amount', 0)

        if quantity == 0:
            price = 0

        if color_name:
            result[color_name] = {
                "color": color_name,
                "color_code": color_code,
                "price": int(price),
                "quantity" : quantity
            }

    return result





# print(extract_product_data('https://hamrahtel.com/products/nothing-phone-2a-plus-256gb-ram-12gb'))