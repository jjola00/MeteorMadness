from typing import Dict, Any, Optional, List
import json
import os
from backend.clients.nasa_api import nasa_api_client
from backend.clients.sbdb_api import sbdb_api_client

def get_complete_asteroid_data(asteroid_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches and merges asteroid data from both NASA NEO API and SBDB API.
    
    Args:
        asteroid_id: The ID of the asteroid to look up.
        
    Returns:
        A merged dictionary containing data from both APIs, or None if NEO API fails.
        If SBDB API fails, orbital data will be None but NEO data is still returned.
    """
    # Fetch data from NASA NEO API
    neo_result = nasa_api_client.get_asteroid_by_id(asteroid_id)
    
    # If NEO API fails, return None
    if neo_result["error"] or not neo_result["data"]:
        return None
    
    neo_data = neo_result["data"]
    
    # Fetch data from SBDB API
    sbdb_result = sbdb_api_client.get_orbital_parameters(asteroid_id)
    
    # Merge the data
    merged_data = {
        "id": neo_data.get("id"),
        "name": neo_data.get("name"),
        "is_hazardous": neo_data.get("is_hazardous"),
        "diameter_meters": neo_data.get("diameter_meters"),
        "diameter_kilometers": neo_data.get("diameter_kilometers"),
        "velocity_kms": neo_data.get("velocity_kms"),
        "close_approach_date": neo_data.get("close_approach_date"),
        "orbital_elements": None,
        "physical_parameters": None,
    }
    
    # Add SBDB data if available
    if sbdb_result["data"]:
        sbdb_data = sbdb_result["data"]
        merged_data["orbital_elements"] = sbdb_data.get("orbital_elements")
        merged_data["physical_parameters"] = sbdb_data.get("physical_parameters")
    
    return merged_data


def get_cached_asteroids() -> List[Dict[str, Any]]:
    """
    Loads and returns cached asteroid data from the JSON file.
    
    Returns:
        A list of cached asteroid dictionaries, or an empty list if file doesn't exist
        or if there's a JSON decode error.
    """
    cache_path = os.path.join("data", "asteroids_cache.json")
    
    if not os.path.exists(cache_path):
        return []
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def find_asteroid_in_cache(asteroid_id: str, cached: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Searches for an asteroid in the cached list by ID.
    
    Args:
        asteroid_id: The ID of the asteroid to find.
        cached: The list of cached asteroid dictionaries.
        
    Returns:
        The asteroid dictionary if found, None otherwise.
    """
    for asteroid in cached:
        if asteroid.get("id") == asteroid_id:
            return asteroid
    return None

