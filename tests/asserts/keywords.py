# pylint: disable=global-at-module-level, invalid-name, too-many-locals
'''
Check for validity of keywords in files
'''
import json
import os
import re
import subprocess
import sys
from flatten_json import flatten

bail = False            # throw an exit code
last_enemy = ""         # helper for enemy validation
uniques = {             # track used IDs and make sure that they're successively unique
    "groupName": [],
    "roomID": [],
    "roomName": [],
    "roomAddress": [],
    "nodeAddress": []
}
messages = {            # track messages and message counts
    "greens": [],
    "yellows": [],
    "reds": [],
    "counts": {
        "greens": 0,
        "yellows": 0,
        "reds": 0
    }
}

def process_keyvalue(k, v, metadata):
    '''
    Take a keyvalue pair and see if the value exists in our list of keywords
    '''
    global last_enemy
    goodValue = True
    processValue = True

    # keys to ignore because they can't have bad data or they've been manually verified
    goodKeys = [
        "subarea",
        "twinDoorAddresses"
    ]

    # keys to ignore for documented reasons
    manualKeys = [
        "clearsObstacles",
        "resetsObstacles",
        "initiateRemotely",
        "obstaclesCleared",
        "obstaclesNotCleared"
    ]

    # keys to ignore for documented reasons
    badKeys = [
        "$schema",          # immaterial
        "description",      # immaterial
        "devNote",          # immaterial
        "note",             # immaterial
        "name",             # !!could check for unique
        "id",               # !!could check for unique
        # "groupName",        # !!could check for unique
        # "nodeAddress",      # !!could check for unique
        # "roomAddress",      # !!could check for unique
        "notable",          # checked explicitly below
        "jumpwayType",      # validated by schema
        "lockType",         # validated by schema
        "nodeType",         # validated by schema
        "nodeSubType",      # validated by schema
        "obstacleType",     # validated by schema
        "physics",          # validated by schema
        "utility",          # validated by schema
        "resourceCapacity", # validated by schema
        "resourceAvailable",# validated by schema
        "refill",           # validated by schema
        "partialRefill",    # validated by schema
        "autoReserveTrigger",    # validated by schema
        "comeInWithSpark",  # validated by schema
        "comeInWithDoorStuckSetup", # validated by schema
        "comeInRunning",  # validated by schema
        "comeInJumping",    # validated by schema,
        "comeInWithGMode",    # validated by schema,
        "leaveWithGModeSetup", # validated by schema
        "gModeRegainMobility",    # validated by schema
        "leaveWithSpark", # validated by schema
        "speedBooster", # validated by schema
        "framesRemaining",  # validated by schema
        "comesThroughToilet",  # validated by schema
        "direction",  # validated by schema
        "blue",  # validated by schema
        "movementType",  # validated by schema
        "doorOrientation",  # validated by schema
        "minExtraRunSpeed", # validated by schema
        "maxExtraRunSpeed", # validated by schema
        "types",  # validated by schema in 'unlocksDoors', manually in 'enemyDamage'
        "type",  # validated by schema in 'resourceAvailable', 'resourceCapacity'
    ]

    # check if it's a key we want to check
    if k in badKeys or k in goodKeys:
        processValue = False
    else:
        for checkKey in badKeys:
            if checkKey in k:
                processValue = False
        for checkKey in manualKeys:
            if checkKey in k:
                processValue = False
        for checkKey in goodKeys:
            if checkKey in k:
                processValue = False

    isSkip = False
    kCheck = k.split(".")[-1]
    # check uniques
    if kCheck in uniques and "twinDoorAddresses" not in k:
        if v not in uniques[kCheck]:
            uniques[kCheck].append(v)
            isSkip = True
        elif kCheck == "nodeAddress" and int(v, 16) in [0x189ca, 0x189d6]:
            # nodeAddress is normally unique but there are two exceptions in West Ocean for the bridge doors.
            isSkip = True
        else:      
            msg = f"🔴ERROR: {k}:{v} not unique!"
            messages["reds"].append(msg)
            messages["counts"]["reds"] += 1

    # let's do this thing
    if processValue:
        # helpers for data type
        isFloat = isinstance(v, float)
        isInt = isinstance(v, int)
        isList = isinstance(v, list)
        isEmptyList = isList and len(v) == 0
        isEmptyDict = v == {}
        isNumeric = not isFloat and not isInt and not isList and not isEmptyDict and v.isnumeric()
        if not isFloat and \
            not isInt and \
            not isEmptyList and \
            not isEmptyDict and \
            not isNumeric and \
            not isSkip:
            # helpers for value type
            isArea = v \
                .replace("Ceres Station", "Ceres") \
                .replace(" ", "") \
                .lower() in keywords["areas"]
            isEnemy = v in keywords["enemies"]["enemyByName"]
            isHelper = v in keywords["helpers"]
            isItem = v in keywords["items"]
            isFlag = v in keywords["flags"]
            isTech = v in keywords["techs"]
            isWeapon = v in keywords["weapons"]
            isValue = v in keywords["values"]

            # process enemy
            if (isEnemy or last_enemy != "") and ".enemy" in k and ".enemyKill" not in k:
                if ".type" not in k:
                    last_enemy = v
                elif ".type" in k:
                    # validate enemy name
                    if last_enemy in keywords["enemies"]["enemyByName"]:
                        enemyID = keywords["enemies"]["enemyByName"][last_enemy]
                        if enemyID in enemies:
                            if "attacks" in enemies[enemyID]:
                                attackExists = False
                                for attack in enemies[enemyID]["attacks"]:
                                    if "name" in attack:
                                        # validate attack name
                                        if attack["name"] == v:
                                            attackExists = True
                                goodValue = attackExists
                                if not goodValue:
                                    msg = f"🔴ERROR: {k}:{last_enemy} doesn't have attack '{v}'"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        last_enemy = ""
                    else:
                        msg = f"🔴ERROR: {last_enemy} not found!"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1
            else:
                # if it doesn't match a known value type
                if not isArea and \
                    not isEnemy and \
                    not isHelper and \
                    not isItem and \
                    not isFlag and \
                    not isTech and \
                    not isWeapon and \
                    not isValue:
                    goodValue = False
                    msg = f"🔴ERROR: {k} {v}"
                    msg = {"msg": msg, "region": metadata["region"]}
                    if v == "":
                        msg["note"] = "Empty string!"
                    messages["reds"].append(msg)
                    messages["counts"]["reds"] += 1
    return goodValue

