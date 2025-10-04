"""
Demo script for the population service.

This script demonstrates the capabilities of the population service
with various real-world impact scenarios.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.population_service import (
    get_population_in_radius,
    get_casualties_by_zone,
    get_nearest_cities,
    haversine_distance
)


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    else:
        print(f"{'='*70}")


def demo_haversine_distance():
    """Demonstrate haversine distance calculations."""
    print_separator("Haversine Distance Calculations")
    
    locations = [
        ("New York", (40.7128, -74.0060)),
        ("London", (51.5074, -0.1278)),
        ("Tokyo", (35.6870, 139.7495)),
        ("Sydney", (-33.8688, 151.2093))
    ]
    
    print("\nDistances between major cities:")
    for i, (city1, (lat1, lng1)) in enumerate(locations):
        for city2, (lat2, lng2) in locations[i+1:]:
            distance = haversine_distance(lat1, lng1, lat2, lng2)
            print(f"  {city1} to {city2}: {distance:,.1f} km")


def demo_population_in_radius():
    """Demonstrate population queries within a radius."""
    print_separator("Population Within Radius")
    
    scenarios = [
        ("New York City", 40.7128, -74.0060, 50),
        ("Tokyo", 35.6870, 139.7495, 50),
        ("Sahara Desert", 23.0, 10.0, 100),
        ("Pacific Ocean", 0, -160, 200)
    ]
    
    for name, lat, lng, radius in scenarios:
        result = get_population_in_radius(lat, lng, radius)
        print(f"\n{name} (radius: {radius} km):")
        print(f"  Total population: {result['total_population']:,}")
        print(f"  Cities affected: {result['city_count']}")
        
        if result['affected_cities']:
            print(f"  Nearest cities:")
            for city in result['affected_cities'][:3]:
                print(f"    - {city['city']}, {city['country']}: "
                      f"{int(city['population']):,} people ({city['distance_km']:.1f} km)")


def demo_nearest_cities():
    """Demonstrate finding nearest cities."""
    print_separator("Nearest Cities to Impact Points")
    
    locations = [
        ("New York City", 40.7128, -74.0060),
        ("Tokyo", 35.6870, 139.7495),
        ("London", 51.5074, -0.1278),
        ("Middle of Pacific", 0, -160)
    ]
    
    for name, lat, lng in locations:
        cities = get_nearest_cities(lat, lng, 5)
        print(f"\n{name}:")
        if cities:
            for i, city in enumerate(cities, 1):
                print(f"  {i}. {city['city']}, {city['country']}")
                print(f"     Distance: {city['distance_km']:.1f} km, "
                      f"Population: {int(city['population']):,}")
        else:
            print("  No cities found nearby")


def demo_casualty_calculations():
    """Demonstrate multi-zone casualty calculations."""
    print_separator("Casualty Calculations for Impact Scenarios")
    
    # Scenario 1: Small asteroid over New York
    print("\nScenario 1: Small Asteroid Impact - New York City")
    print("  Asteroid: 50m diameter, 20 km/s velocity")
    print("  Energy: ~10 megatons")
    
    damage_zones_small = [
        {'radius_km': 2, 'lethality_rate': 1.0, 'zone_name': 'crater'},
        {'radius_km': 10, 'lethality_rate': 0.7, 'zone_name': 'blast_severe'},
        {'radius_km': 30, 'lethality_rate': 0.2, 'zone_name': 'blast_moderate'},
        {'radius_km': 60, 'lethality_rate': 0.05, 'zone_name': 'thermal'}
    ]
    
    result = get_casualties_by_zone(40.7128, -74.0060, damage_zones_small)
    print(f"\n  Total casualties: {result['total_casualties']:,}")
    print(f"  Total affected population: {result['total_affected_population']:,}")
    print(f"\n  Damage zones:")
    for zone in result['zones']:
        print(f"    {zone['zone_name']} ({zone['radius_km']} km):")
        print(f"      Population: {zone['population']:,}")
        print(f"      Casualties: {zone['casualties']:,} ({zone['lethality_rate']*100:.0f}% lethality)")
        print(f"      Cities: {zone['city_count']}")
    
    # Scenario 2: Large asteroid over Tokyo
    print("\n" + "-"*70)
    print("\nScenario 2: Large Asteroid Impact - Tokyo")
    print("  Asteroid: 200m diameter, 25 km/s velocity")
    print("  Energy: ~1000 megatons")
    
    damage_zones_large = [
        {'radius_km': 10, 'lethality_rate': 1.0, 'zone_name': 'crater'},
        {'radius_km': 40, 'lethality_rate': 0.9, 'zone_name': 'blast_severe'},
        {'radius_km': 100, 'lethality_rate': 0.4, 'zone_name': 'blast_moderate'},
        {'radius_km': 200, 'lethality_rate': 0.1, 'zone_name': 'thermal'}
    ]
    
    result = get_casualties_by_zone(35.6870, 139.7495, damage_zones_large)
    print(f"\n  Total casualties: {result['total_casualties']:,}")
    print(f"  Total affected population: {result['total_affected_population']:,}")
    print(f"\n  Damage zones:")
    for zone in result['zones']:
        print(f"    {zone['zone_name']} ({zone['radius_km']} km):")
        print(f"      Population: {zone['population']:,}")
        print(f"      Casualties: {zone['casualties']:,} ({zone['lethality_rate']*100:.0f}% lethality)")
        print(f"      Cities: {zone['city_count']}")
    
    # Scenario 3: Ocean impact with tsunami
    print("\n" + "-"*70)
    print("\nScenario 3: Ocean Impact - Pacific Ocean")
    print("  Asteroid: 100m diameter, 20 km/s velocity")
    print("  Energy: ~100 megatons")
    print("  Location: Middle of Pacific Ocean")
    
    damage_zones_ocean = [
        {'radius_km': 50, 'lethality_rate': 1.0, 'zone_name': 'crater'},
        {'radius_km': 500, 'lethality_rate': 0.05, 'zone_name': 'tsunami_zone'}
    ]
    
    result = get_casualties_by_zone(0, -160, damage_zones_ocean)
    print(f"\n  Total casualties: {result['total_casualties']:,}")
    print(f"  Total affected population: {result['total_affected_population']:,}")
    print(f"  Cities affected: {sum(zone['city_count'] for zone in result['zones'])}")
    print("\n  Note: Ocean impacts have minimal direct casualties but may cause")
    print("        tsunamis affecting coastal regions (not modeled in this demo)")


def demo_edge_cases():
    """Demonstrate edge case handling."""
    print_separator("Edge Cases and Error Handling")
    
    print("\n1. Invalid coordinates:")
    result = get_population_in_radius(100, 0, 50)
    print(f"   Result: {result.get('error', 'No error')}")
    
    print("\n2. Invalid radius:")
    result = get_population_in_radius(40.7128, -74.0060, -10)
    print(f"   Result: {result.get('error', 'No error')}")
    
    print("\n3. Remote location (Sahara Desert):")
    result = get_population_in_radius(23.0, 10.0, 50)
    print(f"   Population: {result['total_population']:,}")
    print(f"   Cities: {result['city_count']}")
    
    print("\n4. Ocean impact (no nearby cities):")
    result = get_population_in_radius(0, -160, 100)
    print(f"   Population: {result['total_population']:,}")
    print(f"   Cities: {result['city_count']}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  POPULATION SERVICE DEMONSTRATION")
    print("  Asteroid Impact Simulator - Casualty Calculations")
    print("="*70)
    
    demo_haversine_distance()
    demo_population_in_radius()
    demo_nearest_cities()
    demo_casualty_calculations()
    demo_edge_cases()
    
    print_separator()
    print("\nDemo complete! The population service provides:")
    print("  ✓ Haversine distance calculations")
    print("  ✓ Population queries within circular zones")
    print("  ✓ Multi-zone casualty estimates with lethality rates")
    print("  ✓ Nearest city lookups")
    print("  ✓ Caching for performance")
    print("  ✓ Edge case handling (ocean impacts, remote areas)")
    print()


if __name__ == "__main__":
    main()
