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
* _Bidirectional:_ The connection is two-way. Samus can use it in both directions.

__Additional Considerations__

By default, a permanent gray door on one side shouldn't make a connection two-way. The absence of a door at all should. Naturally, a door that doesn't actually lead back to the same node would also make a connection one-way.

### node/position
Both nodes in a connection have a position. This can be one of `left`, `right`, `top`, or `bottom`. Please note that this is the position of the node as compared to the other node in the connection, _not_ their position within their respective room.

For example: Suppose that door 1 is the top-right door in Parlor, and door 2 is the bottom-left door in Landing Site. Those doors form a connection. Door 1 is on the right side of its room, but it is on the left side of the connection because it is on the left of door 2. So in this example, door 1 is on the left side of the connection and door 2 is on the right side.

## Logical requirements for connections

A connection describes how two rooms connect, but it is important to note that the existence of a connection does *not* imply that it is logically free for Samus to traverse that connection from one door/exit node to the other door/entrance node. The logical ability to traverse connections is described by entrance conditions and exit conditions on the strats in each room. This is necessary for several reasons:

  - Some strats require entering or exiting the room in a certain way, e.g. with certain amount of speed, in a certain pose, or in a certain position.
  - Some doors require taking unavoidable damage on entry, or have certain item or tech requirements to avoid such damage.
  - Some doors put Samus in a position where returning back through the door is not possible without certain items and/or tech. This can be true even for "Bidirectional" connections.
  
A connection can only logically be traversed by a pair of strats, one with an exit condition, and one in the opposite room with a matching entrance condition. This is true even for "normal" ways of entering and exiting rooms, which are handled by the `leaveNormally` and `comeInNormally` exit and entrance conditions. 

One practical way to interpret this is as follows:

  - For each door, there is an implicit "exit" node for each possible exit condition through that door. A strat with an `exitCondition` should be treated as ending at the corresponding implicit exit node, rather than ending at the regular door node within the room.
  - Likewise, for each door, there is an implicit "entrance" node for each possible entrance condition through that door. A strat with an `entranceCondition` should be treated as starting at the corresponding implicit entrance node, rather than starting at the regular door node within the room.
  - For each matching pair of `exitCondition` and `entranceCondition` on opposite ends of a connection, an implicit strat should be considered to exist, connecting the exit node in one room to the entrance node in the other, including any implicit requirements associated with the given exit and entrance conditions.

Exit conditions and entrance conditions are [described in detail here](../strats.md#cross-room-strats). See also [implicit exit and entrance strats](../strats.md#implicit-entrance-and-exit-strats).