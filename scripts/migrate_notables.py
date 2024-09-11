# Single-time-use script to migrate notable strats into their new format.
#
# To use, run "python migrate_notables.py" from a working directory of "sm-json-data/scripts".
import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    print(f"Processing {path}")
    room_str = path.open("r").read()
    room_json = json.loads(room_str)
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    next_id = 1
    notable_list = []
    
    # Convert reusable room-wide notables:
    for reusable in room_json.get("reusableRoomwideNotable", []):
        notable = {
            "id": next_id,
            "name": reusable["name"],
            "stratIds": [],
            "note": reusable["note"],
        }
        next_id += 1
        if "devNote" in reusable:
            notable["devNote"] = reusable["devNote"]
        notable_list.append(notable)
    
    # Convert regular notables:
    for strat in room_json["strats"]:
        if strat.get("notable") is not True:
            continue
        if "reusableRoomwideNotable" in strat:
            reusable_name = strat["reusableRoomwideNotable"]
            for notable in notable_list:
                if reusable_name == notable["name"]:
                    notable["stratIds"].append(strat["id"])
                    break
            else:
                raise f"Reusable notable not found: {reusable_name}"
        else:
            notable = {
                "id": next_id,
                "name": strat["name"],
                "stratIds": [strat["id"]],
                "note": strat["note"],
            }
            next_id += 1
            notable_list.append(notable)
            
    # Clean up obsolete properties:
    room_json.pop("reusableRoomwideNotable", None)
    for strat in room_json["strats"]:
        strat.pop("notable", None)
        strat.pop("reusableRoomwideNotable", None)
            
    room_json["notables"] = notable_list    
    room_json["nextNotableId"] = next_id
    new_room_str = format_json.format(room_json, indent=2)

    # Write the auto-formatted output:
    if room_str != new_room_str:
        path.write_text(new_room_str)
