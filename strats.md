# Strats
Strats are a concept that encompasses performing a series of maneuvers in a room.

Strats are usually presented within an array of strats, where all individual strats are a way to attain roughly the same goal.

## Structure

A `strat` can have the following properties:
  * _name:_ The name of the strat.
  * _notable:_ Indicates whether the strat is notable.
  * _reusableRoomwideNotable:_ The name of the reusable roomwide notable strat. This must share an identical name with an entry in the `reusableRoomwideNotable` array and the other strats that are connected to this one. This is only applicable for strats where `notable` is `true`.
  * _entranceCondition_: Indicates that this strat requires entering through the door transition in a special way, combining with a strat in the previous room.
  * _requires:_ The [logical requirements](logicalRequirements.md) that must be fulfilled to execute that strat.
  * _exitCondition_: Indicates that this strat leaves through the door transition in a special way that combines with a strat in the next room. 
  * _clearsObstacles:_ An array containing the ID of obstacles that will be cleared by executing this strat (if they are not already cleared).
  
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
  * The strat's name must be unique among all existing strats in the project.
  * Just having the required items and the ability to perform the required techs may not be enough to execute a notable strat. It might require:
    * A higher difficulty than what the tech would typically imply
    * Knowledge of the strat or specific to the strat (such as an obscure strat or unique setup)
  * An algorithm using this project to drive its logic should consider allowing to toggle off (or on) any given notable strat.

## Logical Requirements

A strat has [logical requirements](logicalRequirements.md) which must be fulfilled in order to execute it. These must always be specified, although they may be explicitly set to an empty array if there are no requirements.

## Clears Obstacles

