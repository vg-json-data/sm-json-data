# pylint: disable=global-at-module-level, invalid-name, too-many-locals
'''
Check for validity of keywords in files
'''
import json
import os
import re
import sys
from flatten_json import flatten

last_enemy = ""

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
        "subarea"
    ]
    badKeys = [
        "$schema",      # immaterial
        "name",         # !!could check for unique
        "description",  # immaterial
        "doorAddress",  # !!could check for unique
        "groupName",    # !!could check for unique
        "id",           # !!could check for unique
        "lockType",     # validated by schema
        "nodeAddress",  # !!could check for unique
        "nodeType",     # validated by schema
        "nodeSubType",  # validated by schema
        "note",         # immaterial
        "obstacleType", # validated by schema
        "physics",      # validated by schema
        "roomAddress",  # !!could check for unique
        "utility",      # validated by schema
        "devNote"       # immaterial
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

    if processValue:
        isFloat = isinstance(v, float)
        isInt = isinstance(v, int)
        isList = isinstance(v, list)
        isEmptyList = isList and len(v) == 0
        isNumeric = not isFloat and not isInt and not isList and v.isnumeric()
    if processValue and \
        not isFloat and \
        not isInt and \
        not isEmptyList and \
        not isNumeric:
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
        if (isEnemy or last_enemy != "") and ".enemy" in k:
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
                    print(f"{last_enemy} not found!")
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
                print(k, v)
    return goodValue

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
with open(os.path.join(".","tests","asserts","canLeaveCharged.json")) as cheatSheetFile:
    cheatSheetJSON = json.load(cheatSheetFile)

print("")
print("Check Regions")
bail = False
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
                        if "nodes" in room:
                            roomData = {
                                "id": room["id"],
                                "links": {
                                    "from": {}
                                },
                                "nodes": {
                                    "leaveCharged": {
                                        "from": {}
                                    }
                                }
                            }
                            showNodes = False
                            if "links" in room:
                                for link in room["links"]:
                                    if "from" in link:
                                        roomData["links"]["from"][link["from"]] = {
                                            "to": {}
                                        }
                                        for to in link["to"]:
                                            roomData["links"]["from"][link["from"]]["to"][to["id"]] = {
                                                "strats": []
                                            }
                                            if "strats" in to:
                                                for strat in to["strats"]:
                                                    roomData["links"]["from"][link["from"]]["to"][to["id"]]["strats"].append(strat["name"])
                            for node in room["nodes"]:
                                if "canLeaveCharged" in node:
                                    for leave in node["canLeaveCharged"]:
                                        if "initiateRemotely" in leave:
                                            remote = leave["initiateRemotely"]
                                            if "initiateAt" in remote:
                                                if "pathToDoor" in remote:
                                                    for path in remote["pathToDoor"]:
                                                        if "destinationNode" in path:
                                                            if remote["initiateAt"] not in roomData["nodes"]["leaveCharged"]["from"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][remote["initiateAt"]] = {
                                                                    "to": {}
                                                                }
                                                            if path["destinationNode"] not in roomData["nodes"]["leaveCharged"]["from"][remote["initiateAt"]]["to"]:
                                                                roomData["nodes"]["leaveCharged"]["from"][remote["initiateAt"]]["to"][path["destinationNode"]] = {"strats":[]}
                                                        if "strats" in path:
                                                            showNodes = True
                                                            for strat in path["strats"]:
                                                                stratRef = f"{room['id']}:{room['name']}:{remote['initiateAt']}:{path['destinationNode']}:{strat}"
                                                                if remote["initiateAt"] in roomData["links"]["from"]:
                                                                    if path["destinationNode"] in roomData["links"]["from"][remote["initiateAt"]]["to"]:
                                                                        if strat not in roomData["links"]["from"][remote["initiateAt"]]["to"][path["destinationNode"]]["strats"]:
                                                                            print(f"🔴ERROR: Invalid strat:{stratRef}")
                                                                            bail = True
                                                                        else:
                                                                            if showArea:
                                                                                print(f"🟢{stratRef}")
                                                                                # print(roomData["nodes"]["leaveCharged"]["from"])
                                                                            roomData["nodes"]["leaveCharged"]["from"][remote["initiateAt"]]["to"][path["destinationNode"]]["strats"].append(strat)
                                                                    else:
                                                                        if str(room["id"]) in cheatSheetJSON and \
                                                                            str(remote["initiateAt"]) in cheatSheetJSON[str(room["id"])] and \
                                                                            str(path["destinationNode"]) in cheatSheetJSON[str(room["id"])][str(remote["initiateAt"])]:
                                                                            intermediateNode = cheatSheetJSON[str(room["id"])][str(remote["initiateAt"])][str(path["destinationNode"])]["via"]
                                                                            print(f"🟡{stratRef}::{remote['initiateAt']}:{intermediateNode}:{path['destinationNode']}")
                                                                        else:
                                                                            print(f"🔴ERROR: Destination node not found:{room['id']}:{room['name']}:{remote['initiateAt']}:{path['destinationNode']}")
                                                                            bail = True
                                                                else:
                                                                    print(f"🔴ERROR: From node not found:{room['id']}:{room['name']}:{remote['initiateAt']}")
                                                                    bail = True
                            if showNodes:
                                # print(json.dumps(roomData, indent=2))
                                pass
                    if showArea:
                        print()

if bail:
    sys.exit(1)
