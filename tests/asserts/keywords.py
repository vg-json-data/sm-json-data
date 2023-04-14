# pylint: disable=global-at-module-level, invalid-name, too-many-locals
'''
Check for validity of keywords in files
'''
import json
import os
import re
import sys
from flatten_json import flatten

bail = False
last_enemy = ""
uniques = {
    "groupName": [],
    "roomID": [],
    "roomName": [],
    "roomAddress": [],
    "nodeAddress": []
}

def process_keyvalue(k, v):
    '''
    Take a keyvalue pair and see if the value exists in our list of keywords
    '''
    global bail
    global last_enemy
    global uniques
    goodValue = True
    processValue = True
    goodKeys = [
        "additionalObstacles",
        "obstaclesCleared",
        "obstaclesNotCleared",
        "subarea",
        "twinDoorAddresses"
    ]
    badKeys = [
        "$schema",      # immaterial
        "description",  # immaterial
        "devNote",      # immaterial
        "note",         # immaterial
        "name",         # !!could check for unique
        "id",           # !!could check for unique
        # "groupName",    # !!could check for unique
        # "nodeAddress",  # !!could check for unique
        # "roomAddress",  # !!could check for unique
        "mode",         # validated by schema
        "lockType",     # validated by schema
        "nodeType",     # validated by schema
        "nodeSubType",  # validated by schema
        "obstacleType", # validated by schema
        "physics",      # validated by schema
        "utility"       # validated by schema
    ]
    if k in badKeys or k in goodKeys:
        processValue = False
    else:
        for checkKey in badKeys:
            if checkKey in k:
                processValue = False
        for checkKey in goodKeys:
            if checkKey in k:
                processValue = False

    isSkip = False
    kCheck = k.split(".")[-1]
    if kCheck in uniques and "twinDoorAddresses" not in k:
        if v not in uniques[kCheck]:
            uniques[kCheck].append(v)
            isSkip = True
        else:
            print(f"🔴ERROR: {k}:{v} not unique!")
            bail = True

    if processValue:
        isFloat = isinstance(v, float)
        isInt = isinstance(v, int)
        isList = isinstance(v, list)
        isEmptyList = isList and len(v) == 0
        isNumeric = not isFloat and not isInt and not isList and v.isnumeric()
        if not isFloat and \
            not isInt and \
            not isEmptyList and \
            not isNumeric and \
            not isSkip:
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
            if (isEnemy or last_enemy != "") and ".enemy" in k and ".enemyKill" not in k:
                if ".type" not in k:
                    last_enemy = v
                elif ".type" in k:
                    if last_enemy in keywords["enemies"]["enemyByName"]:
                        enemyID = keywords["enemies"]["enemyByName"][last_enemy]
                        if enemyID in enemies:
                            if "attacks" in enemies[enemyID]:
                                attackExists = False
                                for attack in enemies[enemyID]["attacks"]:
                                    if "name" in attack:
                                        if attack["name"] == v:
                                            attackExists = True
                                goodValue = attackExists
                        last_enemy = ""
                    else:
                        print(f"🔴ERROR: {last_enemy} not found!")
            else:
                if not isArea and \
                    not isEnemy and \
                    not isHelper and \
                    not isItem and \
                    not isFlag and \
                    not isTech and \
                    not isWeapon and \
                    not isValue:
                    goodValue = False
                    print(f"🟡{k} {v}")
    return goodValue

