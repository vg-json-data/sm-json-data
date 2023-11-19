import json
from pathlib import Path
import copy

import format_json

def get_notes(x, key="note"):
    if key not in x:
        return []
    notes = x[key]
    if isinstance(notes, str):
        return [notes]
    return notes


# Extracts from node and entrance condition from a list of logical requirements containing a comeInWithGMode
def get_gmode_entrance(requires):
    from_node = None
    entrance_condition = None
    filtered_reqs = []
    for req in requires:
        if "comeInWithGMode" in req:
            come_in = req["comeInWithGMode"]
            if from_node is not None:
                raise RuntimeError("Non-unique comeInWithGMode")
            if len(come_in["fromNodes"]) != 1:
                raise RuntimeError("Multiple fromNodes")
            from_node = come_in["fromNodes"][0]
            entrance_condition = {
                "comeInWithGMode": {
                    "mode": come_in["mode"],
                    "morphed": come_in["artificialMorph"],
                }
            }
            if "mobility" in come_in:
                entrance_condition["comeInWithGMode"]["mobility"] = come_in["mobility"]
        else:
            filtered_reqs.append(req)
    if from_node is None:
        raise RuntimeError("No comeInWithGMode requirement at top level")
    return from_node, entrance_condition, filtered_reqs


def extract_leave_with_gmode_setup_strats(node_json):
    if "leaveWithGModeSetup" not in node_json:
        return []
    node_id = node_json["id"]
    strats = []
    for setup_json in node_json["leaveWithGModeSetup"]:
        setup_dev_notes = get_notes(setup_json, "devNote")
        setup_notes = get_notes(setup_json, "notes")
        knockback = setup_json.get("knockback")
        for strat_json in setup_json["strats"]:
            dev_notes = setup_dev_notes + get_notes(strat_json, "devNote")
            notes = setup_notes + get_notes(strat_json, "note")

            # Remove strat notes/devNotes so that we can control their position (after exitCondition)
            if "note" in strat_json:
                del strat_json["note"]
            if "devNote" in strat_json:
                del strat_json["devNote"]
            strat_name = strat_json["name"]
            del strat_json["name"]
            new_strat = {
                "link": [node_id, node_id],
                "name": "G-Mode Setup - " + strat_name,
                **copy.deepcopy(strat_json),
                "exitCondition": {
                    "leaveWithGModeSetup": {}
                }
            }
            
            if len(notes) > 0:
                new_strat["note"] = notes
            if len(dev_notes) > 0:
                new_strat["devNote"] = dev_notes
            if knockback is not None:
                new_strat["exitCondition"]["leaveWithGModeSetup"]["knockback"] = knockback
            strats.append(new_strat)
    del node_json["leaveWithGModeSetup"]
    return strats


def extract_leave_with_gmode_strats(node_json):
    if "leaveWithGMode" not in node_json:
        return []
    node_id = node_json["id"]
    strats = []
    for setup_json in node_json["leaveWithGMode"]:
        setup_dev_notes = get_notes(setup_json, "devNote")
        setup_notes = get_notes(setup_json, "notes")
        morphed = setup_json["leavesWithArtificialMorph"]
        for strat_json in setup_json["strats"]:
            try:
                from_node_id, entrance_condition, filtered_reqs = get_gmode_entrance(strat_json["requires"])
            except Exception as e:
                print("Skipping leaveWithGMode strat: ", e)
                return []

            dev_notes = setup_dev_notes + get_notes(strat_json, "devNote")
            notes = setup_notes + get_notes(strat_json, "note")

            # Remove strat notes/devNotes so that we can control their position (after exitCondition)
            if "note" in strat_json:
                del strat_json["note"]
            if "devNote" in strat_json:
                del strat_json["devNote"]
            new_strat = {
                "link": [from_node_id, node_id],
                **copy.deepcopy(strat_json),
                "entranceCondition": entrance_condition,
                "requires": filtered_reqs,
                "exitCondition": {
                    "leaveWithGMode": {
                        "morphed": morphed
                    }
                }
            }
            if len(notes) > 0:
                new_strat["note"] = notes
            if len(dev_notes) > 0:
                new_strat["devNote"] = dev_notes
            strats.append(new_strat)
    del node_json["leaveWithGMode"]
    return strats


def extract_gmode_immobile_strats(node_json):
    if "gModeImmobile" not in node_json:
        return []
    immobile = node_json["gModeImmobile"]
    node_id = node_json["id"]
    strat = {
        "link": [node_id, node_id],
        "name": "G-Mode Regain Mobility",
        "notable": False,
        "requires": immobile["requires"],
        "gModeRegainMobility": {},
    }
    if "note" in immobile:
        strat["note"] = immobile["note"]
    if "devNote" in immobile:
        strat["devNote"] = immobile["devNote"]
    del node_json["gModeImmobile"]
    return [strat]


def extract_come_in_with_gmode_strat(strat_json):
    try:
        from_node_id, entrance_condition, filtered_reqs = get_gmode_entrance(strat_json["requires"])
    except Exception as e:
        return None
    
    new_strat = {
        "link": [from_node_id, strat_json["link"][1]],
        "name": strat_json["name"],
        "notable": strat_json["notable"],
        "entranceCondition": entrance_condition,
        "requires": filtered_reqs,
    }
    for k, v in strat_json.items():
        if k not in new_strat:
            new_strat[k] = v
    return new_strat


def migrate_room(room_json):
    new_strats = []
    for strat_json in room_json["strats"]:
        new_strat_json = extract_come_in_with_gmode_strat(strat_json)
        if new_strat_json is not None:
            new_strats.append(new_strat_json)
        else:
            new_strats.append(strat_json)
    for node_json in room_json["nodes"]:
        new_strats.extend(extract_leave_with_gmode_setup_strats(node_json))
        new_strats.extend(extract_leave_with_gmode_strats(node_json))
        new_strats.extend(extract_gmode_immobile_strats(node_json))
    new_strats.sort(key=lambda x: x["link"])
    room_json["strats"] = new_strats


for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue
    print("Processing", path)
    migrate_room(room_json)
    path.write_text(format_json.format(room_json, indent=2))