# try to navigate a path between nodes if no direct path
def search_for_path(fromNodes, sourceNode, targetNode, stratRef):
    foundPath = False
    msg = ""
    for tNode in fromNodes[str(sourceNode)]["to"]:
        if not foundPath:
            # print(f"Testing {sourceNode}:{tNode}:{targetNode}")
            if (str(tNode) in roomData["links"]["from"]) and \
                (str(targetNode) in roomData["links"]["from"][str(tNode)]["to"]):
                foundPath = True
                # msg = f"🟢Found Path:{stratRef}::{sourceNode}:{tNode}:{targetNode}"
                # print(msg)
                # messages["greens"].append(msg)
                # messages["counts"]["greens"] += 1
    if not foundPath:
        msg = f"🟡WARNING: Path not found:{stratRef}::{sourceNode}:{tNode}:{targetNode}::Is it longer than a 3-node chain? Gave up looking"

    return [foundPath, msg]


def find_door_unlocked_nodes_rec(req):
    if isinstance(req, dict):
        if "doorUnlockedAtNode" in req:
            return set([req["doorUnlockedAtNode"]])
        if "and" in req:
            return find_door_unlocked_nodes_rec(req["and"])
        if "or" in req:
            return find_door_unlocked_nodes_rec(req["or"])
    if isinstance(req, list):
        return set(y for x in req for y in find_door_unlocked_nodes_rec(x))
    return set()


def find_door_unlocked_nodes(strat, node_subtype, nodes_without_implicit_unlocks):
    nodes = find_door_unlocked_nodes_rec(strat["requires"])
    from_node = strat["link"][0]
    to_node = strat["link"][1]
    if "exitCondition" in strat and strat.get("bypassesDoorShell") != True and node_subtype not in ["elevator", "doorway", "sandpit", "passage"]:
        nodes.add(to_node)
    if "entranceCondition" not in strat and from_node in nodes:
        nodes.remove(from_node)
    if to_node in nodes_without_implicit_unlocks and strat.get("bypassesDoorShell") != True and "gModeRegainMobility" not in strat:
        nodes.add(to_node)
    return nodes

def check_node_covered_in_unlocks_doors(strat, node_id):
    unlocks_doors = strat.get("unlocksDoors", [])
    to_node = strat["link"][1]
    types = [t for x in unlocks_doors if x.get("nodeId", to_node) == node_id for t in x["types"]]
    if "ammo" in types: 
        return []
    missing_types = {"missiles", "super", "powerbomb"}.difference(types)
    return missing_types

def check_shinespark_req(req):
    if isinstance(req, dict):
        if "shinespark" in req:
            return True
        if "and" in req:
            return any(check_shinespark_req(v) for v in req["and"])
        if "or" in req:
            return all(check_shinespark_req(v) for v in req["or"])

def check_heat_req(req):
    if isinstance(req, str):
        if req in ["h_heatProof", "h_canHeatedCrystalFlash", "h_canHeatedLavaCrystalFlash", "h_LowerNorfairElevatorDownwardFrames",
                   "h_LowerNorfairElevatorUpwardFrames", "h_MainHallElevatorFrames", "h_canHeatedGreenGateGlitch"]:
            return True
    if isinstance(req, dict):
        if "heatFrames" in req or "heatFramesWithEnergyDrops" in req:
            return True
        if "and" in req:
            return any(check_heat_req(v) for v in req["and"])
        if "or" in req:
            return all(check_heat_req(v) for v in req["or"])