def process_strats(src, paramData):
    key = paramData["key"]
    fromNode = paramData["fromNode"]
    fromNodeRef = paramData["fromNodeRef"]
    roomData = paramData["roomData"]
    toNode = paramData["toNode"]
    bail = paramData["bail"]

    showNodes = True
    toNodeRef = f"{fromNodeRef}:{toNode}"
    for strat in src["strats"]:
        stratRef = f"{toNodeRef}:{strat}"
        if fromNode in roomData["links"]["from"]:
            if toNode in roomData["links"]["from"][fromNode]["to"]:
                if strat not in roomData["links"]["from"][fromNode]["to"][toNode]["strats"]:
                    print(f"🔴ERROR: Invalid strat:{stratRef}")
                    bail = True
                else:
                    if showArea:
                        print(f"🟢{stratRef}")
                    roomData["nodes"][key]["from"][fromNode]["to"][toNode]["strats"].append(strat)
            else:
                foundPath = False
                for tNode in roomData["links"]["from"][fromNode]["to"]:
                    if (not foundPath) and (toNode in roomData["links"]["from"][tNode]["to"]):
                        foundPath = True
                        print(f"🟢{stratRef}::{fromNode}:{tNode}:{toNode}")
                if not foundPath:
                    if str(room["id"]) in cheatSheetJSON and \
                        str(fromNode) in cheatSheetJSON[str(room["id"])] and \
                        str(toNode) in cheatSheetJSON[str(room["id"])][str(fromNode)]:
                        intermediateNode = cheatSheetJSON[str(room["id"])][str(fromNode)][str(toNode)]["via"]
                        print(f"🟡{stratRef}::{fromNode}:{intermediateNode}:{toNode}")
                    else:
                        print(f"🔴ERROR: Destination node path not found:{toNodeRef}")
                        bail = True
        else:
            print(f"🔴ERROR: From node not found:{fromNodeRef}")
            bail = True

    paramData = {
        "fromNode": fromNode,
        "fromNodeRef": fromNodeRef,
        "roomData": roomData,
        "showNodes": showNodes,
        "toNode": toNode,
        "bail": bail
    }
    return paramData

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
                process_keyvalue(k, v)

cheatSheetJSON = {}
with open(os.path.join(".","tests","asserts","canLeaveCharged.json"), encoding="utf-8") as cheatSheetFile:
    cheatSheetJSON = json.load(cheatSheetFile)

