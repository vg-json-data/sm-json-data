# Enemies Data
This section contains data about the enemies in Super Metroid.

## Folder Structure
This folder simply contains the [main.json](main.json) file, which contains data about all normal enemies, and [bosses/main.json](bosses/main.json), which contains data about bosses.

## Contents of an Enemies File
Enemies files follow the schema defined at [/schema/m3-enemies.schema.json](../schema/m3-enemies.schema.json).

Each enemy file is an array of Enemies, and includes data about its weaknesses, immunities, damage and health, drop table, and more.

### areas
This property is intended to just be informative. It indicates what regions of the game have instances of this enemy.

### attacks
This is an object containing attacks that the enemy is able to perform. Each property in the `attacks` object is named for the attack, and is an array with the damage caused to Samus by the attack. The array contains three values which refer, in order, to damage while wearing Power Suit, Varia Suit, and Gravity Suit.

### drops
This is the enemy's drop table. [See the wiki for an exmplanation of drop tables](https://wiki.supermetroid.run/Enemies#How_Drops_Work)

### dims
This is the width and height of the enemy in pixels.

### farmable
Indicates whether this enemy respawns, making it farmable without having to reset the room.

### grapplable
Defines how the enemy reacts to the grapple beam. Can have the following values:
* _yes:_ Grapple latches on to the enemy and allows Samus to swing from it as if it were a grapple block
* _no:_ Grapple has no effect
* _kill:_ Grapple kills the enemy outright

### mult
This object contains numerical properties whose name is a weapon, and whose value is the damage multiplier that should be applied to that weapon's base damage when calculating the damage it does to this enemy.

### invul
This array contains any weapon this enemy is invulnerable to.