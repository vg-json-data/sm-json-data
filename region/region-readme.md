# Region Data
This section contains data about individual rooms in Super Metroid, as well as navigation logic within the rooms.

## Folder Structure
This folder is split up into sub-folders, one for each main region in Super Metroid. Each region is then split into several `json` files, one for each (somewhat arbitrarily-defined) sub-area. Please note that there is one exception to this rule: Inner Maridia is considered as one large sub-area, but was still further split-up into three region files to keep their size manageable.

Region sub-folders also contain a folder called `roomDiagrams` which contains an image for most individual rooms with more than a few nodes, to show how the nodes are placed and connected within that room.

## Contents of a Region File
Region files follow the schema defined at [/schema/m3-region.schema.json](../schema/m3-region.schema.json).

Each region file is an array of Super Metroid rooms. Rooms contain the following elements:

### Room Environments
A room has a mandatory array of environments. Those environments describe some conditions that apply to the entire room. Only one environment should be applicable at any given time, but that environment can depend on which node Samus enters from. Has the following properties:
* _heated:_ Indicates whether the environment is heated, i.e. whether Samus will take gradual damage without heat protection.
* _entranceNodes:_ Indicates this environment is active when Samus entered from which nodes. If omitted, the environment is applicable at all times.

### Nodes
A room has an array of nodes. Nodes represent points of interest in a room. Those are usually doors, items, bosses, or places where a game flag can be triggered. They can have the following types:
* _door:_ A node that is connected to another node in another room, typically via a two-way connection
* _entrance:_ A node that is connected to another node in another room, in a one-way connection. This node can only be used to enter the room it's in, not exit it. Please note that this is not intended to represent gray doors, even those that can never be unlocked. Rather, this is for an entrance node with no exit trigger, such a sand chute at the top of a room.
* _exit:_ A node that is connected to another node in another room, in a one-way connection. This node can only be used to exit the room it's in, not enter it
* _item:_ A node that represents an item that can be picked up
* _junction:_ A node that has no special in-game meaning. Its purpose is to represent a specific spot in a room, to which it would make sense to connect other nodes. They are often used to reduce logic duplication by preventing the very same requirements from having to be repeated in several strats that cross through the same section of a room. In some cases, junctions represent not only a location in a room, but also a condition (e.g. being at a location with specific enemy positioning or Samus is in a specific state).
* _utility:_ A node that represents some kind of utility station, such as a refill station or a save capsule.

A node's `name` property has to be unique across the entire model.

Some node properties are self-explanatory, while others require additional definition:

#### doorEnvironments
Door nodes have an array of environments, much like rooms. Those environments describe some conditions that don't always apply to the entire room, but instead can vary with each door. Only one environment should be applicable at any given time, but that environment can depend on which node Samus enters from. Has the following properties:
* _physics:_ Indicates what kind of physics are in play at this door. Possible values are:
  * air
  * water
  * lava
  * acid
  * previousRoom: This means that no actual movement happens in this room, and all physics and momentum actually carry over from the previous room.
* _entranceNodes:_ Indicates this environment is active when Samus entered from which nodes. If omitted, the environment is applicable at all times.

__Additional considerations__

Door environments are mandatory on door nodes (except elevators). They are forbidden on all nodes where they're not mandatory.

#### useImplicitDoorUnlocks

