# sm-json-data
## Aim of the Project

This project intends to represent Super Metroid's layout and navigation in a format that is handy for software to read and interpret. 
The aim is for it to useful for a wide variety of Super Metroid projects. Currently it is used by the following projects:

- [Map Rando](https://maprando.com), as the basis for its item placement logic.
- Total's quad-crossover randomizer (Zelda 1, Metroid 1, Link to the Past, and Super Metroid), currently in development.

## Project Structure

This project's representation of Super Metroid is split-up between different folders, each with their own data. Here's a breakdown:

### Regions

[A folder that details the game's rooms](region/region-readme.md)

### Connections

[A folder that details connections between the game's rooms](connection/connection-readme.md)

### Enemies

[A folder that details the game's enemies](enemies/enemies-readme.md)

### Weapons

[A folder that details possible types of attacks](weapons/weapons-readme.md)

### helpers.json

A file that defines helper functions. They are [logical requirement](logicalRequirements.md) expressions that are used frequently, and prevent having to copy the same thing all over the place.

### items.json

A file that contains a lot of the initial game state configuration. It contains all existing items and game flags, as well as starting items, resources, game flags, open locks, and location.

### tech.json

A file that contains techs and their [logical requirements](logicalRequirements.md). Techs are in-game techniques that players might want to be able to logically turn off.

At the first level, the techs are grouped into broad tech categories. Each category contains an array of techs.

Each tech can have logical dependencies, which are expressed in two properties `techRequires` and `otherRequires`. When a tech depends on another tech, this should be included in `techRequires`. Other requirements such as items and ammo should be included in `otherRequires`. These different types of requirements are separated because in certain situations item and ammo requirements of a tech may need to be overridden, whereas dependent tech are always included as requirements whenever using a tech. Each item in the `techRequires` should be either the name of a tech or a [`tech` logical requirement](logicalRequirements.md#tech-object), the latter being a way to express that a tech is a dependency but without inheriting its `otherRequires`. 

Each individual tech can itself have an array of extension techs. Extension techs are more complex versions of their parent tech, and this structure is intended to help with organizing techs in a more presentable manner. Extension techs are expected to logically require their parent tech, but their logical requirements can be understood without the context of the extension hierarchy, so the requirement of the parent tech should be stated explicitly in the `techRequires`.

## Important concepts

This section lists key concepts and links to deeper explanations of them.

### Logical Requirements

[Logical requirements define what Samus needs to have and to do in order to perform actions](logicalRequirements.md)

### Strats

[Strats represent a series of maneuvers that need to be executed in a room.](strats.md)
