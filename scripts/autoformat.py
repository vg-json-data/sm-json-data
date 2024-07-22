# Tool to auto-format all the region files in a standard way.
#
# To use, run "python autoformat.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    print("Processing", path)
    new_room_json = format_json.format(room_json, indent=2)

    # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
    assert json.loads(new_room_json) == room_json

    # Write the auto-formatted output:
    path.write_text(new_room_json)
