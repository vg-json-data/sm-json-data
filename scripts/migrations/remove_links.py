# This script removes occurrences of `links` in room files.

import json
from pathlib import Path
import copy

import format_json


for path in sorted(Path("../../region").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue
    print("Processing", path)
    del room_json["links"]
    path.write_text(format_json.format(room_json, indent=2))
