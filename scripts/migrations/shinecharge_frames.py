# Single-time-use script to migrate shinecharge frame requirements from "comeInShinecharged"/"leaveShinecharged"
# entrance/exit conditions, into strat "requires" in the form of "shineChargeFrames" logical requirements.
#
# To use, run "python -m migrations.shinecharge_frames" from a working directory of "sm-json-data/scripts".
import json
from pathlib import Path

import format_json

for path in sorted(Path("../region/").glob("**/*.json")):
    print(f"Processing {path}")
    room_str = path.open("r").read()
    room_json = json.loads(room_str)
    if room_json.get("$schema") != "../../../schema/m3-room.schema.json":
        continue

    for strat in room_json["strats"]:
        frames_used = None
        
        exit_condition = strat.get("exitCondition")
        if exit_condition is not None and "leaveShinecharged" in exit_condition:
            frames_remaining = exit_condition["leaveShinecharged"]["framesRemaining"]
            del exit_condition["leaveShinecharged"]["framesRemaining"]
            if frames_remaining != "auto":
                frames_used = 180 - frames_remaining
                strat["requires"] = strat["requires"] + [{"shineChargeFrames": frames_used}]
        
        entrance_condition = strat.get("entranceCondition")
        if entrance_condition is not None and "comeInShinecharged" in entrance_condition:
            if frames_used is not None:
                raise RuntimeError("frames used in both entrance and exit condition")
            frames_used = entrance_condition["comeInShinecharged"]["framesRequired"]
            strat["requires"] = [{"shineChargeFrames": frames_used}] + strat["requires"]
            del entrance_condition["comeInShinecharged"]["framesRequired"]

    # Write the auto-formatted output:
    new_room_str = format_json.format(room_json, indent=2)
    if room_str != new_room_str:
        path.write_text(new_room_str)
