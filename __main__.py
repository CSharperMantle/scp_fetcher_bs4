import requests
import argparse
import logging
from scp_info import SCPInfo, SCPParsingError


_HUMAN_EXCEPTION_OUTPUT_TEMPLATE = """
Exception caught: {0}
"""

_HUMAN_ACS_OUTPUT_TEMPLATE = """
Information about SCP-{0}:
\tClearance Level: {1}/{2}
\tContainment Class: {3}
\tSecondary Class: {4}
\tDisruption Class: {5}
\tRisk Class: {6}
"""

_HUMAN_NON_ACS_OUTPUT_TEMPLATE = """
Information about SCP-{0}:
\tObject Class: {1}
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
        req = requests.get(each_url)
        text = req.text
        req.close()
        try:
            scp_info = SCPInfo.from_html_page(text)
        except SCPParsingError as ex:
            logging.error(_HUMAN_EXCEPTION_OUTPUT_TEMPLATE.format(ex))
            break
        if not porcelain_run:
            if scp_info.is_acs_present:
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
            else:
                print(_HUMAN_NON_ACS_OUTPUT_TEMPLATE.format(scp_info.id, scp_info.object_class))
        else:
            print(repr(scp_info))


if __name__ == '__main__':
    main()
