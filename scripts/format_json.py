# Library for formatting JSON in a standard way for this project.

import json

# Keys whose values should always be expanded to separate lines
non_one_line_keys = {"requires", "techRequires", "otherRequires", "and", "or", "to", "id", "mapTileMask"}

# Keys whose children are exceptions to the rule about `non_one_line_keys`
one_line_parent_keys = {"unlocksDoors"}

one_line_limit = 80

def is_allowed_one_line_key(key, parent_keys):
    return key not in non_one_line_keys or (len(parent_keys) > 0 and parent_keys[-1] in one_line_parent_keys)

def is_simple_value(x):
    if isinstance(x, (str, int, float, bool)):
        return True
    if isinstance(x, list) and all(isinstance(y, (str, int, float, bool)) for y in x):
        return True


def is_one_liner_dict(obj, parent_keys, nesting_allowed=True):
    if len(json.dumps(obj)) > one_line_limit:
        return False
    if any(not is_allowed_one_line_key(x, parent_keys) for x in obj.keys()):
        return False
    if all(is_simple_value(x) for x in obj.values()):
        return True
    if len(obj) == 1:
        key, value = next(iter(obj.items()))
        if not is_allowed_one_line_key(key, parent_keys):
            return False
        return is_one_liner(value, parent_keys + [key], nesting_allowed=nesting_allowed)
    else:
        return False


def is_one_liner_list(obj, parent_keys, nesting_allowed=True):
    if len(json.dumps(obj)) > one_line_limit:
        return False
    if len(obj) == 0:
        return True
    if len(obj) == 1:
        return is_one_liner(obj[0], parent_keys, nesting_allowed=nesting_allowed)
    else:
        return all(is_simple_value(x) for x in obj)


def is_one_liner(obj, parent_keys, nesting_allowed=True):
    # Only one level of nesting is allowed inside a one-line object or list:
    if isinstance(obj, dict):
        return nesting_allowed and is_one_liner_dict(obj, parent_keys, nesting_allowed=False)
    elif isinstance(obj, list):
        return nesting_allowed and is_one_liner_list(obj, parent_keys, nesting_allowed=False)
    else:
        return True


def format(obj, indent, current_indent=0, one_liner_dict_allowed=True, one_liner_list_allowed=True, parent_keys=[]):
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return json.dumps(obj)
    if isinstance(obj, list):
        if len(obj) == 0 or (one_liner_list_allowed and is_one_liner_list(obj, parent_keys)):
            return json.dumps(obj)
        next_indent = current_indent + indent
        output_list = []
        output_list.append("[\n")
        for i, value in enumerate(obj):
            output_list.append(next_indent * " " + format(value, indent, next_indent, parent_keys=parent_keys))
            if i != len(obj) - 1:
                output_list.append(",\n")
        output_list.append("\n" + current_indent * " " + "]")
        return ''.join(output_list)
    if isinstance(obj, dict):
        if len(obj) == 0 or (one_liner_dict_allowed and is_one_liner_dict(obj, parent_keys)):
            return json.dumps(obj)
        if one_liner_dict_allowed and len(obj) == 1:
            key, value = next(iter(obj.items()))
            formatted_value = format(value, indent, current_indent,
                                     one_liner_dict_allowed=False,
                                     one_liner_list_allowed=is_allowed_one_line_key(key, parent_keys),
                                     parent_keys=parent_keys + [key])
            return '{' + json.dumps(key) + ': ' + formatted_value + '}'
        next_indent = current_indent + indent
        output_list = []
        output_list.append("{\n")
        keys = list(obj.keys())
        for i, key in enumerate(keys):
            value = obj[key]
            formatted_value = format(value, indent, next_indent,
                                     one_liner_dict_allowed=False,
                                     one_liner_list_allowed=is_allowed_one_line_key(key, parent_keys),
                                     parent_keys=parent_keys + [key])
            output_list.append(next_indent * ' ' + json.dumps(key) + ": " + formatted_value)
            if i != len(keys) - 1:
                output_list.append(",\n")
        output_list.append('\n' + current_indent * " " + "}")
        return ''.join(output_list)
    raise ValueError("Unexpected object type {}: {}".format(type(obj), obj))
