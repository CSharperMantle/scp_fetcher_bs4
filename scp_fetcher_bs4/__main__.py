import argparse
import logging

import requests
import requests.exceptions as req_exceptions
from selenium import webdriver

from scp_fetcher_bs4.scp_info import *

_HUMAN_PARSING_EX_OUTPUT_TEMPLATE = """Exception caught: {0}! Is the page an SCP with correct format?
"""

_HUMAN_REQUEST_EX_OUTPUT_TEMPLATE = """Exception caught: {0}! Is the URL reachable?
"""

_HUMAN_PAGE_SOURCE_OUTPUT_TEMPLATE = """
Source code for page '{0}':
---BEGIN SOURCE CODE---
{1}
---END OF SOURCE CODE---
"""

_HUMAN_ACS_OUTPUT_TEMPLATE = """Information about SCP-{0}:
\tClearance Level: {1}/{2}
\tContainment Class: {3}
\tSecondary Class: {4}
\tDisruption Class: {5}
\tRisk Class: {6}
"""

_HUMAN_CLASSICAL_OUTPUT_TEMPLATE = """Information about SCP-{0}:
\tObject Class: {1}
"""

_HUMAN_SEMI_CLASSICAL_OUTPUT_TEMPLATE = """Information about SCP-{0}:
\tClearance Level: {1}
\tObject Class: {2}
"""


def _get_clearance_text_by_number(clearance):
    """
    Get the corresponding clearance string by a number char.

    :param clearance: A char of clearance level number.
    :return: A string represents the clearance level.
    """
    clearance_text = "unknown"
    if clearance == '1':
        clearance_text = "unrestricted"
    elif clearance == '2':
        clearance_text = "restricted"
    elif clearance == '3':
        clearance_text = "confidential"
    elif clearance == '4':
        clearance_text = "secret"
    elif clearance == '5':
        clearance_text = "top secret"
    elif clearance == '6':
        clearance_text = "cosmetic top secret"
    return clearance_text


def _get_page_source(browser, url):
    """
    Get Wikidot page source with a Selenium-powered browser driver.

    :param browser: Selenium webdriver.
    :param url: Url to the page to fetch from.
    :return: A tuple in the following order: (text_page_title, text_page_source)
    """
    browser.get(url)

    elem_more_options_button = browser.find_element_by_id('more-options-button')
    elem_more_options_button.click()

    elem_view_source_button = browser.find_element_by_id('view-source-button')
    elem_view_source_button.click()

    text_page_source = browser.find_element_by_class_name('page-source').text
    text_page_title = browser.find_element_by_id('page-title').text

    return text_page_title, text_page_source


def _init_browser(browser_name):
    """
    Initializes a webdriver.

    :param browser_name: The name of the webdriver. 'chrome' and 'firefox' are supported.
    :return: The browser object initialized.
    """
    if browser_name == 'chrome':
        browser = webdriver.Chrome()
    elif browser_name == 'firefox':
        browser = webdriver.Firefox()
    else:
        raise SCPParsingError('browser not supported: ' + browser_name)

    browser.implicitly_wait(5)
    return browser


def main():
    """
    Entry point of scp_fetcher_bs4 executed as a module.

    :return: None.
    """
    parser = argparse.ArgumentParser(description='Fetch SCP-related information from a given SCP Wiki page')
    parser.add_argument('-u', '--url', dest='url_list',
                        metavar='URL', required=True, action='append',
                        help='the URL of the Wiki page to fetch from')
    parser.add_argument('-p', '--porcelain', dest='porcelain_run',
                        action='store_true',
                        help='machine-readable output')
    parser.add_argument('-v', '--verbose', dest='verbose_run',
                        action='store_true',
                        help='be more verbose')
    parser.add_argument('-f', '--force-continue', dest='force_run',
                        action='store_true',
                        help='do not stop when an error occurs. No effects with porcelain run')
    parser.add_argument('-s', '--fetch-only-source', dest='fetch_source',
                        action='store_true',
                        help='fetch the page source with Selenium')
    parser.add_argument('-d', '--driver', dest='fetch_source_driver',
                        metavar='DRIVER', action='store',
                        choices=['chrome', 'firefox'], default='chrome',
                        help='webdriver used by Selenium')
    args = parser.parse_args()

    url_list = args.url_list
    porcelain_run = args.porcelain_run
    verbose_run = args.verbose_run
    force_run = args.force_run
    fetch_source = args.fetch_source
    fetch_source_driver = args.fetch_source_driver

    if verbose_run:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    browser = None

    # Initializing browser
    if fetch_source:
        logging.info('Initializing webdriver. Please wait...')

        browser = _init_browser(fetch_source_driver)

        # Prompt the user to login
        browser.get(url_list[0])
        input('Please login in the newly opened browser window. This app will NOT record any of your passwords, '
              'username and so on. Press ENTER when finished.>')

    for each_url in url_list:

        logging.info("fetching {0}".format(each_url))

        # Fetch the source
        if fetch_source:
            text_page_title, text_page_source = _get_page_source(browser, each_url)
            if not porcelain_run:
                print(_HUMAN_PAGE_SOURCE_OUTPUT_TEMPLATE.format(text_page_title, text_page_source))
            else:
                print(text_page_source)

        try:
            req = requests.get(each_url)
            text = req.text
            scp_info = SCPInfo.from_html_page(text, silent_error=False)
            req.close()
        except req_exceptions.RequestException as ex:
            if not porcelain_run:
                logging.error(_HUMAN_REQUEST_EX_OUTPUT_TEMPLATE.format(ex))
                if force_run:
                    continue
                else:
                    break
            else:
                raise
        except SCPParsingError as ex:
            if not porcelain_run:
                logging.error(_HUMAN_PARSING_EX_OUTPUT_TEMPLATE.format(ex))
                if force_run:
                    continue
                else:
                    break
            else:
                raise

        if not porcelain_run:
            page_type = scp_info.page_type
            if page_type == PAGE_TYPE_ANOM:
                clearance = scp_info.clearance
                clearance_text = _get_clearance_text_by_number(clearance)

                print(_HUMAN_ACS_OUTPUT_TEMPLATE.format(scp_info.id, clearance, clearance_text, scp_info.object_class,
                                                        scp_info.secondary_class, scp_info.disruption, scp_info.risk))
            elif page_type == PAGE_TYPE_CLASSICAL:
                print(_HUMAN_CLASSICAL_OUTPUT_TEMPLATE.format(scp_info.id, scp_info.object_class))
            elif page_type == PAGE_TYPE_SEMI_CLASSICAL:
                print(_HUMAN_SEMI_CLASSICAL_OUTPUT_TEMPLATE.format(scp_info.id, scp_info.clearance,
                                                                   scp_info.object_class))
        else:
            print(repr(scp_info))

    if fetch_source:
        browser.quit()


if __name__ == '__main__':
    main()
