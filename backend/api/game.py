from flask import Blueprint, jsonify, request

from backend.services.game.manager import GameManager
from backend.services.game.progression import get_level_unlocks
from services.asteroid_service import get_cached_asteroids, find_asteroid_in_cache

# This blueprint handles the game mode API, which is separate from the main simulation API.
game_bp = Blueprint('game', __name__)
game_manager = GameManager()

# --- Game Flow Step 1: Start a new session ---
@game_bp.route('/game/start', methods=['POST'])
def start_game_session():
    """Starts a new game session and returns the session ID."""
    try:
        session_id = game_manager.create_session()
        session = game_manager.get_session(session_id)
        return jsonify({
            "session_id": session_id,
            "player_stats": session.player_stats
        }), 201
    except Exception as e:
        return jsonify({"error": "Failed to create session", "details": str(e)}), 500


# --- Helper Endpoint: Get available asteroid info ---
@game_bp.route('/game/asteroids-info', methods=['GET'])
def get_asteroids_info():
    """
    Returns information about the specific NASA asteroids available in the game
    by loading them from the application's cache.
    """
    # These are the specific asteroid IDs used in the game's progression.
    game_asteroid_ids = {"2000433", "2099942", "2101955"}
    
    try:
        cached_asteroids = get_cached_asteroids()
        game_asteroids_info = {}

        for asteroid in cached_asteroids:
            if asteroid.get("id") in game_asteroid_ids:
                game_asteroids_info[asteroid["id"]] = {
                    "name": asteroid.get("name"),
                    "diameter_m": asteroid.get("diameter_meters", {}).get("estimated_diameter_max"),
                    "source": "NASA NEO API (Cached)",
                    "description": f"A well-documented asteroid, {asteroid.get('name')}."
                }
        
        game_asteroids_info["attribution"] = "Data from NASA Near-Earth Object Program"
        return jsonify(game_asteroids_info)

    except Exception as e:
        return jsonify({"error": "Failed to load asteroid info from cache", "details": str(e)}), 500


# --- Helper Endpoint: Get player stats ---
@game_bp.route('/game/<string:session_id>/stats', methods=['GET'])
def get_session_stats(session_id: str):
    """Retrieves the current stats for a given session."""
    session = game_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session.to_dict()), 200


# --- Helper Endpoint: Get player unlocks ---
@game_bp.route('/game/<string:session_id>/unlocks', methods=['GET'])
def get_player_unlocks(session_id: str):
    """Returns the available unlocks for the player's current level."""
    session = game_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    current_level = session.player_stats.get("level", 1)
    unlocks = get_level_unlocks(current_level)
    return jsonify(unlocks), 200


# --- Game Flow Step 2: Launch an asteroid ---
@game_bp.route('/game/<string:session_id>/launch', methods=['POST'])
def launch_asteroid(session_id: str):
    """
    Launches an asteroid for the given session.
    The asteroid can be a pre-defined one from the cache or a custom one.
    """
    session = game_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    asteroid_config = {}
    if 'asteroid_id' in data:
        # Load a cached asteroid
        cached_asteroids = get_cached_asteroids()
        asteroid_data = find_asteroid_in_cache(data['asteroid_id'], cached_asteroids)
        if not asteroid_data:
            return jsonify({"error": f"Asteroid with ID {data['asteroid_id']} not found in cache"}), 400
        asteroid_config = {
            "diameter_m": asteroid_data.get("diameter_meters", {}).get("estimated_diameter_max"),
            "velocity_kms": asteroid_data.get("velocity_kms"),
            "name": asteroid_data.get("name")
        }
    elif 'diameter_m' in data and 'velocity_kms' in data:
        # Use custom asteroid parameters
        asteroid_config = {
            "diameter_m": data['diameter_m'],
            "velocity_kms": data['velocity_kms']
        }
    else:
        return jsonify({"error": "Request must include either 'asteroid_id' or both 'diameter_m' and 'velocity_kms'"}), 400

    try:
        result = game_manager.launch_asteroid(session_id, asteroid_config)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred during launch", "details": str(e)}), 500


# --- Game Flow Step 3: Calculate impact results ---
@game_bp.route('/game/<string:session_id>/impact', methods=['POST'])
def calculate_impact(session_id: str):
    """
    Calculates the result of an asteroid impact at a given lat/lng.
    This should only be called if the asteroid was not deflected.
    """
    session = game_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"error": "Request body must include 'lat' and 'lng'"}), 400

    lat, lng = data['lat'], data['lng']
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return jsonify({"error": "Invalid latitude or longitude values"}), 400

    try:
        result = game_manager.calculate_impact_result(session_id, lat, lng)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred during impact calculation", "details": str(e)}), 500
