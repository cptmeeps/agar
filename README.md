# Hexagonal Strategy Game

A turn-based strategy game built using functional programming principles in Python.

## Overview

This project implements a hexagonal grid-based strategy game using pure functional programming paradigms. The game emphasizes immutable state management and side-effect-free functions to create a maintainable and testable codebase.

## Game Rules

### Map and Players
- The game is played on a fixed-size hexagonal grid
- Exactly 2 players participate in each game
- Each player controls identical units with the same capabilities

### Units
- Each player can control multiple units
- All units have the same capabilities (movement and combat)
- Multiple units from the same player can occupy the same hex
- Units can move through hexes occupied by friendly units
- Each unit has:
  - Health: 10 hit points
  - Damage: 3 damage per combat phase

### Game Flow
The game proceeds in turns, with each turn divided into three distinct phases:

1. **Movement Phase**
   - Active player can move their units to adjacent hexes
   - Each unit can move only once per turn
   - Units can move into hexes containing friendly units

2. **Combat Phase**
   - Combat occurs when units from opposing players occupy the same hex
   - All combat is resolved simultaneously using the following rules:
     - Each unit deals its damage to all enemy units in the same hex
     - Total damage from each side is calculated by multiplying:
       (Number of units) × (Damage per unit)
     - Damage is distributed equally among all enemy units
     - Units that reach 0 health or below are removed from the game
   - Example:
     - Player A has 2 units (20 total HP, deals 6 damage)
     - Player B has 3 units (30 total HP, deals 9 damage)
     - After combat:
       - Each of Player A's units takes 4.5 damage (9 damage ÷ 2 units)
       - Each of Player B's units takes 2 damage (6 damage ÷ 3 units)
       - Player A units remain with 5.5 HP each
       - Player B units remain with 8 HP each
   - Combat continues in subsequent turns until one side is eliminated or units move away

3. **Spawn Phase**
   - New units spawn at the end of each turn
   - Spawning occurs in hexes where a player has at least one unit
   - A hex is considered valid for spawning if no enemy units are present in that hex
   - One new unit spawns per valid spawn location, regardless of how many friendly units occupy that hex

### Victory Conditions
[To be defined - we should add win conditions such as controlling majority of the board or eliminating all enemy units]

## Technical Implementation

The game is implemented following functional programming principles:
- Immutable state management
- Pure functions for game logic
- No side effects in core game mechanics
