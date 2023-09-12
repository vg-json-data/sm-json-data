# Strats
Strats are a concept that encompasses performing a series of maneuvers in a room.

Strats are usually presented within an array of strats, where all individual strats are a way to attain roughly the same goal.

## Structure

A `strat` can have the following properties:
  * _name:_ The name of the strat.
  * _notable:_ Indicates whether the strat is notable.
  * _reusableRoomwideNotable:_ The name of the reusable roomwide notable strat. This must share an identical name with an entry in the `reusableRoomwideNotable` array and the other strats that are connected to this one. This is only applicable for strats where `notable` is `true`.
  * _requires:_ The [logical requirements](logicalRequirements.md) that must be fulfilled to execute that strat.
  * _clearsObstacles:_ An array containing the ID of obstacles that will be cleared by executing this strat (if they are not already cleared).
  * _leaveWithRunway_: Indicates that this strat uses a runway connected to the destination node to leave through the door transition in a special way. For details see below.
  * _comeInWithRunway_: Indicates that this strat requires using a runway connected to the door in the previous room to enter through the door transition in a special way. For details see below.
  * _leaveCharged_: Indicates that this strat leaves through the door transition at the destination node with a shinecharge. For details see below.
  * _comeInCharged_: Indicates that this strat requires coming into the room with a shinecharge or shinespark, or by running into the room with enough runway tiles to complete a shinecharge in this room. For details see below.

These properties are described below in more detail.
### Example

Here's a simple example of a strat:

```json
{
  "name": "Base",
  "notable": false,
  "requires": ["Morph"]
}
```

## Notable Strats

Some strats are flagged as "notable". this means a few things:
  * The strat's name must be unique amongst all existing strats in the project.
  * Just having the required items and the ability to perform the required techs may not be enough to execute a notable strat. It might require:
    * An increased difficulty than what the tech would typically imply
    * Knowledge of the strat or specific to the strat (such as an obscure strat or unique setup)
  * An algorithm using this project to drive its logic should consider allowing to toggle off (or on) any given notable strat.

## Logical Requirements

A strat has [logical requirements](logicalRequirements.md) which must be fulfilled in order to execute it. These must always be specified, although they may be explicitly set to an empty array if there are no requirements.

## Clears Obstacles

Execution of a strat may have an effect of clearing one or more [obstacles](region/region-readme.md#obstacles) in the room. This can represent, for example, that certain enemies or special blocks are destroyed by executing this strat. This allows later performing strats in the room that have an [`obstaclesCleared`](logicalRequirements.md#obstaclescleared) logical requirement on the same obstacle.

## Reusable Roomwide Notable Strats

Some notable strats may be very similar to each other. If similar notable strats exist in different rooms, a tech might be made for them. Otherwise, if similar notable strats exist in the same room, a [reusable notable strat](region/region-readme.md#reusable) can exist to connect them with a common name and description. A typical example is for symmetric links with strats of notable difficulty, with one notable strat for each of two directions the room can be traversed in, and the two strats being connected by sharing the same reusable notable.

## Cross-room strats

Some strats involve leaving the room in a special way that allows a corresponding strat in the next room to be 
executed. Common examples include leaving the room with a shinespark or shinecharge, or running out of the room
in order to complete a shinecharge in the next room. Strats that exit a room in such a way are identified by specific strat properties starting with "leave", e.g. `leaveWithRunway` and `leaveCharged`. Likewise, strats that require entering the room in a special way are identified by strat properties starting with "comeIn", e.g. `comeInWithRunway` and `comeInCharged`.
### Leave With Runway

The `leaveWithRunway` property indicates that a strat exits the current room using a runway. The `leaveWithRunway` describes the geometry of the runway usable by the strat, while the specific way that the runway is used depends on the requirements in the destination room, as indicated by a `comeInWithRunway` or `comeInCharged` property in that room. `leaveWithRunway` has the following properties:

* _length:_ The number of tiles in the runway
* The following properties further define the tiles in `length`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 45 tiles where it's not relevant, that information will also be ommitted. All up/down tile counts assume Samus is running towards the door, and must be reversed when Samus is coming into the room.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.
  * _endingUpTiles:_  Indicates how many tiles slope upwards getting into the door. A stutter can't be executed on those tiles when starting a run within the room, starting from the door.
* _openEnd:_ Any runway that is used to gain momentum has two ends (although in the case of actual `runway`s one of those ends is always a door transition). An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging ( 0 or 1).

## Come In With Runway

An `comeInWithRunway` object represents the need for Samus to be able to run (or possibly jump) into the room from the neighboring room, through the node where the strat starts. It has the following properties:
* _usedTiles:_ Indicates how many tiles should be avaible for Samus to gather momentum before going into the door
* _physics:_ An optional array that indicates the acceptable physics that can be in effect at the adjacent door. If missing, all physics are acceptable. In addition to the concrete door physics
"air", "water", "lava", and "acid", the special value "normal" requires the neighboring door
to have either "air" physics or "water" physics with Gravity.
* _useFrames:_ An optional property that indicates the number of frames Samus should expect to spend at the adjacent door, being subjected to the door (acid/lava) and room (heat) environments there if applicable.
* _overrideRunwayRequirements:_ An optional boolean (if missing, assume false). If true, indicates the the requirements on the runway itself don't need to be fulfilled.

## Leave Charged

Represents the possibility for Samus to charge a shinespark without using the door's runway, and then carry that charge through the door. This is an array of `canLeaveCharge` objects which have the following properties:
* _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
* The following properties further define the tiles in `usedTiles`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 33 tiles where it's not relevant, that information will also be ommitted. All up/down tile counts assume Samus is running in the most convenient direction for the associated strats.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.
* _openEnd:_ Any runway that is used to gain momentum has two ends. An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (between 0 and 2).
* _framesRemaining:_ The maximum number of frames that Samus should be expected to have left on the shinespark charge when leaving the room. A value of 0 indicates that she should only be expected to shinespark through the door.

Note: this node property is deprecated, and the [strat property](../strats.md) `leaveCharged` should be used instead.

__Additional considerations__

Generating a shinespark charge using the door's runway (assuming the runway has enough tiles for it), and carrying it into the next door, is implicitly assumed to be possible. As such, that is never explicitly defined in a `canLeaveCharged` object. The number of frames remaining in that charge will be:
* 180 frames if there's a usable runway on the other side
* Roughly 175 frames if there's no usable runway on the other side (meaning the charge must be stored while entering the door)

Much like using runways, a `canLeaveCharged` can only be executed if the associated door can be interacted with.


## Come In Charged
  * _leaveWithRunway_: Indicates that this strat uses a runway connected to the destination node to leave through the door transition in a special way. For details see below.
  * _comeInWithRunway_: Indicates that this strat requires using a runway connected to the door in the previous room to enter through the door transition in a special way. For details see below.
  * _leaveCharged_: Indicates that this strat leaves through the door transition at the destination node with a shinecharge. For details see below.
  * _comeInCharged_: Indicates that this strat requires coming into the room with a shinecharge or shinespark, or by running into the room with enough runway tiles to complete a shinecharge in this room. For details see below.
