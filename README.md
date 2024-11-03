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
  - Health: 1 hit point
  - Movement: 1 point per turn

### Game Flow
The game proceeds in turns, with each turn divided into four distinct phases:

1. **Input Collection Phase**
   - Game collects and validates movement orders from both players
   - Each order specifies source hex, destination hex, and number of units to move

2. **Movement Phase**
   - Units are moved according to collected orders
   - Multiple units can move from a single source hex to different destinations
   - Invalid moves are skipped (e.g., if destination is invalid or not enough units available)

3. **Combat Phase**
   - Combat occurs when units from opposing players occupy the same hex
   - Combat is resolved using a dice-roll system:
     - Each player rolls once (1-10)
     - Success occurs on rolls of 5 or higher (60% chance)
     - On success, damage equals the number of attacking units
     - Units are removed based on damage received
   - Combat is simultaneous, using initial unit counts for damage calculation

4. **Spawn Phase**
   - New units spawn in hexes controlled by a single player
   - One new unit spawns per controlled hex
   - Spawned units have 1 health and 1 movement point

### Victory Conditions
The game can end in two ways:
1. A player is eliminated (has no remaining units)
2. Maximum turn limit is reached (default: 100 turns)

## Technical Implementation

The game is implemented following functional programming principles:
- Immutable state management
- Pure functions for game logic
- No side effects in core game mechanics
