# pylint: disable=too-many-branches
"""Determine validity of keyword usage"""

import json
import os

keywords = []

def check_keyword(test):
    """Check to see if a keyword is valid"""
    for [_, kws] in keywords.items():
        if test in kws:
            return True
    print(test + " not found!")
    return False

def find_keywords(item):
    """Search list/dict for keywords"""
    ret = False
    if isinstance(item, dict):
        # print("DICT")
        for [k, val] in item.items():
            ret = find_keywords(val)
    elif isinstance(item, list):
        for ele in item:
            if isinstance(ele, dict):
                for [k, val] in ele.items():
                    # recurse
                    if k in [
                        "and",
                        "or",
                        "requires",
                        "enemyKill"
                    ]:
                        ret = find_keywords(val)
                    # ignore
                    elif k in [
                        "additionalObstacles",
                        "adjacentRunway",
                        "ammo",
                        "canComeInCharged",
                        "canShineCharge",
                        "enemies",
                        "enemy",
                        "enemyDamage",
                        "heatFrames",
                        "hits",
                        "id",
                        "name",
                        "notable",
                        "resetRoom",
                        "spikeHits",
                        "type"
                    ]:
                        pass
                    # this is new!
                    else:
                        print(k, val)
            elif isinstance(ele, str):
                ret = check_keyword(ele)
                # print("S: " + ele)
            elif isinstance(ele, list):
                for el in ele:
                    ret = check_keyword(el)
                # print("L: " + ele)
            else:
                print("?: " + ",".join(ele))
    elif isinstance(item, str):
        # print("STR")
        ret = check_keyword(item)
        # print("S: " + item)
    elif isinstance(item, int):
        # print("INT")
        ret = True
    else:
        print("FAIL: " + str(item))
    return ret

keywordsPath = os.path.join("resources","app","manifests","keywords.json")
with open(keywordsPath, encoding="utf-8") as keywordsFile:
    keywords = json.load(keywordsFile)

# helpers
helpers = []
helpersPath = os.path.join("helpers.json")
with open(helpersPath, encoding="utf-8") as helpersFile:
    helpers = json.load(helpersFile)
    for helper in helpers["helpers"]:
        requires = helper["requires"]
        result = find_keywords(requires)
        # if isinstance(item, str):
        #     print("0: " + helper["name"])
        #     print(item)
        # elif isinstance(item, dict):
        #     print("1: " + helper["name"])
        #     print(flatdict.FlatDict(item, delimiter='.'))
        # elif isinstance(item[0], dict):
        #     print("2: " + helper["name"])
        #     print(flatdict.FlatDict(item[0], delimiter='.'))
        if not result:
            print("H: " + helper["name"])
            print(requires)
            print("")

# techs
techs = []
techsPath = os.path.join("tech.json")
with open(techsPath, encoding="utf-8") as techsFile:
    techsJSON = json.load(techsFile)
    if "techs" in techsJSON:
        techs = techsJSON["techs"]
    elif "techCategories" in techsJSON:
        for techCat in techsJSON["techCategories"]:
            if "techs" in techCat:
                for tech in techCat["techs"]:
                    if "name" in tech:
                        techs.append(tech)

    for tech in techs:
        requires = tech["requires"]
        if len(requires):
            result = find_keywords(requires)
            # if isinstance(item, str):
            #     print("0: " + helper["name"])
            #     print(item)
            # elif isinstance(item, dict):
            #     print("1: " + helper["name"])
            #     print(flatdict.FlatDict(item, delimiter='.'))
            # elif isinstance(item[0], dict):
            #     print("2: " + helper["name"])
            #     print(flatdict.FlatDict(item[0], delimiter='.'))
            if not result:
                print("T: " + tech["name"])
                print(requires)
                print("")

rooms = []
region = "brinstar"
subregion = "blue"
regionPath = os.path.join("region", region, subregion + ".json")
with open(regionPath, encoding="utf-8") as regionFile:
    rooms = json.load(regionFile)
    rooms = rooms["rooms"]
    for room in rooms:
        if "nodes" in room:
            for node in room["nodes"]:
                if "locks" in node:
                    for lock in node["locks"]:
                        if "lock" in lock:
                            result = find_keywords(lock["lock"])
                            if not result:
                                print(room["name"] + " has a broken lock ['" + lock["lock"] + "']!")
                        elif "unlockStrats" in lock:
                            result = find_keywords(lock["unlockStrats"])
                            if not result:
                                print(room["name"] + " has a broken lock ['" + "" + "']!")
        if "enemies" in room:
            for enemy in room["enemies"]:
                if "spawn" in enemy:
                    result = find_keywords(enemy["spawn"])
                    if not result:
                        print(room["name"] + " has a malformed enemy declaration ['" + enemy["groupName"] + "']!")
        if "links" in room:
            for link in room["links"]:
                if "to" in link:
                    for to in link["to"]:
                        if "strats" in to:
                            for strat in to["strats"]:
                                for k in ["requires"]:
                                    if k in strat:
                                        if len(strat[k]):
                                            result = find_keywords(strat[k])
                                            # if not result and "notable" in strat:
                                            #     result = not strat["notable"]
                                            if not result:
                                                print(room["name"] + " [" + str(link["from"]) + " -> " + str(to["id"]) + "] has a malformed strat ['" + strat["name"] + "']!")
