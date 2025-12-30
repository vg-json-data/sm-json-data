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

strat_name_entrance_conditions = [
    ("Come In Normally", "comeInNormally"),
    ("Come In Running", "comeInRunning"),
    ("Come In Jumping", "comeInJumping"),
    ("Come In Space Jumping", "comeInSpaceJumping"),
    ("Come In Blue Space Jumping", "comeInBlueSpaceJumping"),
    ("Come In Shinecharging", "comeInShinecharging"),
    ("Come In Shinecharged Jumping", "comeInShinechargedJumping"),
    ("Come In Shinecharged", "comeInShinecharged"),
    ("Carry Shinecharge", "comeInShinecharged"),
    ("Come In With Spark", "comeInWithSpark"),
    ("Come In With Bomb Boost", "comeInWithBombBoost"),
    ("Come In Speedballing", "comeInSpeedballing"),
    ("Come In With Temporary Blue", "comeInWithTemporaryBlue"),
    ("Come In With Mockball", "comeInWithMockball"),
    ("Come In With Spring Ball Bounce", "comeInWithSpringBallBounce"),
    ("Come In With Blue Spring Ball Bounce", "comeInWithBlueSpringBallBounce"),
    ("Come In Spinning", "comeInSpinning"),
    ("Come In Blue Spinning", "comeInBlueSpinning"),
    ("Stored Moonfall Clip", "comeInWithStoredFallSpeed"),
    ("Transition with Stored Fall Speed", "comeInWithStoredFallSpeed"),
    ("Carry Grapple Teleport", "comeInWithGrappleTeleport"),
    ("Carry G-Mode", "comeInWithGMode"),
    ("Grapple Teleport", "comeInWithGrappleTeleport"),
    # TODO: add checks for cases not covered:
    # G-Mode
    # Cross Room Jump
    # comeInStutterShinecharging
    # comeInWithRMode
]

strat_name_exit_conditions = [
    ("Leave Normally", "leaveNormally"),
    ("Leave With Runway", "leaveWithRunway"),
    ("Leave Shinecharged", "leaveShinecharged"),
    ("Carry Shinecharge", "leaveShinecharged"),
    ("Leave With Spark", "leaveWithSpark"),
    ("Leave With Temporary Blue", "leaveWithTemporaryBlue"),
    ("Leave Spinning", "leaveSpinning"),
    ("Leave With Mockball", "leaveWithMockball"),
    ("Leave With Spring Ball Bounce", "leaveWithSpringBallBounce"),
    ("Leave Space Jumping", "leaveSpaceJumping"),
    ("Leave With Stored Fall Speed", "leaveWithStoredFallSpeed"),
    ("Leave With Moondance", "leaveWithStoredFallSpeed"),
    ("Leave With Extended Moondance", "leaveWithStoredFallSpeed"),
    ("G-Mode Setup", "leaveWithGModeSetup"),
    ("Carry G-Mode", "leaveWithGMode"),
    ("Leave With Door Frame Below", "leaveWithDoorFrameBelow"),
    ("Leave With Platform Below", "leaveWithPlatformBelow"),
    ("Leave With Grapple Teleport", "leaveWithGrappleTeleport"),
]

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
        "detailNote",       # immaterial
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
        "comesInHeated",  # validated by schema
        "direction",  # validated by schema
        "blue",  # validated by schema
        "movementType",  # validated by schema
        "doorOrientation",  # validated by schema
        "minExtraRunSpeed", # validated by schema
        "maxExtraRunSpeed", # validated by schema
        "types",  # validated by schema in 'unlocksDoors',
        "type", # validated by schema in resourceAvailable, resourceCapacity, resourceConsumed, resourceAtMost, resourceMissingAtMost, resourceMaxCapacity
        "position",  # validated by schema
        "environment",  # validated by schema
        "bypassesDoorShell",  # validated by schema
    ]

    # Keys that need validation but share a name with a filtered key
    keys_to_validate = [
        "enemyDamage.enemy",
        "enemyDamage.type"
    ]

    # check if it's a key we want to check
    processValue = not any(checkKey in k for checkKey in (*badKeys, *manualKeys, *goodKeys)) \
                    or any(checkKey in k for checkKey in keys_to_validate) 

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
                    else:
                        msg = f"🔴ERROR: {last_enemy} not found!"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1
            else:
                last_enemy = ""
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
    if "exitCondition" in strat and strat.get("bypassesDoorShell") not in [True, "free"] and node_subtype not in ["elevator", "doorway", "sandpit", "passage"]:
        nodes.add(to_node)
    if "entranceCondition" not in strat and from_node in nodes:
        nodes.remove(from_node)
    if to_node in nodes_without_implicit_unlocks and strat.get("bypassesDoorShell") not in [True, "free"] and "gModeRegainMobility" not in strat:
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

