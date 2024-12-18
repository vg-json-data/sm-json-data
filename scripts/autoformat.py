# Tool to auto-format all the region files in a standard way.
#
# To use, run "python autoformat.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path
from referencing import Registry, Resource
import os

import format_json
import schema_order

resource_list = []
for path_str in sorted(Path("../schema/").glob("**/*.schema.json")):
    path = Path(path_str)
    schema = json.load(open(path, "r"))
    resource = Resource.from_contents(schema)
    resource_list.append((path.name, resource))

registry = Registry().with_resources(resource_list).crawl()
room_schema = registry.contents("m3-room.schema.json")
room_resolver = registry.resolver("m3-room.schema.json")

for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    print("Processing", path)
    new_room_json = schema_order.order_by_schema(room_json, room_schema, room_resolver)
    new_room_json = format_json.format(new_room_json, indent=2)

    # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
    assert json.loads(new_room_json) == room_json

    # Write the auto-formatted output:
    path.write_text(new_room_json)
