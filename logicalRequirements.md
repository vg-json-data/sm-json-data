# Logical Requirements
Logical requirements are an important part of this project. They are used to represent any and all conditions Samus needs to fulfill to be able to perform actions. This can include having items, performing techs, and consuming ammo or health.

## Structure
A logical requirement is an array of logical elements, which are implicitly linked by a logical AND. Those logical elements can be a number of things:
* _The name of a helper._ Helpers are defined in `[helpers.json](helpers.json)` and they themselves represent a logical requirement. Those exist to reduce duplication and make logical requirements more readable.
* _The name of a tech._ Techs are defined in `[tech.json](tech.json)`.  Those represent a technique that players can perform, which may also imply logical requirements of their own.
* _The name of an item._ Those are defined in `[items.json](items.json)`.
* _The name of a game flag._ Those are defined in `[items.json](items.json)`, and are used to represent game events such as defeating a boss, or breaking the Maridia tube.
* _Structural objects._ Those exist to make it possible to group together logical elements. Those include:
  * _or:_ An `or` object contains an array of logical elements, but is fulfilled as soon as at least one of those is met.
  * _and:_ An `and` object contains an array of logical elements, and is fulfilled only if all of those are met.
  * _not:_ A `not`object contains an array of logical elements, and is fulfilled only if none of those are met.
* More complex objects which will be defined in their own sub-sections

### adjacentRunway object
An `adjacentRunway`object represents the need for Samus to be able to run (or possibly jump) into the room from an adjacent room. It has the following properties:
* _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
* _usedTiles:_ Indicates how many tiles should be avaible for Samus to gather momentum before going into the door

Please refer to the section about runways in [the Region documentation](region/region-readme.md) for a more detailed explanation of runways.

### canComeInCharged object
A `canComeInCharged` object represents the need to charge a shinespark in an adjacent room, or to initiate a shinespark in an ajacent room and into the current room. It has the following properties:
 * _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
 * _framesRemaining:_ Indicates the minimum number of frames Samus needs to have left, upon entering the room, before the shinespark charge expires. A value of 0 indicates that shinesparking through the door works.
* _shinesparkFrames:_ Indicates how many frames the shinespark that will be used lasts. This can be 0 in cases where only the blue suit is needed. During a shinespark, Samus is damaged by 1 every frame, and being able to spend that health is part of of being able to fulfill a `canComeInCharged` object.

__Additional considerations:__
* A `canComeInCharged` object implicitly requires the Speed Booster.
* A `canComeInCharged` object implicitly requires the `canShinespark` tech if it has more than 0 `shinesparkFrames`.
* A `canComeInCharged` object is implicitly fulfilled if the runways on the two sides of the door combine into a large enough runway to charge a spark.
The number of framesRemaining in that case is:
  * 180 if there is a usable runway in the destination room
  * Roughly 175 if there is no usable runway in the destination room

Please refer to the section about runways in [the Region documentation](region/region-readme.md) for a more detailed explanation of runways and how to combine them.

### canShineCharge object
A `canShineCharge` object represents the need for Samus to be able to charge a shinespark within the current room. It has the following special properties:
* _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
* _openEnd:_ Any runway that is used to gain momentum has two ends. An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (between 0 and 2).
* _shinesparkFrames:_ Indicates how many frames the shinespark that will be used lasts. This can be 0 in cases where only the blue suit is needed. During a shinespark, Samus is damaged by 1 every frame, and being able to spend that health is part of of being able to fulfill a `canShineCharge` object.

__Additional considerations:__
* A `canShineCharge` object implicitly requires the Speed Booster.
* A `canShineCharge` object implicitly requires the `canShineCharge` tech if it has more than 0 `shinesparkFrames`.

### canVisitNode object
A `canVisitNode` object represents the need for Samus to be able to go to another node, in order to do something unspecified that is required to fulfill requirements. It has the following special properties:
* _nodeid:_ The ID of the node, inside the same room
* _persistence:_ Indicates what can cause Samus' visit to the node to no longer fulfill the `canVisitNode` requirements. Can have the following values:
  * _global:_ Access by Samus at any time will fulfill the requirements
  * _room:_ Samus must be able to access the node during the current visit to the room. This usually involves clearing obstacles that will respawn on re-entry.

__Additional considerations:__ If `canVisitNode` for node `n` is part of the conditions on a link that goes to node `n`, that is not a tautology. It is fulfilled only if there is another way to visit the node that respects the `persistence`.
### cost object
A `cost` object represents the need for Samus to spend resources (ammo or health). It is structured as an array of objects. Each object in a `cost` array has one property, with a name and a value. Possible property names are:
* _acidFrames:_ Represents the need for Samus to spend time (measured in frames) in a pool of acid. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for acid is 6 damage every 4 frames, halved by Varia (3 damage every 4 frames), and halved again by Gravity Suit (3 damage every 8 frames).
* _ammo:_ Represents the need for samus to spend a fixed amount of ammo. The value for an `ammo` object is another object with the following properties:
  * _type:_ The type of ammo that is being spent, such as "PowerBomb" or "Super"
  * _count:_ The amount of that ammo type which is being spent
* _enemyDamage:_ Represents the need for Samus to intentionally take damage from an enemy. This is meant to be converted to a flat health value based on item loadout. The value for an `enemyDamage` object is another object with the following properties:
  * _enemy:_ The ID of the enemy that will damage Samus
  * _type:_ The name of the attack that Samus will take damage from
  * _hits:_ The number of hits Samus will take from that enemy
* _heatFrames:_ Represents the need for Samus to spend time (measured in frames) in a heated room. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for heated rooms is 1 damage every 4 frames, negated by Varia or Gravity Suit.
* _lavaFrames:_ Represents the need for Samus to spend time (measured in frames) in a pool of lava. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for lava is 2 damage every 4 frames, halved by Varia, and negated by Gravity Suit.
* _spikeHits:_ Represents the need for Samus to intentionally take a number of hits from spikes. This is meant to be converted to a flat health value based on item loadout. The vanilla damage per spike hit is 60 with Power Suit, 30 with Varia, and 15 with Gravity Suit.
* _thornHits:_ Represents the need for Samus to intentionally take a number of hits from the game's weaker spikes. This is meant to be converted to a flat health value based on item loadout. The vanilla damage per thorn hit is 16 with Power Suit, 8 with Varia, and 4 with Gravity Suit.
### resetRoomAtNode object
A `resetRoomAtNode` object represents the need for Samus to be able to exit and re-enter the room at one of the specified nodes to perform a strat. This is to guarantee that the room has been reset. It should be expected that entering the room at one of the specified nodes and making a beeline to the node where the `resetRoomAtNode` is present will fulfill the object's requirement.

This object takes the form of an array of node IDs. Any of the nodes in the array can be used to fulfill the requirement.