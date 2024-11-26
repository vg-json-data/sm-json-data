import json
from pathlib import Path
import copy

for path in sorted(Path("../region/").glob("**/roomDiagrams/*.png")):
    parts = path.stem.split("_")
    assert len(parts) == 3
    new_stem = "_".join([parts[0], parts[2], parts[1]])
    new_filename = new_stem + ".png"
    new_path = Path(path.parent) / new_filename
    print("Renaming", path, " -> ", new_path)
    path.rename(new_path)

