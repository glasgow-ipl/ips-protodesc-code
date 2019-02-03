import re


class Names:

    @staticmethod
    def field_name_to_id(field_name):
        if field_name is None:
            return ""
        field_name = field_name.lower()
        field_name = re.sub('[^0-9a-z]+', '_', field_name)
        return field_name.strip('_')