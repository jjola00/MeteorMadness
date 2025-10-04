"""
This service loads and provides access to historical reference data, such as
earthquake records, impact events, and magnitude effect tables. The data is
cached in memory after the first load to ensure efficient access.
"""
import json
import csv
import os
from typing import List, Dict, Optional

# --- Caching Mechanism ---
# Simple in-memory cache for the loaded data.
_earthquake_data_cache = None
_magnitude_effects_cache = None
_impact_events_cache = None

# --- Data Loading Functions ---

def load_earthquake_data() -> List[Dict]:
    """
    Loads historical earthquake data from the CSV file.

    Returns:
        A list of dictionaries, where each dictionary represents an earthquake.
        Returns an empty list if the file is not found.
    """
    global _earthquake_data_cache
    if _earthquake_data_cache is not None:
        return _earthquake_data_cache

    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_data', 'earthquakes_historical.csv')
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            _earthquake_data_cache = [row for row in reader]
            # Convert relevant fields to numeric types
            for event in _earthquake_data_cache:
                event['latitude'] = float(event['latitude'])
                event['longitude'] = float(event['longitude'])
                event['depth'] = float(event['depth'])
                event['mag'] = float(event['mag'])
        return _earthquake_data_cache
    except FileNotFoundError:
        return []

def load_magnitude_effects() -> Dict:
    """
    Loads the magnitude effects lookup table from the JSON file.

    Returns:
        A dictionary representing the magnitude effects table.
        Returns an empty dictionary if the file is not found.
    """
    global _magnitude_effects_cache
    if _magnitude_effects_cache is not None:
        return _magnitude_effects_cache

    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_data', 'magnitude_effects.json')
    try:
        with open(file_path, 'r') as f:
            _magnitude_effects_cache = json.load(f)
        return _magnitude_effects_cache
    except FileNotFoundError:
        return {}

def load_impact_events() -> List[Dict]:
    """
    Loads historical impact event data from the JSON file.

    Returns:
        A list of dictionaries, where each dictionary represents an impact event.
        Returns an empty list if the file is not found.
    """
    global _impact_events_cache
    if _impact_events_cache is not None:
        return _impact_events_cache

    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_data', 'impact_events.json')
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            _impact_events_cache = data.get("impacts", [])
        return _impact_events_cache
    except FileNotFoundError:
        return []

# --- Data Query Functions ---

def find_similar_earthquake(magnitude: float) -> Optional[Dict]:
    """
    Finds a historical earthquake with a similar magnitude.

    Args:
        magnitude: The target magnitude to search for.

    Returns:
        The closest matching earthquake within a ±0.3 magnitude range, or None.
    """
    earthquakes = load_earthquake_data()
    if not earthquakes:
        return None

    closest_quake = None
    min_diff = float('inf')

    for quake in earthquakes:
        diff = abs(quake['mag'] - magnitude)
        if diff <= 0.3 and diff < min_diff:
            min_diff = diff
            closest_quake = quake
            
    return closest_quake

def find_similar_impact(energy_megatons: float) -> Optional[Dict]:
    """
    Finds a historical impact event with similar energy.

    Args:
        energy_megatons: The target energy in megatons to search for.

    Returns:
        The impact event with the closest estimated energy.
    """
    impacts = load_impact_events()
    if not impacts:
        return None

    # Filter out events with non-numeric energy values for safe comparison
    valid_impacts = [imp for imp in impacts if isinstance(imp.get("estimated_energy_megatons"), (int, float))]
    if not valid_impacts:
        return None

    # Find the impact with the minimum energy difference
    closest_impact = min(
        valid_impacts, 
        key=lambda x: abs(x["estimated_energy_megatons"] - energy_megatons)
    )
    return closest_impact

def get_magnitude_effects(magnitude: float) -> Dict:
    """
    Looks up the estimated effects for a given earthquake magnitude.

    Args:
        magnitude: The magnitude of the earthquake.

    Returns:
        A dictionary of effects (felt_radius_km, damage_radius_km, description).
        Returns a default "unknown" state if no matching bin is found.
    """
    effects_table = load_magnitude_effects()
    if not effects_table:
        return {"description": "unknown", "felt_radius_km": 0, "damage_radius_km": 0}

    if magnitude >= 8.0:
        return effects_table.get("8.0+", {})
    if 7.5 <= magnitude < 8.0:
        return effects_table.get("7.5-8.0", {})
    if 7.0 <= magnitude < 7.5:
        return effects_table.get("7.0-7.5", {})
    if 6.5 <= magnitude < 7.0:
        return effects_table.get("6.5-7.0", {})
    if 6.0 <= magnitude < 6.5:
        return effects_table.get("6.0-6.5", {})
        
    return {"description": "Below threshold for significant widespread effects", "felt_radius_km": 0, "damage_radius_km": 0}
