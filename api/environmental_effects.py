"""
Flask API endpoints for environmental effects processing.
Provides temporal effect data and interpolation support for the frontend.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional
import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.environmental_effects import EnvironmentalEffectsProcessor
from physics.impact import ImpactPhysics
from utils.errors import ValidationError, handle_error

# Create blueprint
environmental_effects_bp = Blueprint('environmental_effects', __name__)

# Initialize processor
effects_processor = EnvironmentalEffectsProcessor()


@environmental_effects_bp.route('/temporal-effects', methods=['POST'])
def calculate_temporal_effects():
    """
    Calculate environmental effects over time.
    
    Expected JSON payload:
    {
        "impact_data": {
            "impact_energy": {"effective_energy_j": float},
            "crater": {"volume_m3": float, "ejecta_radius_km": float},
            "effects": {"overpressure_1psi_km": float, ...},
            "impact_location": {"lat": float, "lon": float}
        },
        "time_range_hours": [start_hours, end_hours],
        "time_resolution_hours": float,
        "effect_types": ["seismic", "atmospheric", "thermal", "debris", "infrastructure"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("No JSON data provided")
        
        # Validate required fields
        if 'impact_data' not in data:
            raise ValidationError("Missing 'impact_data' field")
        
        impact_data = data['impact_data']
        time_range_hours = data.get('time_range_hours', [0, 168])  # Default: 1 week
        time_resolution_hours = data.get('time_resolution_hours', 1.0)
        effect_types = data.get('effect_types', None)
        
        # Validate time range
        if len(time_range_hours) != 2 or time_range_hours[0] >= time_range_hours[1]:
            raise ValidationError("Invalid time_range_hours: must be [start, end] with start < end")
        
        if time_resolution_hours <= 0:
            raise ValidationError("time_resolution_hours must be positive")
        
        # Calculate temporal effects
        results = effects_processor.calculate_temporal_effects(
            impact_data=impact_data,
            time_range_hours=tuple(time_range_hours),
            time_resolution_hours=time_resolution_hours,
            effect_types=effect_types
        )
        
        return jsonify({
            "status": "success",
            "data": results
        }), 200
        
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return handle_error(e)


@environmental_effects_bp.route('/point-effects', methods=['POST'])
def get_point_effects():
    """
    Get environmental effects at a specific time and location.
    
    Expected JSON payload:
    {
        "impact_data": {...},
        "time_hours": float,
        "location": {"lat": float, "lon": float},
        "effect_types": ["seismic", "atmospheric", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("No JSON data provided")
        
        # Validate required fields
        required_fields = ['impact_data', 'time_hours', 'location']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        impact_data = data['impact_data']
        time_hours = data['time_hours']
        location_data = data['location']
        effect_types = data.get('effect_types', None)
        
        # Validate location
        if 'lat' not in location_data or 'lon' not in location_data:
            raise ValidationError("Location must contain 'lat' and 'lon' fields")
        
        location = (location_data['lat'], location_data['lon'])
        
        # Validate coordinates
        if not (-90 <= location[0] <= 90) or not (-180 <= location[1] <= 180):
            raise ValidationError("Invalid coordinates: lat must be [-90,90], lon must be [-180,180]")
        
        if time_hours < 0:
            raise ValidationError("time_hours must be non-negative")
        
        # Get effects at point
        results = effects_processor.get_effect_at_time(
            impact_data=impact_data,
            time_hours=time_hours,
            location=location,
            effect_types=effect_types
        )
        
        return jsonify({
            "status": "success",
            "data": results
        }), 200
        
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return handle_error(e)


@environmental_effects_bp.route('/interpolated-effects', methods=['POST'])
def get_interpolated_effects():
    """
    Get interpolated environmental effects for smooth timeline visualization.
    
    Expected JSON payload:
    {
        "impact_data": {...},
        "locations": [{"lat": float, "lon": float}, ...],
        "time_points": [float, float, ...],
        "effect_types": ["seismic", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("No JSON data provided")
        
        # Validate required fields
        required_fields = ['impact_data', 'locations', 'time_points']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        impact_data = data['impact_data']
        locations = data['locations']
        time_points = data['time_points']
        effect_types = data.get('effect_types', None)
        
        # Validate inputs
        if not isinstance(locations, list) or len(locations) == 0:
            raise ValidationError("locations must be a non-empty list")
        
        if not isinstance(time_points, list) or len(time_points) == 0:
            raise ValidationError("time_points must be a non-empty list")
        
        # Validate each location
        for i, loc in enumerate(locations):
            if 'lat' not in loc or 'lon' not in loc:
                raise ValidationError(f"Location {i} must contain 'lat' and 'lon' fields")
            if not (-90 <= loc['lat'] <= 90) or not (-180 <= loc['lon'] <= 180):
                raise ValidationError(f"Invalid coordinates in location {i}")
        
        # Validate time points
        for i, t in enumerate(time_points):
            if not isinstance(t, (int, float)) or t < 0:
                raise ValidationError(f"time_points[{i}] must be a non-negative number")
        
        # Calculate effects for all combinations
        results = []
        
        for time_hours in time_points:
            time_results = {
                'time_hours': time_hours,
                'locations': []
            }
            
            for location in locations:
                loc_tuple = (location['lat'], location['lon'])
                effects = effects_processor.get_effect_at_time(
                    impact_data=impact_data,
                    time_hours=time_hours,
                    location=loc_tuple,
                    effect_types=effect_types
                )
                time_results['locations'].append(effects)
            
            results.append(time_results)
        
        return jsonify({
            "status": "success",
            "data": {
                "time_series": results,
                "metadata": {
                    "num_locations": len(locations),
                    "num_time_points": len(time_points),
                    "effect_types": effect_types or list(effects_processor.effect_types.keys())
                }
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return handle_error(e)


@environmental_effects_bp.route('/sample-scenario', methods=['GET'])
def get_sample_scenario():
    """
    Get a sample environmental effects scenario for testing and development.
    
    Query parameters:
    - scenario: 'small', 'medium', 'large' (default: 'medium')
    - location: 'land' or 'ocean' (default: 'land')
    """
    try:
        scenario_size = request.args.get('scenario', 'medium').lower()
        impact_location_type = request.args.get('location', 'land').lower()
        
        # Define sample scenarios
        scenarios = {
            'small': {
                'diameter_m': 50,
                'velocity_ms': 15000,
                'description': 'Tunguska-like event (50m asteroid)'
            },
            'medium': {
                'diameter_m': 200,
                'velocity_ms': 20000,
                'description': 'Regional impact event (200m asteroid)'
            },
            'large': {
                'diameter_m': 1000,
                'velocity_ms': 25000,
                'description': 'Civilization-threatening event (1km asteroid)'
            }
        }
        
        if scenario_size not in scenarios:
            raise ValidationError("scenario must be 'small', 'medium', or 'large'")
        
        if impact_location_type not in ['land', 'ocean']:
            raise ValidationError("location must be 'land' or 'ocean'")
        
        # Generate sample impact data
        scenario = scenarios[scenario_size]
        
        # Sample impact locations
        if impact_location_type == 'land':
            impact_location = {'lat': 40.7128, 'lon': -74.0060}  # New York area
        else:
            impact_location = {'lat': 30.0, 'lon': -60.0}  # Atlantic Ocean
        
        # Calculate impact analysis
        impact_analysis = ImpactPhysics.complete_impact_analysis(
            diameter_m=scenario['diameter_m'],
            velocity_ms=scenario['velocity_ms'],
            impact_angle_degrees=45.0,
            include_atmospheric_entry=True
        )
        
        # Add location to impact data
        impact_analysis['impact_location'] = impact_location
        
        # Calculate sample temporal effects (first 24 hours)
        temporal_effects = effects_processor.calculate_temporal_effects(
            impact_data=impact_analysis,
            time_range_hours=(0, 24),
            time_resolution_hours=0.5
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "scenario": {
                    "size": scenario_size,
                    "location_type": impact_location_type,
                    "description": scenario['description'],
                    "parameters": {
                        "diameter_m": scenario['diameter_m'],
                        "velocity_ms": scenario['velocity_ms']
                    }
                },
                "impact_analysis": impact_analysis,
                "temporal_effects": temporal_effects
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return handle_error(e)


@environmental_effects_bp.route('/effect-types', methods=['GET'])
def get_available_effect_types():
    """Get list of available environmental effect types."""
    try:
        effect_types = list(effects_processor.effect_types.keys())
        
        # Add descriptions for each effect type
        descriptions = {
            'seismic': 'Seismic wave propagation and ground motion effects',
            'atmospheric': 'Atmospheric disturbances and air quality changes',
            'thermal': 'Thermal radiation and heat effects',
            'debris': 'Ejecta and debris field effects',
            'infrastructure': 'Infrastructure damage and cascading failures'
        }
        
        result = []
        for effect_type in effect_types:
            result.append({
                'type': effect_type,
                'description': descriptions.get(effect_type, 'No description available')
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "effect_types": result,
                "count": len(result)
            }
        }), 200
        
    except Exception as e:
        return handle_error(e)