import re


class Names:

    @staticmethod
    def strip_double_underscore(s: str):
        if s is None:
            return None
        while s.count("__") > 0:
            s = s.replace("__", "_")
        return s

    @staticmethod
    def type_name_formatter(name: str):
        if name is None:
            return None
        name = re.sub(r'[^.a-zA-Z0-9]', "_", name)
        name = Names.strip_double_underscore(name)
        name = name.strip("_")
        name = name[0].upper() + name[1:]
        return name

    @staticmethod
    def field_name_formatter(name: str):
        if name is None:
            return None
        name = name.lower()
        name = re.sub(r'[^.a-zA-Z0-9]', "_", name)
        name = Names.strip_double_underscore(name)
        name = name.strip("_")
        return name
