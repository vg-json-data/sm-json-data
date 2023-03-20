'''
Manage Room Diagrams
'''
import json
import os
from PIL import Image

def coord_calc(origin,dims):
    x1, x2 = origin
    w, h = dims
    return (x1,x2,w+x1,h+x2)

for r,d,f in os.walk(
    os.path.join(
        ".",
        "region"
    )
):
    for filename in f:
        if ".png" in filename and "region_" in filename:
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
                with open(os.path.join(r, "roomDiagrams.json"), mode="r", encoding="utf-8") as roomDataFile:
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
                            roomOrigin = roomData["origin"]
                            roomOrigin = ((roomOrigin[0] * 256) + mapOrigin[0], (roomOrigin[1] * 256) + mapOrigin[1])
                            width = "width" in roomData and roomData["width"] or 1
                            height = "height" in roomData and roomData["height"] or 1
                            cropped_image = region_image.crop(
                                coord_calc(
                                    roomOrigin,
                                    (
                                        width * 256,
                                        height * 256
                                    )
                                )
                            )
                            # Wrecked Ship
                            if "wreckedship" in r:
                                # Main Shaft
                                if roomID == "155":
                                    # Cover Bowling Alley
                                    black_img = Image.new("RGB",
                                        (4 * 256, 5 * 256)
                                    )
                                    cropped_image.paste(black_img)
                                    # Cover Super Missile
                                    black_img = Image.new("RGB",
                                        (4 * 256, 2 * 256)
                                    )
                                    cropped_image.paste(
                                        black_img,
                                        (0, 6 * 256)
                                    )
                                # Bowling Alley
                                if roomID == "161":
                                    # Cover Area Map
                                    black_img = Image.new("RGB",
                                        (1 * 256, 1 * 256)
                                    )
                                    cropped_image.paste(black_img)
                                    # Cover Gravity Suit
                                    black_img = Image.new("RGB",
                                        (1 * 256, 1 * 256)
                                    )
                                    cropped_image.paste(
                                        black_img,
                                        (0, 2 * 256)
                                    )
                            regionName = r.split(os.sep)[2]
                            cropped_image.save(
                                os.path.join(
                                    ".",
                                    r,
                                    "roomDiagrams",
                                    "clean",
                                    f"{regionName}_{roomID}_roomName.png"
                                )
                            )
