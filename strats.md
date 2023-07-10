# Strats
Strats are a concept that encompasses performing a series of maneuvers in a room.

Strats are usually presented within an array of strats, where all individual strats are a way to attain roughly the same goal.

## Notable Strats

Some strats are flagged as "notable". this means a few things:
  * The strat's name must be unique amongst all existing strats in the project.
  * Just having the required items and the ability to perform the required techs may not be enough to execute a notable strat. It might require:
    * An increased difficulty than what the tech would typically imply
    * Knowledge of the strat or specific to the strat (such as an obscure strat or unique setup)
  * An algorithm using this project to drive its logic should consider allowing to toggle off (or on) any given notable strat.

## Logical Requirements

A strat has [logical requirements](logicalRequirements.md) which must be fulfilled in order to execute it. Those will always be specified, although they may be explicitly set to null if there are no requirements.

## Obstacles

Execution of a strat may also require an [obstacle](region/region-readme.md#obstacles) (or more) in the room to be handled in some way. Possible ways to handle an obstacle:
 * Having destroyed the obstacle previously, during the execution of a previous strat. This only works so long as Samus hasn't reset the room since.
 * Destroying the obstacle while executing the current strat, by fulfilling specific [logical requirements](logicalRequirements.md).
 * Bypassing the obstacle without destroying it, by fulfilling specific [logical requirements](logicalRequirements.md).

## Reusable Roomwide Notable Strats

Some notable strats may be very similar to each other. If similar notable strats exist in different rooms, a tech might be made for them. Otherwise, if similar notable strats exist in the same room, a [reusable notable strat](region/region-readme.md#reusable) can exist to connect them with a common name and description. This is often only the case for symmetric links with strats of notable difficulty. 

## Structure

A `strat` can have the following properties:
  * _name:_ The name of the strat.
  * _notable:_ Indicates whether the strat is notable.
  * _requires:_ The [logical requirements](logicalRequirements.md) that must be fulfilled to execute that strat.
  * _clearsObstacles:_ An array containing the ID of obstacles that will be cleared by executing this strat (if they are not already cleared).
  * _obstacles_ An array of objects, each representing an [obstacle](region/region-readme.md#obstacles) that must be destroyed (or bypassed) to execute the strat, either by fulfilling requirements or by having destroyed it previously (without exiting the room). It is preferred to
  use the `clearsObstacles` property (along with `obstaclesCleared` logical requirements) instead of this property. Each object under `obstacles` has the following properties:
    * _id:_ The in-room id of the obstacle
    * _requires:_ The [logical requirements](logicalRequirements.md) that must be fulfilled to destroy the obstacle, if it isn't already destroyed. These requirements are in addition to any requirements already tied to the `obstacle`'s definition within the room.
    * _bypass:_ Some [logical requirements](logicalRequirements.md) that can be fulfilled to bypass the obstacle, if it isn't already destroyed. Voids both the `requires` property and the requirements tied to the `obstacle`'s definition within the room. Naturally, this does not destroy the obstacle.
    * _additionalObstacles:_ An array containing the ID of additional obstacles that may not need to be destroyed to execute the strat, but that will be destroyed by destroying the containing `obstacle` via this `strat`. Additional obstacles are _not_ destroyed when bypassing the main obstacle.
  * _stratProperties:_ An array of keywords, which can be used as a requirement for strats in the destination node. These properties can be used to describe miscellaneous details (such as being in a spinjump) that will impact whether it's possible to follow-up with another specific strat.
  * _reusableRoomwideNotable:_ The name of the reusable roomwide notable strat. This must share an identical name with an entry in the `reusableRoomwideNotable` array and the other strats that are connected to this one. This is only applicable for strats where `notable` is `true`.

### Example

Here's an example of a strat:

```json
{
  "name": "Base",
  "notable": false,
  "requires": ["Morph"],
  "obstacles": [
    {
      "id": "F",
      "requires": [
        "Super",
        {"ammo": {
          "type": "Super",
          "count": 1
        }},
        {"or":[
          "Bombs",
          {"and": [
            "PowerBomb",
            {"ammo": {
              "type": "PowerBomb",
              "count": 1
            }}
          ]}
        ]}
      ]
    }
  ]
}
```
