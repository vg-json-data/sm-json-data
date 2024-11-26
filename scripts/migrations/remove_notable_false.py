# This script removes occurrences of `"notable": false` in strats since this is now the default.

import json
from pathlib import Path
import copy

import format_json


for path in sorted(Path("../region").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue
    print("Processing", path)
    for strat in room_json["strats"]:
        if strat.get("notable") == False:
            del strat["notable"]
    path.write_text(format_json.format(room_json, indent=2))
