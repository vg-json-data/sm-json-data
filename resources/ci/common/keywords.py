"""
Extract keywords for sanity checks
"""

import json
import os

keywords = {
  "areas": [],
  "enemies": {"enemyById":{},"enemyByName":{}},
  "flags": [],
  "helpers": [],
  "items": [],
  "techs": [],
  "weapons": []
}

def dig_for_children(child_type, this_child):
    """
    Recursively find extensionTechs
    """
    if child_type in ["helper"]:
        child_type = child_type + "s"
    if "name" in this_child:
        keywords[child_type].append(this_child["name"])
        # print(this_child["name"])
        if ("extension" + child_type[:1].upper() + child_type[1:]) in this_child:
            for ext_child in this_child["extensionTechs"]:
                # print(" " + extTech["name"])
                dig_for_children(child_type, ext_child)

# areas
regionPath = os.path.join(
    ".",
    "region"
)
for area in os.listdir(regionPath):
    if os.path.isdir(
        os.path.join(
            regionPath,
            area
        )
    ):
        keywords["areas"].append(area)

# enemies
enemiesPaths = [
    os.path.join(".","enemies","main.json"),
    os.path.join(".","enemies","bosses","main.json")
]
for enemiesPath in enemiesPaths:
    with open(enemiesPath, encoding="utf-8") as enemiesFile:
        enemiesJSON = json.load(enemiesFile)
        if "enemies" in enemiesJSON:
            for enemy in enemiesJSON["enemies"]:
                if "id" in enemy and "name" in enemy:
                    keywords["enemies"]["enemyById"][enemy["id"]] = enemy["name"]
                    keywords["enemies"]["enemyByName"][enemy["name"]] = enemy["id"]

# items & flags
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

# helpers, tech
for docType in ["helper", "tech"]:
    docPath = os.path.join(".", docType + ".json")
    if docType in ["helper"]:
        docPath = docPath.replace(docType + ".json", docType + "s.json")
    with open(docPath, encoding="utf-8") as docFile:
        docJSON = json.load(docFile)
        if (docType + "s") in docJSON:
            for child in docJSON[docType + "s"]:
                if "name" in child:
                    dig_for_children(docType + "s", child)
        if (docType + "Categories") in docJSON:
            for docCat in docJSON[(docType + "Categories")]:
                if (docType + "s") in docCat:
                    for child in docCat[(docType + "s")]:
                        dig_for_children(docType + "s", child)

# print(json.dumps(techNames, indent=2))

weaponsPath = os.path.join(".","weapons","main.json")
with open(weaponsPath, encoding="utf-8") as weaponsFile:
    weaponsJSON = json.load(weaponsFile)
    if "weapons" in weaponsJSON:
        for weapon in weaponsJSON["weapons"]:
            if "name" in weapon:
                keywords["weapons"].append(weapon["name"])
    if "categories" in weaponsJSON:
        for category in weaponsJSON["categories"]:
            keywords["weapons"].append(category)
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
