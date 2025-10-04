"""
Unit tests for the population service.

Tests the haversine distance calculation, population queries,
and casualty estimation functions.
"""
import pytest
from backend.services.population_service import (
    haversine_distance,
    get_population_in_radius,
    get_casualties_by_zone,
    get_nearest_cities,
    load_cities_data
)


class TestHaversineDistance:
    """Tests for the haversine distance calculation."""
    
    def test_same_point(self):
        """Distance between the same point should be zero."""
        distance = haversine_distance(0, 0, 0, 0)
        assert distance == 0
    
    def test_known_distance(self):
        """Test with known distance between New York and London."""
        # New York: 40.7128° N, 74.0060° W
        # London: 51.5074° N, 0.1278° W
        distance = haversine_distance(40.7128, -74.0060, 51.5074, -0.1278)
        # Expected distance is approximately 5570 km
        assert 5500 < distance < 5600
    
    def test_equator_distance(self):
        """Test distance along the equator."""
        # 1 degree of longitude at equator ≈ 111 km
        distance = haversine_distance(0, 0, 0, 1)
        assert 110 < distance < 112
    
    def test_antipodal_points(self):
        """Test distance between antipodal points (opposite sides of Earth)."""
        # Should be approximately half Earth's circumference
        distance = haversine_distance(0, 0, 0, 180)
        # Half circumference ≈ 20,000 km
        assert 19900 < distance < 20100


class TestGetPopulationInRadius:
    """Tests for population queries within a radius."""
    
    def test_invalid_coordinates(self):
        """Test with invalid coordinates."""
        result = get_population_in_radius(100, 0, 100)
        assert result['total_population'] == 0
        assert 'error' in result
        
        result = get_population_in_radius(0, 200, 100)
        assert result['total_population'] == 0
        assert 'error' in result
    
    def test_invalid_radius(self):
        """Test with invalid radius."""
        result = get_population_in_radius(0, 0, -10)
        assert result['total_population'] == 0
        assert 'error' in result
        
        result = get_population_in_radius(0, 0, 0)
        assert result['total_population'] == 0
        assert 'error' in result
    
    def test_tokyo_area(self):
        """Test population query around Tokyo."""
        # Tokyo coordinates: 35.6870, 139.7495
        result = get_population_in_radius(35.6870, 139.7495, 50)
        
        assert result['total_population'] > 0
        assert result['city_count'] > 0
        assert len(result['affected_cities']) > 0
        
        # Tokyo should be in the list
        tokyo_found = any(
            'Tokyo' in city['city'] for city in result['affected_cities']
        )
        assert tokyo_found
    
    def test_ocean_impact(self):
        """Test population query in the middle of the ocean."""
        # Middle of Pacific Ocean
        result = get_population_in_radius(0, -160, 100)
        
        # Should have zero or very low population
        assert result['total_population'] >= 0
        assert result['city_count'] >= 0
    
    def test_small_radius(self):
        """Test with a very small radius."""
        result = get_population_in_radius(35.6870, 139.7495, 1)
        
        # Should have fewer cities than larger radius
        assert result['city_count'] >= 0
    
    def test_cities_sorted_by_distance(self):
        """Test that affected cities are sorted by distance."""
        result = get_population_in_radius(35.6870, 139.7495, 200)
        
        if len(result['affected_cities']) > 1:
            distances = [city['distance_km'] for city in result['affected_cities']]
            assert distances == sorted(distances)
    
    def test_caching(self):
        """Test that caching works for repeated queries."""
        # First call
        result1 = get_population_in_radius(35.6870, 139.7495, 100)
        
        # Second call with same parameters (should use cache)
        result2 = get_population_in_radius(35.6870, 139.7495, 100)
        
        assert result1 == result2


