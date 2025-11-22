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




def get_kasrapars_product_data(url):
    match = re.search(r'/product/([^/?#]+)', url)
    if not match:
        return {"error": "❌ آدرس نامعتبر است یا slug پیدا نشد."}

    slug = match.group(1)

    api_url = (
        f'https://api.kasrapars.ir/api/web/v10/product/slug?slug={slug}&expand='
        'is_wish,priceQuality,review,review.items,surveyScores,letMeKnow,images,category,'
        'categoryParents,groupedFeatures,letMeKnowOnAvailability,variety.letMeKnowOnAvailability,'
        'varieties,cartFeatures,coworkerShortName,src,isInWishList,varieties.promotionCoworker,'
        'varieties.color,varieties.canBuyWithBnPlByUser,activeVarietyId,varieties.guarantee,'
        'varieties.company,varieties.pack,varieties.company.surveyStats,varieties.company.city,'
        'videos,surveyCount,surveyAverageScore,questionCount,varieties.company.present_sell,'
        'reserveCeilCount,varieties.prePayment'
    )

    response = requests.get(api_url)

    if response.status_code != 200:
        return {"error": f"❌ خطا در درخواست: {response.status_code}, پاسخ: {response.text}"}

    data = response.json()
    varieties = data.get('varieties', [])

    result = {}

    for variety in varieties:
        color_data = variety.get('color')
        
        if isinstance(color_data, dict):
            color_name = color_data.get('color_name', 'نامشخص')
            color_code = color_data.get('hexcode', None)
        else:
            color_name = 'نامشخص'
            color_code = None

        price = variety.get('price_main') or 0
        quantity = variety.get('stock_count') or 1

        if quantity == 0:
            price = 0

        result[color_name] = {
            "color": color_name,
            "color_code": color_code,
            "price": (int(price)/10),
            "quantity": quantity
        }

    return result


# print(get_kasrapars_product_data("https://plus.kasrapars.ir/product/xiaomi-redmi-pb200lzm-power-bank-20000-mah-with-microusb-conversion-cable"))