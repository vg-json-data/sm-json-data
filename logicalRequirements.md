# Logical Requirements
Logical requirements are an important part of this project. They are used to represent any and all conditions Samus needs to fulfill to be able to perform actions. This can include having items, performing techs, and consuming ammo or health.

## Structure
A logical requirement is an array of logical elements, which are implicitly linked by a logical AND. Those logical elements can be a number of things:
* _The name of a helper._ Helpers are defined in [helpers.json](helpers.json) and they themselves represent a logical requirement. Those exist to reduce duplication and make logical requirements more readable. By convention, a helper's name should start with `h_`.
* _The name of a tech._ Techs are defined in [tech.json](tech.json).  Those represent a technique that players can perform, which may also imply logical requirements of their own. By convention, a tech's name should start with `can`.
* _The name of an item._ Those are defined in [items.json](items.json).
* _The name of a game flag._ Those are defined in [items.json](items.json), and are used to represent game events such as defeating a boss, or breaking the Maridia tube. By convention, a game flag's name should start with `f_`.
* _"free"._ This indicates a logical element that is automatically fulfilled.
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

Requirements are applied in the order in which they are listed; this can matter in cases where "refill",
"ammoDrain", or "resourceAtMost" requirements are involved with other resource usage requirements.

#### or object
An `or` object is fulfilled if at least one of the logical elements it contains is fulfilled

__Example:__
```json
{"or": [
  "canSwim",
  "canSuitlessMaridia"
]}
```

#### not object
A `not` object is fulfilled if the logical element given is not fulfilled

