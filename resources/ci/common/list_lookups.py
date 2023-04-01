# pylint: disable=multiple-statements
'''
Export manifests for lookup tables
'''
import json
import os

data = {
    "regions": {},
    "roomIDsByLCRoomName": {},
    "roomsByRoomID": {}
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
        # cycle through files
        for subregion in os.listdir(os.path.join(regionPath, region)):
            # if it's a JSON file and not a roomDiagram
            if ".json" in subregion and "roomDiagrams" not in subregion:
                # add the subregion to our notes
                data["regions"][region].append(os.path.splitext(subregion)[0])
                # open a subregion file
                with open(os.path.join(regionPath, region, subregion)) as subregionFile:
                    subregionJSON = json.load(subregionFile)
                    # cycle through rooms
                    for room in subregionJSON["rooms"]:
                        # add LC'd name to our notes
                        data["roomIDsByLCRoomName"][room["name"].lower()] = room["id"]

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
                        roomDiagram = os.path.join(
                            # ".",
                            "region",
                            region,
                            "roomDiagrams",
                            f"{room['subarea'].lower()}_{room['id']}_{room['name'].replace(' and ', ' And ').replace(' ', '')}.png"
                        )
                        if os.path.isfile(roomDiagram):
                            room["roomDiagram"] = roomDiagram

                        # add trimmed room to our notes
                        data["roomsByRoomID"][room["id"]] = room

with open(
    os.path.join(
        ".",
        "resources",
        "app",
        "manifests",
        "lookups.json"
    ),
    "w",
    encoding="utf-8"
) as lookupsFile:
    lookupsFile.write(json.dumps(data, indent=2))
