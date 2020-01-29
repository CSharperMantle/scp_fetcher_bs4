import requests
import argparse
import sys
from scp_info import SCPInfo


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch SCP-related information from a given SCP Wiki page')
    parser.add_argument('-u', '--url', dest='url_list',
                        metavar='URL', required=True, action='append',
                        help='the URL of the Wiki page to fetch from')
    parser.add_argument('-ne', '--no-exception', dest='no_exception',
                        action='store_true',
                        help='omit all exceptions, return None objects instead')
    args = parser.parse_args()

    for each in args.url_list:
        req = requests.get(each)
        text = req.text
        req.close()
        scp_info = SCPInfo.from_html_page(text, silent_error=args.no_exception)
        print(str(scp_info))
