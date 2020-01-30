import requests
import requests.exceptions as req_exceptions
import argparse
import logging
from scp_fetcher_bs4.scp_info import *


_HUMAN_PARSING_EX_OUTPUT_TEMPLATE = """Exception caught: {0}! Is the format correct?
"""

_HUMAN_REQUEST_EX_OUTPUT_TEMPLATE = """Exception caught: {0}! Is the URL reachable?
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

def main():
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
    args = parser.parse_args()

    url_list = args.url_list
    porcelain_run = args.porcelain_run
    verbose_run = args.verbose_run

    if verbose_run:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    for each_url in url_list:

        logging.info("fetching {0}".format(each_url))
        try:
            req = requests.get(each_url)
        except req_exceptions.RequestException as ex:
            if not porcelain_run:
                logging.error(_HUMAN_REQUEST_EX_OUTPUT_TEMPLATE.format(ex))
                break
            else:
                raise
        text = req.text
        req.close()

        try:
            scp_info = SCPInfo.from_html_page(text, silent_error=False)
        except SCPParsingError as ex:
            if not porcelain_run:
                logging.error(_HUMAN_PARSING_EX_OUTPUT_TEMPLATE.format(ex))
                break
            else:
                raise
        if not porcelain_run:
            page_type = scp_info.page_type
            if page_type == PAGE_TYPE_ANOM:
                clearance = scp_info.clearance
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
                print(_HUMAN_ACS_OUTPUT_TEMPLATE.format(scp_info.id, clearance, clearance_text, scp_info.object_class,
                                                        scp_info.secondary_class, scp_info.disruption, scp_info.risk))
            elif page_type == PAGE_TYPE_CLASSICAL:
                print(_HUMAN_CLASSICAL_OUTPUT_TEMPLATE.format(scp_info.id, scp_info.object_class))
            elif page_type == PAGE_TYPE_SEMI_CLASSICAL:
                print(_HUMAN_SEMI_CLASSICAL_OUTPUT_TEMPLATE.format(scp_info.id, scp_info.clearance,
                                                                   scp_info.object_class))
        else:
            print(repr(scp_info))


if __name__ == '__main__':
    main()
