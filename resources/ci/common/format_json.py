# Library for formatting JSON in a standard way for this project.

import json

# Keys whose values should always be expanded to separate lines
non_one_line_keys = {"requires", "and", "or"}


def is_one_liner_dict(obj, nesting_allowed=True):
    if len(json.dumps(obj)) > 50:
        return False
    if len(obj) == 0:
        return True
    if len(obj) == 1:
        key, value = next(iter(obj.items()))
        return key not in non_one_line_keys and is_one_liner(value, nesting_allowed=nesting_allowed)
    else:
        return all(isinstance(x, (str, int, float, bool)) for x in obj.values())


def is_one_liner_list(obj, nesting_allowed=True):
    if len(json.dumps(obj)) > 50:
        return False
    if len(obj) == 0:
        return True
    if len(obj) == 1:
        return is_one_liner(obj[0], nesting_allowed=nesting_allowed)
    else:
        return all(isinstance(x, (str, int, float, bool)) for x in obj)


def is_one_liner(obj, nesting_allowed=True):
    # Only one level of nesting is allowed inside a one-line object or list:
    if isinstance(obj, dict):
        return nesting_allowed and is_one_liner_dict(obj, nesting_allowed=False)
    elif isinstance(obj, list):
        return nesting_allowed and is_one_liner_list(obj, nesting_allowed=False)
    else:
        return True


def format(obj, indent, current_indent=0, one_liner_dict_allowed=True, one_liner_list_allowed=True):
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return json.dumps(obj)
    if isinstance(obj, list):
        if len(obj) == 0 or (one_liner_list_allowed and is_one_liner_list(obj)):
            return json.dumps(obj)
        next_indent = current_indent + indent
        output_list = []
        output_list.append("[\n")
        for i, value in enumerate(obj):
            output_list.append(next_indent * " " + format(value, indent, next_indent))
            if i != len(obj) - 1:
                output_list.append(",\n")
        output_list.append("\n" + current_indent * " " + "]")
        return ''.join(output_list)
    if isinstance(obj, dict):
        if len(obj) == 0 or (one_liner_dict_allowed and is_one_liner_dict(obj)):
            return json.dumps(obj)
        if one_liner_dict_allowed and len(obj) == 1:
            key, value = next(iter(obj.items()))
            formatted_value = format(value, indent, current_indent,
                                     one_liner_dict_allowed=False,
                                     one_liner_list_allowed=key not in non_one_line_keys)
            return '{' + json.dumps(key) + ': ' + formatted_value + '}'
        next_indent = current_indent + indent
        output_list = []
        output_list.append("{\n")
        keys = list(obj.keys())
        for i, key in enumerate(keys):
            value = obj[key]
            formatted_value = format(value, indent, next_indent,
                                     one_liner_dict_allowed=False,
                                     one_liner_list_allowed=key not in non_one_line_keys)
            output_list.append(next_indent * ' ' + json.dumps(key) + ": " + formatted_value)
            if i != len(keys) - 1:
                output_list.append(",\n")
        output_list.append('\n' + current_indent * " " + "}")
        return ''.join(output_list)
    raise ValueError("Unexpected object type {}: {}".format(type(obj), obj))