print("")
print("Check Regions")
for r,d,f in os.walk(os.path.join(".","region")):
    for filename in f:
        if ".json" in filename and "roomDiagrams" not in filename:
            regionPath = os.path.join(r, filename)
            with open(regionPath, encoding="utf-8") as regionFile:
                regionJSON = json.load(regionFile)
                flattened_dict = [
                    flatten(d, '.') for d in [regionJSON]
                ][0]
                # print(flattened_dict)
                if "rooms" in regionJSON:
                    room = regionJSON["rooms"][0]
                    area = room["area"]
                    subarea = room["subarea"]
                    subsubarea = "subsubarea" in room and room["subsubarea"] or ""
                    showArea = False
                    print(f"{area}/{subarea}" + ((subsubarea != "") and f"/{subsubarea}" or ""))
                    for [k, v] in flattened_dict.items():
                        ret = process_keyvalue(k, v)
                        if not ret and not showArea:
                            showArea = True
                    for room in regionJSON["rooms"]:
                        roomRef = f"{room['id']}:{room['name']}"
                        if room["id"] not in uniques["roomID"]:
                            uniques["roomID"].append(room["id"])
                        else:
                            print(f"🔴ERROR: Room ID not unique! {roomRef}")
                            bail = True
                        if room["name"] not in uniques["roomName"]:
                            uniques["roomName"].append(room["name"])
                        else:
                            print(f"🔴ERROR: Room Name not unique! {roomRef}")
                            bail = True
                        if "nodes" in room:
                            roomData = {
                                "id": room["id"],
                                "links": {
                                    "from": {}
                                },
                                "nodes": {
                                    "froms": [],
                                    "tos": [],
                                    "leaveCharged": {
                                        "from": {}
                                    }
                                }
                            }
                            showNodes = False
                            gModeObjects = []
                            if "links" in room:
                                for link in room["links"]:
                                    if "from" in link:
                                        roomData["links"]["from"][link["from"]] = {
                                            "to": {}
                                        }
                                        for to in link["to"]:
                                            if to["id"] not in roomData["nodes"]["tos"]:
                                                roomData["nodes"]["tos"].append(to["id"])
                                                gModeTo = to
                                                gModeTo["fromNode"] = link["from"]
                                                gModeObjects.append(gModeTo)
                                            roomData["links"]["from"][link["from"]]["to"][to["id"]] = {
                                                "strats": []
                                            }
                                            if "strats" in to:
                                                for strat in to["strats"]:
                                                    roomData["links"]["from"][link["from"]]["to"][to["id"]]["strats"].append(strat["name"])
                            for node in room["nodes"]:
                                if "id" in node:
                                    nodeRef = f"{roomRef}:{node['id']}"
                                    if node["id"] in roomData["nodes"]["froms"]:
                                        print(f"🔴ERROR: Node ID not unique! {nodeRef}")
                                        bail = True
                                    else:
                                        roomData["nodes"]["froms"].append(node["id"])
                                if "canLeaveCharged" in node:
                                    for leave in node["canLeaveCharged"]:
                                        if "initiateRemotely" in leave:
                                            remote = leave["initiateRemotely"]
                                            if "initiateAt" in remote:
                                                fromNode = remote["initiateAt"]
                                                fromNodeRef = f"{roomRef}:{fromNode}"
                                                if "pathToDoor" in remote:
                                                    for path in remote["pathToDoor"]:
                                                        toNode = -1
                                                        if "destinationNode" in path:
                                                            toNode = path["destinationNode"]
                                                            if fromNode not in roomData["nodes"]["leaveCharged"]["from"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][fromNode] = {
                                                                    "to": {}
                                                                }
                                                            if toNode not in roomData["nodes"]["leaveCharged"]["from"][fromNode]["to"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][fromNode]["to"][toNode] = {
                                                                    "strats": []
                                                                }
                                                        if toNode == -1:
                                                            print(f"🔴ERROR: Destination node not defined:{fromNodeRef}")
                                                            bail = True
                                                        if "strats" in path:
                                                            paramData = {
                                                                "key": "leaveCharged",
                                                                "fromNode": fromNode,
                                                                "fromNodeRef": fromNodeRef,
                                                                "roomData": roomData,
                                                                "toNode": toNode,
                                                                "bail": bail
                                                            }
                                                            paramData = process_strats(path, paramData)
                                                            showNodes = paramData["showNodes"]
                                                            bail = paramData["bail"]

                                if "leaveWithGMode" in node:
                                    for leaveG in node["leaveWithGMode"]:
                                        gModeObjects.append(leaveG)
                            for gModeObj in gModeObjects:
                                if "strats" in gModeObj:
                                    parentNodeRef = ""
                                    if "fromNode" in gModeObj:
                                        parentNodeRef = f"{gModeObj['fromNode']}:"
                                    toNodeRef = f"{roomRef}:{parentNodeRef}"
                                    if "id" in gModeObj:
                                        toNodeRef += f"{gModeObj['id']}:"
                                    for strat in gModeObj["strats"]:
                                        stratRef = f"{toNodeRef}{strat['name']}"
                                        if "requires" in strat:
                                            for req in strat["requires"]:
                                                if "comeInWithGMode" in req:
                                                    if "fromNodes" in req["comeInWithGMode"]:
                                                        for fromNode in req["comeInWithGMode"]["fromNodes"]:
                                                            fromNodeRef = f"{stratRef}:{fromNode}"
                                                            if fromNode not in roomData["nodes"]["froms"]:
                                                                print(f"🔴ERROR: From Node doesn't exist:{fromNodeRef}")
                                                                bail = True
                                                            else:
                                                                print(f"🟢{fromNodeRef}")
                            for node in room["nodes"]:
                                orphaned = False
                                if node["nodeType"] != "door" and \
                                    node["id"] not in roomData["nodes"]["tos"]:
                                    nodeRef = f"{roomRef}:{node['id']}:{node['name']}"
                                    orphaned = True
                                if orphaned:
                                    connections = {
                                        "inter": {},
                                        "intra": {},
                                        "subarea": {}
                                    }
                                    connectionPath = os.path.join(".","connection")
                                    with open(os.path.join(connectionPath, "inter.json"), "r", encoding="utf-8") as connectionFile:
                                        connections["inter"] = json.load(connectionFile)
                                    for sector in ["intra", "subarea"]:
                                        sectorPath = os.path.join(".","connection", area.lower())
                                        filename = sector
                                        if sector == "subarea":
                                            filename = subarea.lower()
                                        with open(os.path.join(sectorPath, f"{filename}.json"), "r", encoding="utf-8") as connectionFile:
                                            connections[sector] = json.load(connectionFile)
                                    foundNode = False
                                    otherRef = ""
                                    for sector in ["subarea", "intra", "inter"]:
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
                                        print(f"🔴ERROR: Orphaned Node! {nodeRef}")
                                        bail = True
                                    else:
                                        print(f"🟢{nodeRef}")
                                        print(f"::{otherRef}")
                                        showArea = True
                            if showNodes:
                                # print(json.dumps(roomData, indent=2))
                                pass
                    if showArea:
                        print()

# print(uniques)

if bail:
    sys.exit(1)
