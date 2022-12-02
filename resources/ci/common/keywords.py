import json
import os

keywords = {"items":[],"helpers":[], "techs":[], "flags":[]}

itemsJSON = {}
itemsPath = os.path.join("items.json")
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

# helpers
helpersJSON = {}
helpersPath = os.path.join("helpers.json")
with open(helpersPath, encoding="utf-8") as helpersFile:
    helpersJSON = json.load(helpersFile)
if "helpers" in helpersJSON:
    for helper in helpersJSON["helpers"]:
        if "name" in helper:
            keywords["helpers"].append(helper["name"])

# tech
techJSON = {}
techPath = os.path.join("tech.json")
with open(techPath, encoding="utf-8") as techFile:
    techJSON = json.load(techFile)
if "techs" in techJSON:
    for tech in techJSON["techs"]:
        if "name" in tech:
            keywords["techs"].append(tech["name"])

for k in keywords.keys():
    keywords[k].sort()

print(json.dumps(keywords, indent=2))

with open(os.path.join("resources","app","manifests","keywords.json"), encoding="utf-8", mode="w+") as keywordsFile:
    json.dump(keywords, keywordsFile, indent=2)
