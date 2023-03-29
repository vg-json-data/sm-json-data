# pylint: disable=unnecessary-pass
"""
Validate JSON against provided schema
"""
import os
import json
import re
from pathlib import Path
from jsonschema import validate, RefResolver

schemas = {}

print("LOAD SCHEMAS")
schemaDir = os.path.join(".", "schema")
schemaAbsPath = os.path.abspath(schemaDir)
schemaURI = Path(schemaAbsPath).as_uri() + "/"
for schemaFileName in os.listdir(schemaDir):
    with open(
        os.path.join(
            schemaDir,
            schemaFileName
        ),
        "r",
        encoding="utf-8"
    ) as schemaFile:
        match = re.match(
            r"^([^-]*)(?:-)([^\.]*)(?:\.schema\.json)$",
            schemaFileName
        )
        if match:
            gameKey = match.group(1)
            schemaKey = match.group(2)
            if gameKey not in schemas:
                schemas[gameKey] = {}
            schemas[gameKey][schemaKey] = json.load(schemaFile)

print("VALIDATE")

# connections
print(" CONNECTIONS")
for region in os.listdir(os.path.join(".", "connection")):
    if os.path.isdir(os.path.join(".", "connection", region)):
        print("  " + region.capitalize())
        for subregion in os.listdir(os.path.join(".", "connection", region)):
            if ".json" in subregion and "roomDiagrams" not in subregion:
                print("   " + subregion[:subregion.find(".")].capitalize())
                with open(
                    os.path.join(
                        ".",
                        "connection",
                        region,
                        subregion
                    ),
                    "r",
                    encoding="utf-8"
                ) as jsonFile:
                    connectionJSON = json.load(jsonFile)
                    result = validate(
                        instance=connectionJSON,
                        schema=schemas["m3"]["connection"],
                        resolver=RefResolver(
                            base_uri=schemaURI,
                            referrer=schemas["m3"]["connection"]
                        )
                    )
                    if result:
                        print("    " + "INVALID")
                        pass
print()

# enemies
print(" ENEMIES")
for r,d,f in os.walk(os.path.join(".", "enemies")):
    for filename in f:
        if ".json" in filename:
            filePath = os.path.join(r, filename)
            scenariosFile = "scenarios" in filePath
            if scenariosFile:
                schema = schemas["m3"]["bossScenarios"]
            else:
                schema = schemas["m3"]["enemies"]
            print("  " + os.path.join(r, filename))
            with open(filePath, "r", encoding="utf-8") as jsonFile:
                enemiesJSON = json.load(jsonFile)
                result = validate(
                    instance=enemiesJSON,
                    schema=schema,
                    resolver=RefResolver(
                        base_uri=schemaURI,
                        referrer=schema
                    )
                )
                if result:
                    print("    " + "INVALID")
                    pass
print()

# regions
print(" REGIONS")
for region in os.listdir(os.path.join(".", "region")):
    if os.path.isdir(os.path.join(".", "region", region)):
        print("  " + region.capitalize())
        for subregion in os.listdir(os.path.join(".", "region", region)):
            if ".json" in subregion and "roomDiagrams" not in subregion:
                print("   " + subregion[:subregion.find(".")].capitalize())
                with open(
                    os.path.join(
                        ".",
                        "region",
                        region,
                        subregion
                    ),
                    "r",
                    encoding="utf-8"
                ) as jsonFile:
                    regionJSON = json.load(jsonFile)
                    result = validate(
                        instance=regionJSON,
                        schema=schemas["m3"]["region"],
                        resolver=RefResolver(
                            base_uri=schemaURI,
                            referrer=schemas["m3"]["region"]
                        )
                    )
                    if result:
                        print("    " + "INVALID")
                        pass
print()

# weapons
print(" WEAPONS")
for r,d,f in os.walk(os.path.join(".", "weapons")):
    for filename in f:
        if ".json" in filename:
            filePath = os.path.join(r, filename)
            print("  " + os.path.join(r, filename))
            with open(filePath, "r", encoding="utf-8") as jsonFile:
                weaponsJSON = json.load(jsonFile)
                result = validate(
                    instance=weaponsJSON,
                    schema=schemas["m3"]["weapons"],
                    resolver=RefResolver(
                        base_uri=schemaURI,
                        referrer=schemas["m3"]["weapons"]
                    )
                )
                if result:
                    print("    " + "INVALID")
                    pass
print()

# root
for rootType in [
    "helpers",
    "items",
    "tech"
]:
    print(" " + rootType.upper())
    filePath = os.path.join(".", rootType + ".json")
    print("  " + filePath)
    with open(filePath, "r", encoding="utf-8") as jsonFile:
        fileJSON = json.load(jsonFile)
        result = validate(
            instance=fileJSON,
            schema=schemas["m3"][rootType],
            resolver=RefResolver(
                base_uri=schemaURI,
                referrer=schemas["m3"][rootType]
            )
        )
        if result:
            print("     " + "INVALID")
            pass
    print()
