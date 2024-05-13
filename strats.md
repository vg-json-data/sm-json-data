# Strats
Strats are a concept that encompasses performing a series of maneuvers in a room.

Strats are usually presented within an array of strats, where all individual strats are a way to attain roughly the same goal.

## Structure

A `strat` can have the following properties:
  * _name_: The name of the strat.
  * _notable_: Indicates whether the strat is notable.
  * _reusableRoomwideNotable_: The name of the reusable roomwide notable strat. This must share an identical name with an entry in the `reusableRoomwideNotable` array and the other strats that are connected to this one. This is only applicable for strats where `notable` is `true`.
  * _entranceCondition_: Indicates that this strat requires entering through the door transition in a special way, combining with a strat in the previous room.
  * _requires_: The [logical requirements](logicalRequirements.md) that must be fulfilled to execute that strat.
  * _exitCondition_: Indicates that this strat leaves through the door transition in a special way that combines with a strat in the next room. 
  * _clearsObstacles_: An array containing the ID of obstacles that will be cleared by executing this strat (if they are not already cleared).
  * _resetsObstacles_: An array containing the ID of obstacles that will be reset (i.e. returned to their original state) by executing this strat.
  * _comesThroughToilet_: Indicates whether this strat is applicable if the Toilet comes between this room and the other room.
  * _gModeRegainMobility_: Indicates that this strat allows regaining mobility when entering with G-mode immobile.
  * _bypassesDoorShell_: Indicates that this strat allows exiting without opening the door.
  * _unlocksDoors_: An array describing possible doors that can be unlocked as part of this strat.
  * _collectsItems_: An array listing items that are collected as part of this strat (e.g. for G-mode remote item acquire).
  * _setsFlags_: An array listing game flags that are set as part of this strat.
These properties are described below in more detail.
  * _flashSuitChecked_: Indicates that the logical requirements of the strat have been verified to be logically sound with respect to whether a flash suit can be carried or not. Note that a `true` value does not necessarily mean that a flash suit can be carried with this strat, only that its logical requirements can be relied on to determine whether it can or not.
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