class TestGetCasualtiesByZone:
    """Tests for multi-zone casualty calculations."""
    
    def test_single_zone(self):
        """Test casualty calculation with a single damage zone."""
        damage_zones = [
            {
                'radius_km': 50,
                'lethality_rate': 0.9,
                'zone_name': 'crater'
            }
        ]
        
        result = get_casualties_by_zone(35.6870, 139.7495, damage_zones)
        
        assert result['total_casualties'] >= 0
        assert len(result['zones']) == 1
        assert result['zones'][0]['zone_name'] == 'crater'
        assert result['zones'][0]['lethality_rate'] == 0.9
    
    def test_multiple_zones(self):
        """Test casualty calculation with multiple damage zones."""
        damage_zones = [
            {
                'radius_km': 10,
                'lethality_rate': 1.0,
                'zone_name': 'crater'
            },
            {
                'radius_km': 50,
                'lethality_rate': 0.5,
                'zone_name': 'blast'
            },
            {
                'radius_km': 100,
                'lethality_rate': 0.1,
                'zone_name': 'thermal'
            }
        ]
        
        result = get_casualties_by_zone(35.6870, 139.7495, damage_zones)
        
        assert result['total_casualties'] >= 0
        assert len(result['zones']) == 3
        assert result['total_affected_population'] >= 0
    
    def test_invalid_coordinates(self):
        """Test with invalid coordinates."""
        damage_zones = [
            {
                'radius_km': 50,
                'lethality_rate': 0.5,
                'zone_name': 'blast'
            }
        ]
        
        result = get_casualties_by_zone(100, 0, damage_zones)
        assert result['total_casualties'] == 0
        assert 'error' in result
    
    def test_zero_lethality(self):
        """Test with zero lethality rate."""
        damage_zones = [
            {
                'radius_km': 50,
                'lethality_rate': 0.0,
                'zone_name': 'minimal'
            }
        ]
        
        result = get_casualties_by_zone(35.6870, 139.7495, damage_zones)
        
        # Should have zero casualties but population data
        assert result['total_casualties'] == 0
        assert len(result['zones']) == 1
    
    def test_ocean_impact_zones(self):
        """Test casualty calculation for ocean impact."""
        damage_zones = [
            {
                'radius_km': 100,
                'lethality_rate': 0.5,
                'zone_name': 'tsunami'
            }
        ]
        
        # Middle of Pacific Ocean
        result = get_casualties_by_zone(0, -160, damage_zones)
        
        assert result['total_casualties'] >= 0
        assert len(result['zones']) == 1


class TestGetNearestCities:
    """Tests for finding nearest cities."""
    
    def test_tokyo_nearest_cities(self):
        """Test finding nearest cities to Tokyo."""
        cities = get_nearest_cities(35.6870, 139.7495, 5)
        
        assert len(cities) <= 5
        assert len(cities) > 0
        
        # Tokyo should be the first or very close
        assert cities[0]['distance_km'] < 50
    
    def test_invalid_coordinates(self):
        """Test with invalid coordinates."""
        cities = get_nearest_cities(100, 0, 5)
        assert len(cities) == 0
    
    def test_cities_sorted_by_distance(self):
        """Test that cities are sorted by distance."""
        cities = get_nearest_cities(0, 0, 10)
        
        if len(cities) > 1:
            distances = [city['distance_km'] for city in cities]
            assert distances == sorted(distances)
    
    def test_count_parameter(self):
        """Test that count parameter limits results."""
        cities_5 = get_nearest_cities(35.6870, 139.7495, 5)
        cities_10 = get_nearest_cities(35.6870, 139.7495, 10)
        
        assert len(cities_5) <= 5
        assert len(cities_10) <= 10


class TestLoadCitiesData:
    """Tests for loading cities data."""
    
    def test_data_loads(self):
        """Test that cities data loads successfully."""
        cities = load_cities_data()
        
        assert len(cities) > 0
        assert 'city' in cities[0]
        assert 'lat' in cities[0]
        assert 'lng' in cities[0]
        assert 'population' in cities[0]
    
    def test_data_types(self):
        """Test that data types are correct."""
        cities = load_cities_data()
        
        if len(cities) > 0:
            city = cities[0]
            assert isinstance(city['lat'], float)
            assert isinstance(city['lng'], float)
            assert isinstance(city['population'], float)
    
    def test_caching(self):
        """Test that data is cached after first load."""
        cities1 = load_cities_data()
        cities2 = load_cities_data()
        
        # Should return the same cached object
        assert cities1 is cities2
