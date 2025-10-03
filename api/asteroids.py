from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from clients.nasa_api import nasa_api_client

asteroids_bp = Blueprint('asteroids', __name__)

@asteroids_bp.route('/asteroids', methods=['GET'])
def list_asteroids():
    """Lists asteroids with pagination."""
    page = request.args.get('page', 0, type=int)
    result = nasa_api_client.browse_asteroids(page=page)
    if result["error"]:
        return jsonify({"error": result["error"]}), 500
    return jsonify(result["data"]), 200

@asteroids_bp.route('/asteroids/<string:asteroid_id>', methods=['GET'])
def get_asteroid(asteroid_id):
    """Gets details for a specific asteroid."""
    result = nasa_api_client.get_asteroid_by_id(asteroid_id)
    if result["error"]:
        return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
    if not result["data"]:
         return jsonify({"error": f"Asteroid with ID {asteroid_id} not found."}), 404
    return jsonify(result["data"]), 200

@asteroids_bp.route('/asteroids/current', methods=['GET'])
def get_current_asteroids():
    """Gets asteroids approaching in the next 30 days."""
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    result = nasa_api_client.get_asteroids_by_date(start_date, end_date)
    if result["error"]:
        return jsonify({"error": result["error"]}), 500
    return jsonify(result["data"]), 200

@asteroids_bp.route('/calculate-impact', methods=['POST'])
def calculate_impact():
    """Calculates the potential impact of an asteroid."""
    data = request.get_json()
    required_fields = ["diameter_m", "velocity_km_s", "impact_lat", "impact_lng", "population_density"]
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    # Placeholder for impact calculation logic
    # In a real application, this would involve complex physics models.
    impact_assessment = {
        "message": "Impact calculation is a placeholder.",
        "input_data": data,
        "estimated_blast_radius_km": data["diameter_m"] * 0.1, # Simplistic placeholder
        "potential_risk": "high" if data["population_density"] > 100 else "medium"
    }
    
    return jsonify(impact_assessment), 200
