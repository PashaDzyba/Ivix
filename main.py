import json
import os
import time

import requests
from bs4 import BeautifulSoup


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,uk;q=0.6",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla /5.0 (Macintosh;Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36(KHTML, likeGecko) Chrome/107.0.0.0 Safari/537.36"
}


def get_all_pages():
    """This function finds all of the pages with businesses with specific category and country  """

    # This lines of code is only to save data on local machine for easier usage

    req = requests.get(url="https://www.yelp.com/search?cflt=contractors&find_loc=San+Francisco%2C+CA", headers=headers)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/yelp.html", 'w') as file:
        file.write(req.text)

    with open("data/yelp.html") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Page_count variable is finding out how many pages in pagination are, so it can go throug every page and find an info

    pages_count = int(soup.find("div", class_='border-color--default__09f24__NPAKY text-align--center__09f24__fYBGO'). \
                      find("span").text.split()[2])

    # You can change pages_count in for loop with another number but so it doesnt goes on every page in pagination

    for i in range(1, pages_count + 1):
        url = f"https://www.yelp.com/search?cflt=contractors&find_loc=San+Francisco%2C+CA&start={(i * 10) - 10}"
        r = requests.get(url=url, headers=headers)

        # This will save every page in specific number html file

        with open(f"data/yelp_page{i}.html", "w") as file:
            file.write(r.text)

        time.sleep(8)

    return pages_count + 1


def collect_data(pages_count):
    """This function collects all of the data and saves it in json file"""
    for page in range(2, 5):
        with open(f"data/yelp_page{page}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        businesses = soup.find_all("div",
                                   class_="businessName__09f24__EYSZE")

        project_urls = []
        for business in businesses:
            if business is None:
                continue
            project_url = "https://www.yelp.com/" + business.find("span", class_="css-1egxyvc").find("a").get('href')

            project_urls.append(project_url)

        project_data_list = []
        for project_url in project_urls:
            req = requests.get(project_url, headers)
            business_name = project_url.split("/")[-1]

            if not os.path.exists("pages_data"):
                os.mkdir("pages_data")

            with open(f"pages_data/{business_name}.html", 'w') as file:
                file.write(req.text)

            time.sleep(8)

            with open(f"pages_data/{business_name}.html") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")

            main_table = soup.find("div", class_="margin-t3__09f24__riq4X margin-b6__09f24__wgl48 "
                                                 "border-color--default__09f24__NPAKY")
            print(main_table)
            try:
                business_name = main_table.find("div", class_="margin-b1__09f24__vaLrm border-color--default__09f24__NPAKY") \
                    .find('h1').text
            except Exception:
                business_name = "No business name"
            try:
                business_rating = main_table.find("div", class_="five-stars__09f24__mBKym five-stars--large__09f24__Waiqf "
                                                                "display--inline-block__09f24__fEDiJ "
                                                                "border-color--default__09f24__NPAKY")['aria-label']
            except Exception:
                business_rating = "No business rating"
            try:
                number_of_reviews = main_table.find("div",
                                                    class_="arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG"
                                                           " border-color--default__09f24__NPAKY nowrap__09f24__lBkC2"). \
                    find("a").text
            except Exception:
                number_of_reviews = "No number of reviews"
            try:
                business_url = main_table.find("div",
                                               class_="css-xp8w2v"). \
                    find("p", class_="css-1p9ibgf").find("a", class_="css-1um3nx").text
            except Exception:
                business_url = "No business url"

            reviews_table = soup.find_all("div", class_="review__09f24__oHr9V")

            review_data = []
            for reviews in reviews_table:
                try:
                    reviewer_name = reviews.find('div', class_="user-passport-info"). \
                        find("span", class_="fs-block css-ux5mu6").text
                except Exception:
                    reviewer_name = "No reviewer name"
                try:
                    reviewer_location = reviews.find("div", class_="responsive-hidden-small__09f24__qQFtj"). \
                        find("span", class_='css-qgunke').text
                except Exception:
                    reviewer_location = "No reviewer location"
                try:
                    reviewer_date = reviews.find("div", class_="margin-t1__09f24__w96jn"). \
                        find('div', class_="arrange__09f24__LDfbs").find('span', class_="css-chan6m").text
                except Exception:
                    reviewer_date = "No reviewer date"
                review_data.append({
                    "reviewer_name": reviewer_name,
                    "reviewer_location": reviewer_location,
                    "reviewer_date": reviewer_date
                })

            project_data_list.append({
                "business_name": business_name,
                "business_rating": business_rating,
                "number_of_reviews": number_of_reviews,
                "business_yelp_url": project_url,
                "business_url": business_url,
                "review_data": review_data[:5]
            })

        with open("business_data.json", "a", encoding="utf-8") as file:
            json.dump(project_data_list, file, indent=4, ensure_ascii=False)

        # Last block of code will remove all files in page_data directory



def main():
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)


if __name__ == "__main__":
    main()
