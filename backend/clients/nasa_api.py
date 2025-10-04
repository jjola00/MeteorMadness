import os
from functools import lru_cache
from .base_api_client import BaseAPIClient

class NasaApiClient(BaseAPIClient):
    """A client for the NASA Near-Earth Object API."""

    def __init__(self, api_key=None, timeout=10):
        super().__init__(
            base_url="https://api.nasa.gov/neo/rest/v1",
            api_key=api_key or os.getenv("NASA_API_KEY", "DEMO_KEY"),
            timeout=timeout
        )

    def _parse_asteroid_data(self, asteroid):
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

    @lru_cache(maxsize=128)
    def get_asteroid_by_id(self, asteroid_id):
        """Fetches a specific asteroid by its ID."""
        data, error = self.get(f"/neo/{asteroid_id}")
        if error:
            return {"data": None, "error": error}
        return {"data": self._parse_asteroid_data(data), "error": None}

    @lru_cache(maxsize=32)
    def get_asteroids_by_date(self, start_date, end_date):
        """Fetches asteroids within a given date range."""
        params = {"start_date": start_date, "end_date": end_date}
        data, error = self.get("/feed", params=params)
        
        if error:
            return {"data": None, "error": error}
        
        asteroids = []
        for date in data.get("near_earth_objects", {}):
            for asteroid in data["near_earth_objects"][date]:
                asteroids.append(self._parse_asteroid_data( asteroid))
        
        return {"data": asteroids, "error": None}

    @lru_cache(maxsize=32)
    def browse_asteroids(self, page=0):
        """Browses all asteroids with pagination."""
        params = {"page": page}
        data, error = self.get("/neo/browse", params=params)
        
        if error:
            return {"data": None, "error": error}
        
        asteroids = [
            self._parse_asteroid_data(asteroid)
            for asteroid in data.get("near_earth_objects", [])
        ]
        return {"data": asteroids, "error": None}

# --- Singleton instance for easy import ---
nasa_api_client = NasaApiClient()
