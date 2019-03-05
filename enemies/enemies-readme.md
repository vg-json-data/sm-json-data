# Enemies Data
This section contains data about the enemies in Super Metroid.

## Folder Structure
This folder simply contains the `main.js` file, which contains data about all normal enemies, and `bosses/main.json`, which contains data about bosses.

## Contents of an Enemies File
Enemies files follow the schema defined at `[/schema/m3-enemies.schema.json](../schema/m3-enemies.schema.json)`.

Each enemy file is an array of Enemies, and includes data about its weaknesses, immunities, damage and health, drop table, and more.

### attacks
This is an object containing attacks that the enemy is able to perform. Each property in the `attacks` object is named for the attack, and is an array with the damage caused to Samus by the attack. The array contains three values which refer, in order, to damage while wearing Power Suit, Varia Suit, and Gravity Suit.

### drops
This is the enemy's drop table. [See the wiki for an exmplanation of drop tables](https://wiki.supermetroid.run/Enemies#How_Drops_Work)

### dims
This is the width and height of the enemy in pixels.

### mult
This array contains any weapon whose damage on this enemy has a bonus multiplier.

### invul
This array contains any weapon this enemy is invulnerable to.