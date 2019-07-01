#!/usr/bin/env python3
import os
import platform
import time

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Chrome Driver location
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if platform.system() == 'Windows':
    driver_path = os.path.join(PATH, "driver", "chromedriver.exe")
else:
    driver_path = os.path.join(PATH, "driver", "chromedriver")


class WebCrawler:
    def __init__(self, url, headless):
        self.url = url
        self.browser = None
        self.headless = headless

    def open_driver(self):
        if self.browser is None:
            self.browser = webdriver.Chrome(executable_path=driver_path)

    def open_website(self):
        self.browser.get(self.url)

    def enter_login(self, user, password, verbose=True):
        if verbose:
            print("Entering User: " + user)
        self.browser.find_element_by_id("emailTextBox") \
            .send_keys(user)

        if verbose:
            print("Entering PW: " + password)
        self.browser.find_element_by_id("passwordTextBox") \
            .send_keys(password)

        self.browser.find_element_by_id("submitButton").click()

    def click_on_project(self):
        class_name = "prjCntlProjectName"
        WebDriverWait(self.browser, 10).until(ec.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
        self.browser.find_element_by_class_name(class_name).click()

    def click_on_schedule(self):
        project_oid = self.browser.current_url[self.browser.current_url.find('projectOID='):]
        link = 'https://www.co-construct.com/app/contractor/schedule.aspx?' + project_oid + '&t=3'
        self.browser.get(link)

    def expand_all(self):
        time.sleep(5)
        self.browser.find_element_by_id('btnExpandAll-btnIconEl').click()

    def convert_table(self):
        df = pd.read_html(self.browser.page_source)[0]
        df[0] = pd.to_numeric(df[0], errors='coerce', downcast='integer')
        df = df[df[0].notnull()]
        df = df.iloc[:, :8]
        df.set_index(0, inplace=True)
        df.rename(index=str, columns={1: "Task Name",
                                      2: "Notes/Files",
                                      3: "Workdays",
                                      4: "Finish",
                                      5: "Predecessors",
                                      6: "Assignees",
                                      7: "% Complete", }, inplace=True)
        df.to_csv(os.path.join(PATH, 'Downloads', 'Tasks.csv'))

    @staticmethod
    def main(user, password):
        crawler = WebCrawler('https://www.co-construct.com/app/default/default.aspx', False)
        crawler.open_driver()
        crawler.open_website()
        crawler.enter_login(user, password)
        crawler.click_on_project()
        crawler.click_on_schedule()
        crawler.expand_all()
        crawler.convert_table()
        crawler.browser.quit()


if __name__ == '__main__':
    f = open("login.txt", "r")
    user = f.readline()
    password = f.readline()
    WebCrawler.main(user=user[:-1], password=password)


