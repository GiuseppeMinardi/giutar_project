import csv
from typing import Iterable
from random import uniform
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

GUITAR_ST_URL = "https://www.thomann.de/it/modelli_st.html"


def click_cookies():
    cookies = chrome_driver.find_element_by_class_name("cookie-consent-button.js-accept-all-cookies")
    if cookies.is_displayed():
        cookies.click()


def get_guitar_links(driver):
    guitar_links = []
    while True:
        try:
            next_page_button = driver.find_element_by_css_selector('a.button.next')
        except NoSuchElementException:
            break
        guitars_in_page = driver.find_elements_by_css_selector("#defaultResultPage > div > div.left > div > a")
        guitar_links_in_page = [guitar.get_attribute("href") for guitar in guitars_in_page]

        guitar_links += guitar_links_in_page
        driver.get(next_page_button.get_attribute("href"))

    return guitar_links


def create_csv(guitar_links: Iterable[str]):
    header = ["Name", "Brand", "Colour", "Body",
              "Top", "Neck", "Fretboard", "Frets", "Scale",
              "Pickups", "Tremolo", "Bag", "Case", "Price"]
    with open("st_guitars_from_thomann.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(header)
        for number, guitar_link in enumerate(guitar_links):
            #click_cookies()
            print(number, "\t", guitar_link)
            chrome_driver.get(guitar_link)
            price = chrome_driver.find_element_by_css_selector("div.prod-pricebox-price").get_attribute("innerText")
            name = chrome_driver.find_element_by_css_selector('div.rs-prod-headline.clearfix '
                                                              '> h1').get_attribute("innerText")
            brand = chrome_driver.find_element_by_css_selector('div.rs-prod-manufacturer-logo > '
                                                               'a > picture > img').get_attribute("alt")

            features_table = chrome_driver.find_elements_by_css_selector("div.rs-prod-keyfeatures > table > tbody > tr")
            guitar_features = [feature.find_element_by_css_selector("td").text for feature in features_table]
            csv_writer.writerow([name] + [brand] + guitar_features + [price])
            # wait to not block the server
            sleep(uniform(3, 5))


if __name__ == "__main__":

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.get(GUITAR_ST_URL)

    click_cookies()

    try:
        lst_of_links = []
        with open("guitar_links.csv") as csv_links:
            reader = csv.reader(csv_links)
            for link in reader:
                lst_of_links += link
    except IOError:
        lst_of_links = get_guitar_links(chrome_driver)
        with open("guitar_links.csv", "w") as csv_links_writer:
            link_writer = csv.writer(csv_links_writer)
            for link in lst_of_links:
                link_writer.writerow([link])

    create_csv(lst_of_links)
    # create_csv(['https://www.thomann.de/it/harley_benton_hwy_25bks_progressive_series.htm'])

    chrome_driver.close()