__Example:__
```json
{"not": "f_KilledMetroidRoom1"}
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

#### shinespark
A `shinespark` object represents the need for Samus to spend energy performing a shinespark for a given number of frames. This implicitly requires the `canShinespark` tech. It has the following properties:

* _frames_: The duration of the shinespark in frames, assuming the spark is completed without being interrupted by reaching 29 energy. The shinespark frames equals the amount of energy spent, as a shinespark uses 1 energy per frame. 
* _excessFrames_: The shinespark duration (in frames) that is not required to complete the objective of the shinespark. Subtracting this from the `frames` defines the lower limit of the shinespark energy cost.

#### acidFrames object
An `acidFrames` object represents the need for Samus to spend time (measured in frames) in a pool of acid. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for acid is 6 damage every 4 frames, halved by Varia (3 damage every 4 frames), and halved again by Gravity Suit (3 damage every 8 frames).

__Example:__
```json
{"acidFrames": 35}
```

__Additional considerations__

Much like the other logical elements that represent environmental frame damage, the acid frame counts listed in this project might not be stricly "perfect" play, but they are very much unforgiving. Their most significant value is to provide relative lengths to different acid runs. It's recommended to apply a leniency factor to those, possibly as an option that can vary by difficulty.

#### gravitylessAcidFrames object
A `gravitylessAcidFrames` object represents Samus interacting with acid physics with Gravity Suit turned off, even if it is available. The number of frames here needs to be represented as `acidFrames` without the reduction effects given by Gravity Suit.

__Example:__
```json
{"gravitylessAcidFrames": 70}
```

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

#### resourceAtMost object

There are situations where progress causes Samus' energy or ammo to be reduced to a specific value, regardless of how much she had before. A `resourceAtMost` object communicates a logical requirement that Samus' resource is reduced to a maximum of the accompanying value. It has the following properties:
* _type:_ The type of resource. Can have the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
  * Energy (total of RegularEnergy + ReserveEnergy)
* _count:_ The amount of the resource that Samus will be reduced down to.

__Example:__
```json
{"resourceAtMost": [
  {"type": "RegularEnergy", "count": 1}
]}
```

#### autoReserveTrigger object

An `autoReserveTrigger` object represents a logical requirement for "auto" reserves to be triggered, which results in Samus' energy becoming equal to the amount of energy in reserves (capped to energy capacity), and reserve energy becoming zero. An `autoReserveTrigger` object has three optional properties:

* _minReserveEnergy_: The minimum amount of energy in reserves which will satisfy this requirement (default: 1).
* _maxReserveEnergy_: The maximum amount of energy in reserves which will satisfy this requirement (default: 400).
* _implicitHeatFrames_: This takes one of three possible values, "yes", "no", or "suitless". The default is "yes", which applies `heatFrames` equal to the amount of reserve transferred if the room is heated. This application is prevented by the value "no", while the value "suitless" applies `suitlessHeatFrames` instead.

__Example:__
```json
{"autoReserveTrigger": {}}
```

#### cycleFrames object
A `cycleFrames` object represents the need for Samus to spend time (measured as an amount of in-game frames) in a room as part of a farming cycle. Including a `cycleFrames` requirement is mandatory in farming strats with a [`farmCycleDrops`](strats.md#farm-cycle-drops) property. The `cycleFrames` can be used to determine how many cycles of a farm a player can reasonably be expected to perform, based on an assumed amount of "patience". The frame counts listed tend to be somewhat optimized, so it recommended to apply a lenience factor based on difficulty.

__Example:__
```json
{"cycleFrames": 100}
```

#### simpleCycleFrames object

A `simpleCycleFrames` object represents the need for Samus to spend time (measured as an amount of in-game frames) in a room as part of a farming cycle. It is identical to `cycleFrames` except that the time spent in `simpleCycleFrames` is intended to be invariant, not affected by leniency. This can be useful in cases that involve doing something simple for a significant amount of time, such as standing in place while farming bugs.


#### heatFrames object
A `heatFrames` object represents the need for Samus to spend time (measured in frames) in a heated room. This is meant to be converted to a flat health value based on item loadout. The vanilla damage for heated rooms is 1 damage every 4 frames, negated by Varia or Gravity Suit. The effect of Gravity suit on heat damage may be modified by randomizers. A `heatFrames` object implicitly includes a requirement `{"or": ["h_heatProof", "canHeatRun"]}`.

__Example:__
```json
{"heatFrames": 100}
```

__Additional considerations__

Much like the other logical elements that represent environmental frame damage, the heat frame counts listed in this project might not be strictly "perfect" play, but they are very much unforgiving. Their most significant value is to provide relative lengths to different heat runs. It's recommended to apply a lenience factor to those, possibly as an option that can vary by difficulty.

#### simpleHeatFrames object

A `simpleHeatFrames` object represents the need for Samus to spend time (measured in frames) in a heated room. It is identical to `heatFrames` except that the time spent in `simpleHeatFrames` is intended to be invariant, not affected by leniency. This can be useful in cases that involve doing something simple for a significant amount of time, such as standing in place or running through a long hallway.

#### suitlessHeatFrames object

A `suitlessHeatFrames` object represents the need for Samus to spend time (measured in frames) in a heated room, while having heat-protection turned off (normally, both Varia and Gravity Suit must be turned off for this apply). This can occur, for example, when using heat to drain energy.

#### heatFramesWithEnergyDrops object

A `heatFramesWithEnergyDrops` object represents the need for Samus to spend time in a heated room, but with the possibility of offsetting some of the heat damage using energy drops from enemies. Any heat damage is logically applied before the energy gain, so Samus must be able to survive the heat before picking up the drops. Any energy gain is logically capped to not exceed the heat damage, so this logical requirement cannot result in a net energy gain. A `heatFramesWithEnergyDrops` object implicitly includes a requirement `{"or": ["h_heatProof", "canHeatRun"]}`.

The actual amount of energy gained typically depends on RNG and also on which ammo types are completely full. The drop probabilities for each enemy type is given in the [enemies](enemies/main.json) file. Because of the randomness involved, the logical amount of energy gain is open to various interpretations. For example, the mean, the median, or a lower confidence limit could be used.

__Example:__
```json
{"heatFramesWithEnergyDrops": {
  "frames": 200,
  "drops": [
    {"enemy": "Magdollite", "count": 3},
    {"enemy": "Multiviola", "count": 2}
  ]
}}
```

#### lavaFramesWithEnergyDrops object

A `lavaFramesWithEnergyDrops` object represents the need for Samus to spend time in lava, but with the possibility of offsetting some of the lava damage using energy drops from enemies. Any lava damage is logically applied before the energy gain, so Samus must be able to survive the heat before picking up the drops. Any energy gain is logically capped to not exceed the heat damage, so this logical requirement cannot result in a net energy gain.

The actual amount of energy gained typically depends on RNG and also on which ammo types are completely full. The drop probabilities for each enemy type is given in the [enemies](enemies/main.json) file. Because of the randomness involved, the logical amount of energy gain is open to various interpretations. For example, the mean, the median, or a lower confidence limit could be used.

__Example:__
```json
{"lavaFramesWithEnergyDrops": {
  "frames": 200,
  "drops": [
    {"enemy": "Fune", "count": 1}
  ]
}}
```

#### gravitylessHeatFrames object
A `gravitylessHeatFrames` object represents Samus in a heated environment with Gravity Suit turned off, even if it is available. The number of frames here needs to be represented as `heatFrames` without the reduction effects given by Gravity Suit.

__Example:__
```json
{"gravitylessHeatFrames": 70}
```

#### shineChargeFrames object

A `shineChargeFrames` object represents the need for Samus to have at least the given amount of shinecharge frames remaining. After this requirement, the new amount of shinecharge frames remaining is updated by subtracting away the given amount of frames. Including a `shineChargeFrames` requirement is mandatory for strats that begin with an already obtained shinecharge (e.g. with `comeInShinecharged`) or which end with an active shinecharge (e.g. with `leaveShinecharged`). For strats that both gain a shinecharge and consume it within the same strat, including `shineChargeFrames` requirements is optional.

The underlying idea is that shinecharge frames can be modeled as a resource, similar to energy or ammo. The level of this resource can be considered to be part of Samus' state at any given point in time. However, unlike energy or ammo, this resource is not treated as persisting across arbitrary sequences of strats. Samus' shinecharge frames are considered to be set to 180 at the point of a `canShinecharge` requirement; but in order to persist across strats, the strat must either be marked with `"endsWithShineCharge": true` or have a `leavesShinecharged` exit condition, and the following strat must be marked with `"startsWithShineCharge": true` or have a `comeInShinecharged` entrance condition. These restrictions are necessary because strats in general do not model the amount of frames consumed, so it would be invalid to assume that Samus' shinecharge frames can remain unchanged across strats that are not designed to model shinecharge frames.

As an example, if a strat requires entering the room with at least 5 shinecharge frames remaining, it should have a requirement of `{"shineChargeFrames": 5}`. This is in spite of the fact that the amount of shinecharge frames would decrease only by 4 (from 5 to 1) between the time of entering the room and activating the spark. Conversely, if measuring the amount that the shinecharge timer decreases when executing a strat that ends in a shinespark, a value of 1 should be added to this amount to determine the minimum possible amount of logical `shineChargeFrames` that should be required.

__Example:__
```json
{"shineChargeFrames": 100}
```

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

#### gravitylessLavaFrames object
A `gravitylessLavaFrames` object represents Samus interacting with lava physics with Gravity Suit turned off, even if it is available. The number of frames here needs to be represented as `lavaFrames` without the reduction effects given by Gravity Suit.

__Example:__
```json
{"gravitylessLavaFrames": 70}
```

#### samusEaterCycles object
A `samusEaterCycles` object represents the need for Samus to take damage from the environmental enemy known as a Samus Eater. When captured, damage is dealt in small hits multiple times. The vanilla damage is 8 hits of 2 damage with Power Suit, 8 hits of 1 damage in Varia Suit, or 4 hits of 1 damage in Gravity Suit. As there is no known way to escape a Samus Eater between hits, this is simplified as energy loss per cycle. Note that Samus is stuck in the ceiling variants for twice as long, which would be represented as 2 cycles.

__Example:__
```json
{"samusEaterCycles": 1}
```

#### metroidFrames object
A `metroidFrames` object represents the need for Samus to spend time (measured in frames) grappled by a Metroid. When captured, the Metroid deals 3 damage every 4 frames. This is halved by Varia (3 damage every 8 frames), and halved again by Gravity Suit (3 damage every 16 frames).

__Example:__
```json
{"metroidFrames": 260}
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

