# Enemies Data
This section contains data about the enemies in Super Metroid.

## Folder Structure
This folder simply contains the main.js file, which contains data about all normal enemies, and bosses/main.json, which contains data about bosses.

## Contents of an Enemies File
Enemies files follow the schema defined at /schema/m3-enemies.schema.json.

Each Enemies file is an array of enemies

### dmgToSamus
This is an array that contains values for contact damage caused to Samus by this enemy. This contains three values which refer, in order, to damage while wearing Power Suit, Varia Suit, and Gravity Suit.

### drops
This is the enemy's drop table. [See the wiki for an exmplanation of drop tables](https://wiki.supermetroid.run/Enemies#How_Drops_Work)

### dims
This is the width and height of the enemy in pixels.

### mult
This array contains any weapon whose damage on this enemy has a bonus multiplier.

### invul
This array contains any weapon this enemy is invulnerable to.