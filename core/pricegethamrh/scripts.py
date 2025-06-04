from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

def extract_product_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".mantine-ll7qhg"))
        )

        container = driver.find_element(By.CSS_SELECTOR, ".mantine-ll7qhg")
        html = container.get_attribute("innerHTML")

        soup = BeautifulSoup(html, "html.parser")
        result = {}

        blocks = soup.select(".mantine-1meq30c")
        for block in blocks:
            color_tag = block.select_one(".mantine-rj9ps7")
            color = color_tag.text.strip() if color_tag else "نامشخص"

            # قیمت با تخفیف
            price_tag = block.select_one(".mantine-1erraa9")
            price = price_tag.text.strip() if price_tag else None
            if price:
                price = price.replace(",", "").replace("٬", "").strip()
                try:
                    cleaned_price = int(price)
                except ValueError:
                    cleaned_price = None
            else:
                cleaned_price = None

            # قیمت بدون تخفیف
            old_price_tag = block.select_one(".mantine-vpcnae")
            old_price = old_price_tag.text.strip() if old_price_tag else None
            if old_price:
                old_price = old_price.replace(",", "").replace("٬", "").strip()
                try:
                    cleaned_old_price = int(old_price)
                except ValueError:
                    cleaned_old_price = None
            else:
                cleaned_old_price = None

            # تخفیف به صورت عدد صحیح
            discount_tag = block.select_one(".mantine-1fdpe25")
            if discount_tag:
                discount_text = discount_tag.text.strip().replace("٪", "").replace("%", "").strip()
                try:
                    discount = int(discount_text)
                except ValueError:
                    discount = None
            else:
                discount = None

            result[color] = {
                "color": color,
                "price": cleaned_price,
                "old_price": cleaned_old_price,
                "discount_persent": discount
            }
       
    finally:
        driver.quit()

    return result
