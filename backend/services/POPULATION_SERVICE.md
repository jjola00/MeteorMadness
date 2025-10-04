# Population Service Documentation

## Overview

The population service provides population density calculations and casualty estimates for asteroid impact scenarios. It uses the worldcities.csv dataset with haversine distance calculations to determine affected populations within circular damage zones.

## Features

- **Haversine Distance Calculation**: Accurate great-circle distance between geographic coordinates
- **Population Queries**: Calculate total population within a specified radius
- **Multi-Zone Casualty Estimates**: Support for multiple damage zones with different lethality rates
- **Nearest City Lookup**: Find cities closest to an impact point
- **Caching**: LRU cache for frequently queried locations (500 entries)
- **Edge Case Handling**: Graceful handling of ocean impacts, remote areas, and invalid inputs

## API Reference

### `haversine_distance(lat1, lng1, lat2, lng2)`

Calculates the great-circle distance between two points on Earth.

**Parameters:**
- `lat1` (float): Latitude of first point in degrees
- `lng1` (float): Longitude of first point in degrees
- `lat2` (float): Latitude of second point in degrees
- `lng2` (float): Longitude of second point in degrees

**Returns:**
- `float`: Distance in kilometers

**Example:**
```python
distance = haversine_distance(40.7128, -74.0060, 51.5074, -0.1278)
# Returns: ~5570 km (New York to London)
```

### `get_population_in_radius(lat, lng, radius_km)`

Calculates total population and affected cities within a circular radius.

**Parameters:**
- `lat` (float): Latitude of impact point in degrees
- `lng` (float): Longitude of impact point in degrees
- `radius_km` (float): Radius of damage zone in kilometers

**Returns:**
- `dict`: Dictionary containing:
  - `total_population` (int): Total population count
  - `affected_cities` (list): List of affected cities with details
  - `city_count` (int): Number of cities affected
  - `error` (str, optional): Error message if validation fails

**Example:**
```python
result = get_population_in_radius(35.6870, 139.7495, 50)
# Returns population data for 50km radius around Tokyo
```

### `get_casualties_by_zone(lat, lng, damage_zones)`

Calculates casualties for multiple damage zones with different lethality rates.

**Parameters:**
- `lat` (float): Latitude of impact point in degrees
- `lng` (float): Longitude of impact point in degrees
- `damage_zones` (list): List of zone dictionaries, each containing:
  - `radius_km` (float): Radius of the zone
  - `lethality_rate` (float): Fraction of population killed (0.0 to 1.0)
  - `zone_name` (str): Name of the damage zone

**Returns:**
- `dict`: Dictionary containing:
  - `total_casualties` (int): Total estimated casualties
  - `zones` (list): List of zone results with casualties
  - `total_affected_population` (int): Total population in all zones
  - `error` (str, optional): Error message if validation fails

**Example:**
```python
damage_zones = [
    {'radius_km': 10, 'lethality_rate': 1.0, 'zone_name': 'crater'},
    {'radius_km': 50, 'lethality_rate': 0.5, 'zone_name': 'blast'},
    {'radius_km': 100, 'lethality_rate': 0.1, 'zone_name': 'thermal'}
]
result = get_casualties_by_zone(40.7128, -74.0060, damage_zones)
```

### `get_nearest_cities(lat, lng, count=10)`

Finds the nearest cities to a given point.

**Parameters:**
- `lat` (float): Latitude of the point in degrees
- `lng` (float): Longitude of the point in degrees
- `count` (int, optional): Number of nearest cities to return (default: 10)

**Returns:**
- `list`: List of nearest cities with details and distances

**Example:**
```python
cities = get_nearest_cities(35.6870, 139.7495, 5)
# Returns 5 nearest cities to Tokyo
```

## Data Source

The service uses `data/reference_data/worldcities.csv` which contains:
- City name and ASCII name
- Latitude and longitude coordinates
- Country and ISO codes
- Administrative region
- Population data
- Unique city ID

## Performance

- **Caching**: `get_population_in_radius()` uses LRU cache (500 entries) for repeated queries
- **Data Loading**: Cities data is loaded once and cached in memory
- **Complexity**: O(n) for population queries where n is the number of cities in the dataset

## Edge Cases

1. **Ocean Impacts**: Returns zero population and empty city list
2. **Remote Areas**: Returns zero population if no cities within radius
3. **Invalid Coordinates**: Returns error message for coordinates outside valid ranges
4. **Invalid Radius**: Returns error message for negative or zero radius
5. **Missing Data**: Gracefully handles missing or invalid city data

## Testing

Comprehensive test coverage includes:
- Unit tests for all functions (`test_population_service.py`)
- Integration tests with real-world scenarios (`test_population_integration.py`)
- Edge case validation
- Performance testing with caching

Run tests:
```bash
python -m pytest backend/tests/test_population_service.py -v
python -m pytest backend/tests/test_population_integration.py -v
```

## Demo

See `demo/population_service_demo.py` for interactive demonstrations of all features.

```bash
python demo/population_service_demo.py
```

## Requirements Satisfied

This service satisfies the following requirements from the specification:
- **2.4**: Population density data integration for casualty calculations
- **4.3**: Accurate casualty estimates based on population density
- **5.3**: Handling of edge cases (ocean impacts, remote areas)
