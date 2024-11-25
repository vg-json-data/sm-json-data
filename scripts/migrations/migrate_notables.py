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
            notable_name = strat["reusableRoomwideNotable"]
        else:
            notable_name = strat["name"]
            notable = {
                "id": next_id,
                "name": strat["name"],
                "note": strat["note"],
            }
            next_id += 1
            notable_list.append(notable)

        notable_require = {"notable": notable_name}
        strat["requires"] = [notable_require] + strat["requires"]

            
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
