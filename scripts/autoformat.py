# Tool to auto-format all the region files in a standard way.
#
# To use, run "python autoformat.py" from a working directory of "sm-json-data/scripts".

import json
from pathlib import Path

import format_json

for dirpath in ["../region/", "../resources/app/manifests/"]:
    for filext in [".json", ".off"]:
        fileList = Path(dirpath).glob(f"**/*{filext}")
        for path in sorted(Path(dirpath).glob(f"**/*{filext}")):
            json_data = []
            json_data = json.load(path.open("r"))
            if "$schema" in json_data and json_data.get("$schema") not in [
                "../../schema/m3-region.schema.json"
            ]:
                continue

            print("Processing", path)
            new_json_data = format_json.format(json_data, indent=2)

            # Validate that the new JSON is equivalent to the old (i.e. the differences affect formatting only):
            assert json.loads(new_json_data) == json_data

            # Write the auto-formatted output:
            path.write_text(new_json_data)
