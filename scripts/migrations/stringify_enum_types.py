# This script changes the speedBooster and bypassesDoorShell enums to have pure
# string values, instead of a mix of boolean and string.
#
# To use, run "PYTHONPATH=. python migrations/stringify_enum_types.py"
# from a working directory of "sm-json-data/scripts".
import json
from pathlib import Path
import argparse
import format_json

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "--path", type=Path, default="..", help="Path to the repo base directory"
)
args = argparser.parse_args()


def remap_values(value, mapping):
    """Update object value by looking it up in mapping, leaving it alone if
    it's already updated"""
    if isinstance(value, list):
        for v in value:
            remap_values(v, mapping)
    elif isinstance(value, dict):
        for k, v in value.items():
            if k in mapping:
                assert (
                    v in mapping[k] or v in mapping[k].values()
                ), f"Unexpected value of '{k}': '{v}'"
                if v in mapping[k]:
                    value[k] = mapping[k][v]
            else:
                remap_values(v, mapping)
    else:
        pass


def update_definitions(value, mapping):
    """Update type definition by looking it up in mapping, replacing the
    values of the fields specified in the mapping"""

    def is_type_definition(v):
        return isinstance(v, dict)

    if isinstance(value, list):
        for v in value:
            update_definitions(v, mapping)
    elif isinstance(value, dict):
        for k, v in value.items():
            if k in mapping and is_type_definition(v):
                value[k].update(mapping[k])
            else:
                update_definitions(v, mapping)
    else:
        pass


region_path = args.path / "region"
schema_path = args.path / "schema"

if not region_path.exists():
    raise FileNotFoundError(f"Path {region_path} does not exist")
if not schema_path.exists():
    raise FileNotFoundError(f"Path {schema_path} does not exist")

for path in sorted(region_path.glob("**/*.json")):
    room_json = json.load(path.open("r"))
    schema = room_json.get("$schema")
    if schema is None or schema.split("/")[-1] != "m3-room.schema.json":
        continue
    print("Processing", path)
    remap_values(
        room_json,
        {
            "speedBooster": {True: "yes", False: "no", "any": "any"},
            "bypassesDoorShell": {True: "yes", False: "no", "free": "free"},
        },
    )
    path.write_text(format_json.format(room_json, indent=2))

for path in sorted(schema_path.glob("**/*.json")):
    schema_json = json.load(path.open("r"))
    schema = schema_json.get("$schema")
    if schema is None:
        continue
    print("Processing", path)
    update_definitions(
        schema_json,
        {
            "speedBooster": {
                "type": "string",
                "enum": ["yes", "no", "any"],
            },
            "bypassesDoorShell": {
                "type": "string",
                "enum": ["yes", "no", "free"],
                "default": "no",
            },
        },
    )
    path.write_text(format_json.format(schema_json, indent=2))
