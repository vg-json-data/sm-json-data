# sm-json-data
## Aim of the Project

This project intends to represent Super Metroid's layout and navigation in a format that is handy for software to read and interpret. The primary goal is to eventually be used by the SMZ3 combo randomizer (https://github.com/tewtal/alttp_sm_combo_randomizer) to build its logic, expanding that project's possibilities.

However, the intent is for the data model to also be usable for other projects related to Super Metroid.

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

## Important concepts

This section lists key concepts and links to deeper explanations of them.

### Logical Requirements

[Logical requirements define what Samus needs to have and to do in order to perform actions](logicalRequirements.md)

### Strats

[Strats represent a series of maneuvers that need to be executed in a room.](strats.md)
