# Tool to auto-format all the JSON files in a standard way.
#
# To use, run "python autoformat.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path
from referencing import Registry, Resource

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

for path in sorted(Path("../").glob("**/*.json")):
    print("Processing", path)
    json_data = json.load(path.open("r"))
    new_json_data = json_data
    full_schema_name = json_data.get("$schema")
    if full_schema_name is None:
        print("Skipping file with no $schema: ", path)
        continue
    schema_name = full_schema_name.split("/")[-1]
    
    if full_schema_name == "http://json-schema.org/draft-07/schema#":
        # For now, skip reordering properties on the schema files.
        # Otherwise we would need to fetch the meta-schema from somewhere.
        pass
    else:
        schema = registry.contents(schema_name)
        resolver = registry.resolver(schema_name)
        new_json_data = schema_order.order_by_schema(new_json_data, schema, resolver)
    new_json_data = format_json.format(new_json_data, indent=2)

    # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
    if json.loads(new_json_data) != json_data:
        print("Old: ", format_json.format(json_data, indent=2))
        print("New: ", format_json.format(json.loads(new_json_data), indent=2))
    assert json.loads(new_json_data) == json_data

    # Write the auto-formatted output:
    path.write_text(new_json_data)
