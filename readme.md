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
## Project Definitions
This section defines concepts that are constant across the project. This includes properties that many different objects can have.
### Logical Requirements
Logical requirements are a representation of what combination of items and techniques allows Samus to perform various actions. They are found all over the project (often as a `requires` or `unlock` property). They are represented as an array whose elements are implicitly linked by a logical AND; those logical elements can be a number of things:
* _The name of a helper._ Helpers are defined in helpers.json and they themselves represent a logical requirement. Those exist to reduce duplication and make logical requirements more readable.
* _The name of a tech._ Techs are defined in tech.json.  Those represent a technique that players can perform, which may also imply logical requirements of their own.
* _The name of an item._ Those are defined in items.json.
* _The name of a game flag._ Those are defined in items.json, and are used to represent game events such as defeating a boss, or breaking the Maridia tube.
* _Structural objects._ Those exist to make it possible to group together logical elements. Those include:
  * _or:_ An `or` object contains an array of logical elements, but is fulfilled as soon as at least one of those is met.
  * _and:_ An `and` object contains an array of logical elements, and is fulfilled only if all of those are met.
  * _not:_ A `not`object contains an array of logical elements, and is fulfilled only if none of those are met.
* More complex objects which will be defined in their own sub-sections
#### Logical element: canComeInCharged object
A `canComeInCharged` object represents the need to charge a shinespark in an adjacent room, or to initiate a shinespark in an ajacent room and into the current room. It has the following properties:
 * _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
 * _framesRemaining:_ Indicates the minimum number of frames Samus needs to have left, upon entering the room, before the shinespark charge expires. A value of 0 indicates that shinesparking through the door works.

 __Additional considerations:__ A `canComeInCharged` object implicitly requires the Speed Booster. It is also implicitly fulfilled (with 180 frames remaining, or roughly 175 frames if 100% of the combined runway is in the adjacent room) if the runways on the two sides of the door combine into a large enough runway to charge a spark.
 #### Logical element: adjacentRunway object
 An `adjacentRunway`object represents the need for Samus to be able to run (or possibly jump) into the room from an adjacent room. It has the following properties: 
 * _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
 * _usedTiles:_ Indicates how many tiles should be avaible for Samus to gather momentum before going into the door
 #### Logical element: canShineCharge object
 A `canShineCharge` object represents the need for Samus to be able to charge a shinespark within the current room. It has the following special properties:
 * _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
 #### Logical element: canVisitNode object
 A `canVisitNode` object represents the need for Samus to be able to go to another node, in order to do something unspecified that is required to fulfill requirements. It has the following special properties:
 * _nodeid:_ The ID of the node, inside the same room
 * _persistence:_ Indicates what can cause Samus' visit to the node to no longer fulfill the `canVisitNode` requirements. Can have the following values:
   * _global:_ Access by Samus at any time will fulfill the requirements
   * _room:_ Samus must be able to access the node during the current visit to the room. This usually involves clearing obstacles that will respawn on re-entry.

 __Additional considerations:__ If `canVisitNode` for node `n` is part of the conditions on a link that goes to node `n`, that is not a tautology. It is fulfilled only if there is another way to visit the node that respects the `persistence`.
 #### Logical element: canTraverseLink object
 A `canTraverseLink` object represents the possibility for Samus to have arrived somewhere by following the link described in the object. It is fulfilled if Samus is able to reach the startNode, and also to fulfill the link's `requires`and `unlock` requirements. It is meant to represents situations where an obstacle has already been destroyed by Samus on the way in. It has the following special properties:
 * _fromNode_: A node that is the starting point of the described link, and which must be accessible in order for the `canTraverseLink` object to be fulfilled
 * _toNode_: A node that is the end point of the described link
 ### Requires properties
 A `requires` property is present on many objects, and is always a logical requirement of its associated object.
 ### Unlock properties
 An `unlock` property, usually tied to a node or a link, represents a logical requirement that must be fulfilled to interact with the node or to traverse the link. It differs from a `requires` property in that it only needs to be fulfilled once per game, and then the associated node or link is considered unlocked indefinitely.