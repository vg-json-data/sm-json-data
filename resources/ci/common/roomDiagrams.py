# pylint: disable=invalid-name
'''
Manage Room Diagrams
'''
import json
import os
import re
from PIL import Image

def coord_calc(origin,dims):
    x1, x2 = origin
    w, h = dims
    return (x1,x2,w+x1,h+x2)

roomIDs = {}

rootPath = os.path.join(
    ".",
    "region",
    "crateria"
)

def lift_pathways(rootPath):
    makedot = 100
    for r,_,f in os.walk(rootPath):
        for filename in f:
            if ".png" in filename and \
                "roomDiagrams" in r and \
                "clean" not in r and \
                "roomPathways" not in r:
                if not os.path.isdir(
                    os.path.join(
                        ".",
                        r,
                        "roomPathways"
                    )
                ):
                    os.makedirs(
                        os.path.join(
                            ".",
                            r,
                            "roomPathways"
                        )
                    )
                roomImg = Image.open(os.path.join(r, filename))
                roomImg = roomImg.convert("RGBA")
                roomID = re.match(r"(?:[^\_]*)(?:[\_])([\d]+)(?:[\_])(?:[^_]*)", filename).group(1)
                if roomID in roomIDs:
                    # areaSlug = roomIDs[roomID]["areaSlug"]
                    # subareaSlug = roomIDs[roomID]["subareaSlug"]
                    roomName = roomIDs[roomID]["name"]
                    # if areaSlug == "ceres":
                    #     subareaSlug = "ceres"
                print(f"  > Extracting {roomID}: {roomName}", end="")
                w, h = roomImg.size
                for i in range(0, w):
                    for j in range(0, h):
                        pixVal = roomImg.getpixel((i, j))
                        if pixVal not in [
                            (255, 255, 255),      # white
                            (255, 255, 255, 255), # white
                            (255, 242,   0),      # yellow
                            (255, 242,   0, 255), # yellow
                            (255, 201,  14),      # orange
                            (255, 201,  14, 255), # orange
                            (181, 230,  29),      # green
                            (181, 230,  29, 255)  # green
                        ]:
                            roomImg.putpixel((i, j), (0, 0, 0, 0))
                    if (i) % (makedot) == 0:
                        print(".", end="")
                roomImg.save(os.path.join(".",r,"roomPathways",filename))
                print()

def make_clean(rootPath):
    for r,_,f in os.walk(rootPath):
        for filename in f:
            if "region_" in filename or "roomDiagrams.json" in filename:
                f.remove(filename)
                f.append(filename)
        for filename in f:
            if ".json" in filename and "roomDiagrams" not in filename:
                # JSON Files
                with open(os.path.join(r, filename), "r", encoding="utf-8") as regionFile:
                    regionJSON = json.load(regionFile)
                    area = ""
                    subarea = ""
                    if "rooms" in regionJSON:
                        for room in regionJSON["rooms"]:
                            areaPath = os.path.dirname(os.path.join(r, filename)).split(os.sep)
                            area = room["area"]
                            subarea = room["subarea"]
                            areaSlug = areaPath[-1]
                            subareaSlug = os.path.splitext(filename)[0]
                            roomIDs[str(room["id"])] = {
                                "name": room["name"],
                                "area": area,
                                "subarea": subarea,
                                "areaSlug": areaSlug,
                                "subareaSlug": subareaSlug
                            }
                        print(f"> Reading {area}/{subarea}")
                    else:
                        print(f"!!! {os.path.join(r,filename)} has no rooms!")
            if ".png" in filename and "region_" in filename:
                # Region Image
                print(f" > Opening {filename}")
                if not os.path.isdir(
                    os.path.join(
                        ".",
                        r,
                        "roomDiagrams",
                        "clean"
                    )
                ):
                    os.makedirs(
                        os.path.join(
                            ".",
                            r,
                            "roomDiagrams",
                            "clean"
                        )
                    )
                if os.path.isfile(os.path.join(r, "roomDiagrams.json")):
                    with open(
                        os.path.join(
                            r,
                            "roomDiagrams.json"
                        ),
                        mode="r",
                        encoding="utf-8"
                    ) as roomDataFile:
                        roomDataJSON = json.load(roomDataFile)
                        with Image.open(
                            os.path.join(
                                r,
                                filename
                            )
                        ) as region_image:
                            region_image = region_image.convert("RGB")
                            mapOrigin = [0, 0]
                            for [roomID, roomData] in roomDataJSON.items():
                                if roomID == "origin":
                                    mapOrigin = roomData
                                    continue
                                subareaSlug = "unknownSubArea"
                                roomName = "unknownRoom"
                                if roomID in roomIDs:
                                    areaSlug = roomIDs[roomID]["areaSlug"]
                                    subareaSlug = roomIDs[roomID]["subareaSlug"]
                                    roomName = roomIDs[roomID]["name"]
                                    if areaSlug == "ceres":
                                        subareaSlug = "ceres"
                                print(f"  > Building {roomID}: {roomName}")
                                roomOrigin = roomData["origin"]
                                roomOrigin = (
                                    (roomOrigin[0] * 256) + mapOrigin[0],
                                    (roomOrigin[1] * 256) + mapOrigin[1]
                                )
                                width = roomData["width"] if "width" in roomData else 1
                                height = roomData["height"] if "height" in roomData else 1
                                cropped_image = region_image.crop(
                                    coord_calc(
                                        roomOrigin,
                                        (
                                            width * 256,
                                            height * 256
                                        )
                                    )
                                )
                                if "covers" in roomData:
                                    for cover in roomData["covers"]:
                                        if "name" in cover:
                                            print(f"   > Cover: {cover['name']}")
                                        origin = cover["origin"] if "origin" in cover else [0, 0]
                                        width = cover["width"] if "width" in cover else 1
                                        height = cover["height"] if "height" in cover else 1
                                        black_img = Image.new(
                                            "RGB",
                                            (width * 256, height * 256)
                                        )
                                        cropped_image.paste(
                                            black_img,
                                            (
                                                origin[0] * 256,
                                                origin[1] * 256
                                            )
                                        )
                                roomName = re.sub(r"[^\w\d]", "", roomName)
                                cropped_image.save(
                                    os.path.join(
                                        ".",
                                        r,
                                        "roomDiagrams",
                                        "clean",
                                        f"{subareaSlug}_{roomID}_{roomName}.png"
                                    )
                                )

make_clean(rootPath)
# lift_pathways(rootPath)
