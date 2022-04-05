
from typing import Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from product import Product

# Retrieves products from the tesla website
class OnlineProductRetriever:
    
    def __init__(self, base_url: str = 'https://shop.tesla.com'):
        self.base_url = base_url

    def set_paths(self, product_paths:list[str] = []):
        self.product_paths = product_paths

    def retrieve_products(self, url: str) -> Optional[set[Product]]:

        items = set[Product]()

        response = requests.get(url)

        if response.status_code != 200:
            print('Server Error: Unable to retrieve products from {}'.format(url))
            return None

        if len(response.text) == 0:
            print('Server Error: Empty response')
            return None

        bs = BeautifulSoup(response.text, features="html.parser")

        img = bs.find_all("li", { 'class': 'product-tile__item' })

        if len(img) == 0:
            print('Parse Error: Unabel to find tags')
            return False

        #  The last part of the url is the catagory
        product_category = url.split('/')[-1].replace('-', ' ').upper()

        for child in img:
            link = child.find('div', { 'class': 'product-tile__name' }).div.a
            price = child.find('p', { 'class': 'product-tile__price' })

            product_id = link['data-productsku']
            product_name = link.text
            product_link = urljoin(self.base_url, link['href'])
            product_price = price.text

            #  We took an L here...
            if product_id is None:
                continue

            item = Product(product_id, product_name, product_price, product_link, product_category)

            items.add(item)
        
        return items

    def retrieve_all(self) -> set[Product]:
        
        products = set[Product]()

        for url_path in self.product_paths:

            full_path = urljoin(self.base_url, url_path)
            products_for_page = self.retrieve_products(full_path)

            #  ERROR: we were not able to retrieve any products due to a server error
            if products_for_page is None:
                continue

            products.update(products_for_page)

        return products