# Boss scenarios
This page explains the contents of the [boss scenarios file](bosses/scenarios.json), and how it can be interpreted.

## What a boss scenario is
In essence, a boss scenario contains tools to determine how often Samus will hit the boss, how often she will take damage from the boss, and how often she will pick up energy. Many of these will depend on item loadout.

The intent is for a program to be able to figure out the fight duration. From that, incoming damage and and incoming energy (via energy pickups) can be calculated, and a flat energy requirement can be determined for a specific item loadout.

A lot of the values are intended to loosely model an actual fight, but the only truly relevant data to extract from a scenario are the energy and ammo costs.

## Damage Delivered
Damage delivered is represented by a combination of a damage window and attack opportunities.

### Damage Window
The damage window is a value (in percentage of time) for the window during which Samus can hit the boss. The point of the damage window is to model a fight duration relative to weapon damage and cooldown. A damage window of 25% means Samus will spend 25% of her time in the fight attacking the boss or waiting for her weapon cooldown, and 75% of the fight doing other things.

The damage window percentage is obtained by adding up the `windowPercent` of all using the `damageWindows` whose requirements are met. This gives the percentage of time Samus can be attacking.

__Example__

A boss fight has 5000 energy and two damage windows: One of 40% with no requirements, and one of 10% which requires Screw Attack.

Samus is fighting using missiles, which can hit every 10 frames for 100 damage. Samus needs 500 frames of damage window to take down the boss. Without Screw Attack, this means the fight will last 1250 frames. With screw attack, the fight is reduced to 1000 frames.

If Samus were using Supers instead, she would need 340 frames of damage window. Without Screw Attack, that would be 850 frames total. Screw Attack would reduce that to 680 franes.

### Attack Opportunities
The above damage window examples all assume a scenario where attack opportunities aren't represented. Attack opportunities, represent by the `attackOpportunityDuration`, are needed for boss fights where Samus spends a lot of time waiting for an opportunity to attack. For example, imagine a fight where you can only hit once during 20 frames of vulnerability, every 15 seconds. A charged shot has 60 frames of cooldown, but that doesn't mean it can only hit once every 45 seconds in that fight.

Attack opportunities are meant to represent this. They effectively place an upper cap on weapon cooldown. During each opportunity, Samus is expected to hit on the first frame and keep hitting, respecting weapon cooldown, until the opportunity has ended.

__Example__

A boss fight has 1000 energy and a damage window of 10%, with an `attackOpportunityDuration` of 30 frames. Every opportunity, Samus can hit with 3 missiles, 2 supers, or one charged shot. Hence, depending on weapon, the fight plays out as explained:
* With Missiles: Samus deals 300 damage (3 shots) every opportunity, so she needs 4 attack opportunities (120 damage window frames) to kill the boss. The fight will last about 1200 frames.
* With Supers: Samus deals 600 damage (2 shots) every opportunity, so she needs 2 attack opportunities (60 damage window frames) to kill the boss. The fight will last 600 frames.
* With Charged Power Beam: Samus deals 60 damage (1 shot) every opportunity, so she needs 17 attack opportunities (510 damage window frames) to kill the boss. The fight will last 5100 frames. Note how without modeling the attack opportunities, the fight would take almost twice as long.
* With Charged Ice Wave Plasma: Samus deals 900 damage (1 shot) every opportunity, so she needs 2 attack opportunities (60 damage window frames) to kill the boss. The fight will last 600 frames. Note how the fight lasts the same duration as with supers, and would not be any shorter without Wave.

## Damage Received
Incoming damage is described as a combination of a specific attack by the boss and a frequency at which the attack hits Samus. Attacks have requirement that must be met in order to avoid them (with attacks that are expected to hit regardless of item loadout having `never` as their `avoidingRequires`). Each attack can be present many times, since it may be easier to avoid with certain item loadouts.

__Example:__ A boss has an unavoidable `contact` attack with 500 `frequencyFrames`. That `contact` attack is also present a second time with 750 `frequencyFrames`, and requiring Screw Attack to avoid.

If Samus fights that boss without ScrewAttack, in a fight that lasts 2500 frames, she is expected to take contact damage 8 times (5 times from the base damage, and 3 more times due to being unable to use Screw Attack to avoid it). If she has Screw Attack, she is expected to take contact damage only 5 times.

## Energy Recovery
Some bosses are farmable for energy, but that doesn't mean recovering faster than the incoming damage is trivial. It does, however, mean that suits have more impact on those fights, since energy pickups give a flat value, and that flat value is worth more hits with a better suit.

This is why scenarios indicate how frequently (in frames) a farmable particle will be destroyed, via the `particleFrequencyFrames`. The expected energy drop rate can then be applied.

## The actual boss scenario json format
Each boss scenario can have the following properties:

### additionalDamageWindowPercent
An array that describes independent requirements that can each increase the damage window by a flat amount of percentage points if met. They each have the following properties:
* _requires:_ The requirements that must be met to widen the damage window
* _windowPercent:_ The amount of percentage points that are added to the `baseDamageWindowPercent`

### attackOpportunityDuration
An optional property which indicates that the damage window is broken up into a multitude of short time periods that last a number of frames. Samus is modeled to attack as fast as possible during those opportunities, and any unfinished cooldown from the last attack performed is considered to happen outside the global damage window. This helps model charged shots more accurately in fights where the damage window is a small percentage.

### incomingDamage
An array containing attacks that are expected to hit Samus (unless she meets avoidance requirements), and their hit frequency. Each object in the array has the following properties:
* _attack:_ The name of the attack. This should match the name of an attack for that boss in the [bosses file](bosses/main.json).
* _avoidingRequires:_ A list of [logical requirements](../logicalRequirements.md) that will allow Samus to avoid the attack if met.
* _frequencyFrames:_ Indicates how often (in frames) the attack will hit Samus.

### baseDamageWindowPercent
Indicates a base value (in percentage of time) for the damage window. This is the base value regardless of item loadout, and can be increased by `additionalDamageWindowPercent`.

### boss
The name of the boss. This should match an entry in the [bosses file](bosses/main.json).

### bossDodgeRate
Indicates a percentage of attacks that the boss is expected to not be hit by. This is separate from a player accuracy property, and is intended to describe bosses that are harder to hit than normal. The norm for this value should be 0, with harder to hit bosses having a value.

### excludedWeapons
An array of weapons that do not apply to the scenario, regardless of the contents of `explicitWeapons`. Those should match an entry in the [weapons file](../weapons/main.json).

### explicitWeapons
An array of weapons that apply to the scenario. Those should match an entry in the [weapons file](../weapons/main.json).

If this property is `null`, all weapons the boss is susceptible to that are not situational will apply to the scenario. However, if this property is present, only the weapons listed here will apply to the scenario.

### name
A unique name that identifies the scenario

### particleFrequencyFrames
Indicates how frequently (in frames) Samus will destroy a farmable particle spawned by the boss. This can be used to determine how frequently energy drops will occur. This property is entirely worthless if the boss has no `farmableDrops` property in the [bosses file](bosses/main.json).
