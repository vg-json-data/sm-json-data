"""
Extract keywords for sanity checks
"""

import json
import os

keywords = {
  "items": [],
  "enemies": {"enemyById":{},"enemyByName":{}},
  "helpers": [],
  "techs": [],
  "flags": []
}

def dig_for_techs(this_tech):
    """
    Recursively find extensionTechs
    """
    if "name" in this_tech:
        keywords["techs"].append(this_tech["name"])
        # print(this_tech["name"])
        if "extensionTechs" in this_tech:
            for ext_tech in this_tech["extensionTechs"]:
                # print(" " + extTech["name"])
                dig_for_techs(ext_tech)

# items & flags
itemsJSON = {}
itemsPath = os.path.join(".", "items.json")
with open(itemsPath, encoding="utf-8") as itemsFile:
    itemsJSON = json.load(itemsFile)
for [k,v] in itemsJSON.items():
    # items
    if "Items" in k and not "starting" in k:
        if isinstance(v, list):
            if isinstance(v[0], dict):
                for item in v:
                    if "name" in item:
                        keywords["items"].append(item["name"])
            else:
                keywords["items"].extend(v)
    # flags
    elif "Flags" in k:
        keywords["flags"].extend(v)

# enemies
enemiesJSON = {}
enemiesPath = os.path.join(".", "enemies", "main.json")
with open(enemiesPath, encoding="utf-8") as enemiesFile:
    enemiesJSON = json.load(enemiesFile)
if "enemies" in enemiesJSON:
    for enemy in enemiesJSON["enemies"]:
        if "id" in enemy and "name" in enemy:
            keywords["enemies"]["enemyById"][enemy["id"]] = enemy["name"]
            keywords["enemies"]["enemyByName"][enemy["name"]] = enemy["id"]

# helpers
helpersJSON = {}
helpersPath = os.path.join(".", "helpers.json")
with open(helpersPath, encoding="utf-8") as helpersFile:
    helpersJSON = json.load(helpersFile)
if "helpers" in helpersJSON:
    for helper in helpersJSON["helpers"]:
        if "name" in helper:
            keywords["helpers"].append(helper["name"])

# tech
techJSON = {}
techPath = os.path.join(".", "tech.json")
with open(techPath, encoding="utf-8") as techFile:
    techJSON = json.load(techFile)
if "techs" in techJSON:
    for tech in techJSON["techs"]:
        if "name" in tech:
            dig_for_techs(tech)
if "techCategories" in techJSON:
    for techCat in techJSON["techCategories"]:
        if "techs" in techCat:
            for tech in techCat["techs"]:
                dig_for_techs(tech)

# print(json.dumps(techNames, indent=2))

for [k, _] in keywords.items():
    if isinstance(keywords[k], list):
        keywords[k].sort()

# print(json.dumps(keywords, indent=2))

with open(os.path.join(
    "resources",
    "app",
    "manifests",
    "keywords.json"
    ), encoding="utf-8", mode="w+") as keywordsFile:
    json.dump(keywords, keywordsFile, indent=2)
