import requests
import re
from requests.exceptions import RequestException, Timeout


def get_kasrapars_product_data(url):
    match = re.search(r'/product/([^/?#]+)', url)
    if not match:
        return None

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

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except (RequestException, Timeout):
        return None

    data = response.json()
    varieties = data.get('varieties')

    if not varieties:
        return None

    result = []

    for variety in varieties:
        color_data = variety.get('color') or {}

        color_name = color_data.get('color_name')
        color_code = color_data.get('hexcode')

        if not color_name:
            continue

        price = variety.get('price_co_worker') or 0
        quantity = variety.get('stock_count') or 1

        # اگر موجودی صفر بود → قیمت صفر
        if price == 0 or price == "0" :
            quantity = 0

        result.append({
            "color": color_name.strip(),
            "color_code": color_code,
            "price": int(price) // 10,  # تبدیل ریال به تومان
            "quantity": int(quantity),
        })

    return result if result else None




# print(get_kasrapars_product_data("https://plus.kasrapars.ir/product/xiaomi-redmi-pb200lzm-power-bank-20000-mah-with-microusb-conversion-cable"))