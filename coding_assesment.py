import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Accept-Language": "en-US, en;q=0.5",
}


def find_results_for_keyword(keyword, max_products):
    search_query = keyword.replace(" ", "+")
    base_url = "https://www.amazon.com/s?k={0}".format(search_query)
    items = []
    completed = False
    page_count = 1
    while not completed:
        print("Processing {0}...".format(base_url + f"&page={page_count}"))
        response = requests.get(
            base_url + f"&page={page_count}", headers=headers, timeout=5
        )
        page_count += 1
        soup = BeautifulSoup(response.content, "html.parser")

        results = soup.find_all(
            "div", {"class": "s-result-item", "data-component-type": "s-search-result"}
        )
        if not len(results):
            completed = True

        for result in results:
            product_name = result.h2.text.split(",")[0]
            if len(items) > max_products:
                completed = True
                break

            try:
                rating = result.find("i", {"class": "a-icon"}).text
                rating_count = result.find_all("span", {"aria-label": True})[1].text
            except AttributeError:
                continue

            try:
                price1 = result.find("span", {"class": "a-price-whole"}).text
                price2 = result.find("span", {"class": "a-price-fraction"}).text
                whole_price_str = (price1 + price2).replace(",", "")
                price = float(whole_price_str)
                # product_url = 'https://amazon.com' + result.h2.a['href']

                # Additional details
                # brand = result.find('span', {'class': 'a-size-base-plus'}).text
                description = result.find("div", {"class": "sg-col-inner"}).text.strip()
                idx = description.index(product_name)
                description = description[idx:]

                items.append(
                    [
                        product_name,
                        rating,
                        rating_count,
                        price,
                        description,
                    ]
                )
            except AttributeError:
                continue
        sleep(1.5)

    df = pd.DataFrame(
        items, columns=["product-title", "rating", "reviews", "price", "description"]
    )
    df.to_csv(
        "{0}.csv".format(search_query),
        index=False,
    )


def main():
    keyword = input("Enter the product you want to search: ")
    max_products = 2000
    find_results_for_keyword(keyword, max_products)


if __name__ == "__main__":
    main()
