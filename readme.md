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
[A folder that details game's enemies](enemies/enemies-readme.md)
Each enemy file is an array of Enemies, and includes data about its weaknesses, immunities, damage and health, drop table, and more.
## Important concepts
This section lists key concepts and links to deeper explanations.
### Logical Requirements
[Logical requirements define what Samus needs to have and to do in order to perform actions](logicalRequirements.md)
### Requires properties
A `requires` property is present on many objects, and is always a logical requirement of its associated object.
### Unlock properties
An `unlock` property, usually tied to a node or a link, represents a logical requirement that must be fulfilled to interact with the node or to traverse the link. It differs from a `requires` property in that it only needs to be fulfilled once per game, and then the associated node or link is considered unlocked indefinitely.