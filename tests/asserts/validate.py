# pylint: disable=unnecessary-pass
"""
Validate JSON against provided schema
"""
import os
import json
import re
from pathlib import Path
from jsonschema import validate, RefResolver
from jsonschema import exceptions as JSONSchemaExceptions

schemas = {}

errors = []
bail = False

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
            try:
                schemas[gameKey][schemaKey] = json.load(schemaFile)
            except json.JSONDecodeError as e:
                jsonFile.seek(0)
                errorLine = ""
                errorCol = 0
                pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                match = re.match(pattern, str(e))
                if match:
                    line_num = int(match.group(1))
                    for i,line in enumerate(jsonFile):
                        if i == (line_num - 1):
                            errorLine = line
                        if i > line_num:
                            break
                    errorCol = int(match.group(2))
                errors.append([
                    f"🔴ERROR: Schema '{schemaFilename}' is malformed!",
                    e,
                    errorLine.replace("\n",""),
                    ("-" * (errorCol - 3)) + "^"
                ])
                bail = True

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
                    connectionJSON = None

                    try:
                        connectionJSON = json.load(jsonFile)
                    except json.JSONDecodeError as e:
                        jsonFile.seek(0)
                        errorLine = ""
                        errorCol = 0
                        pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                        match = re.match(pattern, str(e))
                        if match:
                            line_num = int(match.group(1))
                            for i,line in enumerate(jsonFile):
                                if i == (line_num - 1):
                                    errorLine = line
                                if i > line_num:
                                    break
                            errorCol = int(match.group(2))
                        errors.append([
                            f"🔴ERROR: Connection data '{region}/{subregion}' is malformed!",
                            e,
                            errorLine.replace("\n",""),
                            ("-" * (errorCol - 3)) + "^"
                        ])
                        bail = True

                    if connectionJSON:
                        try:
                            result = validate(
                                instance=connectionJSON,
                                schema=schemas["m3"]["connection"],
                                resolver=RefResolver(
                                    base_uri=schemaURI,
                                    referrer=schemas["m3"]["connection"]
                                )
                            )
                        except JSONSchemaExceptions.ValidationError as e:
                            errors.append([
                                f"🔴ERROR: Connection data '{region}/{subregion}' doesn't validate!",
                                e,
                                "---"
                            ])
                            bail = True

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
                enemiesJSON = None

                try:
                    enemiesJSON = json.load(jsonFile)
                except json.JSONDecodeError as e:
                    jsonFile.seek(0)
                    errorLine = ""
                    errorCol = 0
                    pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                    match = re.match(pattern, str(e))
                    if match:
                        line_num = int(match.group(1))
                        for i,line in enumerate(jsonFile):
                            if i == (line_num - 1):
                                errorLine = line
                            if i > line_num:
                                break
                        errorCol = int(match.group(2))
                    errors.append([
                        f"🔴ERROR: Enemy data '{os.path.join(r,filename)}' is malformed!",
                        e,
                        errorLine.replace("\n",""),
                        ("-" * (errorCol - 3)) + "^"
                    ])
                    bail = True

                if enemiesJSON:
                    try:
                        result = validate(
                            instance=enemiesJSON,
                            schema=schema,
                            resolver=RefResolver(
                                base_uri=schemaURI,
                                referrer=schema
                            )
                        )
                    except JSONSchemaExceptions.ValidationError as e:
                        errors.append([
                            f"🔴ERROR: Enemy data '{os.path.join(r,filename)}' doesn't validate!",
                            e,
                            "---"
                        ])
                        bail = True

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
            if os.path.isdir(os.path.join(".", "region", region, subregion)):
                if "roomDiagrams" not in subregion:
                    for roomFileName in os.listdir(os.path.join(".", "region", region, subregion)):
                        if ".json" in roomFileName:
                            roomName = roomFileName.replace(".json", "")
                            print("   " + roomName)
                            with open(
                                os.path.join(
                                    ".",
                                    "region",
                                    region,
                                    subregion,
                                    roomFileName
                                ),
                                "r",
                                encoding="utf-8"
                            ) as jsonFile:
                                roomJSON = None

                                try:
                                    roomJSON = json.load(jsonFile)
                                except json.JSONDecodeError as e:
                                    jsonFile.seek(0)
                                    errorLine = ""
                                    errorCol = 0
                                    pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                                    match = re.match(pattern, str(e))
                                    if match:
                                        line_num = int(match.group(1))
                                        for i,line in enumerate(jsonFile):
                                            if i == (line_num - 1):
                                                errorLine = line
                                            if i > line_num:
                                                break
                                        errorCol = int(match.group(2))
                                    errors.append([
                                        f"🔴ERROR: Region '{region}/{subregion}/{roomName}' is malformed!",
                                        e,
                                        errorLine.replace("\n",""),
                                        ("-" * (errorCol - 3)) + "^"
                                    ])
                                    bail = True

                                if roomJSON:
                                    try:
                                        result = validate(
                                            instance=roomJSON,
                                            schema=schemas["m3"]["region"],
                                            resolver=RefResolver(
                                                base_uri=schemaURI,
                                                referrer=schemas["m3"]["region"]
                                            )
                                        )
                                    except JSONSchemaExceptions.ValidationError as e:
                                        errors.append([
                                            f"🔴ERROR: Region '{region}/{subregion}/{roomName}' doesn't validate!",
                                            e,
                                            "---"
                                        ])
                                        bail = True

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
                weaponsJSON = None

                try:
                    weaponsJSON = json.load(jsonFile)
                except json.JSONDecodeError as e:
                    jsonFile.seek(0)
                    errorLine = ""
                    errorCol = 0
                    pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                    match = re.match(pattern, str(e))
                    if match:
                        line_num = int(match.group(1))
                        for i,line in enumerate(jsonFile):
                            if i == (line_num - 1):
                                errorLine = line
                            if i > line_num:
                                break
                        errorCol = int(match.group(2))
                    errors.append([
                        f"🔴ERROR: Weapons data '{os.path.join(r,filename)}' is malformed!",
                        e,
                        errorLine.replace("\n",""),
                        ("-" * (errorCol - 3)) + "^"
                    ])
                    bail = True

                if weaponsJSON:
                    try:
                        result = validate(
                            instance=weaponsJSON,
                            schema=schemas["m3"]["weapons"],
                            resolver=RefResolver(
                                base_uri=schemaURI,
                                referrer=schemas["m3"]["weapons"]
                            )
                        )
                    except JSONSchemaExceptions.ValidationError as e:
                        errors.append([
                            f"🔴ERROR: Weapons data '{os.path.join(r,filename)}' doesn't validate!",
                            e,
                            "---"
                        ])
                        bail = True

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
        fileJSON = None

        try:
            fileJSON = json.load(jsonFile)
        except json.JSONDecodeError as e:
            jsonFile.seek(0)
            errorLine = ""
            errorCol = 0
            pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
            match = re.match(pattern, str(e))
            if match:
                line_num = int(match.group(1))
                for i,line in enumerate(jsonFile):
                    if i == (line_num - 1):
                        errorLine = line
                    if i > line_num:
                        break
                errorCol = int(match.group(2))
            errors.append([
                f"🔴ERROR: {rootType} data '{filePath}' is malformed!",
                e,
                errorLine.replace("\n",""),
                ("-" * (errorCol - 3)) + "^"
            ])
            bail = True

        if fileJSON:
            try:
                result = validate(
                    instance=fileJSON,
                    schema=schemas["m3"][rootType],
                    resolver=RefResolver(
                        base_uri=schemaURI,
                        referrer=schemas["m3"][rootType]
                    )
                )
            except JSONSchemaExceptions.ValidationError as e:
                errors.append([
                    f"🔴ERROR: {rootType} data '{filePath}' doesn't validate!",
                    e,
                    "---"
                ])
                bail = True

        if result:
            print("     " + "INVALID")
            pass
    print()

if bail:
    for errorSet in errors:
        for error in errorSet:
            pass
            # print(error)
    print("🔴Something fucked up! Bailing!")
    exit(1)