By default every door node has an implicit strat from the node to itself, for [unlocking the door](../strats.md#implicit-unlock-strats) in a standard way. This can be disabled by setting the node property `useImplicitDoorUnlocks` to false.

#### isDoorImmediatelyClosed

Most doors have a closing animation that occurs when entering through them. However, certain doors are immediately closed when the room is loaded. When entering through such a door in direct G-mode, the door will be closed, making it not possible to return back through the door without first exiting G-mode. It would also not be possible to get stuck inside the door shell using an X-ray climb setup.

#### utility
The `utility` property is an array of utility functions available to Samus at a node. Those include saving, map stations, as well as resource refills. Possible utilities are:
* _save_
* _missile_
* _super_
* _powerbomb_
* _energy:_ Note that this excludes reserve tanks
* _reserve:_ Note that this excludes regular energy. If a node can refill reserves as well as energy, it will have both `energy` and `reserve`
* _map_

#### locks
The `locks` property is an array that contains different ways a node can be locked, and the corresponding way it can be unlocked. Each object in the `locks` property has some properties of its own:
* _lockType:_ An enum indicating the type of lock. It gives a basic idea of what kind of thing has to be done to open this lock. Possible lock types are:
  * _bossFight:_ Meant for locks on actual boss nodes, indicates that the node is unlocked by performing the boss fight.
  * _coloredDoor:_ A door lock that is opened by spending ammo on a door. Includes eye doors.
  * _cutscene:_ A lock that is essentially opened by just waiting in the room.
  * _escapeFunnel:_ Like permanent locks, those are locks that cannot be undone. Escape funnel locks, specifically, are activated by the escape sequence and used to force the player to go to the ship.
  * _gameFlag:_ Indicates a lock that is opened when a game flag has been activated. Most locks that are unlocked by killing a boss are this type, rather than `bossFight`.
  * _killEnemies:_ A lock that is unlocked by killing enemies in a room. This excludes doors in boss rooms, which are `gameFlag` locks.
  * _permanent:_ A lock that can never be unlocked.
* _lock:_ The `lock` property lists [logical requirements](../logicalRequirements.md) that must be fulfilled in order for the node to be locked. If this is missing, the node is considered initially locked at game start.
* _name:_ A name that identifies the lock. This name must be unique across all locks in the model.
* _unlockStrats:_ The `unlockStrats` property is an array of [strats](../strats.md), each of which may be executed in order to unlock this specific lock. Unlocking a node makes it possible to interact with the node until the end of the game.
* _yields:_ Exactly like the `yields` property found directly on a node, the `yields` property is an array of game flags. However, in this case those flags are activated when unlocking a lock.

__Additional considerations__

None of the locks must be active for Samus to be able to properly interact with a node. Note that unlike traversing strats, `unlocking` a lock is an action that needs to be done only once. Interacting with a node, which requires no locks to be active, can take several forms such as:
* Using a door node to go to another room
* Picking up the item at an item node
* Using any `utility` that is present at a node

#### viewableNodes
The `viewableNodes` property is an array of objects, each of which describing how an item node within the room can be viewed from the current node without having to reach the item. It has two properties:
* _id:_ The in-room ID of the item node that can be viewed
* _strats:_ An array of [strats](../strats.md), each of which may be executed in order to view the item node. If none of the strats can be executed, the item cannot be viewed.

#### yields
The `yields` property is an array of game flags that are activated when interacting with a node. Just like interacting with any other node type, this requires having no active lock on the node and fulfilling any interaction requirements.

#### farmCycleDrops
A `farmCycleDrops` is an array of objects describing a set of enemies that can be farmed as part of executing this strat. Each object has the following properties:

* _enemy_: The name of an enemy from which drops can be collected.
* _count_: The amount of drops which can be collected from the given enemy, during one cycle.

A strat with this property should begin and end at the same node, representing one cycle of a farm. The strat should include `cycleFrames` requirements to specify the amount of time required to execute the farm cycle. If the farm involves resetting the room in order to respawn the enemies after collecting their drops, then this should be indicated by including a `resetRoom` requirement, in which case any requirements needed for reaching the door and returning to the starting/ending node should be included. Only in-room time should be included; i.e. time spent in the door transition or in the other room on the other side of the door should not be included. Only frames that are part of the farming cycle need to be included in `cycleFrames`; i.e., in a case where the starting/ending node may not precisely coincide with the farm location, frames would not need to be included for reaching the farm from the starting node on the first cycle, nor for returning to the ending node after the last cycle.

#### twinDoorAddresses
A door node is considered to have a twin when the game has two sections that are visually identical, but are separate in the game's memory. The player will not know during gameplay that the two twin doors aren't actually the same. Both twins lead to the same destination door, but that destination door only ever leads to one of the twins, with the other only being reachable from within its room. An example (and the only known one currently) is East Pants Room, which has a another version of itself within Pants Room.

When a door has a twin, that twin will not be in the JSON model; but knowing the existence of that other door (and its address) can be useful when reorganizing connections between doors.

Each twin door address will be an object with two properties:
* _doorAddress:_ The in-game address of the room in which the twin is found.
* _roomAddress:_ The in-game address of the twin door itself.

### Obstacles
A room can have an array of obstacles. Obstacles are barriers that can be destroyed or opened up to make a section of a room passable, and which stay destroyed or open until the room is reset. The main uses of obstacle are:
* To allow proper ammo requirements when passing somewhere multiple times but only needing to break the obstacle once
* To represent things that can be opened only from one direction, but then can be freely passed once opened (e.g. crumble blocks, green and blue gates)

Clearing an obstacle is done by executing a [strat](../strats.md) that includes the obstacle in its `clearsObstacles` property. An `obstaclesCleared` [logical requirement](../logicalRequirements.md) is used to represent that an obstacle must be already cleared in order to execute a strat.

__Additional considerations__ 

Obstacles are not systematically represented in the model. They are put in as needed, in rooms where there could be a reason to pass by an obstacle twice without exiting.

### Enemies
A room can have an array of enemies. This is the list of enemies that may be present in the room. They may be relevant for farming purposes, or to get an assessment of the danger posed by the enemies in the room. Each `enemy` object can have the following properties:
* _id:_ A short identifier for an `enemy` object that is only unique within the room.
* _groupName:_ A name for an `enemy` object, that is unique across the entire game.
* _enemyName:_ The name of the enemy. This must be the name of an enemy in the [enemies folder](../enemies/enemies-readme.md).
* _quantity:_ How many enemies correspond to the description made by this `enemies` object. Note that if this is an enemy that respawns, it should be grouped according to how many can be farmed simultaneously, rather than the total number of enemies in a room or node. Accordingly, as many groups as needed should be used.
* _homeNodes:_ An array of nodes through which the enemy can naturally roam. A player can expect to encounter that enemy in any of those nodes. Mutually exclusive with `betweenNodes`.
* _betweenNodes:_ An array of exactly two nodes, indicating that the enemy is encountered while travelling between those two nodes. Mutually exclusive with `homeNodes`.
* _spawn:_ The `spawn` property lists [logical requirements](../logicalRequirements.md) that must be fulfilled in order for the enemy to spawn in the room. If this is missing, the enemy can spawn in the room from game start.
* _stopSpawn:_ The `stopSpawn` property lists [logical requirements](../logicalRequirements.md) that must be fulfilled in order for the enemy to no longer spawn in the room. If this is missing, the enemy will never stop spawning in the room after its spawn conditions have been met.

### Notable Strats
Some strats are flagged as "notable". this means a few things:
  * Just having the required items and the ability to perform the required techs may not be enough to execute a notable strat. It might require:
    * A higher difficulty than what the tech would typically imply
    * Knowledge of the strat or specific to the strat (such as an obscure strat or unique setup)
  * An algorithm using this project to drive its logic should consider allowing to toggle off (or on) any given notable strat.
