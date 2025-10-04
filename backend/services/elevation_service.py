"""
This service provides elevation and location context for impact calculations.

The functions in this module use the elevation_client to fetch elevation data
and then derive contextual information such as whether an impact is in the ocean,
the type of terrain, and an estimate of ocean depth. This data is intended to be
used by downstream physics calculations (e.g., tsunami modeling).
"""
from functools import lru_cache
from typing import Optional, Dict

from backend.clients.elevation_api import elevation_client

@lru_cache(maxsize=1000)
def get_elevation_at_point(lat: float, lng: float) -> Optional[float]:
    """
    Gets the elevation for a single point, with validation and caching.

    Args:
        lat: Latitude of the point.
        lng: Longitude of the point.

    Returns:
        The elevation in meters, or None if validation or the API call fails.
    """
    # Validate coordinates
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        return None
    
    return elevation_client.get_elevation(lat, lng)

def is_ocean_impact(lat: float, lng: float) -> bool:
    """
    Determines if a given coordinate is over the ocean.

    Args:
        lat: Latitude of the point.
        lng: Longitude of the point.

    Returns:
        True if the location is at or below sea level, False otherwise.
        If elevation data is unavailable, it safely defaults to False (land).
    """
    elevation = get_elevation_at_point(lat, lng)
    
    if elevation is None:
        return False  # Assume land as a safe default
        
    return elevation <= 0

def get_terrain_type(elevation: Optional[float]) -> str:
    """
    Classifies the terrain based on elevation.

    Args:
        elevation: The elevation in meters.

    Returns:
        A string describing the terrain type.
    """
    if elevation is None:
        return "unknown"
    if elevation <= 0:
        return "ocean"
    if 0 < elevation <= 10:
        return "coastal"
    if 10 < elevation <= 200:
        return "lowland"
    if 200 < elevation <= 1000:
        return "highland"
    return "mountain"

def get_ocean_depth_estimate(elevation: Optional[float]) -> Optional[float]:
    """
    Estimates the ocean depth based on elevation for ocean impacts.
    This provides a value for tsunami calculations.

    Args:
        elevation: The elevation in meters.

    Returns:
        The estimated depth in meters if it's an ocean location, else None.
    """
    if elevation is not None and elevation <= 0:
        return abs(elevation)
    return None

def get_impact_context(lat: float, lng: float) -> Dict:
    """
    Provides a comprehensive context for a given impact location.

    This function aggregates elevation, terrain type, and ocean depth to be
    used in physics calculations.

    Args:
        lat: Latitude of the impact point.
        lng: Longitude of the impact point.

    Returns:
        A dictionary containing detailed context about the location.
    """
    elevation = get_elevation_at_point(lat, lng)
    is_ocean = elevation is not None and elevation <= 0
    terrain_type = get_terrain_type(elevation)
    ocean_depth = get_ocean_depth_estimate(elevation)
    
    return {
        "latitude": lat,
        "longitude": lng,
        "elevation_meters": elevation,
        "is_ocean": is_ocean,
        "terrain_type": terrain_type,
        "ocean_depth_meters": ocean_depth,
        "data_available": elevation is not None
    }
