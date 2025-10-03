import os
import requests
from functools import lru_cache

# --- Configuration ---
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov/neo/rest/v1"
TIMEOUT = 10  # seconds

# --- Helper Functions ---
def _parse_asteroid_data(asteroid):
    """Extracts essential fields from a single asteroid's data."""
    if not asteroid:
        return None

    close_approach_data = asteroid.get("close_approach_data", [])
    if not close_approach_data:
        return {
        "id": asteroid.get("neo_reference_id"),
        "name": asteroid.get("name"),
        "is_hazardous": asteroid.get("is_potentially_hazardous_asteroid"),
        "diameter": asteroid.get("estimated_diameter", {}),
        "velocity": None,
        "close_approach_date": None,
    }

    latest_approach = close_approach_data[0]
    
    return {
        "id": asteroid.get("neo_reference_id"),
        "name": asteroid.get("name"),
        "is_hazardous": asteroid.get("is_potentially_hazardous_asteroid"),
        "diameter_meters": asteroid.get("estimated_diameter", {}).get("meters", {}),
        "diameter_kilometers": asteroid.get("estimated_diameter", {}).get("kilometers", {}),
        "velocity_kms": latest_approach.get("relative_velocity", {}).get("kilometers_per_second"),
        "close_approach_date": latest_approach.get("close_approach_date_full"),
    }

# --- API Functions ---
@lru_cache(maxsize=128)
def get_asteroid_by_id(asteroid_id):
    """Fetches a specific asteroid by its ID."""
    url = f"{BASE_URL}/neo/{asteroid_id}?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return {"data": _parse_asteroid_data(response.json()), "error": None}
    except requests.exceptions.RequestException as e:
        return {"data": None, "error": str(e)}

@lru_cache(maxsize=32)
def get_asteroids_by_date(start_date, end_date):
    """Fetches asteroids within a given date range."""
    url = f"{BASE_URL}/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        asteroids = []
        for date in data.get("near_earth_objects", {}):
            for asteroid in data["near_earth_objects"][date]:
                asteroids.append(_parse_asteroid_data(asteroid))
        
        return {"data": asteroids, "error": None}
    except requests.exceptions.RequestException as e:
        return {"data": None, "error": str(e)}

@lru_cache(maxsize=32)
def browse_asteroids(page=0):
    """Browses all asteroids with pagination."""
    url = f"{BASE_URL}/neo/browse?page={page}&api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        asteroids = [
            _parse_asteroid_data(asteroid) 
            for asteroid in response.json().get("near_earth_objects", [])
        ]
        return {"data": asteroids, "error": None}
    except requests.exceptions.RequestException as e:
        return {"data": None, "error": str(e)}
