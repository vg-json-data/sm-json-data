import json
from pathlib import Path
import copy

import format_json

def restructure_room(room_json):
    new_room_json = {
        "$schema": "../../../schema/m3-room.schema.json",
        **copy.deepcopy(room_json)
    }
    strat_list = []
    for link_json in new_room_json["links"]:
        from_id = link_json["from"]
        for to_json in link_json["to"]:
            to_id = to_json["id"]
            for strat in to_json["strats"]:
                new_strat = {
                    "link": [from_id, to_id],
                    **strat,
                }
                strat_list.append(new_strat)
            del to_json["strats"]
    new_room_json["strats"] = strat_list
    return new_room_json

for path in sorted(Path("../region/").glob("**/*.json")):
    region_json = json.load(path.open("r"))
    if region_json.get("$schema") != "../../schema/m3-region.schema.json":
        continue

    print("Processing", path)
    base_name = path.name.removesuffix('.json')

    # Create a new directory to hold room files
    region_dir = path.parent / base_name
    for file in region_dir.glob("**/*"):
        file.unlink()
    region_dir.mkdir(exist_ok=True)

    for room_json in region_json["rooms"]:
        room_name = room_json["name"].replace('/', 'or')
        room_path = region_dir / (room_name + ".json")
        new_room_json = restructure_room(room_json)
        room_path.write_text(format_json.format(new_room_json, indent=2))

    # Delete the original region file:
    path.unlink()
