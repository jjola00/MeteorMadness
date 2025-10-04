from typing import Dict, Any, Optional
from .base_api_client import BaseAPIClient

class SbdbApiClient(BaseAPIClient):
    """
    A client for NASA's Small-Body Database (SBDB) API.
    """
    def __init__(self, timeout: int = 10):
        super().__init__(
            base_url="https://ssd-api.jpl.nasa.gov",
            timeout=timeout
        )

    def _parse_sbdb_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parses the response from the SBDB API."""
        # --- Extract Orbital Elements ---
        orbital_elements_raw = data.get("orbit", {}).get("elements", [])
        orbital_elements = {
            element['name']: float(element['value'])
            for element in orbital_elements_raw
            if element['name'] in ['e', 'a', 'i', 'om', 'w', 'ma', 'epoch']
        }

        # --- Extract Physical Parameters (FIXED) ---
        physical_params_raw = data.get("phys_par", {})  # Defaults to dict
        physical_params = {
            key: float(physical_params_raw[key]) if physical_params_raw.get(key) else None
            for key in ['diameter', 'density', 'rot_per']
            if key in physical_params_raw
        }
        
        # --- Extract Object Name ---
        object_name = data.get("object", {}).get("fullname")

        return {
            "object_name": object_name,
            "orbital_elements": orbital_elements,
            "physical_parameters": physical_params,
        }

    def get_orbital_parameters(self, asteroid_id: str) -> Dict[str, Any]:
        """
        Fetches orbital and physical parameters for a given asteroid.
        
        Returns:
            A dictionary with 'data' and 'error' keys for consistent interface.
        """
        params = {"sstr": asteroid_id}
        data, error = self.get("/sbdb.api", params=params)

        if error:
            return {"data": None, "error": error}
            
        if data.get("message") == "no data found":
            return {"data": None, "error": "No data found for this asteroid"}
            
        return {"data": self._parse_sbdb_data(data), "error": None}

# --- Singleton instance for easy import ---
sbdb_api_client = SbdbApiClient()
