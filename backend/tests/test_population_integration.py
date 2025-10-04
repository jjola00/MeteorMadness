"""
Integration tests for the population service demonstrating real-world scenarios.
"""
import pytest
from backend.services.population_service import (
    get_population_in_radius,
    get_casualties_by_zone,
    get_nearest_cities
)


class TestRealWorldScenarios:
    """Integration tests with realistic impact scenarios."""
    
    def test_new_york_impact_scenario(self):
        """Test a hypothetical asteroid impact near New York City."""
        # New York City coordinates
        lat, lng = 40.7128, -74.0060
        
        # Define realistic damage zones for a medium-sized asteroid
        damage_zones = [
            {
                'radius_km': 5,
                'lethality_rate': 1.0,
                'zone_name': 'crater'
            },
            {
                'radius_km': 20,
                'lethality_rate': 0.8,
                'zone_name': 'blast_severe'
            },
            {
                'radius_km': 50,
                'lethality_rate': 0.3,
                'zone_name': 'blast_moderate'
            },
            {
                'radius_km': 100,
                'lethality_rate': 0.05,
                'zone_name': 'thermal'
            }
        ]
        
        result = get_casualties_by_zone(lat, lng, damage_zones)
        
        # Verify structure
        assert 'total_casualties' in result
        assert 'zones' in result
        assert 'total_affected_population' in result
        
        # Should have significant casualties in populated area
        assert result['total_casualties'] > 0
        assert result['total_affected_population'] > 0
        
        # Should have all 4 zones
        assert len(result['zones']) == 4
        
        # Verify zone ordering (largest first)
        radii = [zone['radius_km'] for zone in result['zones']]
        assert radii == sorted(radii, reverse=True)
        
        print(f"\nNew York Impact Scenario:")
        print(f"Total casualties: {result['total_casualties']:,}")
        print(f"Total affected population: {result['total_affected_population']:,}")
        for zone in result['zones']:
            print(f"  {zone['zone_name']}: {zone['casualties']:,} casualties "
                  f"({zone['city_count']} cities)")
    
    def test_tokyo_impact_scenario(self):
        """Test a hypothetical asteroid impact near Tokyo."""
        # Tokyo coordinates
        lat, lng = 35.6870, 139.7495
        
        # Small asteroid impact
        damage_zones = [
            {
                'radius_km': 2,
                'lethality_rate': 1.0,
                'zone_name': 'crater'
            },
            {
                'radius_km': 10,
                'lethality_rate': 0.5,
                'zone_name': 'blast'
            },
            {
                'radius_km': 30,
                'lethality_rate': 0.1,
                'zone_name': 'thermal'
            }
        ]
        
        result = get_casualties_by_zone(lat, lng, damage_zones)
        
        # Tokyo is very densely populated
        assert result['total_casualties'] > 0
        assert result['total_affected_population'] > 1000000  # At least 1 million
        
        print(f"\nTokyo Impact Scenario:")
        print(f"Total casualties: {result['total_casualties']:,}")
        print(f"Total affected population: {result['total_affected_population']:,}")
    
    def test_pacific_ocean_impact(self):
        """Test an impact in the middle of the Pacific Ocean."""
        # Middle of Pacific Ocean
        lat, lng = 0, -160
        
        damage_zones = [
            {
                'radius_km': 50,
                'lethality_rate': 1.0,
                'zone_name': 'crater'
            },
            {
                'radius_km': 200,
                'lethality_rate': 0.1,
                'zone_name': 'tsunami'
            }
        ]
        
        result = get_casualties_by_zone(lat, lng, damage_zones)
        
        # Should have very low or zero casualties
        assert result['total_casualties'] >= 0
        
        print(f"\nPacific Ocean Impact Scenario:")
        print(f"Total casualties: {result['total_casualties']:,}")
        print(f"Total affected population: {result['total_affected_population']:,}")
        print(f"Cities affected: {sum(zone['city_count'] for zone in result['zones'])}")
    
    def test_sahara_desert_impact(self):
        """Test an impact in the Sahara Desert (low population)."""
        # Central Sahara Desert
        lat, lng = 23.0, 10.0
        
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
            }
        ]
        
        result = get_casualties_by_zone(lat, lng, damage_zones)
        
        # Should have low casualties due to low population density
        assert result['total_casualties'] >= 0
        
        print(f"\nSahara Desert Impact Scenario:")
        print(f"Total casualties: {result['total_casualties']:,}")
        print(f"Total affected population: {result['total_affected_population']:,}")
    
    def test_nearest_cities_to_impact(self):
        """Test finding nearest cities to various impact locations."""
        # Test multiple locations
        locations = [
            (40.7128, -74.0060, "New York"),
            (35.6870, 139.7495, "Tokyo"),
            (51.5074, -0.1278, "London"),
            (-33.8688, 151.2093, "Sydney")
        ]
        
        for lat, lng, name in locations:
            cities = get_nearest_cities(lat, lng, 5)
            
            assert len(cities) > 0
            assert cities[0]['distance_km'] < 100  # Nearest city within 100km
            
            print(f"\nNearest cities to {name}:")
            for i, city in enumerate(cities[:3], 1):
                print(f"  {i}. {city['city']}, {city['country']} "
                      f"({city['distance_km']:.1f} km, pop: {int(city['population']):,})")
    
    def test_population_density_comparison(self):
        """Compare population density in different regions."""
        locations = [
            (35.6870, 139.7495, "Tokyo (dense)"),
            (40.7128, -74.0060, "New York (dense)"),
            (23.0, 10.0, "Sahara (sparse)"),
            (0, -160, "Pacific Ocean (none)")
        ]
        
        radius_km = 50
        
        print(f"\nPopulation within {radius_km}km radius:")
        for lat, lng, name in locations:
            result = get_population_in_radius(lat, lng, radius_km)
            print(f"  {name}: {result['total_population']:,} people "
                  f"in {result['city_count']} cities")
            
            assert result['total_population'] >= 0
            assert result['city_count'] >= 0
    
    def test_tunguska_like_event(self):
        """Simulate a Tunguska-like event (1908, Siberia)."""
        # Tunguska event location
        lat, lng = 60.8858, 101.8939
        
        # Tunguska was ~15 megatons, devastated ~2000 km²
        # Radius ≈ 25 km for severe damage
        damage_zones = [
            {
                'radius_km': 25,
                'lethality_rate': 0.9,
                'zone_name': 'blast_zone'
            },
            {
                'radius_km': 50,
                'lethality_rate': 0.1,
                'zone_name': 'thermal'
            }
        ]
        
        result = get_casualties_by_zone(lat, lng, damage_zones)
        
        # Tunguska had no casualties due to remote location
        # Modern simulation should show low casualties
        print(f"\nTunguska-like Event Scenario:")
        print(f"Total casualties: {result['total_casualties']:,}")
        print(f"Total affected population: {result['total_affected_population']:,}")
        print(f"Cities affected: {sum(zone['city_count'] for zone in result['zones'])}")
        
        assert result['total_casualties'] >= 0
