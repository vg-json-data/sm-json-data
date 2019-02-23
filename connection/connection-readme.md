# Connection Data
This section contains data about connections between individual rooms in Super Metroid.

## Folder Structure
This folder is split-up into sub-folders, one for each main region in Super Metroid. Each region is then split into several json files; one file for room connections within each (somewhat arbitrarily-defined) sub-area, and and one more file named `intra.json` for connections that transition between sub-areas while still being within the parent region.

The root section of this folder also contains `inter.json`, which contains connections that transition between regions.

## Contents of a Connection File
Connection files follow the schema defined at `[/schema/m3-connection.schema.json](../schema/m3-connection.schema.json)`.

Each Connection file is an array of connections comprised of two nodes (each found in a Super Metroid room). Those nodes are expected to be of type `door`, `entrance` or `exit`.

### connectionType
Each connection has a `type`, which will be one of the following:
* _Horizontal Door:_ The most common type of connection. Just a horizontal door.
* _Vertical Door:_ Just a vertical door.
* _Horizontal Morph Tunnel:_ A transition between two rooms that is a Morph passage. The vanilla game has only one of those, between Main Street and Mt. Everest in Maridia.
* _Vertical Sandpit:_ Found only in Maridia, these are room transitions that are navigated by falling into quicksand. Notably, these connections can only be navigated by Samus in one direction.

### node/position
Both nodes in a connection have a position. This can be one of `left`, `right`, `top`, or `bottom`. Please note that this is the position of the node as compared to the other node in the connection, _not_ their position within their perspective room.

For example: Suppose that door 1 is the top-right room in Parlor, and door 2 is the bottom-left door in Landing Site. Those doors form a connection. Door 1 is on the right side of its room, but it is on the left side of the connection because it is on the left of door 2.