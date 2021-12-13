from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

text_search = "headphones"


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('headless')
options.add_argument('disable-infobars')
options.add_argument('window-size=1920x1080')
options.add_argument('--verbose')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')

PATH = '/Users/elena/PycharmProjects/tip/chromedriver'
driver = webdriver.Chrome(options=options, executable_path=PATH)


def test_shopping(amazon_price, bestbuy_price):
    assert amazon_price > bestbuy_price


def amazon_scraping(link):
    driver.get(link)
    driver.find_element_by_id("twotabsearchtextbox").send_keys(text_search)
    driver.find_element_by_id("nav-search-submit-text").click()
    driver.find_element_by_xpath("//*[@id='p_n_feature_twenty_browse-bin/2972982011']/span/a/span/div").click()
    soup = BeautifulSoup(driver.page_source, features="lxml")
    sections = soup.find_all("div", {"class": "a-section a-spacing-none"})
    baseKey = 0
    priceKey = 0
    for section in sections:
        last_price = 0
        if section.find_all("span", {"class": "a-price-range"}):
            prices = section.find_all("span", {"class": "a-offscreen"})
            for price in prices:
                last_price += float(price.text.replace('$', ''))
            last_price = last_price / 2

        price = section.find_all("span", {"class": "a-offscreen"})
        if len(price) == 1 or len(price) == 2:
            last_price = float(price[0].text.replace('$', '').replace(',', ''))
        else:
            continue
        for base_section in section.find_all("span", {"class": "a-size-base"}):
            if len(base_section["class"]) == 1:
                base = int(base_section.text.replace(',', ''))
                if baseKey < base:
                    baseKey = base
                    priceKey = last_price

    return priceKey



def bestbuy_scraping(link):
    driver.get(link)
    driver.find_element_by_class_name("us-link").click()
    wait(driver, 7).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='c-close-icon c-modal-close-icon']"))).click()
    wait(driver, 8).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[3]/div/div/div[1]/header/div[1]/div/div[1]/div/form/input[1]"))).click()
    driver.find_element_by_xpath(
        "/html/body/div[3]/div/div/div[1]/header/div[1]/div/div[1]/div/form/input[1]").send_keys(text_search,
                                                                                                 Keys.ENTER)
    driver.find_element_by_class_name("header-search-button").click()

    link_to_black_item = driver.find_element_by_xpath(
        '/html/body/div[4]/main/div[10]/div/div/div/div/div/div/div[2]/div[1]/div[1]/div[2]/div/div/div[3]/div['
        '3]/section[6]/fieldset/ul/li[1]/div/div/div/label/span[1]/a').get_attribute(
        "href")
    driver.get(link_to_black_item)

    top_rating_link = driver.find_element_by_xpath(
        '/html/body/div[4]/main/div[10]/div/div/div/div/div/div/div[2]/div[1]/div[1]/div[2]/div/div/div[3]/div['
        '3]/section[7]/fieldset/ul/li[1]/div/div/div/label/span[1]/a').get_attribute(
        "href")
    driver.get(top_rating_link)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    ol_of_items = soup.find("ol", {"class": "sku-item-list"})
    sections = ol_of_items.findChildren("li", recursive=False)
    baseKey = 0
    priceKey = 0

    for section in sections:
        for base_section in section.find_all("span", {"class": "c-reviews-v4 c-reviews order-2"}):
            base = int(base_section.text.replace('(', '').replace(')', '').replace(u'\xa0', '').replace(',', ''))
            if len(base_section["class"]) != 3 or baseKey > base:
                continue
            divPrice = section.find("div", {"class": "priceView-hero-price priceView-customer-price"})
            if divPrice == None:
                continue
            baseKey = base
            priceKey = float(divPrice.find("span").text.replace('$', ''))

    driver.quit()
    return priceKey


amazon_price = amazon_scraping("http://www.amazon.com/")
print('amazon price =', amazon_price)

bestbuy_price = bestbuy_scraping("https://www.bestbuy.com/")
print('bestbuy price =', bestbuy_price)


print(test_shopping(amazon_price, bestbuy_price))
