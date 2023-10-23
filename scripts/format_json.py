import json

def is_one_liner_dict(obj, nesting_allowed=True):
    if len(json.dumps(obj)) > 50:
        return False
    if len(obj) == 0:
        return True
    if len(obj) == 1:
        value = next(iter(obj.values()))
        return is_one_liner(value, nesting_allowed=nesting_allowed)
    else:
        return all(isinstance(x, (str, int, float, bool)) for x in obj.values())

def is_one_liner_list(obj):
    if all(isinstance(x, (str, int, float, bool)) for x in obj):
        return len(json.dumps(obj)) <= 50
    return False

def is_one_liner(obj, nesting_allowed=True):
    if isinstance(obj, dict):
        return nesting_allowed and is_one_liner_dict(obj, nesting_allowed=False)
    elif isinstance(obj, list):
        return nesting_allowed and is_one_liner_list(obj)
    else:
        return True

def format(obj, indent, current_indent=0, one_liner_dict_allowed=True):
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return json.dumps(obj)
    if isinstance(obj, list):
        if is_one_liner_list(obj):
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
            return '{' + json.dumps(key) + ': ' + format(value, indent, current_indent, one_liner_dict_allowed=False) + '}'
        next_indent = current_indent + indent
        output_list = []
        output_list.append("{\n")
        keys = list(obj.keys())
        for i, key in enumerate(keys):
            value = obj[key]
            output_list.append(next_indent * ' ' + json.dumps(key) + ": " + format(value, indent, next_indent, one_liner_dict_allowed=False))
            if i != len(keys) - 1:
                output_list.append(",\n")
        output_list.append('\n' + current_indent * " " + "}")
        return ''.join(output_list)
    raise ValueError("Unexpected object type {}: {}".format(type(obj), obj))

data = {
    "entranceCondition": {
        "comeInWithShinecharge": {
            "framesRequired": 50
        }
    },
    "requires": [
        {"heatFrames": 100},
        {"or": [
            "canTrickyJump",
            {"and": [
                "Morph",
                "canWalljump",
                {"shinespark": {"frames": 50}},
                {"ammo": {"type": "PowerBomb", "count": 1}}
            ]},
        ]}
    ],
    "clearsObstacles": ["A"],
    "exitCondition": {
        "leaveWithSpark": {}
    }
}
print(format(data, indent=2))
