from flask import Blueprint, jsonify, request
from services.asteroid_service import get_cached_asteroids, find_asteroid_in_cache

asteroids_bp = Blueprint('asteroids', __name__)

@asteroids_bp.route('/asteroids', methods=['GET'])
def list_asteroids():
    """Lists all cached asteroids."""
    cached_asteroids = get_cached_asteroids()
    if not cached_asteroids:
        return jsonify({"error": "No asteroids found in cache."}), 404
    return jsonify(cached_asteroids), 200

@asteroids_bp.route('/asteroids/<string:asteroid_id>', methods=['GET'])
def get_asteroid(asteroid_id):
    """Gets details for a specific asteroid from the cache."""
    cached_asteroids = get_cached_asteroids()
    asteroid = find_asteroid_in_cache(asteroid_id, cached_asteroids)
    
    if not asteroid:
        return jsonify({"error": f"Asteroid with ID {asteroid_id} not found in cache."}), 404
    return jsonify(asteroid), 200

@asteroids_bp.route('/asteroids/<string:asteroid_id>/orbital', methods=['GET'])
def get_orbital_data(asteroid_id):
    """Gets Keplerian orbital elements for a specific asteroid."""
    cached_asteroids = get_cached_asteroids()
    asteroid = find_asteroid_in_cache(asteroid_id, cached_asteroids)
    
    if not asteroid:
        return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
        
    orbital_elements = asteroid.get("orbital_elements")
    if not orbital_elements:
        return jsonify({"error": f"Orbital data not available for asteroid {asteroid_id}."}), 404
        
    return jsonify(orbital_elements), 200

@asteroids_bp.route('/asteroids/<string:asteroid_id>/data', methods=['POST'])
def post_asteroid_data(asteroid_id):
    """
    Accepts and returns complete data for an asteroid.
    This is a placeholder to fulfill the requirement.
    """
    cached_asteroids = get_cached_asteroids()
    asteroid = find_asteroid_in_cache(asteroid_id, cached_asteroids)

    if not asteroid:
        return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
    
    # In a real scenario, you might do something with the POSTed data.
    # For now, just return the complete data as a confirmation.
    return jsonify(asteroid), 200
