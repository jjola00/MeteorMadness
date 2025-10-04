from datetime import datetime
from typing import Dict, Optional, Any
from services.game.progression import get_level_from_kills

class GameSession:
    """Manages the state of an individual game session."""

    def __init__(self, session_id: str):
        """
        Initializes a new game session.

        Args:
            session_id (str): The unique identifier for the session.
        """
        self.session_id: str = session_id
        self.player_stats: Dict[str, int] = {
            "level": 1,
            "total_kills": 0,
            "impacts": 0,
            "deflections_survived": 0
        }
        self.current_asteroid: Optional[Dict[str, Any]] = None
        self.created_at: datetime = datetime.utcnow()

    def calculate_score(self, casualties: int, energy_megatons: float) -> int:
        """
        Calculates the score based on casualties and impact energy.

        Args:
            casualties (int): The number of casualties from an impact.
            energy_megatons (float): The energy of the impact in megatons.

        Returns:
            int: The calculated score.
        """
        score = casualties * (1 + energy_megatons / 100)
        return int(score)

    def add_score(self, score: int) -> Dict[str, Any]:
        """
        Adds a score to the player's total kills and checks for level up.

        Args:
            score (int): The score to add.

        Returns:
            Dict[str, Any]: A dictionary indicating if the player leveled up,
                            the new level, and the score added.
        """
        current_level = self.get_current_level()
        self.player_stats["total_kills"] += score
        new_level = self.get_current_level()

        leveled_up = new_level > current_level
        if leveled_up:
            self.player_stats["level"] = new_level

        return {
            "leveled_up": leveled_up,
            "new_level": new_level,
            "score_added": score
        }

    def get_current_level(self) -> int:
        """
        Calculates the player's current level based on total kills.

        This method delegates the level calculation to the progression service
        to ensure consistency with the defined level thresholds.

        Returns:
            int: The current level (1-5).
        """
        return get_level_from_kills(self.player_stats["total_kills"])

    def record_impact(self):
        """Increments the impacts counter."""
        self.player_stats["impacts"] += 1

    def record_deflection_survived(self):
        """Increments the deflections_survived counter."""
        self.player_stats["deflections_survived"] += 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a serializable dictionary representation of the session state.

        Returns:
            Dict[str, Any]: The session state as a dictionary.
        """
        return {
            "session_id": self.session_id,
            "player_stats": self.player_stats,
            "current_asteroid": self.current_asteroid,
            "created_at": self.created_at.isoformat()
        }
