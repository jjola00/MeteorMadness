import logging
from typing import List, Optional, Tuple

from .base_api_client import BaseAPIClient

logger = logging.getLogger(__name__)

class OpenElevationClient(BaseAPIClient):
    """
    A client for the Open-Elevation API.
    
    This client provides methods to get elevation data for single points or
    batches of coordinates. It's free and does not require an API key.
    """
    def __init__(self):
        super().__init__(
            base_url="https://api.open-elevation.com/api/v1",
            timeout=10
        )

    def get_elevation(self, lat: float, lng: float) -> Optional[float]:
        """
        Gets the elevation for a single geographical coordinate.

        Args:
            lat: Latitude of the point.
            lng: Longitude of the point.

        Returns:
            The elevation in meters as a float, or None if an error occurs.
            Negative values indicate locations below sea level.
        """
        params = {"locations": f"{lat},{lng}"}
        
        try:
            data, error = self.get("/lookup", params=params)

            if error:
                logger.error(f"API request failed for ({lat}, {lng}): {error}")
                return None
            
            if not data or 'results' not in data or not data['results']:
                logger.warning(f"No results found for ({lat}, {lng})")
                return None
            
            elevation = data['results'][0]['elevation']
            return float(elevation)

        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Error parsing elevation data for ({lat}, {lng}): {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred for ({lat}, {lng}): {e}")
            return None

    def get_elevations_batch(self, coordinates: List[Tuple[float, float]]) -> List[Optional[float]]:
        """
        Gets elevations for a batch of geographical coordinates.

        Args:
            coordinates: A list of (latitude, longitude) tuples.

        Returns:
            A list of elevations in meters. The order of the list matches the
            input order. A value of None will be present for any coordinate
            where the lookup failed.
        """
        if not coordinates:
            return []
            
        locations_str = "|".join([f"{lat},{lng}" for lat, lng in coordinates])
        params = {"locations": locations_str}
        
        try:
            data, error = self.get("/lookup", params=params)

            if error:
                logger.error(f"Batch API request failed: {error}")
                return [None] * len(coordinates)
            
            if not data or 'results' not in data:
                logger.warning("Batch request returned no results.")
                return [None] * len(coordinates)
            
            # Create a dictionary for efficient lookup of elevations by coordinates
            elevation_map = {
                (r['latitude'], r['longitude']): r['elevation'] 
                for r in data['results'] if 'latitude' in r and 'longitude' in r
            }

            # Map the results back to the original order of coordinates
            results_list = []
            for lat, lng in coordinates:
                elevation = elevation_map.get((lat, lng))
                if elevation is not None:
                    results_list.append(float(elevation))
                else:
                    results_list.append(None)
            
            return results_list

        except Exception as e:
            logger.error(f"An unexpected error occurred during batch processing: {e}")
            return [None] * len(coordinates)

elevation_client = OpenElevationClient()
