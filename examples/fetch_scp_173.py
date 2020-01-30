from scp_fetcher_bs4.scp_info import SCPInfo, SCPParsingError
import requests


_TEMPLATE = """
Information about SCP-{0}:
\tObject Class: {1}
"""


def fetch_scp_173():
    """
    Fetch the information about SCP-173 from http://scp-wiki.wikidot.com
    """
    req = requests.get('http://scp-wiki.wikidot.com/scp-173')
    text = req.text
    req.close()

    try:
        scp_info = SCPInfo.from_html_page(text)
    except SCPParsingError:
        raise
    print(_TEMPLATE.format(scp_info.id, scp_info.object_class))


if __name__ == '__main__':
    fetch_scp_173()
