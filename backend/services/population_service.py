"""
This service provides population density calculations for casualty estimates.

The functions in this module use the worldcities.csv data to calculate
population within circular damage zones using haversine distance.
"""
import csv
import os
from functools import lru_cache
from typing import List, Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

# --- Caching Mechanism ---
_cities_data_cache = None

# --- Data Loading Functions ---

def load_cities_data() -> List[Dict]:
    """
    Loads world cities data from the CSV file.

    Returns:
        A list of dictionaries, where each dictionary represents a city.
        Returns an empty list if the file is not found.
    """
    global _cities_data_cache
    if _cities_data_cache is not None:
        return _cities_data_cache

    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'reference_data', 'worldcities.csv')
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            _cities_data_cache = []
            for row in reader:
                # Convert relevant fields to numeric types
                try:
                    city_data = {
                        'city': row['city'],
                        'city_ascii': row['city_ascii'],
                        'lat': float(row['lat']),
                        'lng': float(row['lng']),
                        'country': row['country'],
                        'iso2': row['iso2'],
                        'iso3': row['iso3'],
                        'admin_name': row['admin_name'],
                        'capital': row['capital'],
                        'population': float(row['population']) if row['population'] else 0.0,
                        'id': row['id']
                    }
                    _cities_data_cache.append(city_data)
                except (ValueError, KeyError):
                    # Skip rows with invalid data
                    continue
        return _cities_data_cache
    except FileNotFoundError:
        return []

# --- Distance Calculation Functions ---

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates the great-circle distance between two points on Earth using the Haversine formula.

    Args:
        lat1: Latitude of the first point in degrees.
        lng1: Longitude of the first point in degrees.
        lat2: Latitude of the second point in degrees.
        lng2: Longitude of the second point in degrees.

    Returns:
        Distance in kilometers.
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

# --- Population Query Functions ---

@lru_cache(maxsize=500)
def get_population_in_radius(lat: float, lng: float, radius_km: float) -> Dict:
    """
    Calculates the total population and affected cities within a circular radius.

    This function uses the haversine distance formula to determine which cities
    fall within the specified radius from the impact point.

    Args:
        lat: Latitude of the impact point in degrees.
        lng: Longitude of the impact point in degrees.
        radius_km: Radius of the damage zone in kilometers.

    Returns:
        A dictionary containing:
        - total_population: Total population count within the radius
        - affected_cities: List of cities with their details (name, country, population, distance)
        - city_count: Number of cities affected
    """
    # Validate coordinates
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        return {
            "total_population": 0,
            "affected_cities": [],
            "city_count": 0,
            "error": "Invalid coordinates"
        }
    
    # Validate radius
    if radius_km <= 0:
        return {
            "total_population": 0,
            "affected_cities": [],
            "city_count": 0,
            "error": "Invalid radius"
        }
    
    cities = load_cities_data()
    
    if not cities:
        return {
            "total_population": 0,
            "affected_cities": [],
            "city_count": 0,
            "error": "Cities data not available"
        }
    
    affected_cities = []
    total_population = 0
    
    for city in cities:
        distance = haversine_distance(lat, lng, city['lat'], city['lng'])
        
        if distance <= radius_km:
            city_info = {
                "city": city['city'],
                "city_ascii": city['city_ascii'],
                "country": city['country'],
                "population": city['population'],
                "distance_km": round(distance, 2),
                "lat": city['lat'],
                "lng": city['lng']
            }
            affected_cities.append(city_info)
            total_population += city['population']
    
    # Sort cities by distance from impact point
    affected_cities.sort(key=lambda x: x['distance_km'])
    
    return {
        "total_population": int(total_population),
        "affected_cities": affected_cities,
        "city_count": len(affected_cities)
    }

def get_casualties_by_zone(lat: float, lng: float, damage_zones: List[Dict]) -> Dict:
    """
    Calculates casualties for multiple damage zones with different lethality rates.

    Args:
        lat: Latitude of the impact point in degrees.
        lng: Longitude of the impact point in degrees.
        damage_zones: List of zone dictionaries, each containing:
            - radius_km: Radius of the zone in kilometers
            - lethality_rate: Fraction of population killed (0.0 to 1.0)
            - zone_name: Name of the damage zone (e.g., "crater", "thermal", "blast")

    Returns:
        A dictionary containing:
        - total_casualties: Total estimated casualties across all zones
        - zones: List of zone results with casualties and affected cities
        - total_affected_population: Total population in all zones
    """
    # Validate coordinates
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        return {
            "total_casualties": 0,
            "zones": [],
            "total_affected_population": 0,
            "error": "Invalid coordinates"
        }
    
    # Sort zones by radius (largest first) to handle overlapping zones
    sorted_zones = sorted(damage_zones, key=lambda x: x.get('radius_km', 0), reverse=True)
    
    zone_results = []
    total_casualties = 0
    cities_counted = set()  # Track cities to avoid double-counting
    
    for zone in sorted_zones:
        radius_km = zone.get('radius_km', 0)
        lethality_rate = zone.get('lethality_rate', 0.0)
        zone_name = zone.get('zone_name', 'unknown')
        
        if radius_km <= 0 or lethality_rate < 0 or lethality_rate > 1:
            continue
        
        population_data = get_population_in_radius(lat, lng, radius_km)
        
        # Calculate casualties for this zone
        zone_casualties = int(population_data['total_population'] * lethality_rate)
        
        zone_result = {
            "zone_name": zone_name,
            "radius_km": radius_km,
            "lethality_rate": lethality_rate,
            "population": population_data['total_population'],
            "casualties": zone_casualties,
            "city_count": population_data['city_count'],
            "major_cities": population_data['affected_cities'][:10]  # Top 10 closest cities
        }
        
        zone_results.append(zone_result)
        total_casualties += zone_casualties
        
        # Track cities for total affected population calculation
        for city in population_data['affected_cities']:
            cities_counted.add(city['city_ascii'])
    
    # Calculate total affected population (from largest zone to avoid double-counting)
    total_affected_population = 0
    if zone_results:
        total_affected_population = zone_results[0]['population']
    
    return {
        "total_casualties": total_casualties,
        "zones": zone_results,
        "total_affected_population": total_affected_population
    }

def get_nearest_cities(lat: float, lng: float, count: int = 10) -> List[Dict]:
    """
    Finds the nearest cities to a given point.

    Args:
        lat: Latitude of the point in degrees.
        lng: Longitude of the point in degrees.
        count: Number of nearest cities to return (default: 10).

    Returns:
        A list of the nearest cities with their details and distances.
    """
    # Validate coordinates
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        return []
    
    cities = load_cities_data()
    
    if not cities:
        return []
    
    # Calculate distances for all cities
    cities_with_distance = []
    for city in cities:
        distance = haversine_distance(lat, lng, city['lat'], city['lng'])
        city_info = {
            "city": city['city'],
            "city_ascii": city['city_ascii'],
            "country": city['country'],
            "population": city['population'],
            "distance_km": round(distance, 2),
            "lat": city['lat'],
            "lng": city['lng']
        }
        cities_with_distance.append(city_info)
    
    # Sort by distance and return top N
    cities_with_distance.sort(key=lambda x: x['distance_km'])
    return cities_with_distance[:count]