#### electricityHits object
A `electricityHits` object represents the need for Samus to intentionally take a number of hits from electricity, found in Wrecked Ship. This is meant to be converted to a flat health value based on item loadout. The vanilla damage per thorn hit is 30 with Power Suit, 15 with Varia, and 7 with Gravity Suit.

__Example:__
```json
{"electricityHits": 1}
```

#### resourceCapacity object
A `resourceCapacity` object represents the need for Samus to be capable of holding at least a set amount of a specific resource. It can have the following properties:
* _type:_ The type of resource. Can have the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
* _count:_ The amount of capacity that Samus must have.

__Example:__
```json
{"resourceCapacity": [
    {"type": "Missile", "count": 10},
    {"type": "Super", "count": 10},
    {"type": "PowerBomb", "count": 11},
    {"type": "RegularEnergy", "count": 899}
]}
```

#### resourceMaxCapacity object
A `resourceMaxCapacity` object represents the need for Samus to have a capacity that does not exceed a set amount of a specific resource. It can have the following properties:
* _type:_ The type of resource. Can have the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
* _count:_ The amount of capacity that Samus must not exceed.

A `resourceMaxCapacity` requirement generally includes an implicit requirement of `canRiskPermanentLossOfAccess`. In some randomizer contexts, this may be unnecessary, for example if it is known that the player cannot have collected items that would exceed the expected capacity, or if it is possible for the player to disable the extra items.

