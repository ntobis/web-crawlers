import time

from selenium import webdriver
from selenium import common
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup

import platform
import os
import argparse
import pandas as pd

pd.set_option('display.max_columns', 500)
import math

# Chrome Driver location
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if platform.system() == 'Windows':
    driver_path = os.path.join(PATH, "driver", "chromedriver.exe")
else:
    driver_path = os.path.join(PATH, "driver", "chromedriver")


class WebCrawler:
    def __init__(self, url, headless, title=None, abstract=None, pages=None):
        self.url = url
        self.browser = None
        self.headless = headless
        self.title = title
        self.abstract = abstract
        self.pages = pages
        self.df = pd.DataFrame(
            columns=['Application Number',
                     'Title',
                     'Application Date',
                     'Status',
                     'Publication Type',
                     'Field Of Invention',
                     'Classification (IPC)',
                     'Address',
                     'Address All',
                     'Abstract'])

    def open_driver(self):
        if self.browser is None:
            chrome_options = webdriver.ChromeOptions()
            if self.headless:
                chrome_options.add_argument('headless')
            self.browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    def open_website(self):
        self.browser.get(self.url)

    def enter_details(self):
        if self.title:
            self.browser.find_element_by_id("TextField1").send_keys(self.title)
        if self.abstract:
            self.browser.find_element_by_id("TextField2").send_keys(self.abstract)

    def perform_search(self):
        self.browser.execute_script("""
                                    window.scrollTo(0, document.body.scrollHeight)
                                    """)
        self.browser.find_element_by_id('CaptchaText').click()
        time.sleep(10)
        self.browser.find_element_by_name("submit").click()

    def parse_main_table(self):
        df = pd.read_html(self.browser.page_source)[0]
        df.to_csv('test.csv')
        self.df = self.df.append(df.iloc[:, :4])

    def go_to_next_page(self):
        self.browser.find_element_by_class_name('next').click()

    def download_main_table(self):
        if self.pages is None:
            self.pages = math.inf
        else:
            self.pages = int(self.pages)
        while self.browser.find_element_by_class_name('next').is_enabled() and self.pages:
            self.parse_main_table()
            self.pages -= 1
            self.get_application_specifics()
            self.go_to_next_page()

    def save_to_csv(self):
        self.df.to_csv('output.csv')

    def clean_df(self):
        self.df = self.df[~self.df['Application Number'].str.contains("Document")]

    def get_application_specifics(self):
        links = self.browser.find_elements_by_name('ApplicationNumber')
        for link in links:
            number = link.text
            # Go to specifics
            link.click()
            self.browser.switch_to.window(self.browser.window_handles[1])

            # Get tables
            tables = pd.read_html(self.browser.page_source)
            patents = tables[0]
            inventors = tables[1]

            # Get info
            try:
                pub_type = patents[patents.iloc[:, 0] == 'Publication Type'].iloc[:, 1].iloc[0]
                inv_field = patents[patents.iloc[:, 0] == 'Field Of Invention'].iloc[:, 1].iloc[0]
                class_ipc = patents[patents.iloc[:, 0] == 'Classification (IPC)'].iloc[:, 1].iloc[0]
                abstract = patents[patents.iloc[:, 0].str.contains("Abstract:", na=False)].iloc[:, 1].iloc[0]
            except:
                pass

            try:
                address_inv = inventors['Address'].iloc[0]
                address_all = inventors['Address'].str.cat(sep=" | ")
            except:
                pass

            # Put info into data frame
            try:
                self.df.loc[self.df['Application Number'] == number, 'Publication Type'] = pub_type
                self.df.loc[self.df['Application Number'] == number, 'Field Of Invention'] = inv_field
                self.df.loc[self.df['Application Number'] == number, 'Classification (IPC)'] = class_ipc
                self.df.loc[self.df['Application Number'] == number, 'Abstract'] = abstract
            except:
                pass

            try:
                self.df.loc[self.df['Application Number'] == number, 'Address'] = address_inv
                self.df.loc[self.df['Application Number'] == number, 'Address All'] = address_all
            except:
                pass

            # Switch back to main tab
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])


def main(args):
    crawler = WebCrawler('https://ipindiaservices.gov.in/PublicSearch',
                         False,
                         args.Title,
                         args.Abstract,
                         args.Pages)
    crawler.open_driver()
    crawler.open_website()
    crawler.enter_details()
    crawler.perform_search()
    crawler.download_main_table()
    crawler.clean_df()
    crawler.save_to_csv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--Title", help="Title of the Article")
    parser.add_argument("--Abstract", help="Abstract Keywords of the Article")
    parser.add_argument("--Pages", help="Maximum number of pages you want to scrape")
    arguments = parser.parse_args()
    main(arguments)
