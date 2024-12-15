import argparse
import json
from pathlib import Path

import format_json

parser = argparse.ArgumentParser(
    'import_map_tile_mask',
    'Import mapTileMask data from Map Rando room_geometry.json')
parser.add_argument('room_geometry_path', type=str)
args = parser.parse_args()

room_geom_list = json.load(open(args.room_geometry_path, "r"))
room_geom_by_addr = {room["rom_address"]: room for room in room_geom_list}

for path in sorted(Path("../region/").glob("**/*.json")):
    room_json = json.load(path.open("r"))
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    addr = int(room_json["roomAddress"], 16)
    if addr not in room_geom_by_addr:
        print("Skipping", path)
        continue
    print("Processing", path)
    room_geom = room_geom_by_addr[addr]
    room_json["mapTileMask"] = room_geom["map"]

    new_room_json = format_json.format(room_json, indent=2)

    # Write the auto-formatted output:
    path.write_text(new_room_json)
