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

def process_keyvalue(k, v):
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
        "mobility",         # validated by schema
        "mode",             # validated by schema
        "jumpwayType",      # validated by schema
        "lockType",         # validated by schema
        "nodeType",         # validated by schema
        "nodeSubType",      # validated by schema
        "obstacleType",     # validated by schema
        "physics",          # validated by schema
        "utility",          # validated by schema
        "resourceCapacity"  # validated by schema
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
        isNumeric = not isFloat and not isInt and not isList and v.isnumeric()
        if not isFloat and \
            not isInt and \
            not isEmptyList and \
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
                    msg = f"🔴{k} {v}"
                    messages["reds"].append(msg)
                    messages["counts"]["reds"] += 1
    return goodValue

# try to navigate a path between nodes if no direct path
def search_for_path(fromNodes, sourceNode, targetNode):
    foundPath = False
    for tNode in fromNodes[str(sourceNode)]["to"]:
        if (not foundPath) and \
            (str(tNode) in roomData["links"]["from"]) and \
            (str(targetNode) in roomData["links"]["from"][str(tNode)]["to"]):
            foundPath = True
            msg = f"🟢{stratRef}::{sourceNode}:{tNode}:{targetNode}"
            print(msg)
            # messages["greens"].append(msg)
            # messages["counts"]["greens"] += 1
    return foundPath

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
    roomIDX = paramData["roomIDX"]
    toNode = paramData["toNode"]
    bail = paramData["bail"]

    showNodes = True
    toNodeRef = f"{fromNodeRef}:destinationNode[{toNode}]"

    # cycle through strats
    for strat in src["strats"]:
        stratRef = f"{toNodeRef}:stratName[{strat}]"
        if "name" in strat:
            stratRef = f"{toNodeRef}:stratName[{strat['name']}]"
        # if fromNode is valid
        if str(fromNode) in roomData["links"]["from"]:
            # if direct path to toNode from fromNode exists
            if str(toNode) in roomData["links"]["from"][str(fromNode)]["to"]:
                # if the strat referenced doesn't exist on this node
                if strat not in roomData["links"]["from"][str(fromNode)]["to"][str(toNode)]["strats"] and \
                    strat["name"] not in roomData["links"]["from"][str(fromNode)]["to"][str(toNode)]["strats"]:
                    msg = f"🔴ERROR: Invalid strat:{stratRef}"
                    messages["reds"].append(msg)
                    messages["counts"]["reds"] += 1
                else:
                    # valid strat
                    # if it's got obstacles
                    if "obstacles" in strat:
                        for obstacle in strat["obstacles"]:
                            # make sure the obstacle exists in the room
                            if obstacle["id"] not in roomData["obstacles"]["ids"]:
                                msg = f"🔴ERROR: Invalid Obstacle ID:{stratRef}:{obstacle['id']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            # check additionalObstacles too
                            if "additionalObstacles" in obstacle:
                                for addtlObstacle in obstacle["additionalObstacles"]:
                                    # make sure it exists in the room
                                    if addtlObstacle not in roomData["obstacles"]["ids"]:
                                        msg = f"🔴ERROR: Invalid Additional Obstacle ID:{stratRef}:{obstacle['id']}:{addtlObstacle}"
                                        messages["reds"].append(msg)
                                        messages["counts"]["reds"] += 1
                    # check cleared obstacles too
                    if "clearedObstacles" in strat:
                        for obstacle in strat["clearedObstacles"]:
                            # make sure it exists in the room
                            if obstacle not in roomData["obstacles"]["ids"]:
                                msg = f"🔴ERROR: Invalid Cleared Obstacle ID:{stratRef}:{obstacle}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                    if showArea:
                        msg = ""
                        area = roomData["area"]
                        subarea = roomData["subarea"]
                        msg += f"🟢{roomData['fullarea']}/rooms.{roomIDX}.nodes.x.canLeaveCharged.x.initiateRemotely.pathToDoor.x.strats.x {strat}"
                        messages["greens"].append(msg)
                        messages["counts"]["greens"] += 1
                    if key == "linkStrats":
                        roomData["links"] \
                          ["from"][str(fromNode)] \
                          ["to"][str(toNode)] \
                          ["strats"].append(strat)
                    else:
                        roomData["nodes"][key] \
                          ["from"][fromNode] \
                          ["to"][toNode] \
                          ["strats"].append(strat)
            else:
                # no direct path to toNode from fromNode exists
                foundPath = False
                fromNodes = roomData["links"]["from"]
                sourceNode = fromNode
                targetNode = toNode
                # try to search for path
                foundPath = search_for_path(fromNodes, sourceNode, targetNode)
                if not foundPath:
                    # still couldn't find a path
                    if str(room["id"]) in cheatSheetJSON and \
                        str(fromNode) in cheatSheetJSON[str(room["id"])] and \
                        str(toNode) in cheatSheetJSON[str(room["id"])][str(fromNode)]:
                        intermediateNode = cheatSheetJSON[str(room["id"])] \
                          [str(fromNode)] \
                          [str(toNode)] \
                          ["via"]
                        msg = f"🟡{stratRef}::{fromNode}:{intermediateNode}:{toNode}"
                        messages["yellows"].append(msg)
                        messages["counts"]["yellows"] += 1
                    else:
                        msg = f"🔴ERROR: Destination node path not found:{toNodeRef}"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1
        else:
            msg = f"🔴ERROR: From node not found:{fromNodeRef}"
            messages["reds"].append(msg)
            messages["counts"]["reds"] += 1

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
                process_keyvalue(k, v)