# give list of keys to check
# give label for output message
# give list of valid values
# give data object
def search_for_valid_keyvalue(keys, label, valids, data):
    keyvalueErrors = []
    data = {
        label: data
    }
    flattened_dict = [
        flatten(d, '.') for d in [data]
    ][0]
    for [k, v] in flattened_dict.items():
        if (isinstance(v, int)) or \
            (isinstance(v, list) and len(v)) or \
            (isinstance(v, str) and len(v)):
            if isinstance(v, list):
                print(v)
            for checkKey in keys:
                goodValue = False
                if k.endswith(checkKey):
                    goodValue = True
                if checkKey.endswith("."):
                    if checkKey in k:
                        if k[k.rfind('.')+1:].isnumeric():
                            goodValue = True
                if goodValue:
                    if isinstance(v, list):
                        for ele in v:
                            if ele not in valids:
                                keyvalueErrors.append((checkKey,k,v,ele))
                    else:
                        if v not in valids:
                            keyvalueErrors.append((checkKey,k,v))

    return keyvalueErrors

# process a list of strats
def process_strats(src, paramData):
    '''
    Process strats
    '''
    key = paramData["key"]
    fromNode = paramData["fromNode"]
    fromNodeRef = paramData["fromNodeRef"]
    roomData = paramData["roomData"]
    toNode = paramData["toNode"]
    bail = paramData["bail"]

    stratNames = []

    showNodes = True
    toNodeRef = f"{fromNodeRef}:destinationNode[{toNode}]"

    # cycle through strats
    for strat in src:
        stratRef = f"{toNodeRef}:stratName[{strat['name']}]"
        if(strat["name"] in stratNames):
            msg = f"🔴ERROR: Duplicate strat:{stratRef}"
            messages["reds"].append(msg)
            messages["counts"]["reds"] += 1
        stratNames.append(strat["name"])

    paramData = {
        "fromNode": fromNode,
        "fromNodeRef": fromNodeRef,
        "roomData": roomData,
        "showNodes": showNodes,
        "toNode": toNode,
        "bail": bail
    }
    return paramData


def has_reset_room(req):
    if isinstance(req, dict):
        if "resetRoom" in req:
            return True
        elif "or" in req:
            return any(has_reset_room(x) for x in req["or"])
        elif "and" in req:
            return any(has_reset_room(x) for x in req["and"])
        else:
            return False


keywords = []

# load keywords
print("Load Keywords")
keywordsPath = os.path.join(
    ".",
    "resources",
    "app",
    "manifests",
    "keywords.json"
)
with open(keywordsPath, encoding="utf-8") as keywordsFile:
    keywords = json.load(keywordsFile)

keywords["values"] = [
    "never",
    "spinjump"
]

# load enemies
print("Load Enemies & Bosses")
enemies = {}
enemiesPaths = [
    os.path.join(".","enemies","main.json"),
    os.path.join(".","enemies","bosses","main.json")
]
for enemiesPath in enemiesPaths:
    with open(enemiesPath, encoding="utf-8") as enemiesFile:
        enemiesJSON = json.load(enemiesFile)
        if "enemies" in enemiesJSON:
            for enemy in enemiesJSON["enemies"]:
                if "id" in enemy:
                    enemies[enemy["id"]] = enemy

# validate enemies, helpers, tech, weapons
for jsonPath in [
    os.path.join(".","enemies","main.json"),
    os.path.join(".","enemies","bosses","main.json"),
    os.path.join(".","helpers.json"),
    os.path.join(".","tech.json"),
    os.path.join(".","weapons","main.json")
]:
    pattern = r"(?:[\.][\\])([\w]+)"
    matches = re.match(pattern, jsonPath)
    if matches:
        dataType = matches.group(1)
        dataType = dataType[0].upper() + dataType[1:]
        print(f"Check {dataType}")
        with open(jsonPath, encoding="utf-8") as dataFile:
            dataJSON = json.load(dataFile)
            flattened_dict = [
                flatten(d, '.') for d in [dataJSON]
            ][0]
            # print(flattened_dict)
            for [k, v] in flattened_dict.items():
                process_keyvalue(k, v, {})

# process connections to identify door positions:
vertical_door_nodes = set()
door_position_dict = {}
connections = {
    "inter": {},
    "intra": {},
    "subarea": {}
}
connectionPath = os.path.join(".","connection")
for root, dirs, files in os.walk(os.path.join(".", "connection")):
    for filename in files:
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(root, filename), "r", encoding="utf-8") as connectionFile:
            connections_json = json.load(connectionFile)
            for connection in connections_json["connections"]:
                for i, node in enumerate(connection["nodes"]):
                    door_position_dict[(node["roomid"], node["nodeid"])] = node["position"]
                if connection["connectionType"] in ["VerticalDoor", "VerticalSandpit"]:
                    for i, node in enumerate(connection["nodes"]):
                        vertical_door_nodes.add((node["roomid"], node["nodeid"]))

