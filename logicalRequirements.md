# Logical Requirements
Logical requirements are an important part of this project. They are used to represent any and all conditions Samus needs to fulfill to be able to perform actions. This can include having items, performing techs, and consuming ammo or health.

## Structure
A logical requirement is an array of logical elements, which are implicitly linked by a logical AND. Those logical elements can be a number of things:
* _The name of a helper._ Helpers are defined in [helpers.json](helpers.json) and they themselves represent a logical requirement. Those exist to reduce duplication and make logical requirements more readable. By convention, a helper's name should start with `h_`.
* _The name of a tech._ Techs are defined in [tech.json](tech.json).  Those represent a technique that players can perform, which may also imply logical requirements of their own. By convention, a tech's name should start with `can`.
* _The name of an item._ Those are defined in [items.json](items.json).
* _The name of a game flag._ Those are defined in [items.json](items.json), and are used to represent game events such as defeating a boss, or breaking the Maridia tube. By convention, a game flag's name should start with `f_`.
* _"never"._ This indicates a logical element that cannot be fulfilled under any conditions.
* More complex elements which will be defined in their own sub-sections

### Structural Logical Elements
Structural logical elements are arrays of other logical elements, and are fulfilled by fulfilling a given amount of those

#### and object
An `and` object is fulfilled only if all of the logical elements it contains are fulfilled

__Example:__
```json
{"and": [
  "canTunnelCrawl",
  "ScrewAttack"
]}
```

#### or object
An `or` object is fulfilled if at least one of the logical elements it contains is fulfilled

__Example:__
```json
{"or": [
  "canSwim",
  "canSuitlessMaridia"
]}
```

### Ammo Management Objects
This section contains logical elements that are fulfilled by spending ammo. Encountering many of those successively without having a chance to refill can impact how many power bomb/missile/super tanks can be required to get through.

#### ammo object
An `ammo` object represents the need for Samus to spend a set amount of a specific ammo. It can have the following properties:
* _type:_ The type of ammo to spend. Can have the following values:
  * PowerBomb
  * Missile
  * Super
* _count:_ The amount of ammo to spend

__Example:__
```json
{"ammo": {
  "type": "PowerBomb",
  "count": 1
}}
```

#### ammoDrain object
An `ammoDrain` object works very much like `ammo`, except that spending the ammo isn't mandatory. The ammo is just always spent if it's there. This has the same properties as an `ammo` object.

__Example:__
```json
{"ammoDrain": {
  "type": "Missile",
  "count": 75
}}
```

__Additional considerations__

Whenever an `ammoDrain` object is part of a strat, it should be applied after all other ammo costs.

#### enemyKill object
An `enemyKill` object communicates the need to kill a given set of enemies, and is satisfied by having the necessary items to use one of the valid [weapons](weapons/weapons-readme.md) that will kill each of the enemies (as well as enough ammo, if applicable).

Determining what items can fulfill an `enemyKill` object should be done by doing the following:
* Identify the weapons that are valid for this `enemyKill`.
  * By default, all weapons that are not `situational` are valid
  * If the `enemyKill` object has an `explicitWeapons` property, its contents entirely overrides those default weapons
  * Weapons that are found in the `enemyKill` object's `excludedWeapons` property are rendered invalid
* For each enemy (or group of enemies), identify which valid weapons, and how many shots of them, will work. This can be determined by using the weapon's base damage and the enemy's health, damage multipliers, and invulnerabilities.
* Use the identified weapons' `useRequires` and `shotRequires` requirements to build an effective logical requirement for killing the enemies.
  * If a weapon's `shotRequires` uses ammo that is flagged as farmable in this `enemyKill`, remove the ammo cost.
  * If one of the enemies to kill has an applicable [boss scenario](enemies/bossScenarios-readme.md), that enemy's ammo cost should be obtained from the scenario calculation instead.
* If one of the enemies to kill has an applicable [boss scenario](enemies/bossScenarios-readme.md), calculate the energy cost.

An `enemyKill` object can have the following properties:
* _enemies:_ An array of groups of enemies. Those groups are themselves represented as an array. Putting enemies together in a group communicates that they can all be hit by the same shot of a weapon that `hitsGroup` (most notably a Power Bomb).
* _explicitWeapons:_ An array of weapons. These must be weapon names, weapon categories are not allowed. If this is present, defines the only weapons that may be used to fulfill this object (assuming they are actually effective to kill the enemies). If this is not present, all non-`situational` weapons may be used.
* _excludedWeapons:_ An array of weapons. These must be weapon names, weapon categories are not allowed. If this property is present, all weapons found in it may not be used to fulfill the object, regardless of whether the enemies are vulnerable to them.
* _farmableAmmo:_ An array of ammo types, which are considered farmable in the context of the `enemyKill` object. No ammo cost should be considered if using weapons that consumes that ammo type. If using a [boss scenario](enemies/bossScenarios-readme.md), this flag should be ignored and replaced by an ammo cost that takes drops and fight duration into account.