cheatSheetJSON = {}
with open(
    os.path.join(
        ".",
        "tests",
        "asserts",
        "canLeaveCharged.json"
    ),
    encoding="utf-8"
) as cheatSheetFile:
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
                # check rooms
                if "rooms" in regionJSON:
                    # get data about this region by getting from first room
                    room = regionJSON["rooms"][0]
                    area = room["area"]
                    subarea = room["subarea"]
                    subsubarea = room["subsubarea"] if "subsubarea" in room else ""
                    showArea = False
                    fullarea = f"{area}/{subarea}" + ((subsubarea != "") and f"/{subsubarea}" or "")
                    print(fullarea)

                    # do a naive pass on all data in this region
                    for [k, v] in flattened_dict.items():
                        ret = process_keyvalue(k, v)
                        if not ret and not showArea:
                            showArea = True

                    # cycle through rooms
                    for [roomIDX, room] in enumerate(regionJSON["rooms"]):
                        roomRef = f"{fullarea}:{room['id']}:{room['name']}"
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
                            },
                            "reusableStrats": {
                                "names": []
                            }
                        }

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
                        # Document Reusable Roomwide Strats
                        if "reusableRoomwideNotable" in room:
                            for strat in room["reusableRoomwideNotable"]:
                                roomData["reusableStrats"]["names"].append(strat["name"])
                        # Document Nodes
                        # Document Links
                        # Document Link Strats
                        if "nodes" in room:
                            showNodes = False
                            gModeObjects = []
                            if "links" in room:
                                for link in room["links"]:
                                    if "from" in link:
                                        fromNode = link["from"]
                                        fromNodeRef = f"Node[{roomRef}:{fromNode}]"
                                        roomData["links"]["from"][str(fromNode)] = {
                                            "to": {}
                                        }
                                        for to in link["to"]:
                                            toNode = to["id"]
                                            if toNode not in roomData["nodes"]["tos"]:
                                                roomData["nodes"]["tos"].append(toNode)
                                                gModeTo = to
                                                gModeTo["fromNode"] = fromNode
                                                gModeObjects.append(gModeTo)
                                            roomData["links"] \
                                              ["from"][str(fromNode)] \
                                              ["to"][str(toNode)] = {
                                                "strats": []
                                            }
                                            if "strats" in to:
                                                for strat in to["strats"]:
                                                    roomData["links"] \
                                                      ["from"][str(fromNode)] \
                                                      ["to"][str(toNode)] \
                                                      ["strats"].append(strat["name"])

                            # Validate Nodes
                            for node in room["nodes"]:
                                if "id" in node:
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
                                if "spawnAt" in node and node["spawnAt"] not in roomData["nodes"]["spawnAts"]:
                                    roomData["nodes"]["spawnAts"].append(node["spawnAt"])

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
                                    "obstaclesCleared",
                                    "obstaclesNotCleared",
                                    "obstaclesToAvoid",
                                ],
                                f"{roomData['fullarea']}/room",
                                roomData["obstacles"]["ids"],
                                room
                            )
                            if obstacleErrors:
                                for obstacleError in obstacleErrors:
                                    msg = f"🔴ERROR: Invalid Obstacles ID:{roomRef}:{obstacleError}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1

                            # Validate Reusable Roomwide Strats
                            # check these keys
                            # check against reusable strat names
                            # pass the whole room object
                            reusableErrors = search_for_valid_keyvalue(
                                [
                                    "reusableRoomwideNotable"
                                ],
                                "room",
                                roomData["reusableStrats"]["names"],
                                room
                            )
                            if reusableErrors:
                                for reusableError in reusableErrors:
                                    msg = f"🔴ERROR: Invalid Reusable Strat Name:{roomRef}:{reusableError}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1

                            # Validate Requires Nodes
                            # check these keys
                            # check against node IDs that have links leading from
                            # pass the whole room object
                            requiresErrors = search_for_valid_keyvalue(
                                [
                                    "fromNode",
                                    "fromNodes.",
                                    "inRoomPath.",
                                    "resetRoom.nodes.",
                                    "nodesToAvoid.",
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


                            # Validate canLeaveCharged
                            # Validate leaveWithGMode
                            for node in room["nodes"]:
                                if "id" in node:
                                    nodeRef = f"{roomRef}:{node['id']}"
                                # node.canLeaveCharged[x]
                                if "canLeaveCharged" in node:
                                    for [leaveID, leave] in enumerate(node["canLeaveCharged"]):
                                        # node.canLeaveCharged[x].initiateRemotely
                                        if "initiateRemotely" in leave:
                                            remote = leave["initiateRemotely"]
                                            # node.canLeaveCharged[x].initiateRemotely.initiateAt
                                            if "initiateAt" in remote:
                                                fromNode = remote["initiateAt"]
                                                fromNodeRef = f"Node[{nodeRef}]:canLeaveCharged[{int(leaveID) + 1}]:initiateRemotelyAt[{fromNode}]"
                                                toNodeRef = f"From{fromNodeRef}"
                                                # node.canLeaveCharged[x].initiateRemotely.pathToDoor[x]
                                                if "pathToDoor" in remote:
                                                    for path in remote["pathToDoor"]:
                                                        toNode = -1
                                                        # node.canLeaveCharged[x].initiateRemotely.pathToDoor[x].destinationNode
                                                        if "destinationNode" in path:
                                                            toNode = path["destinationNode"]
                                                            toNodeRef = f"{fromNodeRef}:{toNode}"
                                                            # Document fromNode
                                                            if fromNode not in roomData["nodes"]["leaveCharged"]["from"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][fromNode] = {
                                                                    "to": {}
                                                                }
                                                            # Document toNode
                                                            if toNode not in roomData["nodes"]["leaveCharged"]["from"][fromNode]["to"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][fromNode]["to"][toNode] = {
                                                                    "strats": []
                                                                }

                                                        # toNode not defined
                                                        if toNode == -1:
                                                            msg = f"🔴ERROR: Destination node not defined:{fromNodeRef}"
                                                            messages["reds"].append(msg)
                                                            messages["counts"]["reds"] += 1

                                                        # Found fromNode but not toNode
                                                        # Could be a false positive
                                                        if str(fromNode) in roomData["links"]["from"]:
                                                            if str(toNode) not in roomData["links"]["from"][str(fromNode)]["to"]:
                                                                foundPath = False
                                                                fromNodes = roomData["links"]["from"]
                                                                sourceNode = fromNode
                                                                targetNode = toNode
                                                                # try to search for path
                                                                foundPath = search_for_path(fromNodes, sourceNode, targetNode)
                                                                if not foundPath:
                                                                    msg = f"🔴ERROR: Destination node path not found:{toNodeRef}"
                                                                    messages["reds"].append(msg)
                                                                    messages["counts"]["reds"] += 1
                                                        else:
                                                            msg = f"🔴ERROR: {fromNodeRef} not found!"
                                                            messages["reds"].append(msg)
                                                            messages["counts"]["reds"] += 1

                                                        # process strats in this path
                                                        if "strats" in path:
                                                            paramData = {
                                                                "key": "leaveCharged",
                                                                "fromNode": fromNode,
                                                                "fromNodeRef": fromNodeRef,
                                                                "roomData": roomData,
                                                                "roomIDX": roomIDX,
                                                                "toNode": toNode,
                                                                "bail": bail
                                                            }
                                                            paramData = process_strats(path, paramData)
                                                            showNodes = paramData["showNodes"]
                                                            bail = paramData["bail"]

                                # Collect GMode objects
                                if "leaveWithGMode" in node:
                                    for leaveG in node["leaveWithGMode"]:
                                        gModeObjects.append(leaveG)

                            # Validate Links
                            for link in room["links"]:
                                if "from" in link:
                                    fromNode = link["from"]
                                    fromNodeRef = f"Node[{roomRef}:{fromNode}]"
                                    for to in link["to"]:
                                        toNode = to["id"]
                                        paramData = {
                                            "key": "linkStrats",
                                            "fromNode": fromNode,
                                            "fromNodeRef": fromNodeRef,
                                            "roomData": roomData,
                                            "roomIDX": roomIDX,
                                            "toNode": toNode,
                                            "bail": bail
                                        }
                                        paramData = process_strats(to, paramData)
                                        showNodes = paramData["showNodes"]
                                        bail = paramData["bail"]

                            # Validate GMode objects
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
                                                            fromNodeRef = f"Node[{stratRef}:{fromNode}]"
                                                            if fromNode not in roomData["nodes"]["froms"]:
                                                                msg = f"🔴ERROR: From Node doesn't exist:{fromNodeRef}"
                                                                messages["reds"].append(msg)
                                                                messages["counts"]["reds"] += 1
                                                            else:
                                                                msg = ""
                                                                msg += f"🟢{area}/{subarea}/rooms.{roomIDX}.nodes.x.canLeaveCharged.x.initiateRemotely.pathToDoor.x.strats.x.{strat['name']}"
                                                                messages["greens"].append(msg)
                                                                messages["counts"]["greens"] += 1
                            # Validate Nodes
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

if bail:
    firstErr = True
    firstWarn = True
    foundErr = False
    foundWarn = False
    for msg in messages["reds"]:
        if "ERROR" in msg or "requires" in msg:
            foundErr = True
            if firstErr:
                print("🔴ERROR🔴")
                firstErr = False
            print(msg)
    for msg in messages["yellows"]:
        if "WARNING" in msg or "requires" in msg:
            foundWarn = True
            if firstWarn:
                print("🟡WARNING🟡")
                firstWarn = False
            print(msg)
    if foundWarn:
        subprocess.run("echo \"::warning title=Warning::Check Log for Details...\"", shell=True)
    if foundErr:
        print("🔴Something fucked up! Bailing!")
        sys.exit(1)
