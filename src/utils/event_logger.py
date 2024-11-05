import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

def setup_logging():
    """Create logs directory if it doesn't exist"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

class GameEventLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameEventLogger, cls).__new__(cls)
            cls._instance.log_file = f"logs/game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            setup_logging()
        return cls._instance

    def _write_log(self, log_level: str, event_type: str, **event_data):
        """Write a log entry to the log file"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": log_level,
            "event_type": event_type,
            **event_data
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def _get_world_state_summary(self, game_state: 'GameState') -> Dict[str, Any]:
        unit_counts = {1: 0, 2: 0}
        for tile in game_state.world.values():
            for unit in tile.units:
                unit_counts[unit.player_id] += 1
                
        return {
            "unit_counts": unit_counts,
            "current_turn": game_state.current_turn,
            "game_status": game_state.game_status
        }

    def log_action(self, 
                   action_type: str,
                   game_state: 'GameState',
                   position: Optional[Tuple[int, int]] = None,
                   details: Dict[str, Any] = None,
                   status: str = "success") -> None:
        
        event = {
            "action": action_type,
            "status": status,
            "game_state": self._get_world_state_summary(game_state)
        }
        
        if position:
            event["position"] = position
        if details:
            event["details"] = details
            
        self._write_log("INFO", "game_action", **event)

    def log_error(self, 
                  action_type: str,
                  error: Exception,
                  game_state: Optional['GameState'] = None,
                  context: Dict[str, Any] = None) -> None:
        
        event = {
            "action": action_type,
            "error": str(error),
            "error_type": error.__class__.__name__
        }
        
        if game_state:
            event["game_state"] = self._get_world_state_summary(game_state)
        if context:
            event["context"] = context
            
        self._write_log("ERROR", "game_error", **event)

    def log_combat(self,
                   game_state: 'GameState',
                   position: Tuple[int, int],
                   casualties: Dict[int, int]) -> None:
        self.log_action(
            "combat",
            game_state,
            position=position,
            details={"casualties": casualties}
        )

    def log_movement(self,
                    game_state: 'GameState',
                    source: Tuple[int, int],
                    destination: Tuple[int, int],
                    units: int,
                    player_id: int) -> None:
        self.log_action(
            "movement",
            game_state,
            position=source,
            details={
                "destination": destination,
                "units_moved": units,
                "player_id": player_id
            }
        ) 