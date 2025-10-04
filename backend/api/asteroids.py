from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from clients.nasa_api import nasa_api_client
from services.asteroid_service import (
    get_cached_asteroids, 
    find_asteroid_in_cache, 
    get_complete_asteroid_data
)
from services.elevation_service import get_impact_context

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


@asteroids_bp.route('/elevation', methods=['GET'])
def get_elevation_data():
    """
    Gets elevation and terrain context for a given latitude and longitude.
    """
    lat_str = request.args.get('lat')
    lng_str = request.args.get('lng')

    # Validate presence of lat/lng
    if not lat_str or not lng_str:
        return jsonify({"error": "Latitude and longitude are required parameters."}), 400

    # Validate that lat/lng are valid floats
    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except ValueError:
        return jsonify({"error": "Latitude and longitude must be valid numbers."}), 400

    # Validate ranges
    if not -90 <= lat <= 90:
        return jsonify({"error": "Latitude must be between -90 and 90."}), 400
    if not -180 <= lng <= 180:
        return jsonify({"error": "Longitude must be between -180 and 180."}), 400

    try:
        # Get the comprehensive impact context
        context = get_impact_context(lat, lng)
        return jsonify(context), 200
    except Exception as e:
        # In a real app, you'd want to log the error e
        return jsonify({"error": "An internal server error occurred."}), 500


@asteroids_bp.route('/simulate-impact', methods=['POST'])
def simulate_impact():
    """
    Simulate asteroid impact with user-provided parameters.
    This endpoint allows frontend users to test custom scenarios with sliders.
    """
    try:
        data = request.get_json()
        
        # Validate required parameters
        diameter_m = data.get('diameter_m')
        velocity_kms = data.get('velocity_kms')
        
        if diameter_m is None or velocity_kms is None:
            return jsonify({
                "error": "diameter_m and velocity_kms are required parameters"
            }), 400
        
        # Validate parameter ranges
        if diameter_m <= 0 or diameter_m > 10000:
            return jsonify({
                "error": "diameter_m must be between 0 and 10000 meters"
            }), 400
            
        if velocity_kms <= 0 or velocity_kms > 100:
            return jsonify({
                "error": "velocity_kms must be between 0 and 100 km/s"
            }), 400
        
        # Optional parameters with defaults
        impact_angle = data.get('impact_angle', 45.0)
        impact_lat = data.get('impact_lat', 0.0)
        impact_lng = data.get('impact_lng', 0.0)
        
        # Import physics modules
        from backend.physics.impact import ImpactPhysics
        from backend.utils.conversions import estimate_asteroid_mass
        
        # Convert velocity to m/s
        velocity_ms = velocity_kms * 1000
        
        # Calculate impact results
        results = ImpactPhysics.complete_impact_analysis(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            impact_angle_degrees=impact_angle
        )
        
        # Add input parameters to results for frontend reference
        results["input_parameters"] = {
            "diameter_m": diameter_m,
            "velocity_kms": velocity_kms,
            "velocity_ms": velocity_ms,
            "impact_angle": impact_angle,
            "impact_coordinates": {"lat": impact_lat, "lng": impact_lng}
        }
        
        # Add estimated mass for reference
        mass_kg = estimate_asteroid_mass(diameter_m)
        results["estimated_mass_kg"] = mass_kg
        
        return jsonify(results), 200
        
    except ImportError as e:
        return jsonify({
            "error": f"Physics module not available: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Simulation failed: {str(e)}"
        }), 500


@asteroids_bp.route('/asteroid-parameters', methods=['GET'])
def get_asteroid_parameters():
    """
    Get parameter ranges for frontend sliders based on cached asteroid data.
    """
    try:
        diameters = []
        velocities = []
        
        for asteroid in CACHED_ASTEROIDS:
            # Collect diameter data
            diameter_data = asteroid.get("diameter_meters", {})
            if diameter_data:
                if "estimated_diameter_min" in diameter_data:
                    diameters.append(diameter_data["estimated_diameter_min"])
                if "estimated_diameter_max" in diameter_data:
                    diameters.append(diameter_data["estimated_diameter_max"])
            
            # Collect velocity data
            velocity_kms = asteroid.get("velocity_kms")
            if velocity_kms and isinstance(velocity_kms, (int, float)):
                velocities.append(float(velocity_kms))
        
        return jsonify({
            "diameter_range_m": {
                "min": min(diameters) if diameters else 10,
                "max": max(diameters) if diameters else 1000,
                "count": len(diameters),
                "data_source": "NASA cached asteroids"
            },
            "velocity_range_kms": {
                "min": min(velocities) if velocities else 5,
                "max": max(velocities) if velocities else 50,
                "count": len(velocities),
                "data_source": "NASA cached asteroids"
            },
            "recommended_defaults": {
                "diameter_m": 100,
                "velocity_kms": 20,
                "impact_angle": 45,
                "description": "Typical small asteroid parameters"
            },
            "total_asteroids": len(CACHED_ASTEROIDS)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get parameters: {str(e)}"}), 500
