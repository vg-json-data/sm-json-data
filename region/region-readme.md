# Region Data
This section contains data about individual rooms in Super Metroid, as well as navigation logic within the rooms.

## Folder Structure
This folder is split up into sub-folders, one for each main region in Super Metroid. Each region is then split into several json files, one for each (somewhat arbitrarily-defined) sub-area. Please note that there is one exception to this rule: Inner Maridia is considered as one large sub-area, but was still further split-up into three region files to keep their size manageable.

Region sub-folders also contain an image for most individual rooms with more than a few nodes, to show how the nodes are placed and connected within that room.

The root section of this folder also contains cleanup.json, which has miscellaneous rooms which were missing from the wiki. These may be moved into the proper region at some point.

## Contents of a Region File
Region files follow the schema defined at /schema/m3-region.schema.json.

Each region file is an array of Super Metroid rooms. Rooms contain the following elements:

### Nodes
Nodes represent points of interest in a room. They can have the following types: Those are usually doors, items, bosses, or places where a game flag can be triggered.
* _door:_ A node that is connected to another node in another room, typically via a two-way connection
* _entrance:_ A node that is connected to another node in another room, in a one-way connection. This node can only be used to enter the room it's in, not exit it
* _exit:_ A node that is connected to another node in another room, in a one-way connection. This node can only be used to exit the room it's in, not enter it
* _event:_ A node where an event that triggers game flags can happen
* _item:_ A node that represents an item that can be picked up
* _junction:_ A node that has no special in-game meaning. Its purpose is to join together several nodes that aren't separated by any obstacles. They are often used to reduce logic duplication by preventing obstacles from having to be repeated in several similar links.

Some node properties are self-explanatory, while others require additional definition:
#### sparking/runways
Represents an array of runways connected to a door. A runway is a series of tiles directly connected to a door, which Samus can use to gather momentum and carry it into the next room. Runways have the following special properties:
* _length:_ The number of tiles in the runway

__Additional considerations:__ Runways on both sides of a door are meant to be combined when determining how much room is available to charge a shinespark. When calculating this, the longest available runway in the origin room can be used, but _only a runway with no requirements in the destination room_ should be used (No time to open up a runway while charging a spark). Additionnally, because of how door transitions work, _the first runway tile when entering a room is not used to gain momentum_. So, two runways of 10 tiles each must only add up to a 19-tile runway.
#### sparking/canLeaveCharged
Represents the possibility for Samus to charge a shinespark without using the door's runway, and then carry that charge through the door. Has the following special properties:
* _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
* _framesRemaining:_ The maximum number of frames that Samus should be expected to have left on the shinespark charge when leaving the room. A value of 0 indicates that she should only be expected to shinespark through the door.

__Additional considerations:__ Generating a shinespark charge using the door's runway (assuming the runway has enough tiles for it), and carrying it into the next door, is implicitly assumed to be possible (with 180 framesRemaining if there's a runway with a positive length on the other side, and with roughly 175 frames remaining otherwise). As such, that is never explicitly defined in a `canLeaveCharged` object.
### Links
Links define how Samus can navigate within a room. Each link is a unidirectional path that can take Samus from one node to another. Links often have logical requirements.