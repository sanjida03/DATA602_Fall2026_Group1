import requests
from bs4 import BeautifulSoup


URL = "https://www.ulta.com/shop/makeup/face/foundation?sort=best_sellers"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(URL, headers=HEADERS, timeout=10)
response.raise_for_status()

print("Status code:", response.status_code)
print("HTML length:", len(response.text))


soup = BeautifulSoup(response.text, "html.parser")

product_list = soup.find(
    "ul",
    attrs={"data-test": "products-list"}
)

print("Product list found:", product_list is not None)

products = product_list.find_all(
    "li",
    attrs={"data-test": "products-list-item"}
)

print("Products found:", len(products))

product_names = []

for product in products:
    name_tag = product.find(
        "span",
        class_="pal-c-Text__isScreenReader"
    )

    if name_tag:
        product_names.append(name_tag.get_text(strip=True))


print("Product names found:", len(product_names))

for number, name in enumerate(product_names, start=1):
    print(f"{number}. {name}")