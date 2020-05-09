# Connection Data
This section contains data about connections between individual rooms in Super Metroid.

## Folder Structure
This folder is split-up into sub-folders, one for each main region in Super Metroid. Each region is then split into several json files; one file for room connections within each (somewhat arbitrarily-defined) sub-area, and and one more file named `intra.json` for connections that transition between sub-areas while still being within the parent region.

The root section of this folder also contains `inter.json`, which contains connections that transition between regions.

## Contents of a Connection File
Connection files follow the schema defined at [/schema/m3-connection.schema.json](../schema/m3-connection.schema.json).

Each Connection file is an array of connections comprised of two nodes (each found in a Super Metroid room). Those nodes are expected to be of type `door`, `entrance` or `exit`.

### connectionType
Each connection has a `type`, which will be one of the following:
* _HorizontalDoor:_ The most common type of connection. Just a horizontal door.
* _VerticalDoor:_ Just a vertical door.
* _HorizontalMorphTunnel:_ A transition between two rooms that is a Morph passage. The vanilla game has only one of those, between Main Street and Mt. Everest in Maridia.
* _VerticalSandpit:_ Found only in Maridia, these are room transitions that are navigated by falling into quicksand. Notably, these connections can only be navigated by Samus in one direction.
* _Elevator:_ A transition between two rooms by an elevator.
* _StoryMarker:_ A transition between two rooms that is handled by story progression rather than in-room mechanics.

### direction
Each connection has a `direction` which indicates how it can be navigated. This can be one of the following:
* _Forward:_ The connection is one-way. Samus can only go from the first node to the second.
* _Backward:_ The connection is one-way. Samus can only go from the second node to the first.
* _Bidirectional:_ The connection is two-way. Samus can use it in both directions.

__Additional Considerations__

By default, a permanent grey door on one side shouldn't make a connection two-way. The absence of a door at all should. Naturally, a door that doesn't actually lead back to the same node would also make a connection one-way.

### node/position
Both nodes in a connection have a position. This can be one of `left`, `right`, `top`, or `bottom`. Please note that this is the position of the node as compared to the other node in the connection, _not_ their position within their respective room.

For example: Suppose that door 1 is the top-right door in Parlor, and door 2 is the bottom-left door in Landing Site. Those doors form a connection. Door 1 is on the right side of its room, but it is on the left side of the connection because it is on the left of door 2. So in this example, door 1 is on the left side of the connection and door 2 is on the right side.