__Example:__
```json
{"resourceMaxCapacity": [{"type": "RegularEnergy", "count": 299}]}
```

#### resourceAvailable object
A `resourceAvailable` object represents the need for Samus to be holding at least a set amount of a specific resource. It has the following properties:
* _type:_ The type of resource. Can have the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
  * Energy (total of RegularEnergy + ReserveEnergy)
* _count:_ The amount of the resource that Samus must have.

This requirement does not consume the resource.

__Example:__
```json
{"resourceAvailable": [
    {"type": "Energy", "count": 99}
]}
```

#### resourceConsumed object
A `resourceConsumed` object represents the need for Samus to spend a set amount of a specific resource. It has the following properties:
* _type:_ The type of resource. Can have the following values:
  * RegularEnergy
  * ReserveEnergy
  * Energy (total of RegularEnergy + ReserveEnergy)
* _count:_ The amount of the resource that Samus must have.

This requirement consumes the resource.

__Example:__
```json
{"resourceConsumed": [
    {"type": "ReserveEnergy", "count": 1}
]}
```

#### resourceMissingAtMost object
A `resourceMissingAtMost` object represents the need for Samus to be missing at most a certain amount of a specific resource, relative to being full capacity. It has the following properties:
* _type:_ The type of resource. Can have the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
  * Energy (total of RegularEnergy + ReserveEnergy)
* _count:_ The amount of the resource that Samus must have.

For example, a count of zero would indicate that Samus must be full on that resource type.

__Example:__
```json
{"resourceMissingAtMost": [
    {"type": "Energy", "count": 0}
]}
```

#### refill object
A `refill` object is always fulfilled and represents a process that refills certain resource types to their current maximum capacity. Possible uses could include a farm, recharge station, or Crystal Flash. The
refilled resource types are listed as an array having the following possible values:

* Missile
* Super
* PowerBomb
* RegularEnergy
* ReserveEnergy
* Energy (shorthand for RegularEnergy + ReserveEnergy)

__Example:__
```json
{"refill": ["Energy", "Missile"]}
```

#### partialRefill object

A `partialRefill` object represents a process that refills a certain resource type up to a certain level, while having no effect if already at or above that level. It has two properties:

* _type_: The resource type being partially refilled, one of the following values:
  * Missile
  * Super
  * PowerBomb
  * RegularEnergy
  * ReserveEnergy
  * Energy (combination of RegularEnergy + ReserveEnergy)
* _limit_: The level of resource amount that the refill stops at.

When applied to `Energy` type, the refill applies first to regular energy; if the refill `limit` exceeds the regular energy capacity, then regular energy will be fully refilled and the remaining amount (after subtracting regular energy capacity) will be applied as a partial refill to reserve energy.

__Example:__
```json
{"partialRefill": {"type": "Energy", "limit": 1500}}
```

### Momentum-Based Objects
This section contains logical elements centered around available running room, as well as the charging (and subsequent execution) of shinesparks.

#### canShineCharge object
A `canShineCharge` object represents the need for Samus to be able to charge a shinespark within the current room. It has the following special properties:
* _usedTiles:_ The number of tiles that are available to charge the shinespark. Smaller amounts of tiles require increasingly more difficult short charging techniques.
* The following properties further define the tiles in `usedTiles`, by indicating how many of them have some particularities. Sloped tiles impact the required number of tiles to charge a shinespark. Those properties will be missing if there are no such tiles. In places with more than 45 tiles where it's not relevant, that information will also be ommitted. All up/down tile counts assume Samus is running in the most convenient direction.
  * _gentleUpTiles:_ Indicates how many tiles gently slope upwards (like in Speed Booster Hall).
  * _gentleDownTiles:_ Indicates how many tiles gently slope downwards (like in Speed Booster Hall).
  * _steepUpTiles:_ Indicates how many tiles steeply slope upwards (like in Landing Site).
  * _steepDownTiles:_ Indicates how many tiles steeply slope downwards (like in Landing Site).
  * _startingDownTiles:_  Indicates how many tiles slope downwards at the expected start of the running space. A stutter can't be executed on those tiles.
* _openEnd:_ Any runway that is used to gain momentum has two ends. An open end is when a platform drops off into nothingness, as opposed to ending against a wall. Since those offer a bit more room, this property indicates the number of open ends that are available for charging (between 0 and 2).

__Example:__
```json
{"canShineCharge": {
  "usedTiles": 25,
  "steepUpTiles": 3,
  "steepDownTiles": 3,
  "openEnd": 1
}},
```

__Additional considerations__

* A `canShineCharge` object implicitly requires the Speed Booster item and `canDash` tech. Energy requirements for the shinespark (if applicable) are specified separately using a `shinespark` object. A `canShineCharge` requirement causes a loss of any flash suit or blue suit.

#### getBlueSpeed object

A `getBlueSpeed` object represents the need for Samus to be able to gain blue speed using a specified runway. It is very similar to `canShineCharge`, including the same set of properties and the same implicit requirements, except that `getBlueSpeed` does not result in the loss of flash suit (it does still result in loss of blue suit). Instead of crouching to enter a shinecharge state for performing a shinespark, `getBlueSpeed` involves using the blue speed directly, such as to destroy enemies, bomb blocks, or Speed blocks.


__Example:__
```json
{"getBlueSpeed": {
  "usedTiles": 25,
  "steepUpTiles": 3,
  "steepDownTiles": 3,
  "openEnd": 1
}},
```

#### speedBall object

A `speedBall` object represents the need for Samus to be able to gain blue speed and jump into a speedball using a specified runway. It includes a `canSpeedball` requirement. Whether a speedball can performed within a given runway length depends on the player's ability to shortcharge as well as to perform a short-hop mockball. The [blue run speed table](strats.md#blue-run-speed-table) describes several tiers of shortcharging skill, their associated runway lengths over which blue speed can be attained, and the resulting run speed. For determining whether a speedball is logically possible, the lowest run speed should be used within the range of what is possible for that skill level; this corresponds to using the "Ideal speed" from the table. The total runway length required can then be computed as follows:

