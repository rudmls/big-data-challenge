import re


def remove_link(expression):
    return re.sub(r'https?://.*[\r\n]*', '', expression, flags=re.MULTILINE)


def change_list_dict_key(old_key: str, new_key: str, list_dictionary):
    return list(dict((new_key, v) if k == old_key else (k, v) for k, v in _.items())
                for _ in list_dictionary)
