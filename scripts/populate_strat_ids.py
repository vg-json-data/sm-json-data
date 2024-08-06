# Tool to assign strat IDs to strats where they are missing.
# This also performs auto-formatting.
#
# To use, run "python populate_strat_ids.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    print("Processing", path)
    
    next_id = room_json.get("nextStratId", 1)
    for i in range(len(room_json["strats"])):
        strat = room_json["strats"][i]
        if "id" not in strat:
            strat = {"id": next_id, **strat}
            room_json["strats"][i] = strat
            next_id += 1
    room_json["nextStratId"] = next_id
    
    new_room_json = format_json.format(room_json, indent=2)
    
    # Write the auto-formatted output:
    path.write_text(new_room_json)