$$\text{minimum speedball runway} = \text{minimal blue speed runway} + \text{short-hop mockball frames} * \text{mid-air speed}$$

Here the "mid-air speed" is obtained by adding the extra run speed (from the "Ideal speed" at the end of getting blue speed) to a base speed of $1.5, which is the average of the spin-jump base speed of $1.6 and the aim-down base speed of $1.4, assuming that roughly half of the jump will be spent in each of those two states. The "short-hop mockball frames" is the amount of frames between the start of the jump and when the morph-sized hitbox is achieved; it is a parameter that can be varied based on assumed player skill: a value of 6 is at or near TAS-level, while 40 would be a lenient value where Samus can jump several tiles into the air.

__Example:__
```json
{"speedBall": {
  "length": 25,
  "steepUpTiles": 3,
  "steepDownTiles": 3,
  "openEnd": 1
}},
```

#### itemNotCollectedAtNode object
An `itemNotCollectedAtNode` object represents the need to have not yet collected the item at a given node in the same room. For example, such
an item could be used to overload PLMs in G-mode assuming the item has spawned. Note that any conditions for the item to spawn (e.g. for
Wrecked Ship items) are not included in this requirement and would need to be specified separately if applicable. In many situations,
an `itemNotCollectedAtNode` requirement should be accompanied by a `canRiskPermanentLossOfAccess`, if it is possible to prematurely obtain
the item and then get stuck from being unable to do the strat.

__Example:__
```json
{"requires": [
  {"itemNotCollectedAtNode": 1},
  "canRiskPermanentLossOfAccess"
]}
```

#### itemCollectedAtNode object
An `itemCollectedAtNode` object represents the need to have collected the item at a given node in the same room. For example, the existance of such an item could unintentionally be used to overload PLMs in G-mode assuming the item has spawned.

__Example:__
```json
{"requires": [
  {"itemCollectedAtNode": 1}
]}
```

### Lock-related objects
This section contains logical elements that are affected by Lock type Objects attached to Nodes.

#### doorUnlockedAtNode object

A `doorUnlockedAtNode` object represents the need for a door to be unlocked, i.e. to be free of a lock such a red, green, yellow, or gray door shell. An example would be if the space in the door frame is needed as runway for a jump or shinecharge. 

