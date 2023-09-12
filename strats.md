# Strats
Strats are a concept that encompasses performing a series of maneuvers in a room.

Strats are usually presented within an array of strats, where all individual strats are a way to attain roughly the same goal.

## Structure

A `strat` can have the following properties:
  * _name:_ The name of the strat.
  * _notable:_ Indicates whether the strat is notable.
  * _requires:_ The [logical requirements](logicalRequirements.md) that must be fulfilled to execute that strat.
  * _clearsObstacles:_ An array containing the ID of obstacles that will be cleared by executing this strat (if they are not already cleared).
  * _leaveWithRunway_: Indicates that this strat involves using a runway connected to the destination node to leave through the door transition in a special way. For details see below.
  * _comeInWithRunway_: Indicates that this strat requires using a runway connected to the door in the previous room to enter through the door transition in a special way. For details see below.
  * _leaveCharged_: Indicates that this strat involves leaving through the door transition at the destination node with a shinecharge. For details see below.
  * _comeInCharged_: Indicates that this strat requires coming into the room with a shinecharge or shinespark, or by running into the room with enough runway tiles to complete a shinecharge in this room. For details see below.
  * _reusableRoomwideNotable:_ The name of the reusable roomwide notable strat. This must share an identical name with an entry in the `reusableRoomwideNotable` array and the other strats that are connected to this one. This is only applicable for strats where `notable` is `true`.

### Example

Here's an example of a strat:

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

A strat has [logical requirements](logicalRequirements.md) which must be fulfilled in order to execute it. Those will always be specified, although they may be explicitly set to an empty array if there are no requirements.

## Obstacles

Execution of a strat may also require an [obstacle](region/region-readme.md#obstacles) (or more) in the room to be handled in some way. Possible ways to handle an obstacle:
 * Having destroyed the obstacle previously, during the execution of a previous strat. This only works so long as Samus hasn't reset the room since.
 * Destroying the obstacle while executing the current strat, by fulfilling specific [logical requirements](logicalRequirements.md).
 * Bypassing the obstacle without destroying it, by fulfilling specific [logical requirements](logicalRequirements.md).

## Reusable Roomwide Notable Strats

Some notable strats may be very similar to each other. If similar notable strats exist in different rooms, a tech might be made for them. Otherwise, if similar notable strats exist in the same room, a [reusable notable strat](region/region-readme.md#reusable) can exist to connect them with a common name and description. This is often only the case for symmetric links with strats of notable difficulty. 
