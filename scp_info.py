from bs4 import BeautifulSoup
import re


_ANOM_RISK_REGEX = re.compile(r'notice|caution|warning|danger|critical')

_ANOM_DISRUPTION_REGEX = re.compile(r'dark|vlam|keneq|ekhi|amida')

_ANOM_SECONDARY_CLASS_REGEX = re.compile(r'none|apollyon|archon|cernunnos|hiemal|tiamat|ticonderoga|thaumiel|unknown')

_ANOM_CLASS_REGEX = re.compile(r'safe|euclid|keter|neutralized|pending|explained|esoteric')

_ANOM_CLEARANCE_REGEX = re.compile(r'clear-([1-9]\d*|0)')

_ANOM_ID_REGEX = re.compile(r'item-(?:scp-)?([0-9]\d*)')  # item-4976 OR item-scp-4979

_CLASSICAL_OBJECT_ID_REGEX = re.compile(r'[Ii]tem #:')

_CLASSICAL_OBJECT_CLASS_REGEX = re.compile(r'[Oo]bject\s[Cc]lass:')

_CLASSICAL_OBJECT_ID_STRIP_REGEX = re.compile(r'scp-([0-9]\d*)')

_CLASSICAL_OBJECT_CLASS_STRIP_REGEX = re.compile(r'safe|euclid|keter|thaumiel|neutralized|explained|esoteric'
                                                 r'|decommissioned|unknown')


class SCPParsingError(Exception):
    pass


class SCPInfo:
    """Main class which contains SCP information.

    """

    __slots__ = ('id', 'clearance', 'object_class', 'is_acs_present', 'secondary_class', 'disruption', 'risk')

    def __str__(self):
        if self.is_acs_present:
            return "[SCPInfo of SCP-{0}. Class: {1}, {2}. Clearance: {3}. Disruption: {4}. Risk: {5}.]"\
                .format(self.id, self.object_class, self.secondary_class, self.clearance, self.disruption, self.risk)
        else:
            return "[SCPInfo of SCP-{0}. Class: {1}.]".format(self.id, self.object_class)

    def __repr__(self):
        return "<SCPInfo {0} {1} {2} {3} {4} {5} {6}>".format(self.id, self.clearance, self.object_class,
                                                             self.is_acs_present, self.secondary_class, self.disruption,
                                                             self.risk)

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
        scp_info = SCPInfo()

        # check Anomaly Classification System
        is_anom_sys_present = True if len(soup.select('.anom-bar-container')) > 0 else False
        scp_info.is_acs_present = is_anom_sys_present

        try:
            if not is_anom_sys_present:
                # scenario 1: classical format
                # obtain id
                object_id_list = soup.find_all(text=_CLASSICAL_OBJECT_ID_REGEX)
                if len(object_id_list) < 1:
                    raise SCPParsingError("no object id definition")
                object_id_obj = object_id_list[0]
                object_id_obj_container_name = object_id_obj.parent.name.lower()
                if object_id_obj_container_name == 'strong':
                    # scenario 1.1: very classical version
                    # we should only get the first ID, for IDs MAY exist in addendum, like SCP-004
                    object_id_str = _CLASSICAL_OBJECT_ID_STRIP_REGEX\
                        .findall(str(object_id_list[0].parent.next_sibling).lower())[0]
                elif object_id_obj_container_name == 'span':
                    # scenario 1.2: newer version, like SCP-4973
                    object_id_str = _CLASSICAL_OBJECT_ID_STRIP_REGEX\
                        .findall(str(object_id_list[0].parent.next_sibling.next_sibling.text).lower())[0]
                else:
                    raise SCPParsingError("malformed object id")

                # obtain object class(es?)
                object_class_list = soup.find_all(text=_CLASSICAL_OBJECT_CLASS_REGEX)
                if len(object_class_list) != 1:
                    raise SCPParsingError("multiple or no object class definitions")
                object_class_obj = object_id_list[0]
                object_class_obj_container_name = object_class_obj.parent.name.lower()
                if object_class_obj_container_name == 'strong':
                    # scenario 1.1: very classical version
                    object_class_str = _CLASSICAL_OBJECT_CLASS_STRIP_REGEX\
                        .findall(str(object_class_list[0].parent.next_sibling).lower())[0]
                elif object_class_obj_container_name == 'span':
                    # scenario 1.2: newer version, like SCP-4973
                    object_class_str = _CLASSICAL_OBJECT_CLASS_STRIP_REGEX\
                        .findall(str(object_class_list[0].parent.next_sibling.next_sibling.text).lower())[0]
                else:
                    raise SCPParsingError("malformed object class")

                scp_info.id = object_id_str
                scp_info.object_class = object_class_str
                scp_info.secondary_class = None
                scp_info.clearance = None
                scp_info.disruption = None
                scp_info.risk = None
                return scp_info
            else:
                # scenario 2: ACS
                anom_container_list = soup.select('.anom-bar-container')
                if len(anom_container_list) != 1:
                    raise SCPParsingError("multiple ACS containers")
                anom_detail_str = ' '.join(anom_container_list[0].attrs['class']).lower()
                try:
                    id_str = _ANOM_ID_REGEX.findall(anom_detail_str)[0]
                    clearance_str = _ANOM_CLEARANCE_REGEX.findall(anom_detail_str)[0]
                    object_class_str = _ANOM_CLASS_REGEX.findall(anom_detail_str)[0]
                    secondary_class_str = _ANOM_SECONDARY_CLASS_REGEX.findall(anom_detail_str)[0]
                    disruption_str = _ANOM_DISRUPTION_REGEX.findall(anom_detail_str)[0]
                    risk_str = _ANOM_RISK_REGEX.findall(anom_detail_str)[0]
                except IndexError as ex:
                    raise SCPParsingError("malformed html page") from ex
                scp_info.id = id_str
                scp_info.object_class = object_class_str
                scp_info.secondary_class = secondary_class_str
                scp_info.clearance = clearance_str
                scp_info.disruption = disruption_str
                scp_info.risk = risk_str
                return scp_info
        except IndexError as ex:
            if not silent_error:
                raise SCPParsingError() from ex
            else:
                scp_info.id = None
                scp_info.object_class = None
                scp_info.secondary_class = None
                scp_info.clearance = None
                scp_info.disruption = None
                scp_info.risk = None
                return scp_info
        except SCPParsingError:
            if not silent_error:
                raise
            else:
                scp_info.id = None
                scp_info.object_class = None
                scp_info.secondary_class = None
                scp_info.clearance = None
                scp_info.disruption = None
                scp_info.risk = None
                return scp_info