Execution of a strat may have an effect of clearing one or more [obstacles](region/region-readme.md#obstacles) in the room. This can represent, for example, that certain enemies or special blocks are destroyed by executing this strat. This allows later performing strats in the room that have an [`obstaclesCleared`](logicalRequirements.md#obstaclescleared) logical requirement on the same obstacle.

## Reusable Roomwide Notable Strats

Some notable strats may be very similar to each other. If similar notable strats exist in different rooms, a tech might be made for them. Otherwise, if similar notable strats exist in the same room, a [reusable notable strat](region/region-readme.md#reusable) can exist to connect them with a common name and description. A typical example is for symmetric links with strats of notable difficulty, with one notable strat for each of two directions the room can be traversed in, and the two strats being connected by sharing the same reusable notable.

## Cross-room strats

Some strats involve leaving the room in a special way that allows a corresponding strat in the next room to be executed. Common examples include leaving the room with a shinespark or shinecharge, or running out of the room in order to complete a shinecharge in the next room. Strats that exit a room in such a way are identified by a strat property `exitCondition`, containing a property describing the type of exit condition, such as `leaveWithRunway`, `leaveShinecharged`, or `leaveWithSpark`. Likewise, strats that require entering the room in a special way are identified by a strat property `entranceCondition`, containing a property describing the type of entrance condition required, such as `comeInRunning`, `comeInShinecharged`, or `comeInWithSpark`.

## Exit conditions

In all strats with an `exitCondition`, the `to` node of the strat must be a door node. If the door has a lock on it, it is required to be unlocked before a strat with an `exitCondition` can be executed: door lock bypass strats cannot be combined with strats having an `exitCondition`. An `exitCondition` object must contain exactly one property, which indicates the type of exit condition provided by the strat:

- _leaveWithRunway_: This indicates that a runway of a certain length is connected to the door, with which Samus can gain speed and run or jump through the door, among other possible actions. 
- _leaveShinecharged_: This indicates that it is possible to charge a shinespark and leave the room with a certain amount of time remaining on the shinecharge timer (e.g., so that a shinespark can be activated in the next room). 
- _leaveWithSpark_: This indicates that it is possible to shinespark through the door transition.

Each of these properties is described in more detail below.

### Leave With Runway
A `leaveWithRunway` object indicates that a strat exits the current room using a runway. The `leaveWithRunway` exit condition is unique in that it describes available geometry rather than a specific way to leave the room. This is done in order to reduce the amount of redundant boilerplate that would otherwise be required, since every door node in the game will have at least one strat with `leaveWithRunway`. The specific way that the runway is used depends on the entrance condition in the destination room.

A `leaveWithRunway` exit condition can satisfy the following entrance conditions in the next room: `comeInRunning`, `comeInJumping`, `comeInShinecharging`, `comeInShinecharged`, `comeInWithSpark`, `comeInWithBombBoost`, `comeInWithStutter`, and `comeInWithDoorStuckSetup`.

`leaveWithRunway` has the following properties:

* _length:_ The number of tiles in the runway. This length should not include the transition tile, but it should include the door shell tile if applicable.
* _openEnd:_ Any runway that is used to gain momentum has two ends (although in this case one of those ends is always a door transition). An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (0 or 1).
* The following properties further define the tiles in `length`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 45 tiles where it's not relevant, that information will also be omitted. All up/down tile counts assume Samus is running towards the door.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.

In most cases, what matters is the effective runway length (ERL), which takes into account how slopes temporarily slow down Samus' horizontal movement:

`ERL = length - startingDownTiles - 9/16 * (1 - openEnd) + 1/3 * steepUpTiles + 1/7 * steepDownTiles + 5/27 * gentleUpTiles + 5/59 * gentleDownTiles`

There is some variance in how much down slopes slow down Samus' movement, depending on specific alignment of Samus' X position. The amount of variance is small enough to be neglected as long as some small amount of lenience is included in how runways are required to be used.

In a heated room, a `leaveWithRunway` exit condition implicitly includes `heatFrames` needed to use the runway. The amount of `heatFrames` required depends on the entrance condition in the next room, and the details of how these `heatFrames` may be calculated are described under each entrance condition [below](#entrance-conditions). If the `from` and `to` nodes of the strat are different nodes, then it is assumed that the strat property `requires` already includes any heat frames needed to reach the starting point of the runway (the side furthest from the door), in which case the implicit `heatFrames` in `leaveWithRunway` will only account for the heat frames needed to use the runway in one direction, moving towards the door. If the `from` and `to` nodes of the strat are the same node, then the implicit `heatFrames` includes all heat frames needed to position appropriately on the runway (starting from the door), execute the required movement, and exit the room through the door.

When a `leaveWithRunway` condition is used to charge a shinespark, it implicitly includes a `canShinecharge` requirement with `usedTiles` based on the runway length (and also based on a continuation of the runway in the destination room where applicable). Again, this is described in more detail under the applicable entrance conditions below.

When a `leaveWithRunway` conditions occurs on a door in a water environment, it may implicitly include a `Gravity` requirement, depending on whether this is needed for the corresponding entrance condition.

#### Example
```json
{
  "name": "Leave With Runway",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveWithRunway": {
      "length": 20,
      "openEnd": 1
    }
  }
}
```

### Leave Shinecharged

A `leaveShinecharged` object represents that Samus can leave through this door with a shinecharge (shinespark charge).

`leaveShinecharged` has a single property:
- _framesRemaining_: The number of frames remaining in the shinecharge when leaving the room.

A strat with a `leaveShinecharged` condition should include a `canShinecharge` requirement in its `requires`, as this is not implicitly included in the condition.

*Note*: Using a runway connected to a door to leave the room with a shinecharge is already covered by `leaveWithRunway`, so `leaveShinecharged` only needs to be used in cases where the shinecharge is obtained in another part of the room and then carried through the door.

#### Example
```json
{
  "name": "Leave Shinecharged",
  "notable": false,
  "requires": [
    {"canShinecharge": {
      "usedTiles": 20,
      "openEnd": 0
    }}
  ],
  "exitCondition": {
    "leaveShinecharged": {
      "framesRemaining": 90
    }
  }
}
```

### Leave With Spark

A `leaveWithSpark` exit condition represents that Samus can leave through this door while shinesparking. A strat with a `leaveWithSpark` condition should include a `canShinecharge` and `shinespark` requirements in its `requires`.

The `leaveWithSpark` object currently has no properties. If needed, properties might be added in the future to describe constraints on the position and direction of the spark. Currently it is implicitly assumed that the position can be fully controlled to be whatever is needed in the next room (e.g. to spark through either the top or bottom part of a horizontal door transition); so the requirements of a `leaveWithSpark` strat should be based on the worst-case scenario. The direction of the spark is assumed to be horizontal when sparking through horizontal door transitions, or vertical when sparking through vertical door transitions.

*Note*: Using a runway connected to a door to leave the room with a shinespark is already covered by `leaveWithRunway`. Likewise `leaveShinecharged` implicitly includes the possibility of leaving the room with a shinespark. It is only necessary to use `leaveWithSpark` in cases where it would not be possible to reach the door before the shinecharge timer expires.

#### Example
```json
{
  "name": "Leave With Spark",
  "notable": false,
  "requires": [
    {"canShinecharge": {
      "usedTiles": 20,
      "openEnd": 0
    }},
    {"shinespark": {
      "frames": 200
    }}
  ],
  "exitCondition": {
    "leaveWithSpark": {}
  }
}
```

## Entrance conditions

In all strats with an `entranceCondition`, the `from` node of the strat must be a door node. An `entranceCondition` object must contain exactly one property:

- _comeInRunning_: This indicates that Samus must run into the room, with speed in a certain range.
- _comeInJumping_: This indicates that Samus must run and jump just before hitting the transition, with speed in a certain range.
- _comeInShinecharging_: This indicates that Samus must run into the room with enough space to complete a shinecharge.
- _comeInShinecharged_: This indicates that Samus must enter the room with a shinecharge with a certain amount of frames remaining.
- _comeInWithSpark_: This indicates that Samus must shinespark into the room.
- _comeInWithBombBoost_: This indicates that Samus must come into the room with a horizontal bomb boost.
- _comeInStutterShinecharging_: This indicates that Samus must run into the room with a stutter immediately before the transition.
- _comeInWithDoorStuckSetup_: This indicates that Samus must enter the room in a way that allows getting stuck in the door as it closes.

Each of these properties is described in more detail below.

### Come In Running

A `comeInRunning` entrance condition represents the need for Samus to be able to run into the room with speed in a certain range. It has the following properties:
* _speedBooster_: If true, then Speed Booster must be used while running into the room. If false, then Speed Booster must not be used. If "any", then Speed Booster may or may not be used.
* _minTiles_: The minimum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.
* _maxTiles_: The maximum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.

A `comeInRunning` condition can be satisfied only by a matching strat on the other side of the door with `leaveWithRunway` exit condition: a match is valid if all of the following are true:
- The effective runway length of the `leaveWithRunway` is at least as long as the `minTiles` in the `comeInRunning` condition.

Where applicable, a `comeInRunning` condition also includes implicit requirements for actions to be performed in the previous room, which are effectively prepended to the start of the strat's `requires` (or equivalently but more properly, onto the end of the `requires` of the `leaveWithRunway` strat in the other room):
- If `speedBooster` is true, then there is an implicit `SpeedBooster` item requirement.
- If `speedBooster` is false, then there is an implicit `canDisableEquipment` tech requirement.
- If the previous room is heated, then `heatFrames` are required based on the time needed to perform the run. 
- If the previous door environment is water, then `Gravity` is required.

Heat frames may be calculated based on the following table of approximations (which include almost no lenience):

| Action                                                                  | Heat frames             |
| ----------------------------------------------------------------------  | ----------------------- |
| Run from a standstill in one direction, without Speedbooster, 0-6 tiles | `9 + 4 * tiles`         |
| Run from a standstill in one direction, without Speedbooster, 7+ tiles  | `13 + 64 / 19 * tiles`  |
| Run from a standstill in one direction, with Speedbooster, 0-6 tiles    | `9 + 4 * tiles`         |
| Run from a standstill in one direction, with Speedbooster, 7-16 tiles   | `15 + 3 * tiles`        |
| Run from a standstill in one direction, with Speedbooster, 17-42 tiles  | `32 + 2 * tiles`        |
| Run from a standstill in one direction, with Speedbooster, 43+ tiles    | `47 + 64 / 39 * tiles`  |
| Turn around                                                             | `8`                     |
| Position using moonwalk (and shoot open the door)                       | `12`                    |

The way to calculate minimally required heat frames depends on the type of `leaveWithRunway`:

- If the `from` node of the `leaveWithRunway` is the same as the `to` node, then this represents that the runway is used starting from the door. In this case heat frames must be included for running in both directions. The distance to run is determined by the `minTiles` in the `comeInRunning` object. The heat frames for this run length should be doubled; then heat frames should be added to allow time to turn around and position. Even with optimal movement, time to position is necessary if the full length of the runway is required; in theory this time could be reduced by using X-Ray Scope to buffer the positioning and to turn-around in place.
- If the `from` node of the `leaveWithRunway` is different from the `to` node, then this represents that the runway is used starting at the end opposite the door. In this case heat frames only need to be included for running in one direction, toward the door. However, if the `comeInRunning` condition has a `maxTiles` and it is less than the effective runway length in the `leaveWithRunway`, then it will not work to run through the entire length of the runway; there are a couple options in this case:
  - The player can hold run until at a distance of `maxTiles` from the transition, then stop and restart running (by briefly releasing forward while holding an angle button). In this case the runway is partitioned into two runs, and the heat frames from the two individual runs must be added, along with any time for positioning.
  - The player can hold dash at the beginning of the runway for a distance between `minTiles` and `maxTiles` (with the optimal strategy being to run as close to `maxTiles` as possible without going over), then release dash for the remainder of the run to maintain a constant speed.

#### Example
```json
{
  "name": "Come In Running",
  "notable": false,
  "entranceCondition": {
    "comeInRunning": {
      "speedBooster": "any",
      "minTiles": 2
    }
  },
  "requires": []
}
```

### Come In Jumping

A `comeInJumping` entrance condition represents the need for Samus to be able to run toward the door in the previous room, with speed in a certain range, and spin jump just before hitting the transition. It has the following properties:
* _speedBooster_: If true, then Speed Booster must be used while running into the room. If false, then Speed Booster must not be used. If "any", then Speed Booster may or may not be used.
* _minTiles_: The minimum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.
* _maxTiles_: The maximum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.

`comeInJumping` is very similar to `comeInRunning`, the only difference being the jump which happens just before the transition. Heat frames and other implicit requirements are generated in exactly the same way.

#### Example
```json
{
  "name": "Cross Room Jump",
  "notable": false,
  "entranceCondition": {
    "comeInJumping": {
      "speedBooster": "any",
      "minTiles": 2
    }
  },
  "requires": []
}
```

### Come In Shinecharging

A `comeInShinecharging` entrance condition represents the need for Samus to run into the room with enough space to complete a shinecharge. It has the following properties:

* _length:_ The number of tiles in the runway in this room that can be used to help complete the shinecharge. This length should not include any tiles that Samus skips over through the transition (e.g. door transition tiles and door shell tiles).
* _openEnd:_ Any runway that is used to gain momentum has two ends (although in this case one of those ends is always a door transition). An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (0 or 1).
* The following properties further define the tiles in `length`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 45 tiles where it's not relevant, that information will also be omitted. All up/down tile counts assume Samus is running away from the door, consistent with the direction that Samus will be traveling.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.

A `comeInShinecharging` must match with a corresponding `leaveWithRunway` condition on the other side of the door. 

A `comeInShinecharging` object also includes implicit requirements for actions to be performed in the previous room, which are effectively prepended to the start of the current strat's `requires` (or equivalently but more properly, onto the end of the `requires` of the `leaveWithRunway` strat in the other room):
- A `canShinecharge` requirement is included based on the combined runway length. This includes a `SpeedBooster` item requirement as well as a check that the combined runway length is long enough that charging a shinespark is possible.
- If the previous room is heated, then `heatFrames` are included based on the time spent running in that room.
- If the current room is heated, then `heatFrames` are included based on the time spent running in this room.
- If the previous door environment is water, then `Gravity` is required.

The way to calculate minimally required heat frames depends on the type of `leaveWithRunway` and on which of the two rooms (or both) are heated:

- If the `from` node of the `leaveWithRunway` is the same as the `to` node, then this represents that the runway in the other room is used starting from the door. In this case Samus will need to run in both directions. The way to calculate heat frames then depends on which rooms are heated:
  - If both rooms are heated, then it is best to use smallest amount of runway possible in the other room. If the required shinecharge tiles
  (based on the desired difficulty) is no more than the effective runway length in the current room (based on the `comeInShinecharging` properties), then there is no need to add heat frames for running in the other room. Otherwise, the amount of runway to use in the other room is the difference between the required shinecharge tiles and the effective runway length in the current room. The run in the other room to get positioned on the runway can be done at full speed, so the [table](#come-in-running) can be used to determine the required heat frames for this run, including heat frames for turning around and positioning. For the run back to charge the spark, there are two cases:
     - If the combined effective runway length is at least 31.3 tiles, then dash can be held through the entire run, so the [table](#come-in-running) can be used to get the total heat frames. 
     - If the combined effective runway length is less than 31.3 tiles, then run back to charge the spark requires a constant 85 frames (essentially independent of shortcharging technique).

  - If only the current room is heated, then heat frames are minimized by using the full available runway in the other room to gain as much speed as possible before the transition. 
    - If the combined effective runway length is at least 31.3 tiles, then dash can be held through the entire run. In this case, the frames spent on the combined run can be found in the [table](#come-in-running), as can the frames spent in the other room; subtracting these two values gives the frames spent on the heated part of the run (i.e. the part in the current room).
    - If the combined effective runway length is less than 31.3 tiles, then the run can be completed in the constant 85 frames needed to perform the shinecharge (regardless of shortcharging technique). The precise amount of frames spent in the current room is complicated to determine as it depends on details of how the shortcharge is performed. We can get a reasonable approximation by modeling as the movement as starting at a speed of 0.125 tiles/frame (somewhat less than the full walking speed of 0.171875 tiles/frame) and having constant acceleration up to the end of the combined runway. This is a quadratic model which has the following solution:

      $$T = \text{total time} = 85 \text{ frames}$$
      $$C = \text{initial speed} = 0.125 \text{ tiles per frame}$$
      $$L = \text{combined effective runway length (in tiles)}$$
      $$L_o = \text{effective runway length in other room}$$
      $$a = \text{acceleration} = 2(L - CT) / T^2$$
      $$T_o = \text{time in other room} = \frac{\sqrt{C^2 + 2aL_o} - C}{a}$$
      $$T_c = \text{time in current room} = T - T_o$$

    For medium-length runways (ones significantly longer than the player's minimum shortcharge length, but significantly less than 31.3 tiles), this model is somewhat lenient. It assumes essentially that the player would perform the shortcharge over the full length of the runway, like doing a 4-tap with relatively long, safe taps. If instead the player did a more precise start to the shortcharge and then held dash for the remainder of the run (e.g. like a stutter 2-tap), then the heat frames in the current room could be slightly reduced. This could be modeled, but it is probably not worth the hassle for the small difference it would make.

  - If only the other room is heated, then it is again best to use smallest amount of runway possible in the other room. The heat frames for the first run in the other room (if it is needed) and to turn-around and position can be obtained using the [table](#come-in-running). Heat frames for the run back can be approximated using either the [table](#come-in-running) or the formula for $T_o$ in the quadratic model above, depending on if the combined runway has length greater 31.3 tiles. In the case of medium-length runways, this model is technically a bit lenient. We are assuming a uniform rate of acceleration, but it could be possible to get out of the other room faster by holding dash at the start of the short-charge for as long as possible and then switch to tapping; this type of movement would be highly unintuitive and only save a few heat frames, so we don't try to model it.

- If the `from` node of the `leaveWithRunway` is different from the `to` node, then this represents that the runway in the other room is used starting at the end opposite the door. The way to calculate heat frames in this case is similar to above, except the full combined runway is used in every case, and it is only necessary to consider the one run from the other room to the current room (there being no need to start by doing a separate run in the opposite direction).


#### Example
```json
{
  "name": "Come In Shinecharging",
  "notable": false,
  "entranceCondition": {
    "comeInShinecharging": {
      "length": 5,
      "openEnd": 1
    }
  },
  "requires": [
    {"shinespark": {
      "frames": 40,
      "excessFrames": 3
    }}
  ]
}
```

### Come In Shinecharged

A `comeInShinecharged` entrance condition represents the need for Samus to run into the room with a shinecharge with a certain amount of time remaining before it would expire. It has the following property:

- _framesRequired_: The number of frames that must be left on the shinespark charge when coming in. This must be a value between 1 and 179. Note that the shinecharge timer begins at 180 frames, and at least one frame must elapse between obtaining the shinecharge in the other room and crossing the door transition.

A strat with a `comeInShinecharged` condition should include a `shinespark` requirement in its `requires`.

A `comeInShinecharged` must match with either a `leaveShinecharged` condition or a `leaveWithRunway` condition on the other side of the door. 

- In order for `comeInShinecharged` to have a valid match with a `leaveShinecharged` condition, the `framesRequired` in the `comeInShinecharged` must be less than or equal to the `framesRemaining` of the `leaveShinecharged` condition. Aside from this, `comeInShinecharged` condition has no implicit requirements when matched with a `leaveShinecharged` conditions: all requirements in the other room are assumed to be explicitly accounted for in the strat with the `leaveShinecharged`. The frame counts in `comeInShinecharged` and `leaveShinecharged` are based on highly skilled (but humanly viable) play; leniency could be added by adjusting these counts (to increase `framesRequired` or decrease `framesRemaining`).

- A `comeInShinecharged` condition may also match with a `leaveWithRunway` condition. In this case it is assumed that the runway in the other room is used to obtain a shinecharge just before entering the transition, with 179 frames remaining. This comes with implicit requirements for actions to be performed in the previous room:
  - A `canShinecharge` requirement is included based on the runway length. This includes a `SpeedBooster` item requirement as well as a check that the effective runway length is enough that charging a shinespark is possible.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here with `comeInShinecharged` there is no second runway to combine with.
  - If the previous door environment is water, then `Gravity` is required.
  
#### Example
```json
{
  "name": "Come In Shinecharged",
  "notable": false,
  "entranceCondition": {
    "comeInShinecharged": {
      "framesRequired": 65
    }
  },
  "requires": [
    {"shinespark": {
      "frames": 40,
      "excessFrames": 3
    }}
  ]
}
```

### Come In With Spark

A `comeInWithSpark` entrance condition indicates that Samus must shinespark into the room. The `comeInWithSpark` object has no properties. Properties might be added in the future to describe requirements on the position and direction of the spark. Currently it is implicitly assumed that the position can be fully controlled in the previous room, so a `comeInWithSpark` strat may make any assumptions needed about the position. The direction of the spark is assumed to be horizontal when sparking through horizontal door transitions, or vertical when sparking through vertical door transitions.

A strat with a `comeInWithSpark` condition should include a `shinespark` requirement in its `requires`.

A `comeInWithSpark` condition must match with either a `leaveWithSpark`, `leaveShinecharged`, or `leaveWithRunway` condition on the other side of the door:

- A match with `leaveWithSpark` or `leaveShinecharged` is always valid and does not come with any implicit requirements.
- A match with `leaveWithRunway` comes with the following implicit requirements (the same as for `comeInShinecharged`) for actions to be performed in the previous room:
  - A `canShinecharge` requirement is included based on the runway length. This includes a `SpeedBooster` item requirement as well as a check that the effective runway length is enough that charging a shinespark is possible.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here with `comeInShinecharged` there is no second runway to combine with.
  - If the previous door environment is water, then `Gravity` is required.

#### Example
```json
{
  "name": "Come In With Spark",
  "notable": false,
  "entranceCondition": {
    "comeInWithSpark": {}
  },
  "requires": [
    {"shinespark": {
      "frames": 50,
      "excessFrames": 3
    }}
  ]
}
```

### Come In Stutter Shinecharging

A `comeInStutterShinecharging` entrance condition indicates that Samus must run into the room with SpeedBooster equipped, with a stutter immediately before the transition. This is used when entering a water room in order to obtain a shinecharge in a shorter amount of space than would otherwise be possible. It has the following property:
- _minTiles_: The minimum amount of effective runway tiles in other room needed for this strat.

A `comeInStutterShinecharging` condition must match with a `leaveWithRunway` condition on the other side of the door, which must have an "air" environment and an effective length of at least `minTiles`. A match comes with the following implicit requirements for actions to be performed in the previous room:
- The tech `canStutterWaterShineCharge`, which includes a requirement for the `SpeedBooster` item.
- If the previous room is heated, then heat frame requirements are included based on `minTiles`, in the same way as for a `comeInRunning` requirement.

#### Example
```json
{
  "name": "Come In Stutter Shinecharging",
  "notable": false,
  "entranceCondition": {
    "comeInStutterShinecharging": {
      "minTiles": 2
    }
  },
  "requires": [
    {"shinespark": {"frames": 60}}
  ]
}
```

### Come In With Bomb Boost

A `comeInWithBombBoost` entrance condition indicates that Samus must come into the room with a horizontal bomb boost. This object has no properties.

A `comeInWithBombBoost` condition must match with a `leaveWithRunway` condition on the other side of the door, which must have an "air" environment. A match comes with the following implicit requirements for actions to be performed in the previous room:
- A requirement `h_canBombThings`, to be able to use Bombs or a Power Bomb.
- If the previous room is heated, a requirement of `{"heatFrames": 100}` is included, for positioning, placing the bomb, and waiting for it to detonate.

#### Example
```json
{
  "name": "Come In With Bomb Boost",
  "notable": false,
  "entranceCondition": {
    "comeInWithBombBoost": {}
  },
  "requires": []
}
```

### Come In With Door Stuck Setup

A `comeInWithDoorStuckSetup` entrance condition indicates that Samus must enter the room in a way that allows getting stuck in the door as it closes. This object has no properties.

A `comeInWithDoorStuckSetup` condition must match with a `leaveWithRunway` condition on the other side of the door. A match comes with the following implicit requirements for actions to be performed in the previous room:
- If the previous room is heated, a minimum requirement of `{"heatFrames": 100}` is included, for positioning and executing the door stuck setup; depending on the desired difficulty, this requirement can be increased to add leniency. Note that if X-Ray Scope is available (and it always should be for a strat with this condition, since the only known application of door stuck setups is for X-Ray climbing), then minimizing heat damage is made easier by using X-Ray to buffer the positioning near the door and to turn around in place.
- If the previous room is to the left, then a tech requirement `canStationarySpinJump` is included.
- If the previous room is to the right, then a tech requirement `canRightSideDoorStuck` is included.
- If the previous door environment is water and is to the right, then a requirement `{"or": ["Gravity", "canRightSideDoorStuckFromWater"]}` is included.

#### Example
```json
{
  "name": "X-Ray Climb",
  "notable": false,
  "entranceCondition": {
    "comeInWithDoorStuckSetup": {}
  },
  "requires": [
    "canXRayClimb"
  ]
}
```