print("")
print("Check Regions")
for r,d,f in os.walk(os.path.join(".","region")):
    for filename in f:
        if ".json" in filename and "roomDiagrams" not in filename:
            roomPath = os.path.join(r, filename)
            with open(roomPath, encoding="utf-8") as regionFile:
                roomJSON = json.load(regionFile)
                flattened_dict = [
                    flatten(d, '.') for d in [roomJSON]
                ][0]
                # print(flattened_dict)
                # check rooms

                room = roomJSON
                roomName = room["name"]
                area = room["area"]
                subarea = room["subarea"]
                subsubarea = room["subsubarea"] if "subsubarea" in room else ""
                showArea = False
                fullarea = f"{area}/{subarea}" + ((subsubarea != "") and f"/{subsubarea}" or "")

                # do a naive pass on all data in this region
                for [k, v] in flattened_dict.items():
                    ret = process_keyvalue(k, v, {"region": fullarea})
                    if not ret and not showArea:
                        showArea = True

                # cycle through rooms
                for room in [roomJSON]:
                    roomRef = f"{fullarea}:{room['id']}:{roomName}"
                    # check for uniqueness
                    if room["id"] not in uniques["roomID"]:
                        uniques["roomID"].append(room["id"])
                    else:
                        msg = f"🔴ERROR: Room ID not unique! {roomRef}"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1
                    if room["name"] not in uniques["roomName"]:
                        uniques["roomName"].append(room["name"])
                    else:
                        msg = f"🔴ERROR: Room Name not unique! {roomRef}"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1

                    # build an outline for this room
                    roomData = {
                        "id": room["id"],
                        "area": area,
                        "subarea": subarea,
                        "subsubarea": subsubarea,
                        "fullarea": fullarea,
                        "links": {
                            "from": {}
                        },
                        "nodes": {
                            "froms": [],
                            "tos": [],
                            "ids": [],
                            "names": [],
                            "spawnAts": [],
                            "leaveCharged": {
                                "from": {}
                            }
                        },
                        "obstacles": {
                            "ids": []
                        },
                        "enemies": {
                            "ids": []
                        }
                    }

                    # Volcano Room will not be tested for heat requirements since it is sometimes not heated.
                    heated = all(e["heated"] for e in room["roomEnvironments"])

                    # Document Obstacles
                    if "obstacles" in room:
                        for obstacle in room["obstacles"]:
                            obstacleRef = f"{roomRef}:{obstacle['id']}:{obstacle['name']}"
                            if obstacle["id"] in roomData["obstacles"]["ids"]:
                                msg = f"🔴ERROR: Obstacle ID not unique! {obstacleRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            else:
                                roomData["obstacles"]["ids"].append(obstacle["id"])

                    # Document Nodes
                    # Validate Nodes
                    node_lookup = {}
                    nodes_without_implicit_unlocks = set()
                    for node in room["nodes"]:
                        node_lookup[node['id']] = node
                        nodeRef = f"{roomRef}:{node['id']}"
                        if node["id"] in roomData["nodes"]["froms"]:
                            msg = f"🔴ERROR: Node ID not unique! {nodeRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        else:
                            roomData["nodes"]["froms"].append(node["id"])
                        if node["name"] in roomData["nodes"]["names"]:
                            msg = f"🔴ERROR: Node Name not unique! {nodeRef}:{node['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        else:
                            roomData["nodes"]["names"].append(node["name"])
                        roomData["nodes"]["ids"].append(node["id"])
                        if "spawnAt" in node and node["spawnAt"] not in roomData["nodes"]["spawnAts"]:
                            roomData["nodes"]["tos"].append(node["spawnAt"])

                        if node.get("useImplicitDoorUnlocks") is False:
                            nodes_without_implicit_unlocks.add(node['id'])

                        node_orientation = node.get("doorOrientation")
                        door_position = door_position_dict.get((room["id"], node["id"]))
                        if (node_orientation, door_position) not in [
                            ("left", "right"),
                            ("right", "left"),
                            ("up", "bottom"),
                            ("down", "top"),
                            (None, None),
                        ]:
                            msg = f"🔴ERROR: Door orientation '{node_orientation}' inconsistent with connection position '{door_position}': {nodeRef}:{node['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            
                    # Document Links
                    link_set = set()
                    for link_from in room["links"]:
                        from_node_id = link_from["from"]
                        if from_node_id not in roomData["nodes"]["ids"]:                            
                            msg = f"🔴ERROR: In links, from node {from_node_id} doesn't exist."
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        for link in link_from["to"]:
                            to_node_id = link["id"]
                            if to_node_id not in roomData["nodes"]["ids"]:                            
                                msg = f"🔴ERROR: In links, to node {to_node_id} doesn't exist."
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            link_set.add((from_node_id, to_node_id))

                    # Document Link Strats
                    for strat in room["strats"]:
                        if "link" not in strat:
                            msg = f"🔴ERROR: Strat is missing `link` property: {roomRef}:{strat['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            continue
                        link = strat["link"]
                        linkRef = str(link)
                        if tuple(strat["link"]) not in link_set:
                            msg = f"🔴ERROR: Link {linkRef} doesn't exist: {roomRef}:{strat['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        toNode = link[1]
                        roomData["nodes"]["tos"].append(toNode)

                    # Validate "enemies"
                    if "enemies" in room:
                        for enemy in room["enemies"]:
                            enemyGroupRef = ""
                            # Unique IDs
                            if enemy["id"] not in roomData["enemies"]["ids"]:
                                roomData["enemies"]["ids"].append(enemy["id"])
                                enemyGroupRef = f"{enemy['id']}:{enemy['groupName']}"
                            else:
                                msg = f"🔴ERROR: Enemy ID not unique! {roomRef}:{enemy['id']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                            if "homeNodes" in enemy:
                                for homeNode in enemy["homeNodes"]:
                                    homeNodeRef = f"Node[{roomRef}:{homeNode}]"
                                    if homeNode not in roomData["nodes"]["froms"]:
                                        msg = f"🔴ERROR: Invalid Home Node:{enemyGroupRef}:{homeNodeRef}"
                                        messages["reds"].append(msg)
                                        messages["counts"]["reds"] += 1
                            if "betweenNodes" in enemy:
                                for betweenNode in enemy["betweenNodes"]:
                                    betweenNodeRef = f"Node[{roomRef}:{betweenNode}]"
                                    if betweenNode not in roomData["nodes"]["froms"]:
                                        msg = f"🔴ERROR: Invalid Between Node:{enemyGroupRef}:{betweenNodeRef}"
                                        messages["reds"].append(msg)
                                        messages["counts"]["reds"] += 1

                    # Validate Obstacles
                    # check these keys
                    # check against obstacle IDs
                    # pass the whole room object
                    obstacleErrors = search_for_valid_keyvalue(
                        [
                            "clearsObstacles.",
                            "resetsObstacles.",
                            "obstaclesCleared.",
                            "obstaclesNotCleared.",
                        ],
                        f"{roomData['fullarea']}:room",
                        roomData["obstacles"]["ids"],
                        room
                    )
                    if obstacleErrors:
                        for obstacleError in obstacleErrors:
                            msg = f"🔴ERROR: Invalid Obstacles ID:{roomRef}:{obstacleError}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1

                    notable_id_set = set()
                    notable_name_set = set()
                    for notable in room.get("notables", []):
                        notable_id = notable["id"]
                        if notable_id in notable_id_set:
                            msg = f"🔴ERROR: Non-unique notable ID {notable_id} in notable:{roomRef}:{notable_name}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        if notable_id >= room["nextNotableId"]:
                            next_notable_id = room["nextNotableId"]
                            msg = f"🔴ERROR: Notable ID {notable_id} is not less than nextNotableId ({next_notable_id}):{roomRef}:{notable_name}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1                            
                        notable_id_set.add(notable["id"])

                        notable_name = notable["name"]
                        if notable_name in notable_name_set:
                            msg = f"🔴ERROR: Non-unique notable name {notable_name} in notable:{roomRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        notable_name_set.add(notable_name)

                    # Validate Requires Nodes
                    # check these keys
                    # check against node IDs that have links leading from
                    # pass the whole room object
                    requiresErrors = search_for_valid_keyvalue(
                        [
                            # "fromNode",
                            "fromNodes.",
                            "inRoomPath.",
                            "resetRoom.nodes.",
                            "itemNotCollectedAtNode"
                        ],
                        "room",
                        roomData["nodes"]["froms"],
                        room
                    )
                    if requiresErrors:
                        for requiresError in requiresErrors:
                            msg = f"🔴ERROR: Invalid Node ID:{roomRef}:{requiresError}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1

                    # Validate Entrance Nodes
                    # gather entrance nodes
                    entranceNodes = []
                    for node in room["nodes"]:
                        if node["id"] in roomData["nodes"]["froms"]:
                            if node["nodeType"] in ["door", "entrance"]:
                                entranceNodes.append(node["id"])
                    # check these keys
                    # check against entrance node IDs
                    # pass the whole room object
                    entranceErrors = search_for_valid_keyvalue(
                        [
                            "entranceNodes."
                        ],
                        "room",
                        entranceNodes,
                        room
                    )
                    if entranceErrors:
                        for entranceError in entranceErrors:
                            msg = f"🔴ERROR: Invalid Entrance Node ID:{roomRef}:{entranceError}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1

                    # Validate strats
                    previous_link = (0, 0)
                    strat_id_set = set()
                    used_notable_name_set = set()
                    for strat in room["strats"]:
                        if "link" not in strat or tuple(strat["link"]) not in link_set:
                            # Errors are already generated above in this case.
                            continue
                        link = strat["link"]
                        if tuple(link) < previous_link:
                            msg = f"🔴ERROR: Strat with link {list(link)} should come before previous link {list(previous_link)}:{stratRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        previous_link = tuple(link) 
                        fromNode = link[0]
                        fromNodeRef = f"Node[{roomRef}:{fromNode}]"
                        toNode = link[1]
                        paramData = {
                            "key": "linkStrats",
                            "fromNode": fromNode,
                            "fromNodeRef": fromNodeRef,
                            "roomData": roomData,
                            "toNode": toNode,
                            "bail": bail
                        }
                        paramData = process_strats([strat], paramData)
                        fromNode = link[0]
                        toNode = link[1]
                        strat_id = strat.get("id")
                        stratRef = f"{roomRef}:LINK:FromNode[{fromNode}]:ToNode[{toNode}]:{strat_id}:'{strat['name']}'"
                        if strat_id is not None:
                            if "id" in strat and strat_id in strat_id_set:
                                msg = f"🔴ERROR: Strat ID {strat_id} is not unique:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            strat_id_set.add(strat_id)
                            if strat_id >= room["nextStratId"]:
                                next_strat_id = room["nextStratId"]
                                msg = f"🔴ERROR: Strat ID {strat_id} is not less than nextStratId ({next_strat_id}):{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                        if heated and not check_heat_req({"and": strat["requires"]}):
                            if fromNode == toNode and "leaveWithRunway" in strat.get("exitCondition", []):
                                # Ok since there is implicit heat frames in leavesWithRunway, and it is normal
                                # if no explicit ones to be present for a strat going from the door to itself.
                                pass
                            elif "comeInWithGMode" in strat.get("entranceCondition", []) and "leaveWithGMode" in strat.get("exitCondition", []):
                                # Strats that come in with G-mode and leave with G-mode will be spending the entire time in G-mode,
                                # so it is normal for these strats to not have heat frames.
                                pass
                            elif "gModeRegainMobility" in strat:
                                # Regain mobility strats also take place entirely in G-mode.
                                pass
                            elif "comeInWithGrappleTeleport" in strat.get("entranceCondition", []) and \
                                  strat.get("bypassesDoorShell") is True:
                                # Strats that use a grapple teleport to bypass a door lock can be done without heat damage, 
                                # since the door transition is touched immediately.
                                pass
                            else:
                                msg = f"🔴ERROR: Strat in heated room lacking a heat requirement:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1                            
                        if "entranceCondition" in strat:
                            if node_lookup[fromNode]["nodeType"] not in ["door", "entrance"]:
                                msg = f"🔴ERROR: Strat has entranceCondition but From Node is not door or entrance:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if (room["id"], fromNode) in vertical_door_nodes and "comesThroughToilet" not in strat["entranceCondition"]:
                                msg = f"🔴ERROR: Strat with vertical entranceCondition is missing 'comesThroughToilet':{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if (room["id"], fromNode) not in vertical_door_nodes and "comesThroughToilet" in strat["entranceCondition"]:
                                msg = f"🔴ERROR: Strat has 'comesThroughToilet' but is not a vertical connection:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if "comeInWithTemporaryBlue" in strat["entranceCondition"]:
                                if (room["id"], fromNode) in vertical_door_nodes and "direction" not in strat["entranceCondition"]["comeInWithTemporaryBlue"]:
                                    msg = f"🔴ERROR: Strat has vertical comeInWithTemporaryBlue entranceCondition without 'direction':{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                if (room["id"], fromNode) not in vertical_door_nodes and "direction" in strat["entranceCondition"]["comeInWithTemporaryBlue"]:
                                    msg = f"🔴ERROR: Strat has non-vertical comeInWithTemporaryBlue entranceCondition with 'direction':{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        if "exitCondition" in strat:
                            if node_lookup[toNode]["nodeType"] not in ["door", "exit"]:
                                msg = f"🔴ERROR: Strat has exitCondition but To Node is not door or exit:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if "leaveShinecharged" in strat["exitCondition"]:
                                if strat["exitCondition"]["leaveShinecharged"]["framesRemaining"] == "auto":
                                    if ("entranceCondition" not in strat or "comeInShinecharged" not in strat["entranceCondition"]) and strat.get("startsWithShineCharge") is not True:
                                        msg = f"🔴ERROR: Strat has leaveShinecharged exitCondition with framesRemaining 'auto' but no comeInShinecharged entranceCondition or startsWithShineCharge:{stratRef}"
                                        messages["reds"].append(msg)
                                        messages["counts"]["reds"] += 1
                            if "leaveWithTemporaryBlue" in strat["exitCondition"]:
                                if (room["id"], toNode) in vertical_door_nodes and "direction" not in strat["exitCondition"]["leaveWithTemporaryBlue"]:
                                    msg = f"🔴ERROR: Strat has vertical leaveWithTemporaryBlue exitCondition without 'direction':{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                if (room["id"], toNode) not in vertical_door_nodes and "direction" in strat["exitCondition"]["leaveWithTemporaryBlue"]:
                                    msg = f"🔴ERROR: Strat has non-vertical leaveWithTemporaryBlue exitCondition with 'direction':{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                            if "resetsObstacles" in strat:
                                msg = f"🔴ERROR: Strat has exitCondition and also resetsObstacles:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if "clearsObstacles" in strat:
                                msg = f"🔴ERROR: Strat has exitCondition and also clearsObstacles:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if "leaveWithSpark" in strat["exitCondition"]:
                                if not check_shinespark_req({"and": strat["requires"]}):
                                    msg = f"🔴ERROR: Strat has leaveWithSpark exitCondition but is lacking a shinespark requirement:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1

                        node_subtype = node_lookup[toNode]["nodeSubType"]
                        door_unlocked_nodes = find_door_unlocked_nodes(strat, node_subtype, nodes_without_implicit_unlocks)
                        for node in door_unlocked_nodes:
                            missing_types = check_node_covered_in_unlocks_doors(strat, node)
                            if len(missing_types) == 3:
                                msg = f"🔴ERROR: Door unlocked requirement for node {node} is not covered in `unlocksDoors`:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            else:
                                for t in missing_types:
                                    msg = f"🔴ERROR: Door unlocked requirement for node {node}, type {t}, is not covered in `unlocksDoors`:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        if strat.get("bypassesDoorShell") == True:
                            if node_lookup[toNode]["nodeType"] != "door":
                                msg = f"🔴ERROR: Strat has bypassesDoorShell but To Node is not door:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        if "collectsItems" in strat:
                            for item_node_id in strat["collectsItems"]:
                                if item_node_id not in node_lookup or node_lookup[item_node_id]["nodeType"] != "item":
                                    msg = f"🔴ERROR: collectsItems references node {item_node_id} which is not an item node:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1

                        if "setsFlags" in strat:
                            for flag in strat["setsFlags"]:
                                if flag not in keywords["flags"]:
                                    msg = f"🔴ERROR: setsFlags references flag '{flag}' which does not exist:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                    
                        if has_reset_room({"and": strat["requires"]}) and "exitCondition" not in strat:
                            for obs in room.get("obstacles", []):
                                obs_id = obs["id"]
                                if obs_id not in strat.get("resetsObstacles", []) and obs_id not in strat.get("clearsObstacles", []):
                                    msg = f"🔴ERROR: strat has resetRoom but does not reset or clear obstacle {obs_id}:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        
                        def check_for_notables(req):
                            if isinstance(req, dict):
                                if "notable" in req:
                                    notable_name = req["notable"]
                                    if notable_name not in notable_name_set:
                                        msg = f"🔴ERROR: Invalid notable name {notable_name} in notable:{stratRef}"
                                        messages["reds"].append(msg)
                                        messages["counts"]["reds"] += 1
                                    used_notable_name_set.add(req["notable"])
                                elif "or" in req:
                                    for r in req["or"]:
                                        check_for_notables(r)
                                elif "and" in req:
                                    for r in req["and"]:
                                        check_for_notables(r)
                        for req in strat["requires"]:
                            check_for_notables(req)

                    for notable_name in notable_name_set.difference(used_notable_name_set):
                        msg = f"🟡WARNING: Unused notable:{roomRef}:{notable_name}"
                        messages["yellows"].append(msg)
                        messages["counts"]["yellows"] += 1

                    # Validate Nodes
                    showNodes = paramData["showNodes"]
                    bail = paramData["bail"]
                    for node in room["nodes"]:
                        orphaned = False
                        # If there's no link, call it orphaned
                        if node["nodeType"] != "door" and \
                            node["id"] not in roomData["nodes"]["tos"]:
                            nodeRef = f"{roomRef}:{node['id']}:{node['name']}"
                            orphaned = True

                        foundNode = False
                        if "spawnAt" in node:
                            foundNode = node["spawnAt"] in roomData["nodes"]["froms"]
                            orphaned = not foundNode
                            if orphaned:
                                msg = f"🔴ERROR: Orphaned SpawnAt! {nodeRef}::{node['spawnAt']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        # If it's orphaned, try to find a connection
                        if orphaned:
                            connections = {
                                "inter": {},
                                "intra": {},
                                "subarea": {}
                            }

                            connectionPath = os.path.join(".","connection")
                            otherRef = ""

                            if not foundNode:
                                with open(os.path.join(connectionPath, "inter.json"), "r", encoding="utf-8") as connectionFile:
                                    connections["inter"] = json.load(connectionFile)
                                for sector in ["intra", "subarea"]:
                                    if subarea.lower() == "upper":
                                        subarea = subsubarea
                                        subsubarea = ""
                                    if subarea.lower() == "lower":
                                        area = "lowernorfair"
                                        subarea = subsubarea
                                        subsubarea = ""
                                    sectorPath = os.path.join(".","connection", area.lower().replace(" station",""))
                                    filename = sector
                                    if sector == "subarea":
                                        filename = subarea.lower()
                                        # if subsubarea != "":
                                        #     filename = f"{filename}-{subsubarea.lower()}"
                                        #     print(os.path.join(sectorPath,f"{filename}.json"))
                                    if os.path.isfile(os.path.join(sectorPath, f"{filename}.json")):
                                        with open(os.path.join(sectorPath, f"{filename}.json"), "r", encoding="utf-8") as connectionFile:
                                            connections[sector] = json.load(connectionFile)
                                for sector in ["subarea", "intra", "inter"]:
                                    if "connections" in connections[sector]:
                                        for connection in connections[sector]["connections"]:
                                            for [cNodeIDX, cNode] in enumerate(connection["nodes"]):
                                                if foundNode:
                                                    break
                                                if cNode["roomid"] == room["id"]:
                                                    if cNode["nodeid"] == node["id"]:
                                                        oNode = connection["nodes"][0 if cNodeIDX == 1 else 1]
                                                        otherRef = f"{oNode['roomid']}:{oNode['roomName']}:{oNode['nodeid']}:{oNode['nodeName']}"
                                                        foundNode = True
                            if not foundNode:
                                msg = f"🔴ERROR: Orphaned Node! {nodeRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            else:
                                msg = f"🟢{nodeRef}" + "\n" + f"::{otherRef}"
                                # messages["greens"].append(msg)
                                # messages["counts"]["greens"] += 1
                                # showArea = True
                    if showNodes:
                        # print(json.dumps(roomData, indent=2))
                        pass

                # See if error got resolved with manual checks
                if showArea:
                    usedGroups = []
                    for clr in ["green", "yellow", "red"]:
                    # for clr in ["green", "red", "yellow"]:
                        if len(messages[f"{clr}s"]) > 0:
                            for [msgIDX, msg] in enumerate(messages[f"{clr}s"]):
                                # print(msg)
                                pattern = r"([🔴|🟡|🟢]{1})" + \
                                    r"(rooms)(?:\.)" + \
                                    r"([\d]+)(?:\.)" + \
                                    r"(nodes)(?:\.)" + \
                                    r"([\w]+)(?:\.)" + \
                                    r"([^\.]+)(?:\.)" + \
                                    r"([\w]+)(?:\.)" + \
                                    r"(initiateRemotely.pathToDoor)(?:\.)" + \
                                    r"([\w]+)(?:\.)" + \
                                    r"(strats)(?:\.)" + \
                                    r"([\w]+)(?:\.)" + \
                                    r"(.*)"
                                region = ""
                                if isinstance(msg, dict):
                                    if "region" in msg:
                                        region = msg["region"]
                                    if "msg" in msg:
                                        msg = msg["msg"]
                                matches = re.match(pattern, msg)
                                if matches:
                                    groups = list(matches.groups())
                                    del groups[0]
                                    groups[3] = 'x'
                                    groups[5] = 'x'
                                    groups[7] = 'x'
                                    groups[9] = 'x'
                                    if ".".join(groups) not in usedGroups:
                                        usedGroups.append(".".join(groups))
                                        showArea = False
                                        if clr not in ["green"]:
                                            showArea = True
                                            print(".".join(groups))
                                            # print(msg)
                                    elif clr == "red":
                                        messages["counts"]["reds"] -= 1
                                else:
                                    # print(msg)
                                    pass
                            # print("\n".join(messages[f"{clr}s"]))
                    if showArea:
                        print()
                # print(messages["counts"])
                if messages["counts"]["reds"] > 0:
                    bail = True