__Example:__
```json
  {"enemyKill":{
    "enemies": [
      [
        "Yellow Space Pirate (wall)",
        "Yellow Space Pirate (standing)"
      ],
      [
        "Yellow Space Pirate (wall)"
      ]
    ],
    "excludedWeapons": ["Bombs"]
  }}
```
Since Yellow Space pirates have 900 health and are immune to uncharged beam shots, this object would be fulfilled by either Charge, Screw Attack, 27 Missiles, 9 Supers, or Morph + 6 Power Bombs (3 per group, expecting that they will double-hit for 400 damage each).

__Additional considerations__

When trying to determine the ammo needed to fulfill an `enemyKill` object, it could be a good idea to factor in a player accuracy variable, to represent different levels of leniency.

### Health Management Objects
This section contains logical elements that are fulfilled by spending health. Encountering enough of those successively without having a chance to refill can impact the number of e-tanks that are needed to get through.

#### acidFrames object
An `acidFrames` object represents the need for Samus to spend time (measured in frames) in a pool of acid. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for acid is 6 damage every 4 frames, halved by Varia (3 damage every 4 frames), and halved again by Gravity Suit (3 damage every 8 frames).

__Example:__
```json
{"acidFrames": 35}
```

__Additional considerations__

Much like the other logical elements that represent environmental frame damage, the acid frame counts listed in this project might not be stricly "perfect" play, but they are very much unforgiving. Their most significant value is to provide relative lengths to different acid runs. It's recommended to apply a leniency factor to those, possibly as an option that can vary by difficulty.

#### draygonElectricityFrames object
A `draygonElectricityFrames` object represents the need for Samus to spend time (measured in frames) grappled to a broken turret in Draygon's room. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for electricity is 1 damage per frame, halved by Varia (1 damage every 2 frames), and halved again by Gravity Suit (1 damage every 4 frames).

__Example:__
```json
{"draygonElectricityFrames": 240}
```

__Additional considerations__

While the demands on the player are very flat for the Draygon kill, execution plays a huge factor in the Draygon grapple jump. Like with other types of environmental frame damage, it might be a good idea to apply a leniency factor (possibly as an option that can vary by difficulty), although that could make the Grapple kill excessively lenient as a side effect.

#### enemyDamage object
An `enemyDamage` object represents the need for Samus to intentionally take damage from an enemy. This is meant to be converted to a flat health value based on item loadout. It has the following properties:
* _enemy:_ The name of the enemy that will damage Samus
* _type:_ The name of the attack that Samus will take damage from
* _hits:_ The number of hits Samus will take from that attack

__Example:__
```json
{"enemyDamage": {
  "enemy": "Sidehopper",
  "type": "contact",
  "hits": 3
}}
```

#### energyAtMost object

There are situations where progress causes Samus' energy to be set to a specific value, regardless of how much she had coming in. An `energyAtMost` object communicates a logical requirement that Samus' energy is reduced to a maximum of the accompanying value. Fulfilling this object does not require draining reserve tanks.

__Example:__
```json
{"energyAtMost": 1}
```

#### heatFrames object
A `heatFrames` object represents the need for Samus to spend time (measured in frames) in a heated room. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for heated rooms is 1 damage every 4 frames, negated by Varia or Gravity Suit.

__Example:__
```json
{"heatFrames": 100}
```

__Additional considerations__

Much like the other logical elements that represent environmental frame damage, the heat frame counts listed in this project might not be stricly "perfect" play, but they are very much unforgiving. Their most significant value is to provide relative lengths to different heat runs. It's recommended to apply a leniency factor to those, possibly as an option that can vary by difficulty.

#### hibashiHits object
A `hibashiHits` object represents the need for Samus to intentionally take a number of hits from the Norfair flame bursts (also called hibashi). This is meant to be converted to a flat health value based on item loadout. The vanilla damage per hibashi hit is 30 with Power Suit, 15 with Varia, and 7 with Gravity Suit.

__Example:__
```json
{"hibashiHits": 1}
```