In order to support randomizers that may modify door colors, a `doorUnlockedAtNode` requirement should be used when appropriate even if the vanilla door color is blue. If a strat has an `exitCondition`, then there is an implicit `doorUnlockedAtNode` requirement on the destination door node, unless the strat has [`bypassesDoorShell`](strats.md#bypasses-door-shell) set to `true` or `"free"`.

If the door node in a `doorUnlockedAtNode` also appears in the strat's [`unlocksDoors`](strats.md#unlocks-doors) property, then the `doorUnlockedAtNode` may also be fulfilled by unlocking the door as part of executing the strat (as an alternative to having been previously unlocked), and any `requires` for that locked door in the `unlocksDoors` then become part of the requirements for the strat.

__Example:__
```json
{"doorUnlockedAtNode": 1}
```

### Obstacle-related objects
This section contains logical elements that are affected by Obstacle type Objects within a room.

#### obstaclesCleared

An `obstaclesCleared` object represents a requirement that all of the listed obstacles must be already cleared.

__Example:__
```json
{"obstaclesCleared": ["A"]}
```

#### obstaclesNotCleared

An `obstaclesNotCleared` object represents a requirement that none of the listed obstacles be already cleared.

__Example:__
```json
{"obstaclesNotCleared": ["A"]}
```

#### resetRoom object
A `resetRoom` object represents the need for the room to be in an initial state in order to perform a strat. A `resetRoom` object can have the following properties:
* _nodes:_ An array containing the in-room ID of nodes at which entering the room can work.

In order to fulfill a `resetRoom` object, Samus must be able to do all of the following:
* Enter the room at one of the listed `nodes`
* Reach the node where the logic contains the `resetRoom` object
* If Samus is already in the room and has done one of the actions to avoid, she must be able to exit at one of the listed `nodes` and re-enter, following all other rules.
  * Please note that if fulfilling a `resetRoom` object involves exiting and re-entering, it will indeed reset the room and cause all obstacles to respawn.

__Example:__
```json
{"resetRoom":{
  "nodes": [1, 2]
}}
```

### Glitched suits

#### gainFlashSuit object

A `gainFlashSuit` object represents that Samus gains a flash suit as part of executing this strat. A flash suit is a special shinecharge state which can be stored indefinitely and used one time to perform a shinespark, potentially in a distant room from where the flash suit was gained. 

A `gainFlashSuit` object has no properties.

With certain exceptions explained below, a flash suit can generally be carried around by any sequence of strats until it is used. A flash suit use is indicated by a `useFlashSuit` logical requirement. 

The need to perform actions that cannot preserve a flash suit are indicated by a `noFlashSuit` logical requirement; typically this is expressed indirectly through tech or helpers, such as `canCrouchJump`, `canXRayStandup`, `canCrystalFlash`, or `h_midAirShootUp`. A `canShineCharge` logical requirement also cannot preserve a flash suit.

The process of verifying which strats allow preserving a flash suit is not yet complete. Strats which have been checked are indicated by a property `"flashSuitChecked": true`. Any strat without this property should be assumed to be logically unusable for carrying a flash suit. Note that a strat with `"flashSuitChecked": true` may or may not be able to preserve a flash suit, depending on its logical requirements.

__Example:__
```json
{"gainFlashSuit": {}}
```

#### useFlashSuit object

A `useFlashSuit` indicates a need to have a flash suit state, which will then be lost as part of executing this strat. A strat with `useFlashSuit` should also have a `shinespark` logical requirement to specify the energy loss from shinesparking. 

A `useFlashSuit` object has no properties.

__Example:__
```json
{"useFlashSuit": {}}
```

#### noFlashSuit

A `noFlashSuit` indicates a need to perform actions that are incompatible with preserving a flash suit; it therefore requires that Samus not be in a flash suit state.

A `noFlashSuit` object has no properties.

__Example:__
```json
{"noFlashSuit": {}}
```

#### gainBlueSuit object

A `gainBlueSuit` object represents that Samus gains a blue suit as part of executing this strat. A blue suit is a special state in which Samus remains blue indefinitely, being able to pass through and destroy bomb blocks, Speed blocks, and most enemies. This state can potentially be carried to distant rooms from where the blue suit was gained. 

A `gainBlueSuit` object has no properties.

With certain exceptions explained below, a blue suit can generally be carried around by any sequence of strats until some action is taken which would cause the blue suit to be lost. The need to perform actions that cannot preserve a blue suit are indicated by a `noBlueSuit` logical requirement; typically this is expressed indirectly through tech or helpers, most notably `canDash`.

The process of verifying which strats allow preserving a blue suit is not yet complete. Strats which have been checked are indicated by a property `"blueSuitChecked": true`. Any strat without this property should be assumed to be logically unusable for carrying a blue suit, as though the strat had an extra requirement `{"noBlueSuit": {}}` appended. Note that a strat with `"blueSuitChecked": true` may or may not be able to preserve a blue suit, depending on its logical requirements.

__Example:__
```json
{"gainBlueSuit": {}}
```

#### haveBlueSuit object

A `haveBlueSuit` indicates a need to have a blue suit. This does not consume the blue suit.

__Example:__
```json
{"haveBlueSuit": {}}
```

#### blueSuitShinecharge object

A `blueSuitShinecharge` indicates a need to have a blue suit, in order to perform a shinecharge. A strat with `blueSuitShinecharge` should have a subsequent `shinespark` logical requirement to specify the energy loss from shinesparking, and the `shinespark` requirement will result in the loss of the blue suit.

A `blueSuitShinecharge` object has no properties.

__Example:__
```json
{"blueSuitShinecharge": {}}
```

#### noBlueSuit

A `noBlueSuit` indicates a need to perform actions that are incompatible with preserving a blue suit; it therefore requires that Samus not be in a blue suit state.

A `noBlueSuit` object has no properties.

__Example:__
```json
{"noBlueSuit": {}}
```

### Boss requirements

#### Ridley kill

A `ridleyKill` requirement represents the need to kill Ridley, including ammo and energy requirements depending on the player's assumed skill level and available items. The expected duration of the fight can be estimated based on the following assumptions:
- Supers can be used once every 0.5 seconds.
- Missiles can be used once every 0.34 seconds.
- A charged beam shot can be used once every 1.4 seconds.
- Power Bombs can be used once every 3 seconds.

Heat frames are included based on the expected duration of the fight. Patience requirements `canBePatient`, `canBeVeryPatient`, and `canBeExtremelyPatient` are likewise also included. In both cases, a leniency multiplier should be applied to the time taken between shots. Leniency should also be applied based on the assumed accuracy rate of shots hitting Ridley successfully.

Heat frame requirements should be included for the period before the fight begins, as well as after the fight until drops occurs, which can be estimated (slightly generously) at 16 seconds, or 960 heat frames.

If neither Morph nor Screw Attack are available, then at the highest skill level it can be assumed that the player takes unavoidable enemy damage at a rate of 10 energy per second. If Morph or Screw Attack is available, then it is possible to avoid all enemy damage, but for leniency normally some damage should still be assumed.

A `ridleyKill` requirement has the following optional properties which modify the assumptions of the fight:
- _powerBombs_: A boolean indicating if Power Bombs can be used during the fight (default: true).
- _gMode_: A boolean indicating if the fight happens in G-mode. If true, then Samus will be protected from heat damage, but Ridley's fireballs become invisible and immobile while still being dangerous to Samus.
- _stuck_: An enum with possible values "top" or "bottom", indicating the part of the room where Ridley gets stuck, allowing Samus to freely avoid damage from Ridley while inflicting damage to Ridley. If Ridley is stuck at the bottom of the room, then damage can be inflicted at a higher rate (not taking into account lag, which may be increased if a Crystal Flash is used in G-mode):
  - Supers can be used once every 0.34 seconds.
  - Missiles can be used once every 0.17 seconds.
  - A charged beam shot can be used once every 1.1 seconds.
  - Power Bombs can be used once every 2.65 seconds, though because there is no known way to keep Ridley stuck while using Power Bombs, strats should set `powerBombs` to `false` when `stuck` is `true`.

### Other requirements

#### tech object

A `tech` object indicates the need to be able to perform a `tech`, but without its `otherRequires`. This can be used to override item, ammo, or other requirements that are normally associated with the tech. The removal of `otherRequires` requirements applies recursively to any tech in the `techRequires` of the referenced tech.

__Example:__
```json
{"tech": "canIBJ"}
```

#### notable object

A `notable` object indicates the need to be able to perform a [notable strat](region/region-readme.md#notable-strats). A notable strat is a strat which requires more than simply having all of its item and tech requirements. This may be one with higher difficulty than what the tech would typically imply, or one which requires specific knowledge relating to the strat. Notable objects can be used like a tech requirement that is specific to the room. The name of the notable must match the `name` of an object in the room `notables` list.

__Example:__
```json
{"notable": "Taco Tank"}
```

#### disableEquipment object

A `disableEquipment` objects indicates the need for a specific item to be disabled, e.g. either by not having that item collected or by disabling it from the equipment screen. This requirement (with any item) implicitly includes a `canDisableEquipment` tech requirement.

__Example:__
```json
{"disableEquipment": "HiJump"}
```

While carrying a blue suit, disabling Speed Booster would result in a loss of the blue suit.

Note that the requirement `{"disableEquipment": "ETank"}` occurs in some strats. This is not a functionality of the vanilla game but may be supported in randomizers or other modifications of the game: it means that the player has a way to control the amount of ETanks that are currently active. It is commonly required in R-mode strats where the player may need to farm non-respawning enemies in the room to put energy back into reserves.