def check_shinecharge_req(req):
    if isinstance(req, str):
        if req in ["h_shinechargeMaxRunway", "canStutterWaterShineCharge", "canPreciseStutterWaterShineCharge"]:
            return True
    if isinstance(req, dict):
        if "canShineCharge" in req:
            return True
        if "and" in req:
            return any(check_shinecharge_req(v) for v in req["and"])
        if "or" in req:
            return all(check_shinecharge_req(v) for v in req["or"])

def check_heat_req(req):
    if isinstance(req, str):
        if req in ["h_heatProof", "h_heatedCrystalFlash", "h_heatedLavaCrystalFlash", "h_heatedAcidCrystalFlash",
                   "h_heatedCrystalFlashForReserveEnergy",
                   "h_heatedCrystalSpark", "h_LowerNorfairElevatorDownwardFrames",
                   "h_LowerNorfairElevatorUpwardFrames", "h_MainHallElevatorFrames", "h_heatedGreenGateGlitch",
                   "h_heatedDirectGModeLeaveSameDoor", "h_heatedIndirectGModeOpenSameDoor",
                   "h_heatedGModeOpenDifferentDoor", "h_heatedGModeOffCameraDoor", "h_heatedGModePauseAbuse",
                   "h_heatedGrappleTeleportWallEscape"]:
            return True
    if isinstance(req, dict):
        if "heatFrames" in req or "heatFramesWithEnergyDrops" or "suitlessHeatFrames" in req in req:
            return True
        if "and" in req:
            return any(check_heat_req(v) for v in req["and"])
        if "or" in req:
            return all(check_heat_req(v) for v in req["or"])


def check_cycle_frames_req(req):
    if isinstance(req, dict):
        if "cycleFrames" in req:
            return True
        if "and" in req:
            return any(check_cycle_frames_req(v) for v in req["and"])
        if "or" in req:
            return all(check_cycle_frames_req(v) for v in req["or"])

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


def check_and_or(req, err_fn):
    if isinstance(req, dict):
        if "or" in req:
            if len(req["or"]) < 2:
                err_fn("'or' should have at least 2 elements")
            for r in req["or"]:
                if isinstance(r, dict) and "or" in r:
                    err_fn("'or' should not have a directly nested 'or' inside.")
                check_and_or(r, err_fn)
        elif "and" in req:
            if len(req["and"]) < 2:
                err_fn("'and' should have at least 2 elements")
            for r in req["and"]:
                if isinstance(r, dict) and "and" in r:
                    err_fn("'and' should not have a directly nested 'and' inside.")
                check_and_or(r, err_fn)


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


def covers_shinecharge_frames(req):
    if isinstance(req, dict):
        if "shineChargeFrames" in req:
            return True
        elif "or" in req:
            return all(covers_shinecharge_frames(x) for x in req["or"])
        elif "and" in req:
            return any(covers_shinecharge_frames(x) for x in req["and"])
        else:
            return False


