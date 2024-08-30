import json
from pathlib import Path

for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    runway_nodes = set()
    for strat_json in room_json["strats"]:
        from_node = strat_json["link"][0]
        to_node = strat_json["link"][1]
        if from_node != to_node:
            continue
        if "exitCondition" in strat_json and "leaveWithRunway" in strat_json["exitCondition"]:
            runway_nodes.add(from_node)
    
    for node_json in room_json["nodes"]:
        node_id = node_json["id"]
        if node_id not in runway_nodes and node_json.get("doorOrientation") in ["left", "right"]:
            print("Missing leaveWithRunway at {}: {} ({})".format(room_json["name"], node_json["name"], node_id))