#### lavaFrames object
A `lavaFrames` object represents the need for Samus to spend time (measured in frames) in a pool of lava. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for lava is 2 damage every 4 frames, halved by Varia, and negated by Gravity Suit.

__Example:__
```json
{"lavaFrames": 70}
```

__Additional considerations__

Much like the other logical elements that represent environmental frame damage, the lava frame counts listed in this project might not be stricly "perfect" play, but they are very much unforgiving. Their most significant value is to provide relative lengths to different lava runs. It's recommended to apply a leniency factor to those, possibly as an option that can vary by difficulty.

#### lavaPhysicsFrames
A `lavaPhysicsFrames` object works exactly like a `lavaFrames` object, except that Samus needs to be working with lava physics during that period of time. This means Gravity Suit will be manually turned off for this duration, even if it's available.

__Example:__
```json
{"lavaPhysicsFrames": 70}
```

#### spikeHits object
A `spikeHits` object represents the need for Samus to intentionally take a number of hits from spikes. This is meant to be converted to a flat health value based on item loadout. The vanilla damage per spike hit is 60 with Power Suit, 30 with Varia, and 15 with Gravity Suit.

__Example:__
```json
{"spikeHits": 6}
```

__Additional considerations__

While this is true to some extent for every strat that requires taking intentional punctual damage, spike hits especially are featured quite prominently in some unforgiving strats. It might be a good idea to apply a leniency factor to those, possibly as an option that can vary by difficulty.

#### thornHits object
A `thornHits` object represents the need for Samus to intentionally take a number of hits from the game's weaker spikes, found mainly in Brinstar. This is meant to be converted to a flat health value based on item loadout. The vanilla damage per thorn hit is 16 with Power Suit, 8 with Varia, and 4 with Gravity Suit.

__Example:__
```json
{"thornHits": 1}
```

### Momentum-Based Objects
This section contains logical elements centered around available running room, as well as the charging (and subsequent execution) of shinesparks.

#### adjacentRunway object
An `adjacentRunway`object represents the need for Samus to be able to run (or possibly jump) into the room from an adjacent room. It has the following properties:
* _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
* _usedTiles:_ Indicates how many tiles should be avaible for Samus to gather momentum before going into the door
* _inRoomPath:_ An array that indicates the path of node IDs that the player should travel, up to and including the node where the `adjacentRunway` logical element is, in order to be able to used the adjacent runway. If this is missing, the player is expected to enter the room at the current node and not move from there.
* _physics:_ An optional array that indicates the acceptable physics that can be in effect at the adjacent door. If missing, all physics are acceptable.
* _useFrames:_ An optional property that indicates the number of frames Samus should expect to spend at the adjacent door, being subjected to the door (acid/lava) and room (heat) environments there if applicable.
* _overrideRunwayRequirements:_ An optional boolean (if missing, assume false). If true, indicates the the requirements on the runway itself don't need to be fulfilled.

Please refer to the section about runways in [the Region documentation](region/region-readme.md) for a more detailed explanation of runways.

__Example:__
```json
{"adjacentRunway": {
  "fromNode": 3,
  "usedTiles": 1
}}
```

__Additional considerations__

Please note that fulfilling this logical element requires interaction with the door in the adjacent room to be possible (so no active locks on it, and fulfilling its interaction requirements). Fulfilling this logical element also causes the room to be reset, which means all obstacles respawn.

#### canComeInCharged object
A `canComeInCharged` object represents the need to charge a shinespark in an adjacent room, or to initiate a shinespark in an ajacent room and into the current room. It has the following properties:
* _fromNode:_ Indicates from what door this logical requirement expects Samus to enter the room
* _inRoomPath:_ An array that indicates the path of node IDs that the player should travel, up to and including the node where the `adjacentRunway` logical element is, in order to be able to used the adjacent runway. If this is missing, the player is expected to enter the room at the current node and not move from there.
* _framesRemaining:_ Indicates the minimum number of frames Samus needs to have left, upon entering the room, before the shinespark charge expires. A value of 0 indicates that shinesparking through the door works.
* _shinesparkFrames:_ Indicates how many frames the shinespark that will be used lasts. This can be 0 in cases where only the blue suit is needed. During a shinespark, Samus is damaged by 1 every frame, and being able to spend that health is part of of being able to fulfill a `canComeInCharged` object.

__Example:__
```json
{"canComeInCharged": {
  "fromNode": 4,
  "framesRemaining": 180,
  "shinesparkFrames": 75
}}
```

__Additional considerations__

