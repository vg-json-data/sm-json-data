# This script removes occurrences of `links` in room files.
# 
# To use, run "PYTHONPATH=. python migrations/remove_links.py"
# from a working directory of "sm-json-data/scripts".
import json
from pathlib import Path
import argparse
import format_json

argparser = argparse.ArgumentParser()
argparser.add_argument("--path", type=Path, default="../region", help="Path to the region directory")
args = argparser.parse_args()

if not args.path.exists():
    raise FileNotFoundError(f"Path {args.path} does not exist")
for path in sorted(args.path.glob("**/*.json")):
    room_json = json.load(path.open("r"))
    schema = room_json.get("$schema")
    if schema is None or schema.split("/")[-1] != "m3-room.schema.json":
        continue
    print("Processing", path)
    del room_json["links"]
    path.write_text(format_json.format(room_json, indent=2))
