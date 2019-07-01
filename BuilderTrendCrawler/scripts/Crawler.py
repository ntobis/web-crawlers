#!/usr/bin/env python3
import zipfile
import time
import json
from collections import deque

import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import platform
import os

# Sleep-times
GENERAL_SLEEP_TIME = 1
PRINT_SLEEP_TIME = 5

# Chrome Driver location
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if platform.system() == 'Windows':
    driver_path = os.path.join(PATH, "driver", "chromedriver.exe")
else:
    driver_path = os.path.join(PATH, "driver", "chromedriver")

# Default Print PDF Path
curr_dir = os.getcwd()
download_path = os.path.join(PATH, 'Downloads')
appState = {
    "recentDestinations": [
        {
            "id": "Save as PDF",
            "origin": "local"
        }
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
}


class WebCrawler:
    def __init__(self, url, headless):
        self.url = url
        self.browser = None
        self.headless = headless

    def open_driver(self, profile):
        if self.browser is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option('prefs', profile)
            chrome_options.add_argument('--kiosk-printing')
            if self.headless:
                chrome_options.add_argument('headless')
            self.browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    def open_website(self):
        self.browser.get(self.url)

    def enter_login(self, user, password, verbose=True):
        if verbose:
            print("Entering User: " + user)
        self.browser.find_element_by_id("ctl00_ctl00_ctl00_"
                                        "MasterMain_MasterMain_"
                                        "MasterMain_txtUserID_Textbox1") \
            .send_keys(user)

        if verbose:
            print("Entering PW: " + password)
        self.browser.find_element_by_id("ctl00_ctl00_ctl00_"
                                        "MasterMain_MasterMain_MasterMain_"
                                        "txtPassword_Textbox1") \
            .send_keys(password)

        self.browser.find_element_by_class_name("login--form-submit-btn").click()

    def _click_id(self, id_tag, verbose=True, timeout=10):
        if verbose:
            print("ID: " + id_tag)
        WebDriverWait(self.browser, timeout).until(ec.presence_of_all_elements_located((By.ID, id_tag)))
        function = self.browser.find_element_by_id(id_tag).click
        self._clicker(function)

    def _click_classes(self, class_name, class_text, verbose=True, timeout=10):
        if verbose:
            print("Class: " + class_name)

        captions = WebDriverWait(self.browser, timeout).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME, class_name)))

        for caption in captions:
            if caption.text == class_text:
                print("Found Caption: " + caption.text)
                caption.click()
                break

    def _switch_to_iframe(self, id_tag):
        iframe = self.browser.find_element_by_id(id_tag)
        self.browser.switch_to.frame(iframe)

    def _try_id(self, id_tag):
        try:
            self._click_id(id_tag)
        except selenium.common.exceptions.WebDriverException:
            pass

    @staticmethod
    def _every_downloads_chrome(driver):
        if not driver.current_url.startswith("chrome://downloads"):
            driver.get("chrome://downloads/")
        driver.execute_script("""
            var items = downloads.Manager.get().items_;
            if (items.every(e => e.state === "COMPLETE"))
                return items.map(e => e.file_url);
            """)

    def _return_to_home(self):
        self.browser.get('https://buildertrend.net/summaryGrid.aspx')

    def download_cost_codes(self, timeout=10):
        # Settings
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl09_pnlNewIcon")

        # Setup
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl09_rptSetupDropDown_ctl00_divLinkTextContainer")

        # Cost Codes
        self._switch_to_iframe("ifrdivBasePopupWithIFrame")
        self._click_classes("caption", "Cost Codes")

        # Cost Code Actions
        self._try_id("btnCancelWizard")
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnCostCodeActions_href1")

        # Download excel
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnCostCodeActions_ctl03_img1")
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass

        # Return to home
        self._return_to_home()

    def download_subs_and_vendors(self, timeout=10):
        # Users
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl06_pnlNewIcon", timeout=timeout)

        # Subs/Vendors
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl06_rptSetupDropDown_ctl01_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns Selected
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_SummaryContent_dgSubsList_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_SummaryContent_dgSubsList_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_customer_contacts(self, timeout=10):
        # Users
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl06_pnlNewIcon", timeout=timeout)

        # Customer contacts
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl06_rptSetupDropDown_ctl02_linkDropDownMenuIcon",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns Selected
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_SummaryContent_dgContactsList_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_SummaryContent_dgContactsList_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_lead_opportunities(self, timeout=10):
        # Sales
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl00_dropdownLabel", timeout=timeout)

        # Lead Opportunities
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl00_rptSetupDropDown_ctl00_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgLeads_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgLeads_savedSettings_btnApplyColumns",
                       timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_schedule(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # Schedule
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl00_divLinkTextContainer",
                       timeout=timeout)

        # List View
        self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_BTTab5_LinkButton1",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Export
        self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_btnExcel_ImageButton1", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_daily_logs(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # Daily Logs
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl01_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Print
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnPrint_btn1", timeout=timeout)
        time.sleep(PRINT_SLEEP_TIME)

        # Get job name and save file under job name
        pyautogui.typewrite("daily_logs", interval=0.1)
        pyautogui.hotkey('enter')
        self.browser.switch_to.window(self.browser.current_window_handle)

        # Return to home
        self._return_to_home()

    def download_to_dos(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # To Dos
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl02_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_dgToDos_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_dgToDos_savedSettings_btnApplyColumns",
                       timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass

        # Return to home
        self._return_to_home()

    def download_change_orders(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # To Dos
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl03_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_dgChangeOrders_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_dgChangeOrders_savedSettings_btnApplyColumns",
                       timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass

        # Return to home
        self._return_to_home()

    def download_selections(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # To Dos
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl04_divLinkTextContainer",
                       timeout=timeout)

        # Get Projects
        time.sleep(GENERAL_SLEEP_TIME)
        projects = self.browser.execute_script("""
                                    var elements = document.getElementsByClassName('jobIconDiv')
                                    return elements.length
                                    """)
        # For Each Project
        print("Number of projects: ", projects)
        for num in range(projects):
            try:
                # Click on Project
                time.sleep(GENERAL_SLEEP_TIME)
                self.browser.execute_script('''
                                            var elements = document.getElementsByClassName('jobIconDiv');
                                            elements[arguments[0]].click();
                                            ''', num)

                # Grid
                self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_BTTab1_LinkButton1")

                # Clear Filter
                self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

                # Select all
                time.sleep(GENERAL_SLEEP_TIME)
                self.browser.execute_script("""
                                            var selections = document.getElementById("selections");
                                            selections.getElementsByTagName('label')[0].click();
                                            """)

                # Checked actions
                self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_btnMassActions_href1", timeout=timeout)

                # Print All
                self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_btnMassActions_ctl01_divLinkTextContainer",
                               timeout=timeout)

                # Wait for print dialogue to disappear
                time.sleep(PRINT_SLEEP_TIME)

                # Get job name and save file under job name
                job = self.browser.find_element_by_id('spnJobName')
                file_name = "selections_" + job.text[3:-1]
                pyautogui.typewrite(file_name, interval=0.1)
                pyautogui.hotkey('enter')
                self.browser.switch_to.window(self.browser.current_window_handle)

            except selenium.common.exceptions.UnexpectedAlertPresentException:
                print("Empty Project, skip.")
                pyautogui.hotkey('esc')

        self._return_to_home()
        self.display_all_jobs()

    def download_warranty(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # Warranty
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl05_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_dgWarranties_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_dgWarranties_savedSettings_btnApplyColumns",
                       timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_time_clock(self, timeout=10):
        # Project Management
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_dropdownLabel", timeout=timeout)

        # Time Clock
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl02_rptSetupDropDown_ctl06_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_TimeClockPageContent_dgTimeClock_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_ctl00_BaseMain_MainContentHolder_tcTabs_TimeClockPageContent_dgTimeClock_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_bids(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # Bids
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl00_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Export
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnExcel_ImageButton1", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_estimates(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # Estimates
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl01_divLinkTextContainer",
                       timeout=timeout)

        # Get Projects
        time.sleep(GENERAL_SLEEP_TIME)
        projects = self.browser.execute_script("""
                                            var elements = document.getElementsByClassName('jobIconDiv')
                                            return elements.length
                                            """)
        # For Each Project
        print("Number of projects: ", projects)
        for num in range(projects):
            try:
                # Click on Project
                time.sleep(GENERAL_SLEEP_TIME)
                self.browser.execute_script('''
                                                    var elements = document.getElementsByClassName('jobIconDiv');
                                                    elements[arguments[0]].click();
                                                    ''', num)

                # Select all
                time.sleep(GENERAL_SLEEP_TIME)
                self._click_classes("checkAll", "")

                # Print All
                self._click_id("ctl00_ctl00_ctl00_BaseMain_MainContentHolder_btProposalHeader_btnPrint",
                               timeout=timeout)

                # Wait for print dialogue to disappear
                time.sleep(PRINT_SLEEP_TIME)

                # Get job name and save file under job name
                job = self.browser.find_elements_by_class_name('selectedJobSubData')
                file_name = "estimates_" + job[0].text
                pyautogui.typewrite(file_name, interval=0.1)
                pyautogui.hotkey('enter')
                self.browser.switch_to.window(self.browser.current_window_handle)

            except selenium.common.exceptions.UnexpectedAlertPresentException:
                print("Empty Project, skip.")
                pyautogui.hotkey('esc')

        self._return_to_home()
        self.display_all_jobs()

    def download_bills_and_pos(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # Bills/POs
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl02_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_tcBudgetTabs_dgPurchaseOrders_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_tcBudgetTabs_dgPurchaseOrders_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_po_payments(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # PO Payments
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl03_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgPayments_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgPayments_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_budget(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # Budget
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl04_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Export
        self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnExcel_ImageButton1", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_owner_invoices(self, timeout):
        # Financial
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_dropdownLabel", timeout=timeout)

        # PO Payments
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl05_rptSetupDropDown_ctl05_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_dgInvoices_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_dgInvoices_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_lead_proposals_list(self, timeout):
        # Sales
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl00_dropdownLabel", timeout=timeout)

        # Lead Proposals
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl00_rptSetupDropDown_ctl02_divLinkTextContainer",
                       timeout=timeout)

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgLeadProposals_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id(
            "ctl00_ctl00_BaseMain_MainContentHolder_BTTabControl1_dgLeadProposals_savedSettings_btnApplyColumns",
            timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_jobs_list(self, timeout):
        # Main
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl01_pnlNewIcon", timeout=timeout)

        # Jobs list
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl01_rptSetupDropDown_ctl03_divLinkTextContainer",
                       timeout=timeout)

        # Switch to iFrame
        self._switch_to_iframe("ifrdivBasePopupWithIFrame")

        # Clear Filter
        self._click_classes("bt-result-filters--clear-filters", "clear", timeout=timeout)

        # Gear Icon
        self._click_classes("ui-icon-gridsettings", "", timeout=timeout)

        # Columns selected
        self._click_id(
            "ctl00_BaseMain_dgJobsitesList_savedSettings_lstColumnChooser_outerContainer",
            timeout=timeout)

        # Select all columns
        self._click_classes("ui-icon-check", "", timeout=timeout)

        # Apply view
        self._click_id("ctl00_BaseMain_dgJobsitesList_savedSettings_btnApplyColumns",
                       timeout=timeout)

        # Export
        self._click_classes("ui-icon-excel", "", timeout=timeout)
        try:
            WebDriverWait(self.browser, timeout).until(self._every_downloads_chrome)
        except selenium.common.exceptions.TimeoutException:
            pass
        # Return to home
        self._return_to_home()

    def download_documents(self, timeout=10):
        # Files
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl03_dropdownLabel", timeout=timeout)

        # Documents
        self._click_id("ctl00_ctl00_BaseMain_ctlMainMenu_ctl03_rptSetupDropDown_ctl00_divLinkTextContainer",
                       timeout=timeout)

        # Get Projects
        time.sleep(GENERAL_SLEEP_TIME)
        projects = self.browser.execute_script("""
                                            var elements = document.getElementsByClassName('jobIconDiv')
                                            return elements.length
                                            """)
        # For Each Project
        print("Number of projects: ", projects)
        for num in range(projects):
            print("Project number: " + str(num))
            print("Number of Projects left: " + str(projects - num))

            # Go to documents home
            self.browser.get('https://buildertrend.net/Documents/Documents.aspx')

            try:
                # Click on Project
                time.sleep(GENERAL_SLEEP_TIME)
                self.browser.execute_script('''
                                                    var elements = document.getElementsByClassName('jobIconDiv');
                                                    elements[arguments[0]].click();
                                                    ''', int(num))

                try:
                    # Get Project Name
                    job = WebDriverWait(self.browser, timeout).until(
                        ec.presence_of_all_elements_located((By.CLASS_NAME, 'selectedJobSubData')))
                    folder_name = job[0].text

                    # Check All
                    try:
                        self._click_id("chkAll", timeout=5)
                    except selenium.common.exceptions.WebDriverException:
                        raise selenium.common.exceptions.TimeoutException

                    # Dropdown
                    self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnActionsDD_dropDownMenuDiv",
                                   timeout=timeout)

                    # Download
                    self._click_id("ctl00_ctl00_BaseMain_MainContentHolder_btnActionsDD_ctl01_divLinkTextContainer",
                                   timeout=timeout)

                    # Confirm Dialog
                    WebDriverWait(self.browser, 5).until(ec.alert_is_present())
                    self.browser.switch_to.alert.accept()

                    # Unzip toplevel folder
                    self.browser.execute_script('''window.history.go(-1);''')
                    file_location = self._move_to_download_folder(str(folder_name), "My_Downloaded_Documents.zip")
                    self._unzip_file(os.path.join(file_location, "My_Downloaded_Documents.zip"), file_location)
                    os.remove(os.path.join(file_location, "My_Downloaded_Documents.zip"))

                    # Download folder contents
                    self.dfs_folder_download(folder_name, timeout=timeout, verbose=True)

                except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.NoSuchElementException):
                    print("No elements to download.")

            except selenium.common.exceptions.UnexpectedAlertPresentException:
                print("Empty Project, skip.")
                pyautogui.hotkey('esc')

        self._return_to_home()
        self.display_all_jobs()

    def dfs_folder_download(self, parent_folder, timeout=10, verbose=True):

        # Get all folders
        jobs = self.browser.find_elements_by_xpath('//*[@title="View folder contents" and @class="entryLink"]')
        link_queue = deque()
        names_queue = deque()

        # Put folders in a queue and the corresponding names in a separate queue
        for job in jobs:
            link_queue.append(job.get_attribute("href"))
            names_queue.append(job.text)

        print("Subfolders found: " + str(len(link_queue)))

        while link_queue:
            print("Subfolders remaining: " + str(len(link_queue)))

            # Enter Folder
            folder = link_queue.popleft()
            name = names_queue.popleft()
            print("Folder: " + str(name))
            self.browser.get(folder)

            # Check for elements
            jobs = self.browser.find_elements_by_class_name('entryLink')
            if len(jobs) > 0:

                # Click Check All
                time.sleep(1)
                self._click_id("chkAll", timeout=timeout)

                # Click Download
                print("Download files")
                self.browser.execute_script('''
                                            document.getElementById('ctl00_ctl00_BaseMain_MainContentHolder_btnDownloadDocuments').click();
                                            ''')
                # Extract Files
                file_location = self._move_to_download_folder(os.path.join(parent_folder, name), name + ".zip")
                print("LOCATION: ", file_location)
                self._unzip_file(os.path.join(file_location, (name + ".zip")), file_location)
                os.remove(os.path.join(file_location, name) + ".zip")

                # Dive into next folder
                if verbose:
                    print("Going into the next level")
                self.dfs_folder_download(os.path.join(parent_folder, name))

            else:
                print("Nothing to do in subfolder.")

        # Return from initial dive
        if verbose:
            print("Going back up again")
        self.browser.execute_script("window.history.go(-1)")

    @staticmethod
    def _move_to_download_folder(sub_folder, file_name):
        current_file = os.path.join(download_path, file_name)
        file_destination = os.path.join(download_path, sub_folder)
        if not os.path.exists(file_destination):
            os.mkdir(file_destination)
        print(current_file)
        print(file_destination)
        while not os.path.exists(current_file):
            time.sleep(1)

        # Move file
        print(os.path.join(file_destination, file_name))
        os.rename(current_file, os.path.join(file_destination, file_name))
        return file_destination

    def display_all_jobs(self, timeout=10):
        # Filter
        self._click_id("tdJobPickerFilter", timeout=timeout)

        # Reset Filter
        self._click_classes("mainButton", "Reset", timeout=timeout)

        # Return to home
        self._return_to_home()

    @staticmethod
    def _unzip_file(file_path, destination_path):
        print("UNZIP")
        print(file_path)
        zip_ref = zipfile.ZipFile(file_path, 'r')
        zip_ref.extractall(destination_path)
        zip_ref.close()

    def close_browser(self):
        self.browser.quit()

    @staticmethod
    def _clicker(function, timeout=10):
        success = False
        start_time = time.time()
        while not success:
            try:
                function()
                success = True
            except selenium.common.exceptions.WebDriverException:
                if time.time() - start_time > timeout:
                    raise selenium.common.exceptions.WebDriverException

    def download_general(self, timeout=10):
        self.download_cost_codes(timeout=timeout)
        self.download_subs_and_vendors(timeout=timeout)
        self.download_customer_contacts(timeout=timeout)
        self.download_lead_opportunities(timeout=timeout)
        self.download_lead_proposals_list(timeout=timeout)
        self.download_jobs_list(timeout=timeout)

    def download_financial(self, timeout=10):
        self.download_owner_invoices(timeout=timeout)
        self.download_bids(timeout=timeout)
        self.download_bills_and_pos(timeout=timeout)
        self.download_po_payments(timeout=timeout)
        self.download_budget(timeout=timeout)

    def download_project_management(self, timeout=10):
        self.download_schedule(timeout=timeout)
        self.download_to_dos(timeout=timeout)
        self.download_change_orders(timeout=timeout)
        self.download_warranty(timeout=timeout)
        self.download_time_clock(timeout=timeout)

    def print_to_pdf(self, timeout=10):
        self.download_estimates(timeout=timeout)
        self.download_daily_logs(timeout=timeout)
        self.download_selections(timeout=timeout)

    def download(self, flags):
        functions = [self.download_cost_codes,
                     self.download_subs_and_vendors,
                     self.download_customer_contacts,
                     self.download_lead_opportunities,
                     self.download_lead_proposals_list,
                     self.download_jobs_list,
                     self.download_owner_invoices,
                     self.download_bids,
                     self.download_bills_and_pos,
                     self.download_po_payments,
                     self.download_budget,
                     self.download_schedule,
                     self.download_to_dos,
                     self.download_change_orders,
                     self.download_warranty,
                     self.download_time_clock,
                     self.download_estimates,
                     self.download_daily_logs,
                     self.download_selections]

        for i, function in enumerate(functions):
            if flags[i]:
                function()


def main(customer, user, password, flags):
    global download_path
    try:

        # Create Download Folder if necessary
        if not os.path.exists(download_path):
            os.mkdir(download_path)

        # Create Customer Folder
        folder_path = os.path.join(download_path, customer)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        download_path = folder_path

        profile = {
            'printing.print_preview_sticky_settings.app': json.dumps(appState),
            'download.default_directory': download_path,
        }

        # WebCrawler
        crawler = WebCrawler('https://buildertrend.net/?_ga=2.56714542.524941111.1554234437-574163046.1553977405',
                             headless=False)
        crawler.open_driver(profile)
        crawler.open_website()
        crawler.enter_login(user=user, password=password)
        crawler.display_all_jobs(timeout=10)
        crawler.download(flags)
        crawler.browser.quit()

    except IndexError:
        pass


if __name__ == '__main__':
    flags = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
             True]
    f = open("login.txt", "r")
    customer = f.readline()
    user = f.readline()
    password = f.readline()
    main(customer=customer[:-1], user=user[:-1], password=password, flags=flags)
