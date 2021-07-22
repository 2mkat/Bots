#!/usr/bin/env python3
from re import findall
from typing import List, Any
import json

from requests import get


class products_titile:

    def __init__(self, name, price, sale):
        self.name = name
        self.old_price = price
        self.all_sale = sale

class Products(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, products_titile):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

def parse_price(products_list: list) -> None:
    sale = 0
    all_products = []

    for product in products_list:
        resp_product = get(product)

        if resp_product.status_code != 200:
            return 1

        text_resp = resp_product.text
        parse_str = findall(r"\"product_title entry-title\">.*", text_resp)
        name_product: list[Any] = findall(r"\"product_title entry-title\">(.*)<\/h1>", str(parse_str))
        first_price_product = findall(r"</span>(.*)</bdi></span></del>", str(parse_str))
        second_price_product = findall(r"(\d+.\d+)</bdi></span></ins>", str(parse_str))
        sale_product = False
        if first_price_product and second_price_product != []:
            sale_product = True
            sale = 100 - (float(second_price_product[0]) * 100) / float(first_price_product[0])

        if sale_product:
            subject = products_titile(name_product[0], second_price_product[0], sale)
            all_products.append(subject)

    with open('sale.json', "w") as outfile:
        json.dump(all_products, outfile, cls=Products, indent=4)
        outfile.write('\n')


def scrape_bot(url):
    resp = get(url)

    if resp.status_code != 200:
        return 1

    products = []
    for idx in range(1, 11):
        resp = get(F"{url}/page/{idx}/")
        if resp.status_code == 200:
            text_resp = resp.text
            sale_products = findall(r"\"(http://shop\.ghostin\.space/product/.*/)\"", text_resp)
            products.extend(sale_products)
            continue
        break

    products: list[Any] = list(set(products))  # delete duplicates

    return products


if __name__ == "__main__":
    str_url = "http://shop.ghostin.space/shop/"
    product_list = scrape_bot(str_url)
    parse_price(product_list)
