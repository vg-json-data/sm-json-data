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
messages = {
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
        "jumpwayType",  # validated by schema
        "lockType",     # validated by schema
        "nodeType",     # validated by schema
        "nodeSubType",  # validated by schema
        "obstacleType", # validated by schema
        "physics",      # validated by schema
        "utility",      # validated by schema
        "resourceCapacity"  # validated by schema
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
            msg = f"🔴ERROR: {k}:{v} not unique!"
            messages["reds"].append(msg)
            messages["counts"]["reds"] += 1
            # bail = True

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
                                if not goodValue:
                                    msg = f"🔴ERROR: {k}:{last_enemy} doesn't have attack '{v}'"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                    # bail = True
                        last_enemy = ""
                    else:
                        msg = f"🔴ERROR: {last_enemy} not found!"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1
                        # bail = True
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
                    msg = f"🔴{k} {v}"
                    messages["reds"].append(msg)
                    messages["counts"]["reds"] += 1
    return goodValue

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
    for strat in src["strats"]:
        stratRef = f"{toNodeRef}:stratName[{strat}]"
        if "name" in strat:
            stratRef = f"{toNodeRef}:stratName[{strat['name']}]"
        if str(fromNode) in roomData["links"]["from"]:
            if str(toNode) in roomData["links"]["from"][str(fromNode)]["to"]:
                if strat not in roomData["links"]["from"][str(fromNode)]["to"][str(toNode)]["strats"] and \
                    strat["name"] not in roomData["links"]["from"][str(fromNode)]["to"][str(toNode)]["strats"]:
                    msg = f"🔴ERROR: Invalid strat:{stratRef}"
                    messages["reds"].append(msg)
                    messages["counts"]["reds"] += 1
                    # bail = True
                else:
                    if "obstacles" in strat:
                        for obstacle in strat["obstacles"]:
                            if obstacle["id"] not in roomData["obstacles"]["ids"]:
                                msg = f"🔴ERROR: Obstacle not found:{stratRef}:{obstacle['id']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                    if showArea:
                        msg = ""
                        msg += f"🟢rooms.{roomIDX}.nodes.x.canLeaveCharged.x.initiateRemotely.pathToDoor.x.strats.x {strat}"
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
                foundPath = False
                for tNode in roomData["links"]["from"][str(fromNode)]["to"]:
                    if (not foundPath) and \
                        (str(tNode) in roomData["links"]["from"]) and \
                        (str(toNode) in roomData["links"]["from"][str(tNode)]["to"]):
                        foundPath = True
                        msg = f"🟢{stratRef}::{fromNode}:{tNode}:{toNode}"
                        # messages["greens"].append(msg)
                        # messages["counts"]["greens"] += 1
                if not foundPath:
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
                        # bail = True
        else:
            msg = f"🔴ERROR: From node not found:{fromNodeRef}"
            messages["reds"].append(msg)
            messages["counts"]["reds"] += 1
            # bail = True

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
                if "rooms" in regionJSON:
                    room = regionJSON["rooms"][0]
                    area = room["area"]
                    subarea = room["subarea"]
                    subsubarea = room["subsubarea"] if "subsubarea" in room else ""
                    showArea = False
                    print(f"{area}/{subarea}" + ((subsubarea != "") and f"/{subsubarea}" or ""))
                    for [k, v] in flattened_dict.items():
                        ret = process_keyvalue(k, v)
                        if not ret and not showArea:
                            showArea = True
                    for [roomIDX, room] in enumerate(regionJSON["rooms"]):
                        roomRef = f"{area}/{subarea}" + ((subsubarea != "") and f"/{subsubarea}" or "") + f":{room['id']}:{room['name']}"
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

                        roomData = {
                            "id": room["id"],
                            "links": {
                                "from": {}
                            },
                            "nodes": {
                                "froms": [],
                                "tos": [],
                                "spawnAts": [],
                                "leaveCharged": {
                                    "from": {}
                                }
                            },
                            "obstacles": {
                                "ids": []
                            }
                        }

                        # Document Obstacles
                        if "obstacles" in room:
                            for obstacle in room["obstacles"]:
                                obstacleRef = f"🔴{roomRef}:{obstacle['id']}:{obstacle['name']}"
                                if obstacle["id"] in roomData["obstacles"]["ids"]:
                                    msg = f"ERROR: Obstacle ID not unique! {obstacleRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                else:
                                    roomData["obstacles"]["ids"].append(obstacle["id"])
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
                                if "spawnAt" in node and node["spawnAt"] not in roomData["nodes"]["spawnAts"]:
                                    roomData["nodes"]["spawnAts"].append(node["spawnAt"])

                            # Validate canLeaveCharged
                            # Validate leaveWithGMode
                            for node in room["nodes"]:
                                if "id" in node:
                                    nodeRef = f"{roomRef}:{node['id']}"
                                if "canLeaveCharged" in node:
                                    for [leaveID, leave] in enumerate(node["canLeaveCharged"]):
                                        if "initiateRemotely" in leave:
                                            remote = leave["initiateRemotely"]
                                            if "initiateAt" in remote:
                                                fromNode = remote["initiateAt"]
                                                fromNodeRef = f"Node[{nodeRef}]:canLeaveCharged[{int(leaveID) + 1}]:initiateRemotelyAt[{fromNode}]"
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
                                                            msg = f"🔴ERROR: Destination node not defined:{fromNodeRef}"
                                                            messages["reds"].append(msg)
                                                            messages["counts"]["reds"] += 1
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
                                                                msg += f"🟢rooms.{roomIDX}.nodes.x.canLeaveCharged.x.initiateRemotely.pathToDoor.x.strats.x.{strat['name']}"
                                                                messages["greens"].append(msg)
                                                                messages["counts"]["greens"] += 1
                            for node in room["nodes"]:
                                orphaned = False
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
    foundErr = False
    for msg in messages["reds"]:
        if "ERROR" in msg or "requires" in msg:
            foundErr = True
            if firstErr:
                print("🔴ERROR🔴")
                firstErr = False
            print(msg)
    if foundErr:
        print("🔴Something fucked up! Bailing!")
        sys.exit(1)
