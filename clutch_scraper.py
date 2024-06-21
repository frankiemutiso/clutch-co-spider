import csv
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
from time import sleep
import json
from fake_useragent import UserAgent


class ClutchScraper:
    def __init__(self) -> None:
        self.page = 1
        self.max_page = 100
        self.driver = None
        self.url = None

    def setup_driver(self) -> WebDriver:
        ua = UserAgent()

        user_agent = {"userAgent": f"{ua.random}"}

        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)

        driver.execute_cdp_cmd("Network.setUserAgentOverride", user_agent)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.set_window_size(1280, 820)
        driver.set_window_position(0, 0)

        return driver

    def random_sleep(self, min, max) -> float:
        wait = random.uniform(min, max)
        print(f"Sleeping for {wait} seconds...")
        sleep(wait)

    def get_seen_jobs(self):
        jobs_cache = {}

        try:
            with open("seen.json", "r") as f:
                jobs_cache = json.load(f)
            f.close()
        except Exception as ex:
            print("Get Seen Jobs Exception: ", ex)

        return jobs_cache

    def update_cache(self, data):
        with open("seen.json", "w") as f:
            json.dump(data, f)
        f.close()

    def empty_cache(self):
        with open("seen.json", "w") as f:
            json.dump({}, f)
        f.close()

    def build_url(self, url):
        url = url.split("?")[0]
        url = url + f"?page={self.page}"

        return url

    def scroll(self) -> int:
        # class="pagination justify-content-center"
        element = self.driver.find_element(
            By.CSS_SELECTOR, "[class='pagination justify-content-center']"
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.random_sleep(2, 4)

    def scrape(self, url):
        driver = self.setup_driver()

        cols = ["name", "location", "website", "services"]
        self.init_csv(cols)
        self.empty_cache()

        driver.get(url)
        self.driver = driver

        self.close_cookie_banner()

        # keep looping this part till you  have no more data to extract
        while True:
            if self.page > self.max_page:
                break

            print(f"Currently extracting data from page {self.page}")
            self.random_sleep(3, 5)
            self.get_list()

            self.scroll()
            self.get_next_page()

        if self.driver:
            self.driver.quit()

    def init_csv(self, row):
        filename = "digital_marketing_agencies_in_us.csv"
        with open(filename, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
        csv_file.close()

    def output_to_csv(self, row):
        filename = "digital_marketing_agencies_in_us.csv"
        with open(filename, "a", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
        csv_file.close()

    def package_csv_data(self, details):
        return [
            details["name"],
            details["location"],
            details["website"],
            details["services"],
        ]

    def get_list(self):
        # class=directory-list
        # div:class="row"

        list = self.driver.find_element(By.CSS_SELECTOR, "[class='directory-list']")
        list_elements = list.find_elements(By.CSS_SELECTOR, "[class='row']")

        bulk_details = []

        for element in list_elements:
            details = {}

            name = self.get_company_name(element)
            location = self.get_company_location(element)
            website = self.get_company_website(element)
            services = self.get_service_focus(element)

            details = {
                "name": name,
                "location": location,
                "website": website,
                "services": services,
            }

            cached_jobs = self.get_seen_jobs()

            combination_str = details["name"] + details["website"]

            if combination_str not in cached_jobs:
                packaged = self.package_csv_data(details)
                self.output_to_csv(packaged)
                entry = {combination_str: 1}
                updated_dict = {**cached_jobs, **entry}
                self.update_cache(updated_dict)

                bulk_details = [*bulk_details, details]

        if self.page == 1:
            self.click_random_profile(list_elements, None)

    def get_company_name(self, element: WebElement):
        # h3:class="company_info"
        name = ""
        try:
            name_element = element.find_element(
                By.CSS_SELECTOR, "[class='company_info']"
            )
            name = name_element.text
            pass
        except Exception as ex:
            print("Company Name: ", ex)
        return name

    def get_company_website(self, element: WebElement):
        # li:website-link website-link-a
        # a:class="website-link__item"
        website = ""

        element_soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
        # print(element_soup)
        li_element = element.find_elements(
            By.CSS_SELECTOR, "[class='website-link website-link-a']"
        )
        if len(li_element) > 0:
            website_element = li_element[0].find_element(By.TAG_NAME, "a")
            website = website_element.get_attribute("href")
        else:
            website = self.click_random_profile(None, element)

        return website

    def get_company_location(self, element: WebElement):
        # span:class="locality"
        location = ""
        try:
            location_element = element.find_element(
                By.CSS_SELECTOR, "[class='locality']"
            )
            location = location_element.text
        except Exception as ex:
            print("Location Exception: ", ex)

        return location

    def get_rating(self):
        # span:class="rating sg-rating__number"
        pass

    def get_min_project_size(self):
        pass

    def avg_hourly_rate(self):
        pass

    def get_head_size(self):
        pass

    def agency_details(self):
        pass

    def get_service_focus(self, element: WebElement):
        # div:class="chartAreaContainer spm-bar-chart"
        # div:data-content
        # data-content="<i>10%</i><b>Search Engine Optimization</b>"

        services = {}

        try:
            container = element.find_element(
                By.CSS_SELECTOR, "[class='chartAreaContainer spm-bar-chart']"
            )
            div_elements = container.find_elements(By.TAG_NAME, "div")

            for element in div_elements:
                data_content = element.get_attribute("data-content")

                soup = BeautifulSoup(data_content, "html.parser")

                ratio = soup.find("i").text
                service = soup.find("b").text

                services[service] = ratio
        except Exception as ex:
            print("Services Exception: ", ex)

        return services

    def get_last_page(self):
        # li:class="page-item last"
        # a:data-page="617"
        last_page = ""

        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR, "[class='page-item last']"
            )
            link = element.find_element(By.TAG_NAME, "a")

            last_page = link.get_attribute("data-page")
        except Exception as ex:
            print("Last Page Exception: ", ex)

        return last_page

    def click_random_profile(self, elements, parent_element):
        # class="website-profile"
        website = ""
        current_tab = self.driver.current_window_handle
        element = None

        if parent_element is None:
            max_index = len(elements) - 1
            index = random.randint(0, max_index)
            element = elements[index].find_element(
                By.CSS_SELECTOR, "[class='website-profile']"
            )

        if parent_element:
            print("Extracting website url from profile screen...")
            element = parent_element.find_element(
                By.CSS_SELECTOR, "[class='website-profile']"
            )

        location = element.location_once_scrolled_into_view

        x = location["x"]
        y = location["y"] - 260

        script = f"window.scrollTo({x}, {y});"
        self.driver.execute_script(script)

        element.click()

        self.random_sleep(2, 5)

        if current_tab != self.driver.window_handles[-1]:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.random_sleep(3, 5)
            website = self.get_website_from_profile(self.driver)
            self.driver.close()

        self.driver.switch_to.window(current_tab)

        if elements is None:
            return website

    def get_website_from_profile(self, driver):
        # class="profile-quick-menu__visit-website"

        element = driver.find_element(
            By.CSS_SELECTOR, "[class='profile-quick-menu__visit-website']"
        )
        link_element = element.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute("href")

        return link

    def close_cookie_banner(self):
        # id="CybotCookiebotDialogBodyButtonAccept"
        selector = "[id='CybotCookiebotDialogBodyButtonAccept']"

        self.random_sleep(1, 2)
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()

    def get_next_page(self):
        # a:data-page="1"

        self.page += 1
        element = self.driver.find_element(
            By.CSS_SELECTOR, f"[data-page='{self.page}']"
        )
        location = element.location_once_scrolled_into_view
        x = location["x"]
        y = location["y"] - 240

        script = f"window.scrollTo({x}, {y});"
        self.driver.execute_script(script)

        element.click()
        self.random_sleep(1, 3)