def check_disallowed_reqs(req, err_fn):
    if isinstance(req, dict):
        if "or" in req:
            for r in req["or"]:
                check_disallowed_reqs(r, err_fn)
        elif "and" in req:
            for r in req["and"]:
                check_disallowed_reqs(r, err_fn)
    if isinstance(req, str):
        if req in ["canCrystalSpark"]:
            err_fn(f"{req} disallowed outside of helper.")
                            

def process_req_speed_state(req, states, err_fn):
    if isinstance(req, str):
        if req in ["h_shinechargeMaxRunway", "canWaterShineCharge", "canStutterWaterShineCharge", "canPreciseStutterWaterShineCharge", "h_shinechargeSlideTemporaryBlue"]:
            states = {"shinecharging"}
        elif req in ["h_getBlueSpeedMaxRunway", "canSpeedKeep", "h_waterGetBlueSpeed", "h_stutterWaterGetBlueSpeed"]:
            # Note: "canSpeedKeep" can be used for other purposes than obtaining blue, but its presence should be
            # enough to satisfy the test as a way that blue may be obtained.
            states = {"blue"}
        elif req in ["h_flashSuitIceClip", "h_spikeXModeSpikeSuit", "h_thornXModeSpikeSuit", "h_storedSpark"]:
            states = {"preshinespark"}
        elif req in ["canSpikeSuit"]:
            if not states.issubset(["shinecharging", "shinecharged", "preshinespark"]):
                err_fn(f"{req} while not shinecharging/shinecharged/preshinespark")
            states = {"preshinespark"}
        elif req in ["h_CrystalSpark", "h_CrystalSparkWithoutLenience",
                     "h_underwaterCrystalSpark", "h_underwaterCrystalSparkWithoutLenience", "h_heatedCrystalSpark",
                     "canRModeSparkInterrupt", "canRModePauseAbuseSparkInterrupt", "h_RModeKnockbackSpark", "h_heatTriggerRModeSparkInterrupt"]:
            if not states.issubset(["shinecharging", "shinecharged", "preshinespark"]):
                err_fn(f"{req} while not shinecharging/shinecharged/preshinespark")
            states = {"normal"}
        elif req in ["canTemporaryBlue", "canChainTemporaryBlue", "canLongChainTemporaryBlue", "canSpeedball", "canXRayCancelShinecharge"]:
            if not states.issubset(["shinecharging", "blue"]):
                err_fn(f"{req} while not in blue state")
            states = {"blue"}
        elif req in ["h_spikeXModeShinecharge", "h_thornXModeShinecharge", "h_spikeDoubleXModeBlueSuit", "h_thornDoubleXModeBlueSuit"]:
            states = {"shinecharged"}

    elif isinstance(req, dict):
        if "canShineCharge" in req:
            states = {"shinecharging"}
        elif "blueSuitShinecharge" in req:
            states = {"shinecharged"}
        elif "shineChargeFrames" in req:
            if not states.issubset(["shinecharging", "shinecharged"]):
                err_fn(f"shineChargeFrames requirement while not in shinecharged state: {req}")
        elif "useFlashSuit" in req:
            states = {"preshinespark"}
        elif "shinespark" in req:
            if not states.issubset(["shinecharging", "shinecharged", "shinespark", "preshinespark"]):
                err_fn(f"shinespark requirement while not in shinecharging/shinecharged/shinespark state: {req}")
            states = {"shinespark"}
        elif "getBlueSpeed" in req or "speedball" in req:
            states = {"blue"}
        elif "and" in req:
            for r in req["and"]:
                states = process_req_speed_state(r, states, err_fn)
        elif "or" in req:
            # Apply the check independently to each branch of the "or", taking the union of the ending sets of states
            new_states = set()
            for r in req["or"]:
                branch_states = process_req_speed_state(r, states, err_fn)
                new_states.update(branch_states)
            states = new_states
    else:
        raise RuntimeError(f"Unexpected requirement type {type(req)}: {req}")
    return states


