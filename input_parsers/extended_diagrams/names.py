import re
from typing import Optional


class Names:
    """
    Helper class for generating names
    """

    @staticmethod
    def _strip_double_underscore(s: str) -> Optional[str]:
        """
        Strip all double underscores from a string until there are none left
        :param s: The input string
        :return: The string with no double underscores
        """
        if s is None:
            return None
        while s.count("__") > 0:
            s = s.replace("__", "_")
        return s

    @staticmethod
    def type_name_formatter(s: str) -> Optional[str]:
        """
        Format a string into a type name
        :param s: The input string
        :return: The type name
        """
        if s is None:
            return None
        s = re.sub(r'[^.a-zA-Z0-9]', "_", s)
        s = Names._strip_double_underscore(s)
        s = s.strip("_")
        s = s[0].upper() + s[1:]
        return s

    @staticmethod
    def field_name_formatter(s: str) -> Optional[str]:
        """
        Format a string into a field name
        :param s: The input string
        :return: The field name
        """
        if s is None:
            return None
        s = s.lower()
        s = re.sub(r'[^.a-zA-Z0-9]', "_", s)
        s = Names._strip_double_underscore(s)
        s = s.strip("_")
        while len(s) < 2:
            s += "$"
        return s
