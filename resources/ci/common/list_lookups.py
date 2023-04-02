# pylint: disable=multiple-statements
'''
Export manifests for lookup tables
'''
import json
import os
import re

data = {
    "regions": {},
    "roomIDsByLCRoomName": {},
    "roomsByRegion": {}
}
regionPath = os.path.join(
    ".",
    "region"
)

# cycle through regions
for region in os.listdir(regionPath):
    # if it's a folder
    if os.path.isdir(os.path.join(regionPath, region)):
        # add the region to our notes
        data["regions"][region] = []
        data["roomsByRegion"][region] = {}
        # cycle through files
        for subregion in os.listdir(os.path.join(regionPath, region)):
            # if it's a JSON file and not a roomDiagram
            if ".json" in subregion and "roomDiagrams" not in subregion:
                # add the subregion to our notes
                data["regions"][region].append(os.path.splitext(subregion)[0])
                # open a subregion file
                with open(os.path.join(regionPath, region, subregion), "r", encoding="utf-8") as subregionFile:
                    subregionJSON = json.load(subregionFile)
                    # cycle through rooms
                    for room in subregionJSON["rooms"]:
                        # add LC'd name to our notes
                        data["roomIDsByLCRoomName"][room["name"].lower()] = room["id"]
                        for stripped in [
                            room["name"].lower(),
                            "".join([s for s in room["name"].lower() if s.isalnum() or s.isspace()])
                        ]:
                            for [search, repls] in {"": "", "\\W": " "}.items():
                                for repl in repls:
                                    stripped = re.sub(r"[" + search + "]+", repl, room["name"].lower())
                                stripped = re.sub(r"[\s]{2,}", " ", stripped)
                                stripped = re.sub(r" s ", "s ", stripped)
                                if stripped != room["name"].lower():
                                    data["roomIDsByLCRoomName"][stripped] = room["id"]

                        if "ceres" in room["area"].lower():
                            room["area"] = "Ceres"
                            room["subarea"] = "Ceres"

                        # trim nodes
                        for [i, node] in enumerate(room["nodes"]):
                            if "runways" in node:         del node["runways"]
                            if "canLeaveCharged" in node: del node["canLeaveCharged"]
                            if "viewableNodes" in node:   del node["viewableNodes"]
                            if "locks" in node:           del node["locks"]
                            room["nodes"][i] = node

                        # trim room
                        if "reusableRoomwideNotable" in room: del room["reusableRoomwideNotable"]
                        if "obstacles" in room: del room["obstacles"]
                        if "enemies" in room:   del room["enemies"]

                        # trim links
                        if "links" in room:
                            for [i, link] in enumerate(room["links"]):
                                for [j, toNode] in enumerate(link["to"]):
                                    if "strats" in toNode: del toNode["strats"]
                                    link["to"][j] = toNode
                                room["links"][i] = link

                        # add roomDiagram path
                        sanitizedRoomName = room["name"]
                        for [repl, chars] in {
                            "": [
                                "-",
                                ".",
                                "(",
                                ")",
                                "'"
                            ],
                            "-": [
                                "\\",
                                "/"
                            ]
                        }.items():
                            for char in chars:
                                sanitizedRoomName = sanitizedRoomName.replace(char, repl)
                        sanitizedRoomName = sanitizedRoomName \
                            .replace(" and ", " And ") \
                            .replace(" ", "")

                        subarea = room["subarea"].lower()

                        if "subsubarea" in room:
                            subsubarea = room["subsubarea"]
                            subarea = f"{subarea.lower()}-{subsubarea.lower()}"

                        roomDiagram = os.path.join(
                            # ".",
                            "region",
                            region,
                            "roomDiagrams",
                            f"{subarea}_{room['id']}_{sanitizedRoomName}.png"
                        )

                        if os.path.isfile(roomDiagram):
                            room["roomDiagram"] = roomDiagram
                        else:
                            print(f"ERROR: {region}:{subarea}:{room['id']}:{room['name']} roomDiagram not found!")

                        # add trimmed room to our notes
                        if subarea.lower() not in data["roomsByRegion"][region]:
                            data["roomsByRegion"][region][subarea] = {}
                        data["roomsByRegion"][region][subarea][room["id"]] = room

with open(
    os.path.join(
        ".",
        "resources",
        "app",
        "manifests",
        "regions.json"
    ),
    "w",
    encoding="utf-8"
) as regionsLookupFile:
    regionsLookupFile.write(json.dumps(data["regions"], indent=2))

with open(
    os.path.join(
        ".",
        "resources",
        "app",
        "manifests",
        "roomIDsByLCRoomName.json"
    ),
    "w",
    encoding="utf-8"
) as lcNamesFile:
    lcNamesFile.write(json.dumps(data["roomIDsByLCRoomName"], indent=2))

for region, regionData in data["roomsByRegion"].items():
    for subregion, subregionData in regionData.items():
        regionPath = os.path.join(
            ".",
            "resources",
            "app",
            "manifests",
            "abridgedRooms",
            region
        )

        if not os.path.isdir(regionPath):
            os.makedirs(regionPath)

        with open(
            os.path.join(
                regionPath,
                f"{subregion}.json"
            ),
            "w",
            encoding="utf-8"
        ) as subregionFile:
            subregionFile.write(json.dumps(data["roomsByRegion"][region][subregion], indent=2))