* A `canComeInCharged` object implicitly requires the Speed Booster.
* A `canComeInCharged` object implicitly requires the `canShinespark` tech if it has more than 0 `shinesparkFrames`.
* A `canComeInCharged` object is implicitly fulfilled if the runways on the two sides of the door combine into a large enough runway to charge a spark. Combining with the adjacent room's runway is _not_ necessary if the current room's runway by itself is large enough.
The number of framesRemaining in that case is:
  * 180 if there is a usable runway in the destination room
  * Roughly 175 if there is no usable runway in the destination room
* Please note that unless the adjacent room is not used at all, fulfilling this logical element also causes the room to be reset. This means all obstacles respawn.

Please refer to the section about runways in [the Region documentation](region/region-readme.md) for a more detailed explanation of runways and how to combine them.

#### canShineCharge object
A `canShineCharge` object represents the need for Samus to be able to charge a shinespark within the current room. It has the following special properties:
* _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
* The following properties further define the tiles in `usedTiles`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 33 tiles where it's not relevant, that information will also be ommitted. All up/down tile counts assume Samus is running in the most convenient direction.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.
* _openEnd:_ Any runway that is used to gain momentum has two ends. An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (between 0 and 2).
* _shinesparkFrames:_ Indicates how many frames the shinespark that will be used lasts. This can be 0 in cases where only the blue suit is needed. During a shinespark, Samus is damaged by 1 every frame, and being able to spend that health is part of of being able to fulfill a `canShineCharge` object.

__Example:__
```json
{"canShineCharge": {
  "usedTiles": 25,
  "steepUpTiles": 3,
  "steepDownTiles": 3,
  "shinesparkFrames": 0,
  "openEnd": 1
}},
```

__Additional considerations__

* A `canShineCharge` object implicitly requires the Speed Booster.
* A `canShineCharge` object implicitly requires the `canShineCharge` tech if it has more than 0 `shinesparkFrames`.

### Room Pathing Objects
This section contains logical elements that are affected by Samus' pathing within a room.

#### previousNode object
A `previousNode` object represents the need for Samus to have arrived to the node directly from a given node. This usually has to do with quick-respawn blocks not being back yet.

__Example:__
```json
{"previousNode": 1}
```

#### previousStratProperty object
A `previousStratProperty` object represents the need for Samus to have arrived to the node via a strat that has a given stratProperty. This usually has to do with quick-respawn blocks not being back yet, or spinjump conservation. In those cases, arriving via other strats doesn't allow reproducing those conditions.

__Example:__
```json
{"previousStratProperty": "spinjump"}
```

__Additional considerations__
Entering a room does not count as executing a strat, so this logical element cannot be fulfilled instantly upon entering a room.

#### resetRoom object
A `resetRoom` object represents the need for the room to be in an initial state in order to perform a strat. A `resetRoom` object can have the following properties:
* _nodes:_ An array containing the in-room ID of nodes at which entering the room can work.
* _nodesToAvoid:_ An array containing the in-room ID of nodes that Samus must not visit after resetting the room. If any of those nodes have to be visited, the `resetRoom` object cannot be fulfilled, regardless of where Samus entered the room.
* _obstaclesToAvoid:_ An array containing the in-room ID of obstacles that Samus must not destroy after resetting the room. If any of those obstacles have to be broken, the `resetRoom` object cannot be fulfilled, regardless of where Samus entered the room.
* _mustStayPut:_ This property is mutually exclusive with `nodesToAvoid` and is only meaningful for `resetRoom` objects whose only `nodes` is the one they are at. If it is present and `true`, it is equivalent to having a `nodesToAvoid` property containing all other nodes in the room.

In order to fulfill a `resetRoom` object, Samus must be able to do all of the following:
* Enter the room at one of the listed `nodes`
* Reach the node where the logic contains the `resetRoom` object
  * If `mustStayPut` is true, Samus should be entering the room at the correct node and staying there
* Do this while visiting none of the listed `nodesToAvoid`. However, it's ok if a node to avoid ends up being visited directly afterwards, as a result of fulfilling the `resetRoom` object.
* Do this while destroying none of the listed `obstaclesToAvoid`
* If Samus is already in the room and has done one of the actions to avoid, she must be able to exit at one of the listed `nodes` and re-enter, following all other rules.
  * Please note that if fulfilling a `resetRoom` object involves exiting and re-entering, it will indeed reset the room and cause all obstacles to respawn.

__Example:__
```json
{"resetRoom":{
  "nodes": [1, 2],
  "obstaclesToAvoid": ["A"]
}}
```