def check_speed_states(strat, err_fn):
    # Check that transitions between Speedbooster-related states are valid, to help prevent
    # requirements (or entrance/exit conditions) from being accidentally omitted or included by mistake.
    #
    # states:
    #   "normal": normal movement state
    #   "shinecharging": just gained a shinecharge, still valid to convert to "blue" (via canTemporaryBlue)
    #   "shinecharged": gained a shinecharge earlier, no longer valid to convert to "blue"
    #   "shinespark": performed a shinespark, valid to continue with additional "shinespark" requirements
    #   "preshinespark": expecting a subsequent shinespark requirement (e.g. after comeInWithSpark or useFlashSuit)
    #   "blue": gained blue in some way, e.g. getBlueSpeed, speedball, comeInBlueSpinning, etc.
    #
    # States are represented as a set of strings, representing possible states, since different branches of
    # "or" can lead to different states.
    
    states = {"normal"}
    if "entranceCondition" in strat:
        keys = set(strat["entranceCondition"].keys())
        if keys.intersection(["comeInShinecharging", "comeInStutterShinecharging"]):
            states = {"shinecharging"}
        elif keys.intersection(["comeInShinecharged", "comeInShinechargedJumping"]):
            states = {"shinecharged"}
        elif "comeInWithSpark" in keys:
            states = {"preshinespark"}
        elif keys.intersection(["comeInWithTemporaryBlue", "comeInGettingBlueSpeed", "comeInSpeedballing", "comeInWithBlueSpringBallBounce", 
                                "comeInBlueSpinning", "comeInBlueSpaceJumping"]):
            states = {"blue"}
        if strat.get("startsWithShineCharge") is True:
            err_fn("startsWithShineCharge should not be combined with an entranceCondition")
    elif strat.get("startsWithShineCharge") is True:
        states = {"shinecharged"}
    
    for req in strat["requires"]:
        states = process_req_speed_state(req, states, err_fn)

    # TODO: handle door unlock requires

    if "exitCondition" in strat:
        keys = set(strat["exitCondition"].keys())
        if "leaveShinecharged" in keys:
            if not states.issubset({"shinecharging", "shinecharged"}):
                err_fn("leaveShinecharged missing requirements to gain shinecharge")
        if "leaveWithTemporaryBlue" in keys:
            if not states.issubset({"shinecharging", "blue"}):
                err_fn("leaveWithTemporaryBlue missing requirements to gain blue")
        if "leaveWithSpark" in keys:
            if states != {"shinespark"}:
                err_fn("leaveWithSpark missing shinespark requirement")
        if strat.get("endsWithShineCharge") is True:
            err_fn("endsWithShineCharge should not be combined with an exitCondition")
    elif strat.get("endsWithShineCharge") is True:
        if not states.issubset({"shinecharging", "shinecharged"}):
            err_fn("endsWithShineCharge missing requirements to gain shinecharge")
    else:
        if "preshinespark" in states:
            err_fn("strat ends while expecting a shinespark requirement")
        if "shinecharged" in states or "shinecharging" in states:
            err_fn("strat ends without using shinecharge")

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
    "free",
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
                        "nodes": {
                            "froms": [],
                            "tos": [],
                            "ids": [],
                            "names": [],
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

                    # Check that room `mapTileMask` is a rectangle:
                    mapHeight = len(room["mapTileMask"])
                    mapWidth = len(room["mapTileMask"][0])
                    if not all(len(row) == mapWidth for row in room["mapTileMask"]):
                        msg = f"🔴ERROR: Not all rows of room mapTileMask have the same length: {roomRef}"
                        messages["reds"].append(msg)
                        messages["counts"]["reds"] += 1

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
                    node_tile_set = set()
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

                        if len(node["mapTileMask"]) != mapHeight or not all(len(row) == mapWidth for row in node["mapTileMask"]):
                            msg = f"🔴ERROR: Node mapTileMask has wrong shape: {nodeRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                        else:
                            for y in range(mapHeight):
                                for x in range(mapWidth):
                                    node_tile = node["mapTileMask"][y][x]
                                    room_tile = room["mapTileMask"][y][x]
                                    if node_tile == 2:
                                        node_tile_set.add((x, y))
                                        if room_tile == 0:
                                            msg = f"🔴ERROR: Node mapTileMask has 2 at invalid position ({x}, {y}): {nodeRef}"
                                            messages["reds"].append(msg)
                                            messages["counts"]["reds"] += 1
                                    else:
                                        if room_tile != node_tile:
                                            msg = f"🔴ERROR: Node mapTileMask is inconsistent with room mapTileMask at position ({x}, {y}): {nodeRef}"
                                            messages["reds"].append(msg)
                                            messages["counts"]["reds"] += 1

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

                        if node.get("useImplicitLeaveNormally") is False and not any(
                            s["link"][1] == node["id"]
                            and s.get("exitCondition", {}).get("leaveNormally") is not None
                            for s in room["strats"]
                        ):
                            msg = f"🔴ERROR: Node disables useImplicitLeaveNormally but has no leaveNormally strat: {nodeRef}:{node['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            
                        if node.get("useImplicitComeInNormally") is False and not any(
                            s["link"][0] == node["id"]
                            and s.get("entranceCondition", {}).get("comeInNormally") is not None
                            for s in room["strats"]
                        ):
                            msg = f"🔴ERROR: Node disables useImplicitComeInNormally but has no comeInNormally strat: {nodeRef}:{node['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1

                        if node.get("useImplicitComeInWithMockball") is False and not any(
                            s["link"][0] == node["id"]
                            and s.get("entranceCondition", {}).get("comeInWithMockball") is not None
                            for s in room["strats"]
                        ):
                            msg = f"🔴ERROR: Node disables useImplicitComeInWithMockball but has no comeInWithMockball strat: {nodeRef}:{node['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1

                        if node.get("useImplicitCarryGModeBackThrough") is False and not any(
                            s["link"][0] == node["id"]
                            and s.get("entranceCondition", {}).get("comeInWithGMode") is not None
                            and s.get("exitCondition", {}).get("leaveWithGMode") is not None
                            for s in room["strats"]
                        ):
                            if room["id"] == 321 or (room["id"] == 44 and node["id"] == 1):
                                # Toilet Bowl (321) is an exception where there legitimately is no comeInWithGMode+leaveWithGMode strat
                                # Green Brinstar Main Shaft (44) is also an exception because the elevator takes Samus to a G-mode junction which can lead back up
                                pass
                            else:
                                msg = f"🔴ERROR: Node disables useImplicitCarryGModeBackThrough but has no comeInWithGMode+leaveWithGMode strat: {nodeRef}:{node['name']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        if node.get("useImplicitCarryGModeMorphBackThrough") is False and not any(
                            s["link"][0] == node["id"]
                            and s.get("entranceCondition", {}).get("comeInWithGMode") is not None
                            and s.get("exitCondition", {}).get("leaveWithGMode") is not None
                            and s["exitCondition"]["leaveWithGMode"]["morphed"]
                            for s in room["strats"]
                        ):
                            if room["id"] == 321 or node["nodeSubType"] == "elevator":
                                # Toilet Bowl and elevators are an exception where there legitimately is no comeInWithGMode+leaveWithGMode morphed strat
                                pass
                            else:
                                msg = f"🔴ERROR: Node disables useImplicitCarryGModeMorphBackThrough but has no comeInWithGMode+leaveWithGMode morphed strat: {nodeRef}:{node['name']}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                    # Check that every map tile is covered by some node:
                    for y in range(mapHeight):
                        for x in range(mapWidth):
                            if room["mapTileMask"][y][x] == 1 and (x, y) not in node_tile_set:
                                msg = f"🔴ERROR: Map tile ({x}, {y}) is not covered by any node:{roomRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                    # Document Link Strats
                    for strat in room["strats"]:
                        if "link" not in strat:
                            msg = f"🔴ERROR: Strat is missing `link` property: {roomRef}:{strat['name']}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            continue
                        link = strat["link"]
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
                        notable_name = notable["name"]
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
                            "itemNotCollectedAtNode",
                            "itemCollectedAtNode"
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
                    link_strat_names = set()
                    for strat in room["strats"]:
                        if "link" not in strat:
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

                        strat_id = strat.get("id")
                        stratRef = f"{roomRef}:LINK:FromNode[{fromNode}]:ToNode[{toNode}]:{strat_id}:'{strat['name']}'"
                        if fromNode not in roomData["nodes"]["ids"]:
                            msg = f"🔴ERROR: From node {fromNode} doesn't exist:{stratRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            continue
                        if toNode not in roomData["nodes"]["ids"]:
                            msg = f"🔴ERROR: To node {toNode} doesn't exist:{stratRef}"
                            messages["reds"].append(msg)
                            messages["counts"]["reds"] += 1
                            continue

                        paramData = {
                            "key": "linkStrats",
                            "fromNode": fromNode,
                            "fromNodeRef": fromNodeRef,
                            "roomData": roomData,
                            "toNode": toNode,
                            "bail": bail
                        }
                        paramData = process_strats([strat], paramData)

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

                        if (link[0], link[1], strat['name']) in link_strat_names:
                                msg = f"🔴ERROR: Strat name not unique within link:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                        link_strat_names.add((link[0], link[1], strat['name']))

                        def strat_err_fn(msg):
                            messages["reds"].append(f"🔴ERROR: {stratRef}:{msg}")
                            messages["counts"]["reds"] += 1
                            
                        def make_and(reqs):
                            if len(reqs) == 0:
                                return "free"
                            elif len(reqs) == 1:
                                return reqs[0]
                            else:
                                return {"and": reqs}
                            
                        def make_or(reqs):
                            if len(reqs) == 0:
                                return "never"
                            elif len(reqs) == 1:
                                return reqs[0]
                            else:
                                out = []
                                for r in reqs:
                                    if isinstance(r, dict) and "or" in r:
                                        out.extend(r["or"])
                                    else:
                                        out.append(r)
                                return {"or": out}
                            
    
                        requires = strat["requires"]
                        if "entranceCondition" in strat and "comeInWithSidePlatform" in strat["entranceCondition"]:
                            reqs = []
                            for platform in strat["entranceCondition"]["comeInWithSidePlatform"]["platforms"]:
                                reqs.append(make_and(platform.get("requires", [])))
                            requires.append(make_or(reqs))
                            if len(requires) == 1 and isinstance(requires[0], dict) and "and" in requires[0]:
                                requires = requires[0]["and"]
                            
                        for req in requires:
                            check_and_or(req, strat_err_fn)
                            if isinstance(req, dict) and "and" in req:
                                strat_err_fn("'and' not allowed at top level.")
                        
                        if heated and not check_heat_req({"and": requires}):
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
                                  strat.get("bypassesDoorShell") in [True, "free"]:
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
                            if "comeInShinecharged" in strat["entranceCondition"]:
                                if not covers_shinecharge_frames({"and": strat["requires"]}):
                                    msg = f"🔴ERROR: Strat has comeInShinecharged entranceCondition without `shineChargeFrames` covering all cases:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                            if "comeInShinechargedJumping" in strat["entranceCondition"]:
                                if not covers_shinecharge_frames({"and": strat["requires"]}):
                                    msg = f"🔴ERROR: Strat has comeInShinechargedJumping entranceCondition without `shineChargeFrames` covering all cases:{stratRef}"
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
                        if strat.get("startsWithShineCharge") is True:
                                if not covers_shinecharge_frames({"and": strat["requires"]}):
                                    msg = f"🔴ERROR: Strat has startsWithShineCharge without `shineChargeFrames` covering all cases:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        if "exitCondition" in strat:
                            if node_lookup[toNode]["nodeType"] not in ["door", "exit"]:
                                msg = f"🔴ERROR: Strat has exitCondition but To Node is not door or exit:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                            if "leaveShinecharged" in strat["exitCondition"]:
                                if not covers_shinecharge_frames({"and": strat["requires"]}):
                                    msg = f"🔴ERROR: Strat has leavesShinecharged exitCondition without `shineChargeFrames` covering all cases:{stratRef}"
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
                        if strat.get("endsWithShineCharge") is True:
                            if not covers_shinecharge_frames({"and": strat["requires"]}):
                                msg = f"🔴ERROR: Strat has endsWithShineCharge without `shineChargeFrames` covering all cases:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        strat_name_lower = strat["name"].lower()
                        for (phrase, entrance_condition_name) in strat_name_entrance_conditions:
                            if phrase.lower() in strat_name_lower:
                                if entrance_condition_name not in strat.get("entranceCondition", {}):
                                    if phrase == "Carry G-Mode" and node_lookup[fromNode].get("nodeSubType") == "g-mode":
                                        # A "Carry G-Mode" strat doesn't need a "comeInWithGMode" if it comes from a G-mode junction
                                        continue
                                    if phrase == "Grapple Teleport" and "leave with grapple teleport" in strat_name_lower:
                                        # A "Grapple Teleport" strat doesn't need a "comeInWithGrappleTeleport" if it is a "Leave With Grapple Teleport"
                                        continue
                                    msg = f"🔴ERROR: Strat name contains '{phrase}' but there is no {entrance_condition_name} entrance condition:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                                break
                        for (phrase, exit_condition_name) in strat_name_exit_conditions:
                            if phrase.lower() in strat["name"].lower():
                                if exit_condition_name not in strat.get("exitCondition", {}):
                                    msg = f"🔴ERROR: Strat name contains '{phrase}' but there is no {exit_condition_name} exit condition:{stratRef}"
                                    messages["reds"].append(msg)
                                    messages["counts"]["reds"] += 1
                        if "g-mode-regain mobility" in strat_name_lower and "gModeRegainMobility" not in strat:
                                msg = f"🔴ERROR: Strat name contains 'G-Mode Regain Mobility' but strat has no gModeRegainMobility property:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        def generic_err_fn(msg):
                            messages["reds"].append(f"🔴ERROR: {stratRef}:{msg}")
                            messages["counts"]["reds"] += 1
                        check_disallowed_reqs({"and": strat["requires"]}, generic_err_fn)

                        def speed_err_fn(msg):
                            messages["reds"].append(f"🔴ERROR: Invalid speed state transition:{stratRef}:{msg}")
                            messages["counts"]["reds"] += 1

                        check_speed_states(strat, speed_err_fn)

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
                        if strat.get("bypassesDoorShell") in [True, "free"]:
                            if node_lookup[toNode]["nodeType"] != "door":
                                msg = f"🔴ERROR: Strat has bypassesDoorShell but To Node is not door:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1

                        has_cycle_frames = check_cycle_frames_req({"and": strat["requires"]})
                        if has_cycle_frames and "farmCycleDrops" not in strat:
                                msg = f"🔴ERROR: Strat has cycleFrames requirement but no farmCycleDrops:{stratRef}"
                                messages["reds"].append(msg)
                                messages["counts"]["reds"] += 1
                        if "farmCycleDrops" in strat and not has_cycle_frames:
                                msg = f"🔴ERROR: Strat has farmCycleDrops but is missing cycleFrames covering all cases:{stratRef}"
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

                        foundNode = False  # spawnAts were removed, so this code can be simplified

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
