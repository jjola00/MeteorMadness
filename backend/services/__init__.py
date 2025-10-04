"""
Services module for backend functionality.

This module provides various services for the asteroid impact simulator:
- asteroid_service: Asteroid data and calculations
- elevation_service: Elevation and terrain data
- population_service: Population density and casualty calculations
- reference_data_service: Historical reference data
"""

from backend.services.population_service import (
    get_population_in_radius,
    get_casualties_by_zone,
    get_nearest_cities,
    haversine_distance
)

__all__ = [
    'get_population_in_radius',
    'get_casualties_by_zone',
    'get_nearest_cities',
    'haversine_distance'
]

