from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from clients.nasa_api import nasa_api_client
from services.asteroid_service import (
    get_cached_asteroids, 
    find_asteroid_in_cache, 
    get_complete_asteroid_data
)

asteroids_bp = Blueprint('asteroids', __name__)

# Load the cache once when the application starts
CACHED_ASTEROIDS = get_cached_asteroids()

def _get_asteroid_data(asteroid_id: str):
    """
    Helper function to retrieve asteroid data.
    First checks the local cache, then falls back to the live API.
    """
    # 1. Check the cache first
    asteroid = find_asteroid_in_cache(asteroid_id, CACHED_ASTEROIDS)
    if asteroid:
        return asteroid
    
    # 2. If not in cache, try the live API
    return get_complete_asteroid_data(asteroid_id)


@asteroids_bp.route('/asteroids', methods=['GET'])
def list_cached_asteroids():
    """
    Returns the list of asteroids loaded from the local cache.
    This endpoint does NOT fall back to the live API to ensure a stable
    list for the frontend.
    """
    return jsonify({
        "asteroids": CACHED_ASTEROIDS,
        "count": len(CACHED_ASTEROIDS)
    }), 200


@asteroids_bp.route('/asteroids/current', methods=['GET'])
def get_current_asteroids():
    """
    Gets a list of asteroids approaching Earth in the next 7 days.
    This endpoint always uses the live NASA API.
    """
    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        result = nasa_api_client.get_asteroids_by_date(start_date, end_date)
        
        if result["error"]:
            return jsonify({"error": result["error"]}), 500
            
        return jsonify(result["data"]), 200
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500


@asteroids_bp.route('/asteroids/<string:asteroid_id>', methods=['GET'])
def get_asteroid(asteroid_id):
    """
    Gets complete data for a specific asteroid, checking the cache first
    and falling back to a live API call if not found.
    """
    try:
        asteroid = _get_asteroid_data(asteroid_id)
        if asteroid:
            return jsonify(asteroid), 200
        else:
            return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
    except Exception as e:
        # Log the exception e in a real application
        return jsonify({"error": "An internal server error occurred."}), 500


@asteroids_bp.route('/asteroids/<string:asteroid_id>/orbital', methods=['GET'])
def get_orbital_data(asteroid_id):
    """
    Gets orbital and physical parameters for a specific asteroid.
    """
    try:
        asteroid = _get_asteroid_data(asteroid_id)
        if not asteroid or "orbital_elements" not in asteroid or not asteroid["orbital_elements"]:
            return jsonify({
                "error": f"Orbital data not available for asteroid {asteroid_id}."
            }), 404
            
        return jsonify({
            "asteroid_id": asteroid.get("id"),
            "name": asteroid.get("name"),
            "orbital_elements": asteroid.get("orbital_elements"),
            "physical_parameters": asteroid.get("physical_parameters")
        }), 200
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500


@asteroids_bp.route('/asteroids/<string:asteroid_id>/data', methods=['POST'])
def post_asteroid_data(asteroid_id):
    """
    Accepts a POST request and returns complete data for an asteroid.
    Functionally identical to the GET endpoint as per requirements.
    """
    try:
        asteroid = _get_asteroid_data(asteroid_id)
        if asteroid:
            return jsonify(asteroid), 200
        else:
            return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500