Execution of a strat may have an effect of clearing one or more [obstacles](region/region-readme.md#obstacles) in the room. This is indicated by a `clearsObstacles` property on the strat. It can represent, for example, that certain enemies or special blocks are destroyed by executing this strat. This allows later performing strats in the room that have an [`obstaclesCleared`](logicalRequirements.md#obstaclescleared) logical requirement on this obstacle, while disallowing strats that have an [`obstaclesNotCleared`] requirement.

Similarly, the `resetsObstacles` property is used to indicate that a strat results in an obstacle returning to its original, uncleared state.

## Reusable Roomwide Notable Strats

Some notable strats may be very similar to each other. If similar notable strats exist in different rooms, a tech might be made for them. Otherwise, if similar notable strats exist in the same room, a [reusable notable strat](region/region-readme.md#reusable) can exist to connect them with a common name and description. A typical example is for symmetric links with strats of notable difficulty, with one notable strat for each of two directions the room can be traversed in, and the two strats being connected by sharing the same reusable notable.

## Cross-room strats

Some strats involve leaving the room in a special way that allows a corresponding strat in the next room to be executed. Common examples include leaving the room with a shinespark or shinecharge, or running out of the room in order to complete a shinecharge in the next room. Strats that exit a room in such a way are identified by a strat property `exitCondition`, containing a property describing the type of exit condition, such as `leaveWithRunway`, `leaveShinecharged`, or `leaveWithSpark`. Likewise, strats that require entering the room in a special way are identified by a strat property `entranceCondition`, containing a property describing the type of entrance condition required, such as `comeInRunning`, `comeInShinecharged`, or `comeInWithSpark`.

## Runway geometry

Many cross-room strats involve the use of runways. The geometry of a runway is summarized by an object having the following properties:

* _length:_ The number of tiles in the runway. 
* _openEnd:_ Any runway that is used to gain momentum has two ends. An open end is when a platform drops off into nothingness, as opposed to ending against a wall or a door transition tile. An open end offers a bit more room to run. This property indicates the number of open ends that are available to use (0 or 1).
* The following properties further define the tiles in `length`, by indicating how many of them have some particularities. Samus temporarily moves more slowly over sloped tiles, which effectively gives a longer distance over which to gain speed on the runway. These properties will be missing if there are no such tiles. In places with more than 45 tiles where it's not relevant, that information will also be omitted.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.

In most cases, what matters is the effective runway length (ERL), which takes into account how slopes temporarily slow down Samus' horizontal movement:

`ERL = length - startingDownTiles - 9/16 * (1 - openEnd) + 1/3 * steepUpTiles + 1/7 * steepDownTiles + 5/27 * gentleUpTiles + 5/59 * gentleDownTiles`

There is some variance in how much downward slopes slow Samus' movement, depending on specific alignment of Samus' X position. The amount of variance is small enough to be neglected as long as some small amount of lenience is included in how runways are required to be used.

## Exit conditions

In all strats with an `exitCondition`, the `to` node of the strat must be a door node or exit node. An `exitCondition` object must contain exactly one property, which indicates the type of exit condition provided by the strat:

- _leaveNormally_: This indicates that can Samus leave through this door in a "normal" way, by walking, falling, or jumping.
- _leaveWithRunway_: This indicates that a runway of a certain length is connected to the door, with which Samus can gain speed and run or jump through the door, among other possible actions. 
- _leaveShinecharged_: This indicates that it is possible to charge a shinespark and leave the room with a certain amount of time remaining on the shinecharge timer (e.g., so that a shinespark can be activated in the next room). 
- _leaveWithTemporaryBlue_: This indicates that Samus may leave through this door by jumping with temporary blue.
- _leaveWithSpark_: This indicates that it is possible to shinespark through the door transition.
- _leaveSpinning_: This indicates that it is possible to jump through this door with a spin jump from a runway not connected to the door, possibly with blue speed.
- _leaveWithMockball_: This indicates that it is possible to mockball through the door with a certain amount of momentum, and possibly with blue speed, from a runway not connected to the door.
- _leaveWithSpringBallBounce_: This indicates that it is possible to leave through this door with a spring ball bounce with a certain amount of momentum.
- _leaveSpaceJumping: This indicates that it is possible to Space Jump through the bottom of the doorway (through a horizontal transition) with a certain amount of momentum, and possibly with blue speed.
- _leaveWithStoredFallSpeed_: This indicates that is is possible to walk through the door with the stored velocity to clip through floor tiles using a Moonfall.
- _leaveWithGModeSetup_: This indicates that Samus can take enemy damage through the door transition, to set up R-mode or direct G-mode in the next room.
- _leaveWithGMode_: This indicates that Samus can carry G-mode into the next room (where it will become indirect G-mode).
- _leaveWithDoorFrameBelow_: This indicates that Samus can go up through this door with momentum by jumping in the door frame, e.g. using a wall-jump or Space Jump.
- _leaveWithPlatformBelow_: This indicates that Samus can go up through this door with momentum by jumping from a platform below, possibly with run speed.
- _leaveWithGrappleTeleport_: This indicates that Samus can leave through this door while grappling, which can enable a teleport in the next room.

Each of these properties is described in more detail below.

A strat with an exit condition implicitly has a `doorUnlockedAtNode` requirement on its `to` node, unless it has the `bypassesDoorShell` property set to `true`. This means that if the `to` door has a lock on it, it must either be unlocked before the strat can be executed, or the door's requirements under the strat property `unlocksDoors` must be satisfied. 

### Leave Normally

A `leaveNormally` object indicates that Samus can leave the room through this door, with no other particular requirements.

#### Example
```json
{
  "name": "Leave Normally",
  "exitCondition": {
    "leaveNormally": {}
  },
  "requires": []
}
```

### Leave With Runway
A `leaveWithRunway` object indicates that a strat exits the current room using a runway. The `leaveWithRunway` exit condition is unique in that it describes available geometry rather than a specific way to leave the room. This is done in order to reduce the amount of redundant boilerplate that would otherwise be required, since every door node in the game will have at least one strat with `leaveWithRunway`. The specific way that the runway is used depends on the entrance condition in the destination room. A `leaveWithRunway` condition implies that the area around the door must be clear of any enemies that would interfere with using the runway.

A `leaveWithRunway` exit condition can satisfy the following entrance conditions in the next room: `comeInRunning`, `comeInJumping`, `comeInShinecharging`, `comeInGettingBlueSpeed`, `comeInShinecharged`, `comeInWithSpark`, `comeInWithBombBoost`, `comeInWithStutter`, `comeInWithDoorStuckSetup`, `comeInSpeedballing`, `comeInWithTemporaryBlue`, `comeInBlueSpinning`, and `comeInWithMockball`. Details are given under the corresponding entrance conditions below.

`leaveWithRunway` has the following properties describing the runway geometry (see [runway geometry](#runway-geometry) above for details):

* _length_, _openEnd_, _gentleUpTiles_, _gentleDownTiles_, _steepUpTiles_, _steepDownTiles_, _startingDownTiles_

The runway length should not include the transition tile, but it should include the door shell tile if applicable.

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
- _framesRemaining_: The number of frames remaining in the shinecharge when leaving the room. A special value "auto" may be used when the strat has a `comeInShinecharged` entrance condition: in this case, the frames remaining when leaving the room depends on how many frames are remaining when entering the room, with the `framesRequired` property of the `comeInShinecharged` indicating the amount of frames by which the shinecharge timer decreases between entering and exiting the room.

A strat with a `leaveShinecharged` condition should either include a `canShinecharge` requirement in its `requires` or have a `comeInShinecharged` entrance condition.

*Note*: Using a runway connected to a door to leave the room with a shinecharge is already covered by `leaveWithRunway`, so `leaveShinecharged` only needs to be used in cases where the shinecharge is obtained in another part of the room and then carried through the door.

#### Position and Momentum Details

A `leaveShinecharged` object does not provide any way to specify Samus' position or momentum through the door transition, but these details can affect the execution of the strat in the next room. Instead, as a way of normalizing these requirements, we make the following assumptions:

- For a horizontal door transition, the `framesRemaining` (and any other strat requirements such as heat frames) should be based on Samus touching the door transition while running, with an unspecified amount of horizontal momentum but no vertical momentum.

- For a vertical door transition, the `framesRemaining` (and other strat requirements) should be based on the worst-case position, among all possible horizontal positions within the door frame, with an unspecified amount of horizontal and vertical momentum. Samus must enter the transition in a normal "jumping" or "falling" pose. For example, entering an upward transition with a jump into mid-air morph would not be valid, because in the next room it would not be possible to control the effects of the jump in the expected way. Breaking spin before the transition would be valid, and it is recommended to do so since it allows reaching the transition more quickly.

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

### Leave With Temporary Blue

A `leaveWithTemporaryBlue` exit condition represents that Samus can leave through this door by jumping with temporary blue. It can be applied to either horizontal or vertical transitions.

The `leaveWithTemporaryBlue` object has the following property:
- _direction_: This takes three possible values "left", "right", and "any", indicating the direction that Samus is facing through the transition. It should be specified for all vertical transitions but not horizontal ones.

*Note*: Using a runway connected to a door to leave the room with temporary blue is already covered by `leaveWithRunway`.

#### Example
```json
{
  "name": "Leave With Temporary Blue",
  "notable": false,
  "requires": [
    {"canShinecharge": {
      "usedTiles": 20,
      "openEnd": 0
    }}
  ],
  "exitCondition": {
    "leaveWithTemporaryBlue": {}
  }
}
```

### Leave With Spark

A `leaveWithSpark` exit condition represents that Samus can leave through this door while shinesparking. A strat with a `leaveWithSpark` condition should include a `canShinecharge` and `shinespark` requirements in its `requires`.

The `leaveWithSpark` object has the following property:
- _position_: For a horizontal transition, if specified, this takes two possible values, "top" or "bottom". The value "top" represents that the strat sparks through the doorway high enough to clear a single-tile block level with the bottom of the doorway. The value "bottom" represents that the strat sparks through the doorway low enough to clear a single-tile block level with the top of the doorway. If unspecified, it is understood that the strat can exit through either the top or bottom of the doorway, whichever is needed in the next room.

The direction of the spark is assumed to be horizontal when sparking through horizontal door transitions, or vertical when sparking through vertical door transitions. There is an implicit requirement of `canHorizontalShinespark` when sparking through a horizontal door.

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

### Leave Spinning

A `leaveSpinning` exit condition represents that Samus can spin jump through a horizontal transition with a certain amount of momentum, and possibly with blue speed, depending on the length of available runway and short-charging skill assumption. This exit condition applies to jumps from a runway disconnected from the door (e.g. below a ledge in front of the door). It should only be applied where there is air physics at the door. It should also only be applied in cases where there is flexibility to exit at a wide range of positions between the top and bottom of the doorway. Specifically, for every vertical position at least 8 pixels below the top of the doorway, it should be possible to control the jump to leave at that position. This means being able to leave at screen positions in the range between 116 ($74) and 148 ($94); the highest of these positions corresponds to Samus' hitbox just barely fitting in the top half of the doorway.

The `leaveSpinning` object has the following properties:

- _remoteRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to gain speed for the jump.
- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. For leaving with blue speed, there is already an implicit minimum speed based on shortcharging skill, so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at low speeds.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. There is already an implicit speed limit based on the length of the remote runway (see the [full run speed table](#full-run-speed-table)), and for leaving with blue speed there is a different implicit limit based on a combination of runway length and shortcharging skill (see the [blue run speed table](#blue-run-speed-table)); so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at high speeds.
- _blue_: This takes one of three possible values, "yes", "no", or "any", indicating whether this strat can be used for leaving with blue speed, without blue speed, or either. This could be used, for example, in case of a difference in usable runway length if shortcharging is being performed, or a difference in heat damage taken. The default is "any".

If a `leaveSpinning` condition is used for blue speed in the next room, then it implicitly includes a `canShinecharge` requirement (including the `SpeedBooster` item). Heat frames are not included and would have to described explicitly in the strat "requires".

#### Example
```json
{
  "name": "Leave Spinning",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveSpinning": {
      "remoteRunway": {
        "length": 12,
        "openEnd": 1
      }
    }
  }
}
```

### Leave With Mockball

A `leaveWithMockball` exit condition represents that Samus can leave through a horizontal transition while in a mockball (or process of morphing into a mockball) with a certain amount of momentum, and possibly with blue speed, depending on the length of available runway and short-charging skill assumption. It should only be applied where there is air physics at the door.

The `leaveWithMockball` object has the following properties:

- _remoteRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to gain speed for the jump before the mockball.
- _landingRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to land and gain speed in a mockball before hitting the transition.
- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. For leaving with blue speed, there is already an implicit minimum speed based on shortcharging skill, so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at low speeds.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. There is already an implicit speed limit based on the length of the remote runway (see the [full run speed table](#full-run-speed-table)), and for leaving with blue speed there is a different implicit limit based on a combination of runway length and shortcharging skill (see the [blue run speed table](#blue-run-speed-table)); so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at high speeds.
- _blue_: This takes one of three possible values, "yes", "no", or "any", indicating whether this strat can be used for leaving with blue speed, without blue speed, or either. The default is "any".

A `leaveWithMockball` condition implicitly includes the `canMockball` tech requirement (including the `Morph` item requirement). If it is used for blue speed in the next room, then it also implicitly includes a `canShinecharge` requirement (including the `SpeedBooster` item) and the `canSpeedball` tech requirement. Heat frames are not included and would have to described explicitly in the strat "requires".

#### Example
```json
{
  "name": "Leave With Mockball",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveWithMockball": {
      "remoteRunway": {
        "length": 12,
        "openEnd": 1
      },
      "landingRunway": {
        "length": 3,
        "openEnd": 1
      }
    }
  }
}
```

### Leave With Spring Ball Bounce

A `leaveWithSpringBallBounce` exit condition represents that Samus can leave through a horizontal transition with a spring ball bounce in front of the door, with a certain amount of momentum, and possibly with blue speed. It should only be applied where there is air physics at the door.

The `leaveWithSpringBallBounce` object has the following properties:

- _remoteRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to gain speed for the jump before the mockball.
- _landingRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to land and gain speed in a mockball before hitting the transition.
- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. For leaving with blue speed, there is already an implicit minimum speed based on shortcharging skill, so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at low speeds.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. There is already an implicit speed limit based on the length of the remote runway (see the [full run speed table](#full-run-speed-table)), and for leaving with blue speed there is a different implicit limit based on a combination of runway length and shortcharging skill (see the [blue run speed table](#blue-run-speed-table)); so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at high speeds.
- _blue_: This takes one of three possible values, "yes", "no", or "any", indicating whether this strat can be used for leaving with blue speed, without blue speed, or either. The default is "any".
- _movementType_: This takes one of three possible values, "controlled", "uncontrolled", or "any", indicating the type of bounce that can be used. 
  - "controlled" refers to movement type $12, which occurs when jumping using Spring Ball while rolling on the ground (e.g. from a mockball). In this state it is possible to control the height of each bounce by releasing jump.
  - "uncontrolled" refers to movement type $13, which occurs when performing a lateral mid-air morph high enough that the morph animation completes before landing and bouncing. This state also occurs when rolling off of a ledge (e.g. after a mockball). In this state, Samus' horizontal speed will reach a slightly higher value, and without the need for a longer landing platform to accelerate on. However, it will not be possible to control the height of the bounce.

A `leaveWithSpringBallBounce` condition implicitly includes the `canSpringBallBounce` tech requirement (including the `Morph` and `SpringBall` item requirements). If it is used for blue speed in the next room, then it also implicitly includes a `canShinecharge` requirement (including the `SpeedBooster` item) and the `canSpeedball` tech requirement. Heat frames are not included and would have to described explicitly in the strat "requires".

Note that using a mockball in front of the door to perform a spring ball bounce is already covered by `leaveWithMockball`. Therefore strats for `leaveWithStringBallBounce` are generally only needed to cover the "uncontrolled" case; they can also be used for cases where a controlled-type bounce is carried from elsewhere by bouncing across the room.

#### Example
```json
{
  "name": "Leave With Spring Ball Bounce",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveWithSpringBallBounce": {
      "remoteRunway": {
        "length": 12,
        "openEnd": 1
      },
      "landingRunway": {
        "length": 3,
        "openEnd": 1
      },
      "movementType": "uncontrolled"
    }
  }
}
```

### Leave Space Jumping

A `leaveSpaceJumping` exit condition represents that Samus can Space Jump through the bottom of a horizontal transition just before hitting the transition, using momentum (and possibly blue speed) available from a remote runway (one not connected to the door). It should also only be applied where there is air physics at the door.

The `leaveSpaceJumping` object has the following properties:

- _remoteRunway_: A [runway geometry](#runway-geometry) object describing the tiles available to gain speed for the Space Jump.
- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. For leaving with blue speed, there is already an implicit minimum speed based on shortcharging skill, so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at low speeds.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) with which it is possible to leave with this condition. There is already an implicit speed limit based on the length of the remote runway (see the [full run speed table](#full-run-speed-table)), and for leaving with blue speed there is a different implicit limit based on a combination of runway length and shortcharging skill (see the [blue run speed table](#blue-run-speed-table)); so this property only needs to be specified as an additional constraint in case something else prevents Samus from reaching the door transition (in the needed positions) at high speeds.
- _blue_: This takes one of three possible values, "yes", "no", or "any", indicating whether this strat can be used for leaving with blue speed, without blue speed, or either. The default is "any".

A `leaveSpaceJumping` condition implicitly includes the `SpaceJump` item requirement. If it is used for blue speed in the next room, then it also implicitly includes a `canShinecharge` requirement (including the `SpeedBooster` item) and the `canBlueSpaceJump` tech requirement. Heat frames are not included and would have to described explicitly in the strat "requires".

#### Example
```json
{
  "name": "Leave Space Jumping",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveSpaceJumping": {
      "remoteRunway": {
        "length": 12,
        "openEnd": 1
      }
    }
  }
}
```

### Leave With Stored Fall Speed

A `leaveWithStoredFallSpeed` exit condition represents that Samus can leave through this door with stored fall speed.

The `leaveWithStoredFallSpeed` object has a single property:
- _fallSpeedInTiles_: The number of tiles Samus would clip through by Moonfalling on top of a solid floor.

A `leaveWithStoredFallSpeed` entrance condition must match with a `comeInWithStoredFallSpeed` condition on the other side of the door.  A strat with a `leaveWithStoredFallSpeed` condition must include a method of storing fall speed within its requirements, such as a Moondance.  Entering a room with a `comeInWithStoredFallSpeed` condition would also be a possible way to exit with a `leaveWithStoredFallSpeed` condition so long as the stored speed is not lost.  For this to happen, both doors must be connected by one `Runway`, and Samus must not Crouch or become Knocked back.

#### Example
```json
{
  "name": "Moondance to Store Fall Speed",
  "notable": false,
  "requires": [
    "h_canUseBombs",
    "canMoondance"
  ],
  "exitCondition": {
    "leaveWithStoredFallSpeed": {
      "fallSpeedInTiles": 1
    }
  }
}
```

### Leave with G-Mode Setup

A `leaveWithGModeSetup` exit condition represents that Samus can leave through this door while taking damage through the transition, in a pose that would allow using X-Ray on the first frame after the transition. This sets up the player to enter R-mode or direct G-mode in the next room. The only known way to achieve this is to use an enemy that can follow Samus into the doorway during the transition. It will not work with enemy projectiles since these do not move during transitions, and environmental damage such as heat, lava, acid do not work as these are not active during the transition. Also note that the damage must happen *during* (not *before*) the transition, so being able to take a hit that knocks Samus into the door transition does not work. The enemy damage through the transition should _not_ be included in the `requires`, as the type/amount of enemy damage is irrelevant since Samus' energy will always reach zero here in order to trigger reserves.

A `leaveWithGModeSetup` object contains the following property:
- _knockback_: If true, then Samus gets knockback frames through the transition. This makes it possible for Samus to retain mobility in the next room if reserve energy is at most 4. Most enemies provide knockback, so this property is true by default if unspecified. Certain enemies such as Beetoms, Metroids, and Mochtroids do not provide knockback, so this property should be set to false for strats that use these enemies for the transition damage.

A `leaveWithGModeSetup` comes with implicit requirements, which are described in detail under the entrance conditions `comeInWithRMode` and `comeInWithGMode`. The implicit requirements depend on the specifics of the entrance condition in the next room, but they always include at least the following:
- The `XRayScope` item requirement.
- A requirement to have at least 1 reserve energy.
- A requirement to damage down to 0 energy, triggering reserves.

#### Example
```json
{
  "name": "Leave With G-Mode Setup",
  "notable": false,
  "requires": [],
  "exitCondition": {
    "leaveWithGModeSetup": {}
  }
}
```

### Leave with G-Mode

A `leaveWithGMode` exit condition represents that Samus can leave through this door while in G-mode, resulting in indirect G-mode in the next room. A strat with a `leaveWithGMode` exit condition should always also have a `comeInWithGMode` entrance condition since the only (known) way to enter G-mode is while (or before) coming into the room.

A `leaveWithGMode` object has the following property:
- _morphed_: If true, then this strat results in leaving the room in a morphed state, either by maintaining artificial morph or by having the Morph item.

For most doors in the game, it is possible to enter the room with a G-mode setup and then immediately exit back through the same door. This is because in direct G-mode the door does not close behind Samus. To avoid the need to write out tedious boilerplate, these strats are understood to be included implicitly. The implicit strats are included for every door node excluding vertical doors with `"position": "bottom"` as well as any with a `spawnAt` property. There are two implicit strats, with `leaveWithGMode` exit conditions, one of the form

```json
{
  "name": "G-Mode Go Back Through Door",
  "notable": false,
  "entranceCondition": {
    "comeInWithGMode": {
      "mode": "direct",
      "morphed": false
    }
  },
  "requires": [],
  "exitCondition": {
    "leaveWithGMode": {
      "morphed": false
    }
  }
}
```

and another where the `false` values for `morphed` are replaced with `true`. Here we are referring to nodes with `"nodeType": "door"`, which excludes sand entrances (which instead have `"nodeType": "entrance"`). These implicit strats have the same door node for both their `from` and `to` nodes.

Aside from the implicit strats, there are a limited amount of `leaveWithGMode` strats possible. Normally entering a room with G-mode (or a G-mode setup) and then leaving with G-mode through a different door is not possible, since door shells cannot be opened while in G-mode. However, some door transitions do not have door shells (e.g. in Crateria Tube, Glass Tunnel, Crab Hole, Big Pink; also elevators and sand transitions), and some door shells are possible to bypass using glitches, so `leaveWithGMode` can be used in these situations.

### Leave With Door Frame Below

A `leaveWithDoorFrameBelow` exit condition represents that Samus can go up through this door with momentum by jumping in the door frame, e.g. using a wall-jump or Space Jump. A `leaveWithDoorFrameBelow` exit condition can satisfy `comeInWithWallJumpBelow` and `comeInWithSpaceJumpBelow` entrance conditions in the room above.

A `leaveWithDoorFrameBelow` object has the following property:

- _height_: The number of tiles beneath the door transition (not including the transition tiles) usable for wall-jumping.

In a heated room, heat frames must be explicitly included in the strat `requires`, based on an assumption of wall-jumping up through the door. If the strat in the neighboring room has a `comeInWithSpaceJumpBelow` entrance condition, then additional heat frames will be implicitly included to use Space Jump, so that does not need to be included in the `leaveWithDoorFrameBelow` strat. Likewise, requirements for `canWalljump` or `SpaceJump` do not need to included, as these will be implicitly included in the corresponding entrance conditions. If a strat starts at the same (door) node that it ends at, then heat frames should include the time required to fall down from the door, shoot it open, and then wall-jump back out.

#### Example
```json
{
  "name": "Leave With Door Frame Below",
  "requires": [],
  "exitCondition": {
    "leaveWithDoorFrame": {
      "height": 2
    }
  }
}
```

### Leave With Platform Below

A `leaveWithPlatformBelow` exit condition represents that that Samus can go up through this door with momentum by jumping from a platform below, possibly with run speed. A `leaveWithPlatformBelow` exit condition can satisfy a `comeInWithPlatformBelow` entrance condition in the room above.

A `leaveWithPlatformBelow` object has the following properties:

- _height_: The number of tiles between the door transition and the platform, not including the transition tiles or platform itself. A horizontal slope tile (as in Blue Hopper Room) counts as a half tile.
- _leftPosition_: This indicates the position of the furthest left usable tile of the platform, relative to the center of the door. A negative values indicates a position to the left of the door center, while a positive value indicates a position to the right of the door center. An open end, if applicable, is represented by an extra half tile.
- _rightPosition_: This indicates the position of the furthest right usable tile of the platform, relative to the center of the door. A negative values indicates a position to the left of the door center, while a positive value indicates a position to the right of the door center. An open end, if applicable, is represented by an extra half tile.

In a heated room, heat frames must be explicitly included in the strat `requires`, based on a worst-case assumption of how the platform could need to be used. If a strat starts at the same (door) node that it ends at, then heat frames should include the time required to fall down from the door, shoot it open, position at the far end of the runway, and jump out.

#### Example
```json
{
  "name": "Leave With Platform Below",
  "requires": [],
  "exitCondition": {
    "leaveWithDoorFrame": {
      "height": 7,
      "leftPosition": -2.5,
      "rightPosition": 2.5,
    }
  }
}
```

## Leave With Grapple Teleport

A `leaveWithGrappleTeleport` exit condition represents that Samus can leave through this door while grappled, which can enable a teleport in the next room. The position of the block that Samus is grappled to (counted in tiles from the top left corner of the room) determines the destination of the teleport in the next room. For the teleport to work, the next room must have a block in a corresponding position that Samus can remain grappled to; e.g. a solid tile will work but air will not.

A `leaveWithGrappleTeleport` object has the following property:

- _blockPositions_: A list of tile coordinates of (grapple) blocks that Samus could be grappled to while exiting the room. Coordinates `[x, y]` are represented as tile counts with `[0, 0]` representing the top-left corner of the room.

A `leaveWithGrappleTeleport` comes with an implicit tech requirement `canGrappleTeleport`.

#### Example
```json
{
  "name": "Leave with Grapple Teleport",
  "requires": [],
  "exitCondition": {
    "leaveWithGrappleTeleport": {
      "blockPositions": [[5, 3]]
    }
  }
}
```

## Entrance conditions

In all strats with an `entranceCondition`, the `from` node of the strat must be a door node or entrance node. An `entranceCondition` object must contain exactly one of the following properties:

- _comeInNormally_: This indicates that Samus must come into the room through the specified door, with no other particular requirements.
- _comeInRunning_: This indicates that Samus must run into the room, with speed in a certain range.
- _comeInJumping_: This indicates that Samus must run and jump just before hitting the transition, with speed in a certain range.
- _comeInSpaceJumping_: This indicates that Samus must Space Jump through the bottom of the doorway.
- _comeInShinecharging_: This indicates that Samus must run into the room with enough space to complete a shinecharge.
- _comeInShinecharged_: This indicates that Samus must enter the room with a shinecharge with a certain amount of frames remaining.
- _comeInShinechargedJumping_: This indicates that Samus must jump into the the room with a shinecharge with a certain amount of frames remaining.
- _comeInWithSpark_: This indicates that Samus must shinespark into the room.
- _comeInWithBombBoost_: This indicates that Samus must come into the room with a horizontal bomb boost.
- _comeInStutterShinecharging_: This indicates that Samus must run into the room with a stutter immediately before the transition.
- _comeInWithDoorStuckSetup_: This indicates that Samus must enter the room in a way that allows getting stuck in the door as it closes.
- _comeInSpeedballing_: This indicates that Samus must enter the room either in a speedball from the previous room, or in a process of running, jumping, or falling into a speedball.
- _comeInWithTemporaryBlue_: This indicates that Samus must come in by jumping through this door with temporary blue.
- _comeInWithMockball_: This indicates that Samus must roll into the room with a mockball with a certain amount of momentum.
- _comeInWithSpringBallBounce_: This indicates that Samus get a spring ball bounce in the doorway of the previous room.
- _comeInWithBlueSpringBallBounce_: This indicates that Samus get a spring ball bounce in the doorway of the previous room while having blue speed.
- _comeInBlueSpinning_: This indicates that Samus come in with a spin jump through the doorway while having blue speed.
- _comeInWithStoredFallSpeed_: This indicates that Samus must enter the room with fall speed stored, and is able to clip through a floor with a Moonfall.
- _comeInWithRMode_: This indicates that Samus must have or obtain R-mode while coming through this door.
- _comeInWithGMode_: This indicates that Samus must have or obtain G-mode (direct or indirect) while coming through this door. 
- _comeInWithWallJumpBelow_: This indicates that Samus must come up through this door with momentum by wall-jumping in the door frame below.
- _comeInWithSpaceJumpBelow_: This indicates that Samus must come up through this door with momentum by using Space Jump in the door frame below.
- _comeInWithPlatformBelow_: This indicates that Samus must come up through this door with momentum by jumping from a platform below, possibly with run speed.
- _comeInWithGrappleTeleport_: This indicates that Samus must come into the room while grappling, teleporting Samus to a position in this room corresponding to the location of the (grapple) block in the other room.

In addition it may contain the following property:

- _comesThroughToilet_: This indicates whether the strat is applicable if the Toilet comes between this room and the other room.

Each of these properties is described in more detail below.

### Come In Normally

A `comeInNormally` entrance condition represents the need for Samus to enter the room through this door, with no other particular requirements. It has no properties.

A `comeInNormally` condition can be satisfied by a matching strat on the other side of the door with a `leaveNormally` or `leaveWithRunway` exit condition. 

When matching with a `leaveWithRunway` condition in a heated room on a strat having distinct `from` and `to` nodes, heat frame requirements must be included for the run performed in the other room; for details, see the `comeInRunning` condition below.

#### Example
```json
{
  "name": "Come In Normally",
  "notable": false,
  "entranceCondition": {
    "comeInNormally": {}
  },
  "requires": []
}
```

### Come In Running

A `comeInRunning` entrance condition represents the need for Samus to be able to run into the room with speed in a certain range. It has the following properties:
* _speedBooster_: If true, then Speed Booster must be used while running into the room. If false, then Speed Booster must not be used. If "any", then Speed Booster may or may not be used.
* _minTiles_: The minimum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.
* _maxTiles_: The maximum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held.

A `comeInRunning` condition can be satisfied only by a matching strat on the other side of the door with a `leaveWithRunway` exit condition: a match is valid if all of the following are true:
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

### Come In Space Jumping

A `comeInSpaceJumping` entrance condition indicates that Samus must come in with a Space Jump through the bottom of the doorway, applicable to horizontal transitions. It has the following properties:

* _speedBooster_: If true, then Speed Booster must be used while gaining run speed. If false, then Speed Booster must not be used. If "any", then Speed Booster may or may not be used.
* _minTiles_: The minimum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held on the remote runway.
* _maxTiles_: The maximum horizontal speed that will satisfy the condition, measured in effective runway tiles with dash held on the remote runway.

A `comeInSpaceJumping` entrance condition must match with a `leaveSpaceJumping` on the other side of the door. To match, the `blue` property of `leaveSpaceJumping` must be "no" or "any". This comes with an implicit `SpaceJump` item requirement.

```json
{
  "name": "Come In Space Jumping",
  "notable": false,
  "entranceCondtion": {
    "comeInSpaceJumping": {
      "speedBooster": "any",
      "minTiles": 4
    }
  },
  "requires": [
    "canCrossRoomJumpIntoWater"
  ]
}
```

### Come In Shinecharging

A `comeInShinecharging` entrance condition represents the need for Samus to run into the room with enough space to complete a shinecharge. It has the following properties describing the geometry of the runway in the current room which can be used to help complete the shinecharge (see [runway geometry](#runway-geometry) above for details):

* _length_, _openEnd_, _gentleUpTiles_, _gentleDownTiles_, _steepUpTiles_, _steepDownTiles_

The length should not include any tiles that Samus skips over through the transition (e.g. door transition tiles and door shell tiles). 

A `comeInShinecharging` must match with a corresponding `leaveWithRunway` condition on the other side of the door. 

A `comeInShinecharging` object also includes implicit requirements for actions to be performed in the previous room, which are effectively prepended to the start of the current strat's `requires` (or equivalently but more properly, onto the end of the `requires` of the `leaveWithRunway` strat in the other room):
- A `canShinecharge` requirement is included based on the combined runway length. This includes a `SpeedBooster` item requirement as well as a check that the combined runway length is long enough that charging a shinespark is possible.
- If the previous room is heated, then `heatFrames` are included based on the time spent running in that room.
- If the current room is heated, then `heatFrames` are included based on the time spent running in this room.
- If the previous door environment is water, then `Gravity` is required.

The way to calculate minimally required heat frames depends on the type of `leaveWithRunway` and on which of the two rooms (or both) are heated:

- If the `from` node of the `leaveWithRunway` is the same as the `to` node, then this represents that the runway in the other room is used starting from the door. In this case Samus will need to run in both directions. The way to calculate heat frames then depends on which rooms are heated:
  - If both rooms are heated, then it is best to use smallest amount of runway possible in the other room. If the required shinecharge tiles
  (based on the desired difficulty) is no more than the effective runway length in the current room (based on the `comeInShinecharging` properties), then there is no need to add heat frames for running in the other room. Otherwise, the amount of runway to use in the other room is the difference between the required shinecharge tiles and the effective runway length in the current room (but at least `minTiles`, if specified). The run in the other room to get positioned on the runway can be done at full speed, so the [table](#come-in-running) can be used to determine the required heat frames for this run, including heat frames for turning around and positioning. For the run back to charge the spark, there are two cases:
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

### Come In Getting Blue Speed

A `comeInGettingBlueSpeed` entrance condition represents the need for Samus to run into the room with enough space to gain blue speed. It is similar to `comeInShinecharging` and includes the same set of properties, with the following additional properties:

- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) needed at the end of the combined runway. This can be specified if something would prevent the strat from working at too low of a speed.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) needed at the end of the combined runway.  This can be specified if something would prevent the strat from working at too high of a speed.

A `comeInGettingBlueSpeed` must match with a corresponding `leaveWithRunway` condition on the other side of the door, and it includes the same requirements as a `comeInShinecharging` except with a `getBlueSpeed` requirement in place of a `canShinecharge`.

Note that a `comeInGettingBlueSpeed` entrance condition is compatible with preserving a flash suit, while `comeInShinecharging` is not.

#### Example
```json
{
  "name": "Come In Getting Blue Speed",
  "notable": false,
  "entranceCondition": {
    "comeInGettingBlueSpeed": {
      "length": 5,
      "openEnd": 1
    }
  },
  "requires": []
}
```

### Come In Shinecharged

A `comeInShinecharged` entrance condition represents the need for Samus to run or jump into the room with a shinecharge with a certain amount of time remaining before it would expire. It has the following property:

- _framesRequired_: The number of frames that must be left on the shinespark charge when coming in. This must be a value between 1 and 179. Note that the shinecharge timer begins at 180 frames, and at least one frame must elapse between obtaining the shinecharge in the other room and crossing the door transition.

A strat with a `comeInShinecharged` condition should include a `shinespark` requirement in its `requires`.

A `comeInShinecharged` must match with either a `leaveShinecharged` condition or a `leaveWithRunway` condition on the other side of the door. 

- In order for `comeInShinecharged` to have a valid match with a `leaveShinecharged` condition, the `framesRequired` in the `comeInShinecharged` must be less than or equal to the `framesRemaining` of the `leaveShinecharged` condition. Aside from this, `comeInShinecharged` condition has no implicit requirements when matched with a `leaveShinecharged` conditions: all requirements in the other room are assumed to be explicitly accounted for in the strat with the `leaveShinecharged`. The frame counts in `comeInShinecharged` and `leaveShinecharged` are based on highly skilled (but humanly viable) play; leniency could be added by adjusting these counts (to increase `framesRequired` or decrease `framesRemaining`).

- A `comeInShinecharged` condition may also match with a `leaveWithRunway` condition. In this case it is assumed that the runway in the other room is used to obtain a shinecharge just before entering the transition, with 170 frames remaining. This comes with implicit requirements for actions to be performed in the previous room:
  - A `canShinecharge` requirement is included based on the runway length. This includes a `SpeedBooster` item requirement as well as a check that the effective runway length is enough that charging a shinespark is possible.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here with `comeInShinecharged` there is no second runway to combine with. An extra 10 heat frames are assumed for leaving the room after the shinecharge is obtained.
  - If the previous door environment is water, then `Gravity` is required.

#### Position and Momentum Details

A `comeInShinecharged` object does not provide any way to specify Samus' position or momentum through the door transition, but these details can affect the execution of the strat. As a way of normalizing the requirements, we make the following assumptions:

- For a horizontal door transition, the `framesRequired` (and any other strat requirements such as heat frames) should be based on an assumption that Samus enters the room either while running or spin-jumping just before the transition, with an unspecified amount of momentum. So the requirements should be based on the worst-case scenario, which in most cases means entering the room with no momentum. If entering with a spin jump is required, keep in mind that a `comeInShinecharged` condition does not require air physics in the previous room, so the jump may be low; if a spin jump with more momentum is required then the `comeInShinechargedJumping` condition should be used.

- For an vertical door transition, the `framesRemaining` (and other strat requirements) should be based on an assumption that Samus can enter through any horizontal position of the doorway (whichever is most favorable), in a jumping or falling pose, but with an unspecified amount of horizontal and vertical momentum. The requirements should be based on the worst-case momentum scenario, which generally means entering the room with no momentum, since any unwanted vertical momentum can be cancelled by releasing jump through the transition.

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

### Come In Shinecharged Jumping

A `comeInShinechargedJumping` entrance condition represents the need for Samus to jump into the room with a shinecharge with a certain amount of time remaining before it would expire. The jump must occur from an air environment on the other side of the door. It has the following property:

- _framesRequired_: The number of frames that must be left on the shinespark charge when coming in. This must be a value between 1 and 179. Note that the shinecharge timer begins at 180 frames, and at least one frame must elapse between obtaining the shinecharge in the other room and crossing the door transition.

A strat with a `comeInShinechargedJumping` condition should include a `shinespark` requirement in its `requires`.

The conditions for `comeInShinechargedJumping` are the same as for `comeInShinecharged`, with the added condition that the other side of the door must be an air environment.

### Come In With Spark

A `comeInWithSpark` entrance condition indicates that Samus must shinespark into the room.

The `comeInWithSpark` object has the following property:
- _position_: For a horizontal transition, if specified, this takes two possible values, "top" or "bottom". The value "top" represents that the strat requires sparking through the doorway high enough to clear a single-tile block level with the bottom of the doorway. The value "bottom" represents that the strat requires sparking through the doorway low enough to clear a single-tile block level with the top of the doorway. If unspecified, it is understood that sparking in any position will work.

The direction of the spark is assumed to be horizontal when sparking through horizontal door transitions, or vertical when sparking through vertical door transitions.

A strat with a `comeInWithSpark` condition should include a `shinespark` requirement in its `requires`.

A `comeInWithSpark` condition must match with either a `leaveWithSpark`, `leaveShinecharged`, or `leaveWithRunway` condition on the other side of the door:

- A match with `leaveWithSpark` is valid as long as the `position` properties are compatible. The `position` properties of a `leaveWithSpark` and `comeInWithSpark` are compatible if they are equal or if at least one of them are unspecified.
- A match with `leaveShinecharged` is always valid.
- A match with `leaveWithRunway` comes with the following implicit requirements (the same as for `comeInShinecharged`) for actions to be performed in the previous room:
  - A `canShinecharge` requirement is included based on the runway length. This includes a `SpeedBooster` item requirement as well as a check that the effective runway length is enough that charging a shinespark is possible.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here with `comeInShinecharged` there is no second runway to combine with.
  - If the previous door environment is water, then `Gravity` is required.

In all three cases, there is an implicit requirement of `canHorizontalShinespark` when sparking through a horizontal door.

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
- A requirement `h_canBombThings`, to be able to use Bombs or a Power Bomb, as well as the tech `canBombHorizontally`.
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
- If the current room is heated and leniency is desired for failed attempts, then a minimum requirement of `{"heatFrames": 50}` should be included per potential failed attempt.
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

### Come In Speedballing

A `comeInSpeedballing` entrance condition indicates that Samus must enter the room either in a speedball from the previous room, or in a process of running, jumping, or falling into a speedball. It has the following property:

- _runway_: A [runway geometry](#runway-geometry) object describing the tiles available in the current room to complete the speedball. The end of this runway represents the point by which the speedball must be complete (i.e. when Samus must be morphed and on the ground with blue speed). A runway length of 0 would represent that the speedball must be completed before the transition.

It is assumed that the runway in the current room is level or sloping up; adjustments would be needed to handle a case where it sloped down.

Note that a `comeInSpeedballing` entrance condition can always be satisfied by coming into the room while already in a speedball. Therefore, a different entrance condition (e.g. `comeInGettingBlueSpeed` or `comeInBlueSpinning`) must be used if the strat specifically requires obtaining the speedball after entering the room (either by jumping through the transition, or by running through the transition and jumping afterward).

A `comeInSpeedballing` entrance condition must match with one of the following conditions on the other side of the door: `leaveWithRunway`, `leaveSpinning`, `leaveWithMockball`. 

In every case, there is an implicit tech requirement of `canSpeedball`. A match with a `leaveWithRunway` comes with the following implicit requirements:
  - A `speedBall` requirement based on the combined runway length.
  - If the previous door environment is water, then `Gravity` is required.
  - If the previous room is heated, then `heatFrames` are required based on the time needed. This can be calculated in the same way as for `comeInShinecharging`.

For `leaveSpinning` and `leaveWithMockball`, their `blue` property must be either "yes" or "any", and there is an implicit `getBlueSpeed` requirement based on the runway length in the exit condition.

### Come In With Temporary Blue

A `comeInWithTemporaryBlue` entrance condition indicates that Samus must come in by jumping through this door with temporary blue. It is applicable to horizontal and vertical transitions. It has the following property:
- _direction_: This takes three possible values "left", "right", and "any", indicating the direction that Samus must be facing through the transition. It should be specified for all vertical transitions but not horizontal ones.

A `comeInWithTemporaryBlue` entrance condition must match with one of the following exit conditions on the other side of the door: `leaveWithTemporaryBlue`, `leaveWithRunway`:

- To match with a `leaveWithTemporaryBlue`, its `direction` properties must equal that of `comeInWithTemporaryBlue`, unless one of them is unspecified or "any". It has an implicit tech requirement of `canTemporaryBlue`. 
- A match with `leaveWithRunway` comes with implicit requirements:
  - The tech `canTemporaryBlue`.
  - A `canShinecharge` requirement based on the runway length (including the `SpeedBooster` item requirement).
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here there is no second runway to combine with. An extra `{"heatFrames": 200}` is assumed for gaining temporary blue and leaving the room.
  - If the previous door environment is water, then `Gravity` is required.

### Come In Blue Spinning

A `comeInBlueSpinning` entrance condition indicates that Samus must come in with a spin jump through the doorway, possibly while having blue speed, applicable to horizontal transitions. It has the following properties:

- _unusableTiles_: For a runway connected to the door, the number of tiles before the door that are unusable for gaining speed, because of needing to jump.
- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) needed. This only needs to be specified if something would prevent the strat from working at too low of a speed.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) needed. This only needs to be specified if something would prevent the strat from working at too high of a speed.

A `comeInBlueSpinning` entrance condition must match with a `leaveSpinning` or `leaveWithRunway` exit condition on the other side of the door.

- A match with `leaveSpinning` has the following requirements:
  - The `blue` property must be "yes" or "any".
  - A `SpeedBooster` requirement.
  - There must exist a possible value of extra run speed satisfying any applicable constraints, including any `minExtraRunSpeed` or `maxExtraRunSpeed` properties in the entrance condition and/or exit condition, along with implicit constraints based on shortcharge skill and the effective runway length of the `remoteRunway` in the exit condition (see the [blue run speed table](#blue-run-speed-table)). Note that `unusableTiles` is ignored in this case.
- A match with `leaveWithRunway` has the following requirements:
  - There must exist a possible value of extra run speed satisfying any applicable constraints: `minExtraRunSpeed` or `maxExtraRunSpeed` in the entrance condition, along with implicit constraints based on shortcharge skill and the effective runway length (with `unusableTiles` subtracted) in the exit condition (see the [blue run speed table](#blue-run-speed-table)).
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as in `comeInShinecharging`, except here there is no second runway to combine with. The `unusableTiles` are ignored (i.e. not subtracted) for the purposes of determining heat frames, since heat damage is still taken during the jump.
  - If the previous door environment is water, then `Gravity` is required.

```json
{
  "name": "Come In Blue Spinning",
  "notable": false,
  "entranceCondtion": {
    "comeInBlueSpinning": {
      "unusableTiles": 2
    }
  },
  "requires": []
}
```

### Come In With Mockball

A `comeInWithMockball` entrance condition indicates that Samus must roll into the room in a mockball with a certain amount of momentum, applicable to horizontal transitions. It has the following properties:

- _adjacentMinTiles_: This is the minimum effective runway length in case an adjacent runway (connected to the door) is used to gain speed, jump, and enter a mockball.
- _remoteAndLandingMinTiles_: When entering a mockball, it takes some time to accelerate up to full speed, which means that even when using a remote runway (i.e. one not connected to the door) to gain speed for the jump, the amount of landing space in front of the door still matters. Depending on the strat, different combinations of remote runway and landing lengths may work (e.g. with shorter landing lengths possibly requiring longer remote runways to compensate). This property is a list of pairs, where in each pair the first value gives a minimal remote runway used to gain speed, and the second value gives the corresponding minimal amount of landing tiles in front of the door usable to gain speed at the start of the mockball. 

A `comeInWithMockball` entrance condition must match with one of the following conditions on the other side of the door: `leaveWithMockball` or `leaveWithRunway`:

- A match with `leaveWithMockball` has the following requirements:
  - The `blue` property of `leaveWithMockball` must be "no" or "any".
  - `remoteAndLandingMinTiles` must contain at least one pair `(minRemoteLength, minLandingLength)` such that the effective length of the `remoteRunway` is at least `minRemoteLength` and the effective length of the `landingRunway` is at least `minLandingLength`.
  - The `canMockball` tech (including `Morph` item).
- A match with `leaveWithRunway` has the following requirements:
  - The effective runway length must be at least `adjacentMinTiles`.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as for `comeInRunning` (and `comeInJumping`).
  - If the previous door environment is water, then `Gravity` is required.
  - The `canMockball` tech (including `Morph` item) is required.

```json
{
  "name": "Come In With Mockball",
  "notable": false,
  "entranceCondtion": {
    "comeInWithMockball": {
      "adjacentMinTiles": 11,
      "remoteAndLandingMinTiles": [[8, 2], [7, 3]]
    }
  },
  "requires": []
}
```

### Come In With Spring Ball Bounce

A `comeInWithSpringBallBounce` entrance condition indicates that Samus must enter the room by spring ball bouncing in from the previous room, applicable to horizontal transitions. It has the following properties:

- _adjacentMinTiles_: This is the minimum effective runway length in case an adjacent runway (connected to the door) is used to gain speed, jump, and bounce.
- _remoteAndLandingMinTiles_: A list of pairs, where in each pair the first value gives a minimal remote runway used to gain speed, and the second value gives the corresponding minimal amount of landing tiles in front of the door usable for the bounce.
- _movementType_: This takes one of three possible values, "controlled", "uncontrolled", and "any", indicating the type of bounce that is required.
  - "controlled" refers to movement type $12, which occurs when jumping using Spring Ball while rolling on the ground (e.g. from a mockball). In this state it is possible to control the height of each bounce by releasing jump.
  - "uncontrolled" refers to movement type $13, which occurs when performing a lateral mid-air morph high enough that the morph animation completes before landing and bouncing. This state also occurs when rolling off of a ledge (e.g. after a mockball). In this state, Samus' horizontal speed will reach a slightly higher value, and without the need for a longer landing platform to accelerate on. However, it will not be possible to control the height of the bounce.

A `comeInWithSpringBallBounce` entrance condition must match with a `leaveWithSpringBallBounce`, `leaveWithMockball`, or `leaveWithRunway` on the other side of the door. The following requirement applies in every case:
- The `canSpringBallBounce` tech (including `Morph` and `SpringBall` items) is implicitly required.

There are additional requirements depending on the exit condition:

- A match with `leaveWithSpringBallBounce` has the following additional requirements:
  - The `movementType` of the exit condition must equal that of the entrance condition, or one of them must be "any".
  - If the `movementType` of either the exit condition or entrance condition is "controlled", then `canMockball` is required.
  - `remoteAndLandingMinTiles` must contain at least one pair `(minRemoteLength, minLandingLength)` such that the effective length of the `remoteRunway` is at least `minRemoteLength` and the effective length of the `landingRunway` is at least `minLandingLength`.
  - The `blue` property of the exit condition must be "no" or "any". 
- A match with `leaveWithMockball` has the following requirements:
  - The `movementType` of the entrance condition must be "controlled" or "any".
  - The `canMockball` tech is required.
  - `remoteAndLandingMinTiles` must contain at least one pair `(minRemoteLength, minLandingLength)` such that the effective length of the `remoteRunway` is at least `minRemoteLength` and the effective length of the `landingRunway` is at least `minLandingLength`.
  - The `blue` property of the exit condition must be "no" or "any".
- A match with `leaveWithRunway` has the following requirements:
  - The effective runway length must be at least `adjacentMinTiles`.
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames are calculated the same way as for `comeInRunning` (and `comeInJumping`).
  - If the previous door environment is water, then `Gravity` is required.
  - The `canMockball` tech (including `Morph` item) is required.


```json
{
  "name": "Come In With Spring Ball Bounce",
  "notable": false,
  "entranceCondition": {
    "comeInWithSpringBallBounce": {
      "remoteAndLandingMinTiles": [[4, 1]],
      "movementType": "any"
    }
  },
  "requires": [
    "canCrossRoomJumpIntoWater"
  ]
}
```

### Come In With Blue Spring Ball Bounce

A `comeInWithBlueSpringBallBounce` entrance condition indicates that Samus must enter the room by spring ball bouncing in from the previous room, while having blue speed. This is applicable to horizontal transitions. It has the following properties:

- _minExtraRunSpeed_: The minimum extra run speed (as a hexadecimal string) needed. This only needs to be specified if something would prevent the strat from working at too low of a speed.
- _maxExtraRunSpeed_: The maximum extra run speed (as a hexadecimal string) needed.  This only needs to be specified if something would prevent the strat from working at too high of a speed.
- _minLandingTiles_: The minimum effective length of landing runway in the other room which is needed to ensure the strat can work.
- _movementType_: This takes one of three possible values, "controlled", "uncontrolled", and "any", indicating the type of bounce that is required.
  - "controlled" refers to movement type $12, which occurs when jumping using Spring Ball while rolling on the ground (e.g. from a mockball). In this state it is possible to control the height of each bounce by releasing jump.
  - "uncontrolled" refers to movement type $13, which occurs when performing a lateral mid-air morph high enough that the morph animation completes before landing and bouncing. This state also occurs when rolling off of a ledge (e.g. after a mockball). In this state, Samus' horizontal speed will reach a slightly higher value, and without the need for a longer landing platform to accelerate on. However, it will not be possible to control the height of the bounce.

A `comeInWithBlueSpringBallBounce` entrance condition must match with a `leaveWithSpringBallBounce`, `leaveWithMockball`, or `leaveWithRunway` on the other side of the door. The following requirement applies in every case:
- The `canSpringBallBounce` tech (including `Morph` and `SpringBall` items).
- The `Speedbooster` item.
- There must exist a possible value of extra run speed satisfying any applicable constraints, including any `minExtraRunSpeed` or `maxExtraRunSpeed` properties in the entrance condition and/or exit condition, along with implicit constraints based on shortcharge skill and the effective runway length of the runway in the exit condition (see the [blue run speed table](#blue-run-speed-table)).

There are additional requirements depending on the exit condition:

- A match with `leaveWithBlueSpringBallBounce` has the following additional requirements:
  - The `movementType` of the exit condition must equal that of the entrance condition, or one of them must be "any".
  - If the `movementType` of either the exit condition or entrance condition is "controlled", then `canSpeedball` is required.
  - The effective length of the `landingRunway` is at least `minLandingLength` (if specified).
  - The `blue` property of the exit condition must be "yes" or "any". 
  - A `getBlueSpeed` requirement is included based on the remote runway length.
- A match with `leaveWithMockball` has the following requirements:
  - The `movementType` of the entrance condition must be "controlled" or "any".
  - The `canSpeedball` tech is required.
  - The effective length of the `landingRunway` is at least `minLandingLength` (if specified).
  - The `blue` property of the exit condition must be "yes" or "any".
  - A `getBlueSpeed` requirement is included based on the remote runway length.
- A match with `leaveWithRunway` has the following requirements:
  - A `speedBall` requirement is included based on the runway length minus `minLandingLength`, except that the `canSpeedball` tech requirement is only included if the `movementType` of the entrance condition is "controlled".
  - If the previous room is heated, then `heatFrames` are included based on the time spent running in that room. The minimally required heat frames can be approximately calculated in the same way as for `comeInGettingBlueSpeed`.
  - If the previous door environment is water, then `Gravity` is required.

```json
{
  "name": "Come In With Blue Spring Ball Bounce",
  "notable": false,
  "entranceCondition": {
    "comeInWithBlueSpringBallBounce": {
      "remoteAndLandingMinTiles": [[15, 1]],
      "movementType": "controlled"
    }
  },
  "requires": []
}
```

### Come In With Stored Fall Speed

A `comeInWithStoredFallSpeed` entrance condition represents that Samus can enter through this door with stored fall speed. 

The `comeInWithStoredFallSpeed` object has a single property:
- _fallSpeedInTiles_: The number of tiles Samus would clip through by Moonfalling on top of a solid floor.

A `comeInWithStoredFallSpeed` entrance condition must match with a `leaveWithStoredFallSpeed` condition on the other side of the door.  The `comeInWithStoredFallSpeed` can lead to another `leaveWithStoredFallSpeed` so long as the stored speed is not lost.  For this to happen, both doors must be connected by one `Runway`, and Samus must not Crouch or become Knocked back.  A strat with a `comeInWithStoredFallSpeed` condition should only include requirements needed to position Samus for the clip.

*Note*: There is an implicit `canMoonfall` requirement on strats which have the `comeInWithStoredFallSpeed` condition as a means of using the stored fall speed.

#### Example
```json
{
  "name": "Stored Fall Speed Clip",
  "notable": false,
  "entranceCondtion": {
    "comeInWithStoredFallSpeed": {
      "fallSpeedInTiles": 1
    }
  },
  "requires": []
}
```
### Come In With R-Mode

A `comeInWithRMode` entrance condition indicates that Samus must obtain R-mode while coming through this door.

A `comeInWithRMode` object does not have any properties.

A `comeInWithRMode` entrance condition must match with a `leaveWithGModeSetup` entrance condition on the other side of the door. It comes with the following implicit requirements:
- The tech requirement `canEnterRMode`.
- The `XRayScope` item requirement.
- A requirement to have at least 1 reserve energy.
- A requirement to damage down to 0 energy, triggering reserves (causing the reserve energy to become zero and the regular energy to become what the reserve energy was).

```json
{
  "name": "Red Tower R-Mode Frozen Beetom X-Ray Climb",
  "notable": true,
  "entranceCondition": {
    "comeInWithRMode": {}
  },
  "requires": [
    "canWalljump",
    {"enemyDamage": {
      "enemy": "Beetom",
      "type": "contact",
      "hits": 1
    }},
    {"enemyDamage": {
      "enemy": "Ripper",
      "type": "contact",
      "hits": 1
    }},
    "canWallIceClip",
    "canXRayClimb"
  ]
}
```

### Come In With G-Mode

A `comeInWithGMode` entrance condition indicates that Samus must have or obtain G-mode (direct or indirect) while coming through this door. 

A `comeInWithGMode` object has the following properties:
* _mode_: Takes one of three possible values, "direct", "indirect", or "any", indicating whether Samus must enter in direct G-mode, indirect G-mode, or either. Direct G-mode is the state obtained when G-mode is first entered (i.e., the next room after the G-mode setup is performed), while indirect G-mode is the state after passing a door transition with G-mode (usually back into the room where the G-mode setup was performed).
* _morphed_: A boolean indicating whether Samus must enter the room in a morphed state. This can be satisfied by obtaining or already being in an artificially morphed state, or by having collected the Morph item.
* _mobility_: Takes one of three possible values, "mobile", "immobile", or "any", indicating whether or not Samus is
required to be mobile (or immobile) after entering the room. The default value is "any". When entering with indirect G-mode, Samus is always mobile. With direct G-mode, Samus can be mobile if she takes knockback through the door transition and the reserve energy is low enough (<= 4 energy) so that knockback frames do not expire until after reserves finish filling.

A `comeInWithGMode` entrance condition must match with either a `leaveWithGModeSetup` or `leaveWithGMode` entrance condition on the other side of the door:
- If `mode` is "direct", then it can only match with a `leaveWithGModeSetup`. If `mode` is "indirect", then it can only match with a `leaveWithGMode`.

When matching with a `leaveWithGModeSetup`, a `comeInWithGMode` has implicit requirements:
- The tech requirement `canEnterGMode`.
- The `XRayScope` item requirement.
- A requirement to have at least 1 reserve energy.
- A requirement to damage down to 0 energy, triggering reserves (causing the reserve energy to become zero and the regular energy to become what the reserve energy was).
- The requirement `{"or": ["Morph", "canArtificialMorph"]}`, if the `morphed` property of `comeInWithGMode` is true.
- The Toilet must not come between the room with the `leaveWithGModeSetup` and the `comeInWithGMode`, because obtaining direct G-mode in the Toilet is not possible, due to Samus not having an ability to use X-Ray while entering the room.
- Requirements for regaining mobility (there may be multiple options here, and they should be treated either as separate strats or the requirements should be joined as though with an `or`):
  - G-mode mobile: Samus uses the knockback from the previous room to retain mobility. Here the `knockback` property of the `leaveWithGModeSetup` must be true, and reserve energy is assumed to have been drained to at most 4 before doing the strat.
  - G-mode immobile: Samus uses knockback from a hit in the current room to regain mobility. The possibility of doing this is indicated by the presence of a strat with a `gModeRegainMobility` property with `from` and `to` node matching entrance/door node of the current strat (the `from` node of the strat with `comeInWithGMode`). Any requirements of the `gModeRegainMobility` strat should be included as requirements to execute the current strat; it is important that these requirements be applied *after* the requirement to damage down to 0 energy and trigger reserves. If there are multiple such `gModeRegainMobility` strats, then these should be treated as multiple options.

When matching with a `leaveWithGMode`, a `comeInWithGMode` has an implicit requirement in one scenario:
- If `morphed` property of `comeInWithGMode` is true but a matching `leaveWithGMode` has `morphed` false, then the `Morph` item is implicitly required.

__Example:__
```json
{
  "name": "G-Mode Morph",
  "entranceCondition": {
    "comeInWithGMode": {
      "mode": "any",
      "morphed": true
    }
  },
  "requires": []
}
```

### Come In With Wall Jump Below

A `comeInWithWallJumpBelow` entrance condition indicates that Samus must come up through this door with momentum by wall-jumping in the door frame below.

A `comeInWithWallJumpBelow` object has the following property:

- _minHeight_: Minimum height of door frame (tiles below the transition tiles) that will satisfy the condition.

A `comeInWithWallJumpBelow` entrance condition must match with a `leaveWithDoorFrameBelow` exit condition on the other side of the door:
- A match is valid provided the `height` property on the `leaveWithDoorFrameBelow` is at least as large as the `minHeight` property on the `comeInWithWallJumpBelow`.

A `comeInWithWallJumpBelow` implicitly includes a `canWalljump` tech requirement.

__Example:__
```json
{
  "name": "Cross Room Jump - Wall Jump",
  "entranceCondition": {
    "comeInWithWallJumpBelow": {
      "minHeight": 2
    }
  },
  "requires": [
    "canCrossRoomJumpIntoWater"
  ]
}
```

### Come In With Space Jump Below

A `comeInWithSpaceJumpBelow` entrance condition indicates that Samus must come up through this door with momentum by using Space Jump in the door frame below. It has no properties.

A `comeInWithSpaceJumpBelow` entrance condition must match with a `leaveWithDoorFrameBelow` exit condition on the other side of the door.

A `comeInWithSpaceJumpBelow` implicitly includes a `SpaceJump` item requirement. If the room below is heated, then a requirement of `{"heatFrames": 30}` is implicitly included.

__Example:__
```json
{
  "name": "Cross Room Jump - Space Jump",
  "entranceCondition": {
    "comeInWithSpaceJumpBelow": {}
  },
  "requires": [
    "canCrossRoomJumpIntoWater"
  ]
}
```

### Come In With Platform Below

A `comeInWithPlatformBelow` entrance condition indicates that Samus must come up through this door with momentum by jumping from a platform below, possibly with run speed. It has the following properties:

* _minHeight:_ Minimum height of the platform below that can satisfy this condition. It expresses that the platform must be positioned at least a certain distance below the door transition (in tiles, not including the transition tiles or platform tiles).
* _maxHeight:_ Maximum height of the platform below that can satisfy this condition. It expresses that the platform must be positioned at most a certain distance below the door transition.
* _maxLeftPosition:_ Maximum value of "leftPosition" of the platform below that can satisfy this condition. It expresses that the platform extends at least a certain distance to the left (in tiles, relative to the center of the door, with negative values indicating a position to the left of the door center).
* _minRightPosition:_ Minimum value of "rightPosition" of the platform below that can satisfy this condition. It expresses that the platform extends at least a certain distance to the right (in tiles, relative to the center of the door, with negative values indicating a position to the left of the door center).

A `comeInWithPlatformBelow` entrance condition must match with a `leaveWithPlatformBelow` exit condition on the other side of the door. A match is valid provided the `height`, `leftPosition`, and `rightPosition` properties on the `leaveWithDoorFrameBelow` satisfy all applicable constraints indicated by properties in the `comeInWithPlatformBelow`:
$$\text{minHeight} \leq \text{height} \leq \text{maxHeight}$$
$$\text{leftPosition} \leq \text{maxLeftPosition}$$
$$\text{rightPosition} \geq \text{minRightPosition}$$

A `comeInWithPlatformBelow` entrance condition has no implicit requirements.

__Example:__
```json
{
  "name": "Cross Room Jump - Standing Jump",
  "entranceCondition": {
    "comeInWithPlatformBelow": {
      "minHeight": 6,
      "maxHeight": 6,
      "maxLeftPosition": 1,
      "minRightPosition": 2
    }
  },
  "requires": [
    "canCrossRoomJumpIntoWater"
  ]
}
```


### Come In With Grapple Teleport

A `comeInWithGrappleTeleport` entrance condition represents that Samus must come into the room while grappling, teleporting Samus to a position in this room corresponding to the location of the (grapple) block in the other room.

A `comeInWithGrappleTeleport` object has the following property:

- _blockPositions_: A list of tile coordinates of (grapple) blocks that Samus could be grappled to while exiting the other room. Coordinates `[x, y]` are represented as tile counts with `[0, 0]` representing the top-left corner of the room.

A `comeInWithGrappleTeleport` comes with an implicit tech requirement `canGrappleTeleport`.

#### Example
```json
{
  "name": "Come in With Grapple Teleport",
  "requires": [],
  "exitCondition": {
    "leaveWithGrappleTeleport": {
      "blockPositions": [[5, 3]]
    }
  }
}
```

### Comes Through Toilet

Inside an `entranceCondition` object, a `comesThroughToilet` property indicates if the strat is applicable when the Toilet comes between this room and the other room (one with a matching `exitCondition`). This property should be specified on every strat having an `entranceCondition` through a vertical transition. It has three possible values:

- "yes": The strat is applicable only if the Toilet comes between this room and the other room.
- "no": The strat is applicable only if the Toilet *does not* come between this room and the other room.
- "any": The strat is applicable regardless of whether the Toilet comes between this room and the other room.

### Example
```json
{
  "name": "Cross Room Jump - Toilet HiJump Wall Jump",
  "entranceCondition": {
    "comeInWithWallJumpBelow": {
      "minHeight": 2
    },
    "comesThroughToilet": "yes"
  },
  "requires": [
    "canCrossRoomJumpIntoWater",
    "HiJump",
    "canPreciseWalljump",
    "canDownGrab"
  ]
}
```

## G-Mode Regain Mobility

A `gModeRegainMobility` property on a strat indicates that the strat allows Samus to regain mobility (by taking knockback from an enemy) after entering with G-mode immobile. In all strats with a `gModeRegainMobility` property, the `from` node of the strat must be the same as the `to` node and must be a door or entrance node. A strat with `gModeRegainMobility` should normally include an `enemyDamage` requirement in its `requires`.

A `gModeRegainMobility` object has no properties.

### Example
```json
{
  "name": "G-Mode Regain Mobility",
  "notable": false,
  "requires": [
    "h_ZebesIsAwake",
    {"enemyDamage": {
      "enemy": "Geemer (blue)",
      "type": "contact",
      "hits": 1
    }}
  ],
  "gModeRegainMobility": {}
}
```

## Bypasses Door Shell

A `bypassesDoorShell` property on a strat indicates that Samus can leave through the door transition in the `to` node
without first unlocking or opening the door. For this to be valid, the `to` node must have `"nodeType": "door"`. This can be used even for doors that are easy to open (e.g. blue doors), to support randomizers that may alter door colors. A strat with `"bypassesDoorShell": true` may also have an exit condition, but it is not required to have one.

A strat with `"bypassesDoorShell": true` has an implicit tech requirement of `canSkipDoorLock`.

### Example
```json
{
  "name": "Bypass Door Shell",
  "notable": false,
  "requires": [
    "canWallIceClip"
  ],
  "bypassesDoorShell": true
}
```

## Unlocks Doors

An `unlocksDoors` array lists possibilities of doors that can be unlocked as part of executing this strat. The objects in the array have the following properties:

- _nodeId_: The node ID of the door that can be unlocked. If unspecified, it is assumed to be the destination node of the strat.
- _types_: A list of door unlock types, among "missiles", "super", "powerbomb", "gray", "gadoraMissiles" and "gadoraSuper":
    - "missiles": A door which can be opened using 5 Missiles, e.g. red doors.
    - "super": A door which can be opened using a single Super, e.g. red or green doors.
    - "powerbomb": A door which can be opened using a single Power Bomb, e.g. a yellow door.
    - "ammo": A door which can be opened with ammo. This is a shorthand for ["missiles", "super", "powerbomb"].
    - "gadoraMissiles": A gadora eye door which is opened using 3 Missiles.
    - "gadoraSuper": A gadora eye door which is opened using a single Super.
- _requires_: A list of additional logical requirements which must be satisfied in order for the door to be unlocked using this strat. 
- _useImplicitRequires_: A boolean, true by default, indicating whether standard requirements should be implicitly appended to the `requires` in this object. This can be set this to false if the standard requirements are already accounted for in the strat `requires`, for example if the strat involves using a Power Bomb which would already unlock the door as a side effect, or if it uses a Super as a hero shot to open the door. If this property is set to true, the implicit standard requirements are based on the door type, as follows:
    - For "missiles", the implicit requirement is `{"ammo": {"type": "Missile", "count": 5}}`.
    - For "super", the implicit requirement is `{"ammo": {"type": "Super", "count": 1}}`.
    - For "powerbomb", the implicit requirement is `h_canUsePowerBombs`.
    - For "gadoraMissiles", the implicit requirement is `{"ammo": {"type": "Missile", "count": 3}}`.
    - For "gadoraSuper", the implicit requirement is `{"ammo": {"type": "Super", "count": 1}}`.
    
In general the `requires` in an `unlocksDoors` object do not need to be satisfied in order to perform the strat; if satisfied, they provide a way to unlock the door. However, if the strat has a [`doorUnlockedAtNode`](logicalRequirements.md#doorunlockedatnode-object) requirement and the door is locked, then these requirements become part of the strat requirements; this applies, in particular, if the strat has an exit condition, in which case there is an implicit `doorUnlockedAtNode` requirement on the destination door except if [`bypassesDoorShell`](strats.md#bypasses-door-shell) is set to `true`.

If an `unlocksDoors` property is not specified, then it is assumed to be an empty array. If a strat has any `doorUnlockedAtNode` requirements (including an implicit one based on having an exit condition without a `bypassesDoorShell`), then the `unlocksDoors` property should be specified explicitly and include items for each of the three possible types "missiles", "super", and "powerbomb" (or the catch-all "any") for each applicable node. The only exception is if the strat has no entrance condition then the starting node of the strat does not need to be included in the `unlocksDoors` property; in this case, the door could be unlocked immediately prior to the strat being executed (e.g. by an implicit unlock strat; see below), so generally it would not be necessary to describe how to unlock it as part of the strat. Where applicable, cases should be included for all three main types of door unlock methods, "missiles", "super", and "powerbomb" (or using "ammo" as a catch-all), in order to support randomizers which may modify the door colors. Currently the inclusion of "gadoraMissiles" and "gadoraSuper" are optional, and cross-room strats going through them are not usable unless the door has previously been unlocked.

When using this data to support vanilla door colors, which are specified by their `nodeSubType`, the door is required to be unlocked with an `unlocksDoors` object if and only if there is no `locks` property with a `lockType` of `coloredDoor` specified; otherwise the strats included in the `locks` should be used.

### Implicit Unlock Strats

By default every door node has an implicit strat from the node to itself, for unlocking the door in a standard way. In an unheated room, this implicit strat has an `unlocksDoors` of the following form:

```json
{
  "link": [1, 1],
  "name": "Unlock Door",
  "requires": [],
  "unlocksDoors": [
    {"types": ["ammo"], "requires": []},
    {"types": ["gadoraMissiles"], "requires": []},
    {"types": ["gadoraSuper"], "requires": []}
  ]
}
```

In a heated room, it instead has the form:

```json
{
  "link": [1, 1],
  "name": "Unlock Door",
  "requires": [],
  "unlocksDoors": [
    {"types": ["missiles"], "requires": [{"heatFrames": 50}]},
    {"types": ["super"], "requires": []},
    {"types": ["powerbomb"], "requires": [{"heatFrames": 110}]},
    {"types": ["gadoraMissiles"], "requires": [{"heatFrames": 300}]},
    {"types": ["gadoraSuper"], "requires": [{"heatFrames": 100}]}
  ]
}
```

The implicit unlock strats can be disabled by setting the node property `useImplicitDoorUnlocks` to false.

## Collects Items

A `collectsItems` array lists the node IDs (within the room) of items that become collected (if not already collected) as part of executing this strat. This can be useful, for example, for strats that use G-mode to "remote acquire" items at a location different from the item node.

For items collected in this way, the `locks` property of the item node plays no role, so the strat `requires` must include any necessary requirements to ensure the item has spawned.

```json
{
  "link": [1, 2],
  "name": "G-Mode Remote Acquire Item",
  "requires": [],
  "collectsItems": [3]
}
```

## Sets Flags

A `setsFlags` array lists the names of game flags that become set (if not already set) as part of executing this strat.

```json
{
  "link": [5, 6],
  "name": "Break the Tube",
  "requires": [
    "h_canUsePowerBombs"
  ],
  "setsFlags": ["f_MaridiaTubeBroken"]
}
```

## Run Speed

There are many kinds of cross-room strats that require Samus to enter the room with a certain amount of speed. For easier interpretation, these requirements are usually specified in terms of runway tiles required. In certain situations, however, it is necessary to directly reference speed values. There are several types of Samus horizontal speed:

- Base speed: This gradually increases from to $0.0 to $2.C over the first 11 frames of Samus beginning walking or running. It gradually decreases to $0.0 when stopping holding forward while walking/running. Base speed will change in certain ways when Samus jumps, breaks spin, morphs, or performs other actions.
- Extra run speed: This increases by $0.1 for each frame that dash is held while running. With Speed Booster it reaches a maximum value of $7.0, while without Speed Booster it reaches a maximum value of $2.0. When stopping holding forward while walking/running, the extra run speed is immediately converted into base speed, i.e., base speed is increased by the value of the extra run speed, while the extra run speed immediately becomes zero. Other actions will either leave the extra run speed unchanged (e.g., jumping, breaking spin with jump held, or performing an airball or mockball) or immediately set it to zero (e.g., turning around, or breaking spin without jump held).
- Combined run speed: This is the total of base speed and extra run speed, and represents the actual amount that Samus will move horizontally.

All these speed values are measured in pixels (and subpixels) per frame. Since extra run speed remains stable through various movement actions, it is generally the more useful quantity to reference in cross-room strats. The following table shows how Samus' relative position and horizontal speeds change while running, starting from a stand, with dash held the entire time, with Speedbooster equipped. 

| Frame | Position | Base Speed | Extra Run Speed |
| ----- | -------- | ---------- | --------------- |
| 0     |  $0.0    |    $0.0     |      $0.0       |
| 1     |  $1.0    |    $0.0     |      $0.0       |
| 2     |  $1.4    |    $0.3     |      $0.1       |
| 3     |  $1.C    |    $0.6     |      $0.2       |
| 4     |  $2.8    |    $0.9     |      $0.3       |
| 5     |  $3.8    |    $0.C     |      $0.4       |
| 6     |  $4.C    |    $0.F     |      $0.5       |
| 7     |  $6.4    |    $1.2     |      $0.6       |
| 8     |  $8.0    |    $1.5     |      $0.7       |
| 9     |  $A.0    |    $1.8     |      $0.8       |
| 10    |  $C.4    |    $1.B     |      $0.9       |
| 11    |  $E.C    |    $1.E     |      $0.A       |
| 12    |  $12.3   |    $2.C     |      $0.B       |
| 13    |  $15.B   |    $2.C     |      $0.C       |
| 14    |  $19.4   |    $2.C     |      $0.D       |
| 15    |  $1C.E   |    $2.C     |      $0.E       |
| 16    |  $20.9   |    $2.C     |      $0.F       |
| 17    |  $24.5   |    $2.C     |      $1.0       |
| 18    |  $28.2   |    $2.C     |      $1.1       |
| 19    |  $2C.0   |    $2.C     |      $1.2       |
| 20    |  $2F.F   |    $2.C     |      $1.3       |
| 21    |  $33.F   |    $2.C     |      $1.4       |
| 22    |  $38.0   |    $2.C     |      $1.5       |
| 23    |  $3C.2   |    $2.C     |      $1.6       |
| 24    |  $40.5   |    $2.C     |      $1.7       |
| 25    |  $44.9   |    $2.C     |      $1.8       |
| 26    |  $48.E   |    $2.C     |      $1.9       |
| 27    |  $4D.4   |    $2.C     |      $1.A       |
| 28    |  $51.B   |    $2.C     |      $1.B       |
| 29    |  $56.3   |    $2.C     |      $1.C       |
| 30    |  $5A.C   |    $2.C     |      $1.D       |
| 31    |  $5F.6   |    $2.C     |      $1.E       |
| 32    |  $64.1   |    $2.C     |      $1.F       |
| 33    |  $68.D   |    $2.C     |      $2.0       |
| 34    |  $6D.A   |    $2.C     |      $2.1       |
| 35    |  $72.8   |    $2.C     |      $2.2       |
| 36    |  $77.7   |    $2.C     |      $2.3       |
| 37    |  $7C.7   |    $2.C     |      $2.4       |
| 38    |  $81.8   |    $2.C     |      $2.5       |
| 39    |  $86.A   |    $2.C     |      $2.6       |
| 40    |  $8B.D   |    $2.C     |      $2.7       |
| 41    |  $91.1   |    $2.C     |      $2.8       |
| 42    |  $96.6   |    $2.C     |      $2.9       |
| 43    |  $9B.C   |    $2.C     |      $2.A       |
| 44    |  $A1.3   |    $2.C     |      $2.B       |
| 45    |  $A6.B   |    $2.C     |      $2.C       |
| 46    |  $AC.4   |    $2.C     |      $2.D       |
| 47    |  $B1.E   |    $2.C     |      $2.E       |
| 48    |  $B7.9   |    $2.C     |      $2.F       |
| 49    |  $BD.5   |    $2.C     |      $3.0       |
| 50    |  $C3.2   |    $2.C     |      $3.1       |
| 51    |  $C9.0   |    $2.C     |      $3.2       |
| 52    |  $CE.F   |    $2.C     |      $3.3       |
| 53    |  $D4.F   |    $2.C     |      $3.4       |
| 54    |  $DB.0   |    $2.C     |      $3.5       |
| 55    |  $E1.2   |    $2.C     |      $3.6       |
| 56    |  $E7.5   |    $2.C     |      $3.7       |
| 57    |  $ED.9   |    $2.C     |      $3.8       |
| 58    |  $F3.E   |    $2.C     |      $3.9       |
| 59    |  $FA.4   |    $2.C     |      $3.A       |
| 60    |  $100.B  |    $2.C     |      $3.B       |
| 61    |  $107.3  |    $2.C     |      $3.C       |
| 62    |  $10D.C  |    $2.C     |      $3.D       |
| 63    |  $114.6  |    $2.C     |      $3.E       |
| 64    |  $11B.1  |    $2.C     |      $3.F       |
| 65    |  $121.D  |    $2.C     |      $4.0       |
| 66    |  $128.A  |    $2.C     |      $4.1       |
| 67    |  $12F.8  |    $2.C     |      $4.2       |
| 68    |  $136.7  |    $2.C     |      $4.3       |
| 69    |  $13D.7  |    $2.C     |      $4.4       |
| 70    |  $144.8  |    $2.C     |      $4.5       |
| 71    |  $14B.A  |    $2.C     |      $4.6       |
| 72    |  $152.D  |    $2.C     |      $4.7       |
| 73    |  $15A.1  |    $2.C     |      $4.8       |
| 74    |  $161.6  |    $2.C     |      $4.9       |
| 75    |  $168.C  |    $2.C     |      $4.A       |
| 76    |  $170.3  |    $2.C     |      $4.B       |
| 77    |  $177.B  |    $2.C     |      $4.C       |
| 78    |  $17F.4  |    $2.C     |      $4.D       |
| 79    |  $186.E  |    $2.C     |      $4.E       |
| 80    |  $18E.9  |    $2.C     |      $4.F       |
| 81    |  $196.5  |    $2.C     |      $5.0       |
| 82    |  $19E.2  |    $2.C     |      $5.1       |
| 83    |  $1A6.0  |    $2.C     |      $5.2       |
| 84    |  $1AD.F  |    $2.C     |      $5.3       |
| 85    |  $1B5.F  |    $2.C     |      $5.4       |
| 86    |  $1BE.0  |    $2.C     |      $5.5       |
| 87    |  $1C6.2  |    $2.C     |      $5.6       |
| 88    |  $1CE.5  |    $2.C     |      $5.7       |
| 89    |  $1D6.9  |    $2.C     |      $5.8       |
| 90    |  $1DE.E  |    $2.C     |      $5.9       |
| 91    |  $1E7.4  |    $2.C     |      $5.A       |
| 92    |  $1EF.B  |    $2.C     |      $5.B       |
| 93    |  $1F8.3  |    $2.C     |      $5.C       |
| 94    |  $200.C  |    $2.C     |      $5.D       |
| 95    |  $209.6  |    $2.C     |      $5.E       |
| 96    |  $212.1  |    $2.C     |      $5.F       |
| 97    |  $21A.D  |    $2.C     |      $6.0       |
| 98    |  $223.A  |    $2.C     |      $6.1       |
| 99    |  $22C.8  |    $2.C     |      $6.2       |
| 100   |  $235.7  |    $2.C     |      $6.3       |
| 101   |  $23E.7  |    $2.C     |      $6.4       |
| 102   |  $247.8  |    $2.C     |      $6.5       |
| 103   |  $250.A  |    $2.C     |      $6.6       |
| 104   |  $259.D  |    $2.C     |      $6.7       |
| 105   |  $263.1  |    $2.C     |      $6.8       |
| 106   |  $26C.6  |    $2.C     |      $6.9       |
| 107   |  $275.C  |    $2.C     |      $6.A       |
| 108   |  $27F.3  |    $2.C     |      $6.B       |
| 109   |  $288.B  |    $2.C     |      $6.C       |
| 110   |  $292.4  |    $2.C     |      $6.D       |
| 111   |  $29B.E  |    $2.C     |      $6.E       |
| 112   |  $2A5.9  |    $2.C     |      $6.F       |
| 113   |  $2AF.5  |    $2.C     |      $7.0       |

Without Speedbooster, the same table is also valid up through row 33 (when extra run speed reaches $2.0).

# Full run speed table

The following table shows the maximum extra run speed attainable with a last-frame jump from a given runway length, with a closed end at the start and an open end before the jump, with Speedbooster equipped and holding dash the entire time:

| Runway length | Extra run speed |
| ------------- | --------------- |
| 1             |      $0.A       |
| 2             |      $0.E       |
| 3             |      $1.2       |
| 4             |      $1.6       |
| 5             |      $1.A       |
| 6             |      $1.E       |
| 7             |      $2.1       |
| 8             |      $2.4       |
| 9             |      $2.7       |
| 10            |      $2.A       |
| 11            |      $2.D       |
| 12            |      $3.0       |
| 13            |      $3.3       |
| 14            |      $3.5       |
| 15            |      $3.8       |
| 16            |      $3.A       |
| 17            |      $3.D       |
| 18            |      $3.F       |
| 19            |      $4.2       |
| 20            |      $4.4       |
| 21            |      $4.6       |
| 22            |      $4.8       |
| 23            |      $4.A       |
| 24            |      $4.D       |
| 25            |      $4.F       |
| 26            |      $5.1       |
| 27            |      $5.3       |
| 28            |      $5.5       |
| 29            |      $5.7       |
| 30            |      $5.9       |
| 31            |      $5.B       |
| 32            |      $5.C       |
| 33            |      $5.E       |
| 34            |      $6.0       |
| 35            |      $6.2       |
| 36            |      $6.4       |
| 37            |      $6.5       |
| 38            |      $6.7       |
| 39            |      $6.9       |
| 40            |      $6.B       |
| 41            |      $6.C       |
| 42            |      $6.E       |
| 43+           |      $7.0       |

Without Speed Booster, the same table is valid except that extra run speed is capped at $2.0.

### Blue run speed table

Calculating attainable run speed becomes more complex when using a runway to gain blue speed state before jumping, e.g. to be able to destroy bomb blocks and enemies on contact. The amount of speed obtained can depend on how the shortcharge is executed as well as the length of runway used. Lowest speed can be achieved by pressing dash only with crisp taps on the 4 magic frames, in order to minimize the time that dash is held; given a limited length of runway, stutters also help to reset Samus' base speed at the start of the run. High speed can be achieved by again using stutters and crisp taps, but with as few taps as necessary, holding dash continuously at the end of the run, starting as soon as possible while still getting blue before the end of the runway. We define several levels of shortcharging skill:

| Difficulty level | Minimal shortcharge length | Description                                                        |
| ---------------- | -------------------------- | ------------------------------------------------------------------ |
|        A         |             25             | No stutter, 1-tap held at least 15 frames before first magic frame |
|        B         |             20             | Single stutter, up to 2-tap, taps at least 11 frames each          |
|        C         |             16             | Single stutter, up to 3-tap, taps at least 7 frames each           |
|        D         |             15             | Single stutter, up to 4-tap, taps at least 5 frames each           |
|        E         |             14             | Double stutter, up to 4-tap, taps at least 4 frames each           |
|        F         |             13             | Triple stutter, up to 4-tap, taps at least 3 frames each           |
|        G         |             11             | Near-perfect stutters and taps                                     |

Based on these definitions and some testing, we can determine a range of attainable run speed for each combination of runway length and skill level. For each runway length, we define an "ideal speed" to be the extra run speed that would result by performing the shortcharge in the easiest possible way for that length of runway, i.e. using the techniques in the lowest possible difficulty level. For each difficulty level at or above that level, we then measure a maximum speed reasonably attainable using those techniques. The following table shows possible values for representative runway lengths; values for other runway lengths can be obtained by linearly interpolating the values in this table. All speed values refer to extra run speed:

| Runway length | Ideal speed  |  A   |  B   |  C   |  D   |  E   |  F   |  G   |
| ------------- | ------------ | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
|      30       |     $5.9     | $5.9 | $5.9 | $5.9 | $5.9 | $5.9 | $5.9 | $5.9 |
|      25       |     $4.8     | $4.9 | $4.B | $4.C | $4.D | $4.E | $4.E | $4.E |
|      20       |     $3.7     |  -   | $3.A | $3.C | $3.E | $4.0 | $4.1 | $4.2 |
|      17       |     $1.E     |  -   |  -   | $2.9 | $2.D | $3.3 | $3.8 | $3.A |
|      16       |     $1.B     |  -   |  -   | $2.3 | $2.B | $3.1 | $3.3 | $3.5 |
|      15       |     $1.6     |  -   |  -   |  -   | $1.B | $2.9 | $2.B | $2.F |
|      14       |     $1.2     |  -   |  -   |  -   |  -   | $1.A | $2.4 | $2.A |
|      13       |     $1.0     |  -   |  -   |  -   |  -   |  -   | $1.2 | $1.E |
|      12       |     $0.B     |  -   |  -   |  -   |  -   |  -   |   -  | $0.B |
|      11       |     $0.7     |  -   |  -   |  -   |  -   |  -   |  -   | $0.7 |
