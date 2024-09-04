# Tool to assign tech IDs where they are missing.
# This also performs auto-formatting.
#
# To use, run "python populate_tech_ids.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

path = Path("../tech.json")
all_tech_str = path.open("r").read()
all_tech_json = json.loads(all_tech_str)

next_id = all_tech_json.get("nextTechId", 1)
orig_next_id = next_id

def process_tech(tech_json):
    global next_id
    if "id" not in tech_json:
        new_tech_json = {"id": next_id, **tech_json}
        tech_json.clear()
        tech_json.update(new_tech_json)
        next_id += 1
    for t in tech_json.get("extensionTechs", []):
        process_tech(t)

for category_json in all_tech_json["techCategories"]:
    for t in category_json["techs"]:
        process_tech(t)

all_tech_json["nextTechId"] = next_id
    
new_tech_str = format_json.format(all_tech_json, indent=2)

if next_id != orig_next_id:
    print("Added {} tech IDs".format(next_id - orig_next_id))
elif new_tech_str != all_tech_str:
    print("Formatted tech")
    
# Write the auto-formatted output:
if new_tech_str != all_tech_str:
    path.write_text(new_tech_str)
