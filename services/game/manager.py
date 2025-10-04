import uuid
from typing import Dict, Optional, Any

from services.game.session import GameSession
from services.game.defense import simulate_defense_attempt
# Import the physics calculation class, assuming the user meant backend.physics
from backend.physics.impact import ImpactPhysics
# This service is not yet implemented, so we will use mock data.
# from services.population_service import get_population_in_radius

# Note: get_level_unlocks is not directly used in the manager but is part of the game logic suite.
from services.game.progression import get_level_unlocks
# This service function is available but not used in the current game logic.
# from services.asteroid_service import get_complete_asteroid_data


# TODO: Implement tactual physics calculations once we have them @jjola00 
class GameManager:
    """Manages game sessions and orchestrates the main game loop."""
    sessions: Dict[str, GameSession] = {}

    def create_session(self) -> str:
        """
        Creates a new game session and stores it.

        Returns:
            str: The newly created session ID.
        """
        session_id = str(uuid.uuid4())
        session = GameSession(session_id)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[GameSession]:
        """
        Retrieves a game session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            Optional[GameSession]: The GameSession object if found, otherwise None.
        """
        return self.sessions.get(session_id)

    def launch_asteroid(self, session_id: str, asteroid_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Launches an asteroid, simulates defense, and determines the outcome.

        Args:
            session_id (str): The ID of the current game session.
            asteroid_config (Dict[str, Any]): Configuration for the asteroid.
                                             Requires 'diameter_m'.

        Returns:
            Dict[str, Any]: The result of the launch attempt.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        session.current_asteroid = asteroid_config
        
        diameter = asteroid_config.get("diameter_m")
        if diameter is None:
            raise ValueError("Asteroid config must include 'diameter_m'")

        # Simulate defense with a default warning time
        defense_result = simulate_defense_attempt(
            asteroid_diameter_m=diameter,
            warning_time_days=365
        )

        if defense_result.get("deflected"):
            session.record_deflection_survived()
            return {
                "success": False, 
                "deflected": True, 
                "defense_result": defense_result
            }
        else:
            return {
                "success": True, 
                "deflected": False, 
                "proceed_to_impact": True,
                "defense_result": defense_result
            }

    def calculate_impact_result(self, session_id: str, impact_lat: float, impact_lng: float) -> Dict[str, Any]:
        """
        Calculates the final result of an asteroid impact.

        Args:
            session_id (str): The ID of the current game session.
            impact_lat (float): The latitude of the impact.
            impact_lng (float): The longitude of the impact.

        Returns:
            Dict[str, Any]: A complete dictionary of the impact results.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        if not session.current_asteroid:
            raise ValueError("No asteroid has been launched in this session")

        asteroid = session.current_asteroid
        
        # Call the physics engine to get impact effects
        impact_effects = ImpactPhysics.complete_impact_analysis(
            diameter_m=asteroid.get("diameter_m", 100),
            velocity_ms=asteroid.get("velocity_kms", 20) * 1000, # convert to m/s
            impact_angle_degrees=asteroid.get("impact_angle_deg", 45),
        )
        
        # MOCK DATA for population as the service doesn't exist yet
        # A real implementation would call:
        # population_data = get_population_in_radius(impact_lat, impact_lng, radius_km)
        casualties = int(impact_effects.get("effects", {}).get("thermal_radius_km", 0) * 10000)

        # Calculate score based on impact
        energy_megatons = impact_effects.get("impact_energy", {}).get("effective_energy_tnt_mt", 0)
        score = session.calculate_score(casualties, energy_megatons)
        
        # Update session state
        score_result = session.add_score(score)
        session.record_impact()

        return {
            "impact_effects": impact_effects,
            "casualties": casualties,
            "score_added": score,
            "leveled_up": score_result["leveled_up"],
            "new_level": score_result["new_level"],
            "player_stats": session.player_stats
        }