# print(uniques)

firstErr = True
firstWarn = True
foundErr = False
foundWarn = False
lastRegion = ""
region = ""
for msg in messages["reds"]:
    if isinstance(msg, dict):
        if "region" in msg:
            region = msg["region"]
        if "msg" in msg:
            if "note" in msg:
                msg["msg"] += " !! " + msg["note"]
            msg = msg["msg"]
    if "ERROR" in msg or "requires" in msg:
        foundErr = True
        if firstErr:
            print("🔴 {} ERRORs 🔴".format(len(messages["reds"])))
            firstErr = False
        if region != lastRegion:
            print(region)
            lastRegion = region
        print(msg)
for msg in messages["yellows"]:
    if isinstance(msg, dict):
        if "region" in msg:
            region = msg["region"]
        if "msg" in msg:
            if "note" in msg:
                msg["msg"] += " !! " + msg["note"]
            msg = msg["msg"]
    if "WARNING" in msg or "requires" in msg:
        foundWarn = True
        if firstWarn:
            print("🟡 {} WARNINGs 🟡".format(len(messages["yellows"])))
            firstWarn = False
        if region != lastRegion:
            print(region)
            lastRegion = region
        print(msg)
if foundErr:
    print("🔴Something fucked up! Bailing!")
    sys.exit(1)
