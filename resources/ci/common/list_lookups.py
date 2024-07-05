# pylint: disable=multiple-statements
'''
Export manifests for lookup tables
'''
import json
import os
import re

from collections import OrderedDict

data = {
    "regions": {},
    "roomIDsByLCRoomName": {},
    "roomMetasByID": {},
    "roomsByRegion": {},
    "smooshedRoomNames": []
}
regionPath = os.path.join(
    ".",
    "region"
)

def mySort(toSort):
    ret = toSort
    if isinstance(toSort, list):
        ret = sorted(toSort)
    elif isinstance(toSort, dict):
        ret = dict(sorted(toSort.items()))
    return ret

# cycle through regions
print("> Cycling regions")
for region in os.listdir(regionPath):
    # if it's a folder
    if os.path.isdir(os.path.join(regionPath, region)):
        print(f" > {region}")
        # add the region to our notes
        data["regions"][region] = []
        data["roomsByRegion"][region] = {}
        # cycle through subregions
        for subregion in os.listdir(os.path.join(regionPath, region)):
            if os.path.isdir(os.path.join(regionPath, region, subregion)):
                # if it's not a roomDiagram
                if "roomDiagrams" not in subregion:
                    print(f"  > {region}/{subregion}")
                    # cycle through files
                    for roomFileName in os.listdir(os.path.join(regionPath, region, subregion)):
                        # if it's a JSON file
                        if ".json" in roomFileName:
                            roomName = roomFileName.replace(".json", "")
                            print(f"   > {region}/{subregion}/{roomName}")
                            # add the subregion to our notes
                            if os.path.splitext(subregion)[0] not in data["regions"][region]:
                                data["regions"][region].append(os.path.splitext(subregion)[0])
                                data["regions"][region] = mySort(data["regions"][region])
                            # open a room file
                            with open(os.path.join(regionPath, region, subregion, roomFileName), "r", encoding="utf-8") as roomFile:
                                roomJSON = json.load(roomFile)
                                # read through room
                                rooms = [roomJSON]
                                for room in rooms:
                                    # add smooshed name to our notes
                                    data["smooshedRoomNames"].append("".join([s for s in room["name"] if s.isalnum()]))
                                    data["smooshedRoomNames"].sort()
                                    # add LC'd name to our notes
                                    data["roomIDsByLCRoomName"][room["name"].lower()] = room["id"]
                                    data["roomIDsByLCRoomName"] = mySort(data["roomIDsByLCRoomName"])
                                    for stripped in [
                                        room["name"].lower(),
                                        "".join([s for s in room["name"].lower() if s.isalnum() or s.isspace()])
                                    ]:
                                        for [search, repls] in {"": "", "\\W": " "}.items():
                                            for repl in repls:
                                                stripped = re.sub(r"[" + search + "]+", repl, room["name"].lower())
                                            stripped = re.sub(r"[\s]{2,}", " ", stripped)
                                            stripped = re.sub(r" s ", "s ", stripped)
                                            if stripped.startswith("the "):
                                                data["roomIDsByLCRoomName"][stripped[4:]] = room["id"]
                                            if stripped != room["name"].lower():
                                                data["roomIDsByLCRoomName"][stripped] = room["id"]
                                            data["roomIDsByLCRoomName"] = mySort(data["roomIDsByLCRoomName"])

                                    nukes = [
                                        "runways",
                                        "canLeaveCharged",
                                        "leaveWithGMode",
                                        "leaveWithGModeSetup",
                                        "gModeImmobile",
                                        "viewableNodes",
                                        "locks",
                                        "$schema",
                                        "enemies",
                                        "obstacles",
                                        "reusableRoomwideNotable",
                                        "requires",
                                        "clearsObstacles",
                                        "jumpways",
                                        "gModeRegainMobility",
                                        "entranceCondition",
                                        "exitCondition"
                                    ]

                                    if "ceres" in room["area"].lower():
                                        room["area"] = "Ceres"
                                        room["subarea"] = "Ceres"

                                    # trim nodes
                                    for [i, node] in enumerate(room["nodes"]):
                                        for nuke in nukes:
                                            if nuke in node:
                                                del node[nuke]
                                        room["nodes"][i] = node

                                    # trim room
                                    for key in nukes:
                                        if key in room:
                                            del room[key]

                                    # trim links
                                    if "links" in room:
                                        for [i, link] in enumerate(room["links"]):
                                            for [j, toNode] in enumerate(link["to"]):
                                                if "strats" in toNode: del toNode["strats"]
                                                link["to"][j] = toNode
                                            room["links"][i] = link

                                    # trim strats
                                    if "strats" in room:
                                        for [i, strat] in enumerate(room["strats"]):
                                            for key in nukes:
                                                if key in strat:
                                                    del strat[key]

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

                                    roomTrans = {
                                        "GreenBrinstarMainShaft": "GreenBrinstarMainShaft-EtecoonRoom",
                                        "KraidRoom": "KraidsRoom",
                                        "XRayScopeRoom": "X-RayScopeRoom"
                                    }
                                    if sanitizedRoomName in roomTrans.keys():
                                        sanitizedRoomName = roomTrans[sanitizedRoomName]

                                    subarea = room["subarea"].lower()

                                    if "subsubarea" in room:
                                        subsubarea = room["subsubarea"]
                                        subarea = f"{subarea.lower()}-{subsubarea.lower()}"
                                        if "norfair" in region:
                                            subarea = subsubarea.lower()

                                    roomDiagram = os.path.join(
                                        # ".",
                                        "region",
                                        region,
                                        "roomDiagrams",
                                        # f"{subarea}_{room['id']}_{sanitizedRoomName}.png"
                                        f"{subarea}_{sanitizedRoomName}_{room['id']}.png"
                                    )

                                    if os.path.isfile(roomDiagram):
                                        room["roomDiagram"] = roomDiagram
                                    else:
                                        print(f"ERROR: {region}:{subarea}:{room['id']}:{room['name']} ['{roomDiagram}'] roomDiagram not found!")

                                    # add trimmed room to our notes
                                    if subarea.lower() not in data["roomsByRegion"][region]:
                                        data["roomsByRegion"][region][subarea] = {}
                                    data["roomsByRegion"][region][subarea][room["id"]] = room
                                    data["roomsByRegion"][region][subarea] = mySort(data["roomsByRegion"][region][subarea])
                                    data["roomMetasByID"][room["id"]] = {
                                         "region": region,
                                         "subarea": subarea,
                                         "roomName": room["name"]
                                    }
                                    data["roomMetasByID"] = mySort(data["roomMetasByID"])

for jsonKey in [
    "regions",
    "roomIDsByLCRoomName",
    "roomMetasByID",
    "smooshedRoomNames"
]:
    with open(
        os.path.join(
            ".",
            "resources",
            "app",
            "manifests",
            f"{jsonKey}.json"
        ),
        "w",
        encoding="utf-8"
    ) as jsonFile:
        # if isinstance(data[jsonKey], dict):
        #     data[jsonKey] = OrderedDict(sorted(data[jsonKey].items(), reverse=True))
        jsonFile.write(json.dumps(data[jsonKey], indent=2))

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
