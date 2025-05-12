import re
import requests


def getspecificationDigikala(url):
    match = re.search(r"dkp-(\d+)", url)
    if match:
        product_url = match.group(1)
        api_url = f'https://api.digikala.com/v2/product/{product_url}/'
        response = requests.get(api_url)
        response_json = response.json()
        data_specifications = response_json['data']['product']['specifications']

        item_list = {}
        for item in data_specifications:
            all_item = item['attributes']
            for items in all_item:
                values = items.get('values', [])
                if values:
                    # تبدیل لیست به رشته با جداکننده‌ی " / "
                    item_list[items['title']] = " / ".join(values)
        return item_list
   