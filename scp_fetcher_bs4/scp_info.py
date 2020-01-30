from bs4 import BeautifulSoup
import re


_ANOM_ID_REGEX = re.compile(r'(?:scp-)?([0-9]\d*)')  # item-4976 OR item-scp-4979

_ANOM_CLEARANCE_REGEX = re.compile(r'(?:level)?([0-9]\d*)')

_CLASSICAL_OBJECT_ID_REGEX = re.compile(r'[Ii]tem #:')

_CLASSICAL_OBJECT_CLASS_REGEX = re.compile(r'[Oo]bject\s[Cc]lass:')

_CLASSICAL_OBJECT_ID_STRIP_REGEX = re.compile(r'scp-([0-9]\d*)')

_CLASSICAL_OBJECT_CLASS_STRIP_REGEX = re.compile(r'safe|euclid|keter|thaumiel|neutralized|explained|esoteric'
                                                 r'|decommissioned|unknown')
PAGE_TYPE_CLASSICAL = 1

PAGE_TYPE_ANOM = 2

PAGE_TYPE_SEMI_CLASSICAL = 3

PAGE_TYPE_UNKNOWN = -1


class SCPParsingError(Exception):
    pass


class SCPInfo:
    """Main class which contains SCP information.

    """

    __slots__ = ('id', 'clearance', 'object_class', 'page_type', 'secondary_class', 'disruption', 'risk')

    def __repr__(self):
        return "<SCPInfo {0} {1} {2} {3} {4} {5} {6}>".format(self.id, self.clearance, self.object_class,
                                                              self.page_type, self.secondary_class,
                                                              self.disruption, self.risk)

    @classmethod
    def from_html_page(cls, html_str, *, silent_error=False):
        """Create a SCPInfo object from a HTML page.
        :param html_str: A string contains the page from SCP Wiki which has
         the description of the SCP.
        :param silent_error: A bool indicating whether to throw exceptions
         or just return a None object.
        :return: A object created from the page.
        """
        soup = BeautifulSoup(html_str, features='html.parser')
        page_type = PAGE_TYPE_UNKNOWN
        scp_info = SCPInfo()

        # DETECTION PHASE
        if len(soup.select('.anom-bar-container')) > 0:
            page_type = PAGE_TYPE_ANOM
        else:
            object_id_list = soup.find_all(text=_CLASSICAL_OBJECT_ID_REGEX)
            if len(object_id_list) >= 1:
                object_id_obj = object_id_list[0]
                object_id_obj_container_name = object_id_obj.parent.name.lower()
                if object_id_obj_container_name == 'strong':
                    page_type = PAGE_TYPE_CLASSICAL
                elif object_id_obj_container_name == 'span':
                    page_type = PAGE_TYPE_SEMI_CLASSICAL
        scp_info.id = None
        scp_info.object_class = None
        scp_info.page_type = page_type
        scp_info.secondary_class = None
        scp_info.clearance = None
        scp_info.disruption = None
        scp_info.risk = None

        # RETRIEVING PHASE
        if page_type == PAGE_TYPE_ANOM:
            anom_container_list = soup.select('.anom-bar-container')
            if len(anom_container_list) != 1:
                raise SCPParsingError("multiple ACS containers")
            id_ = soup.select('div.top-left-box > span.number')
            clearance = soup.select('div.top-right-box > div.level')
            contain = soup.select('div.contain-class > div.class-text')
            disrupt = soup.select('div.disrupt-class > div.class-text')
            risk = soup.select('div.risk-class > div.class-text')
            try:
                secondary = soup.select('div.second-class > div.class-text')
                secondary_class_str = secondary[0].text.strip(' ').lower()
            except IndexError:
                secondary_class_str = 'none'

            try:
                id_str = _ANOM_ID_REGEX.findall(id_[0].text.strip(' ').lower())[0]
                object_class_str = contain[0].text.strip(' ').lower()
                clearance_str = _ANOM_CLEARANCE_REGEX.findall(clearance[0].text.strip(' ').lower())[0]
                disruption_str = disrupt[0].text.strip(' ').lower()
                risk_str = risk[0].text.strip(' ').lower()
            except IndexError as ex:
                raise SCPParsingError("malformed html page") from ex
            scp_info.id = id_str
            scp_info.object_class = object_class_str
            scp_info.secondary_class = secondary_class_str
            scp_info.clearance = clearance_str
            scp_info.disruption = disruption_str
            scp_info.risk = risk_str
        elif page_type == PAGE_TYPE_CLASSICAL:
            object_id_list = soup.find_all(text=_CLASSICAL_OBJECT_ID_REGEX)
            object_id_str = _CLASSICAL_OBJECT_ID_STRIP_REGEX \
                .findall(str(object_id_list[0].parent.next_sibling).lower())[0]
            object_class_list = soup.find_all(text=_CLASSICAL_OBJECT_CLASS_REGEX)
            object_class_str = _CLASSICAL_OBJECT_CLASS_STRIP_REGEX\
                .findall(str(object_class_list[0].parent.next_sibling).lower())[0]

            scp_info.id = object_id_str
            scp_info.object_class = object_class_str
        elif page_type == PAGE_TYPE_SEMI_CLASSICAL:
            object_id_list = soup.find_all(text=_CLASSICAL_OBJECT_ID_REGEX)
            object_id_str = _CLASSICAL_OBJECT_ID_STRIP_REGEX\
                .findall(str(object_id_list[0].parent.next_sibling.next_sibling.text).lower())[0]
            object_class_list = soup.find_all(text=_CLASSICAL_OBJECT_CLASS_REGEX)
            object_class_str = _CLASSICAL_OBJECT_CLASS_STRIP_REGEX\
                .findall(str(object_class_list[0].parent.next_sibling.next_sibling.text).lower())[0]

            scp_info.id = object_id_str
            scp_info.object_class = object_class_str
        else:
            if not silent_error:
                raise SCPParsingError('unknown page type')

        return scp_info
