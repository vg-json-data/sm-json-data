# Tool to assign strat IDs to strats where they are missing.
# This also performs auto-formatting.
#
# To use, run "python populate_strat_ids.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    room_str = path.open("r").read()
    room_json = json.loads(room_str)
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    next_id = room_json.get("nextStratId", 1)
    orig_next_id = next_id
    for i in range(len(room_json["strats"])):
        strat = room_json["strats"][i]
        if "id" not in strat:
            strat = {"id": next_id, **strat}
            room_json["strats"][i] = strat
            next_id += 1
    room_json["nextStratId"] = next_id
    
    new_room_str = format_json.format(room_json, indent=2)

    if next_id != orig_next_id:
        print("Added {} strat IDs in {}".format(next_id - orig_next_id, path))
    elif room_str != new_room_str:
        print("Formatted {}".format(path))
    
    # Write the auto-formatted output:
    if room_str != new_room_str:
        path.write_text(new_room_str)
