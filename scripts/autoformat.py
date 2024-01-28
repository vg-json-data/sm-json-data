# Tool to auto-format all the region files in a standard way.
#
# To use, run "python -m tests.asserts.autoformat" from a working directory of "sm-json-data".

import json
import tempfile
from pathlib import Path

import scripts.format_json as format_json

def autoformat(test=False):
    made_changes = False
    for path in sorted(Path("./region/").glob("**/*.json")):
        with path.open("r") as room_file:
            room_json = json.load(room_file)
            if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
                continue

            new_room_json = format_json.format(room_json, indent=2)
            new_room_json += "\n"

            # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
            assert json.loads(new_room_json) == room_json

            # Compare binary of the file to a temp with the newly-formatted data
            _, temp_file = tempfile.mkstemp(suffix=".json")
            with open(temp_file, "r+") as temp_handle:
                room_file.seek(0)
                temp_handle.write(new_room_json)
                temp_handle.seek(0)
                room_data = room_file.read()
                temp_data = temp_handle.read()
                identical = room_data == temp_data
                if not identical:
                    made_changes = True
                    print("🟡Processing", path)
                    # Write the auto-formatted output:
                    path.write_text(new_room_json)
    if test and made_changes:
        print("🔴ERROR: Had to make edits, bailing!")
        exit(1)

if __name__ == "__main__":
    autoformat()
