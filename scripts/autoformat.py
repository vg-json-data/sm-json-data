# Tool to auto-format all the region files in a standard way.
#
# To use, run "python autoformat.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    region_json = json.load(path.open("r"))
    if region_json.get("$schema") != "../../schema/m3-region.schema.json":
        continue

    print("Processing", path)
    new_region_json = format_json.format(region_json, indent=2)

    # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
    assert json.loads(new_region_json) == region_json

    # Write the auto-formatted output:
    path.write_text(new_region_json)
