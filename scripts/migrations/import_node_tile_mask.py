import argparse
import json
from pathlib import Path
import copy

import format_json

parser = argparse.ArgumentParser(
    'import_node_tile_mask',
    'Import node-level mapTileMask data from Map Rando room_geometry.json')
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

    node_tiles_by_id = {}    
    for [node_id, map_tile_list] in room_geom["node_tiles"]:
        node_tiles_by_id[node_id] = map_tile_list
    for node_json in room_json["nodes"]:
        node_id = node_json["id"]
        map_tile_list = node_tiles_by_id[node_id]
        height = len(room_geom["map"])
        width = len(room_geom["map"][0])
        map_tile_mask = copy.deepcopy(room_geom["map"])
        for [x, y] in map_tile_list:
            map_tile_mask[y][x] = 2
        node_json["mapTileMask"] = map_tile_mask

    new_room_json = format_json.format(room_json, indent=2)

    # Write the auto-formatted output:
    path.write_text(new_room_json)
