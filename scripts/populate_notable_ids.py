# Tool to assign notable IDs where they are missing.
# This also performs auto-formatting.
#
# To use, run "python populate_notable_ids.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    room_str = path.open("r").read()
    room_json = json.loads(room_str)
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    next_id = room_json.get("nextNotableId", 1)
    orig_next_id = next_id

    # Build a map of existing notableId values in reusable notable strats:
    # This shouldn't matter because the tests won't allow IDs to be specified in reusable
    # notable strats without also being specified in the top-level reusable object.
    # We do it to be safe and avoid mismatched IDs, in case something changes in how this works.
    reusable_id_dict = {}    
    for strat in room_json["strats"]:
        if "reusableRoomwideNotable" in strat and "notableId" in strat:
            reusable_id_dict["reusableRoomwideNotable"] = strat["notableId"]
            
    # Populate notableIds in top-level definitions of reusable notables
    for reusable in room_json.get("reusableRoomwideNotable", []):
        if "notableId" not in reusable:
            if reusable["name"] in reusable_id_dict:
                notable_id = reusable_id_dict[reusable["name"]]
            else:
                notable_id = next_id
                next_id += 1
            new_reusable = {"notableId": notable_id, **reusable}
            reusable.clear()
            reusable.update(new_reusable)
        reusable_id_dict[reusable["name"]] = reusable["notableId"]
    
    # Populate notableIds in strats
    for strat in room_json["strats"]:
        if strat.get("notable") is not True:
            continue
        if "notableId" not in strat:
            if "reusableRoomwideNotable" in strat:
                notable_id = reusable_id_dict[strat["reusableRoomwideNotable"]]
            else:
                notable_id = next_id
                next_id += 1                
            new_strat = {"id": strat["id"], "notableId": notable_id, 
                        **{k: v for k, v in strat.items() if k not in ["id", "notableId"]}}
            strat.clear()
            strat.update(new_strat)
    
    room_json["nextNotableId"] = next_id
    
    new_room_str = format_json.format(room_json, indent=2)

    if next_id != orig_next_id:
        print("Added {} notable IDs in {}".format(next_id - orig_next_id, path))
    elif room_str != new_room_str:
        print("Updated {}".format(path))
    
    # Write the auto-formatted output:
    if room_str != new_room_str:
        path.write_text(new_room_str)
