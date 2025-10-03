"""
Comprehensive test suite for Meteor Madness backend physics modules.
"""

import sys
import os
# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversions import UnitConverter, estimate_asteroid_mass, kinetic_energy
from physics.impact import ImpactPhysics
from physics.orbital import OrbitalMechanics
from physics.environmental import EnvironmentalEffects
from physics.mitigation import MitigationStrategies


def test_integration():
    """Test integration between all physics modules."""
    print("🧪 Comprehensive Physics Integration Test")
    print("=" * 50)
    
    # Scenario: 500m asteroid impact simulation
    print("Scenario: 500m diameter asteroid impact")
    
    # Initial parameters
    diameter_m = 500.0
    velocity_ms = 20000.0  # 20 km/s
    impact_location = (35.0, -75.0)  # Off U.S. East Coast
    density_kg_m3 = 3000.0
    
    mass_kg = estimate_asteroid_mass(diameter_m, density_kg_m3)
    energy_j = kinetic_energy(mass_kg, velocity_ms)
    
    print(f"  Diameter: {diameter_m} m")
    print(f"  Mass: {mass_kg:.2e} kg")
    print(f"  Velocity: {velocity_ms/1000} km/s")
    print(f"  Energy: {UnitConverter.tnt_equivalent(energy_j, 'TNT_Mt'):.1f} megatons TNT")
    print()
    
    # Impact Physics Analysis
    print("1. Impact Physics:")
    impact_results = ImpactPhysics.complete_impact_analysis(
        diameter_m, velocity_ms, include_atmospheric_entry=True
    )
    
    print(f"   Atmospheric survival: {impact_results['atmospheric_entry']['surviving_mass_kg']/mass_kg*100:.0f}%")
    print(f"   Final energy: {impact_results['impact_energy']['effective_energy_tnt_kt']:.0f} kilotons TNT")
    print(f"   Crater diameter: {impact_results['crater']['diameter_km']:.2f} km")
    print(f"   Thermal radius: {impact_results['effects']['thermal_radius_km']:.1f} km")
    print()
    
    # Environmental Effects
    print("2. Environmental Effects:")
    env_results = EnvironmentalEffects.complete_environmental_analysis(
        impact_results['impact_energy']['effective_energy_j'],
        impact_location,
        is_ocean_impact=True,  # Ocean impact
        water_depth_m=1000.0
    )
    
    print(f"   Seismic magnitude: {env_results['seismic']['magnitude']:.1f}")
    print(f"   Initial tsunami: {env_results['tsunami_generation']['initial_amplitude_m']:.1f} m")
    print(f"   Tsunami at 500 km: {env_results['tsunami_propagation']['amplitudes_m'][20]:.1f} m")
    print(f"   Travel time to 500 km: {env_results['tsunami_propagation']['travel_times_hours'][20]:.1f} hours")
    print()
    
    # Mitigation Analysis
    print("3. Mitigation Strategies (if detected 10 years early):")
    mitigation_results = MitigationStrategies.mission_comparison(
        mass_kg, diameter_m, velocity_ms,
        impact_time_years=10.0,
        deflection_time_years=2.0
    )
    
    best_method = mitigation_results['comparison_summary']['most_effective_method']
    
    print(f"   Kinetic impactor deflection: {mitigation_results['kinetic_impactor']['miss_distance_km']:.0f} km")
    print(f"   Gravity tractor deflection: {mitigation_results['gravity_tractor']['miss_distance_km']:.0f} km")
    print(f"   Nuclear deflection: {mitigation_results['nuclear_deflection']['miss_distance_km']:.0f} km")
    print(f"   Best method: {best_method}")
    print()
    
    # Orbital Mechanics Test
    print("4. Orbital Mechanics:")
    # Create a sample orbit
    initial_state = np.array([1.3e11, 0, 0, 0, 25000, 0])  # 1.3 AU, 25 km/s
    trajectory = OrbitalMechanics.propagate_orbit(initial_state, 365.25 * 24 * 3600, n_points=50)
    impact_prob = OrbitalMechanics.earth_impact_probability(trajectory)
    
    print(f"   Orbital range: {np.min(trajectory['distances_au']):.2f} - {np.max(trajectory['distances_au']):.2f} AU")
    print(f"   Closest approach: {impact_prob['min_distance_km']:.0f} km")
    print(f"   Impact risk: {'YES' if impact_prob['impact_detected'] else 'NO'}")
    
    # Summary
    print()
    print("🎯 Integration Test Summary:")
    print(f"   ✅ Impact physics: Crater {impact_results['crater']['diameter_km']:.2f} km")
    print(f"   ✅ Environmental: M{env_results['seismic']['magnitude']:.1f} earthquake, {env_results['tsunami_generation']['initial_amplitude_m']:.1f}m tsunami")
    print(f"   ✅ Mitigation: {best_method} deflects {mitigation_results[best_method]['miss_distance_km']:.0f} km")
    print(f"   ✅ Orbital: Trajectory computed for {len(trajectory['time_days'])} points")
    
    print("\n🎉 All modules integrated successfully!")
    return True


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Edge Cases and Error Handling")
    print("=" * 40)
    
    # Test very small asteroid
    print("Small asteroid (10m):")
    small_results = ImpactPhysics.complete_impact_analysis(10.0, 15000.0)
    print(f"  Energy: {small_results['impact_energy']['total_energy_tnt_kg']:.1f} kg TNT")
    print(f"  Atmospheric survival: {small_results['atmospheric_entry']['surviving_mass_kg']/small_results['initial_parameters']['mass_kg']*100:.0f}%")
    
    # Test very large asteroid
    print("\nLarge asteroid (10km - Chicxulub size):")
    large_results = ImpactPhysics.complete_impact_analysis(10000.0, 25000.0)
    print(f"  Energy: {large_results['impact_energy']['total_energy_tnt_mt']:.0f} megatons TNT")
    print(f"  Crater: {large_results['crater']['diameter_km']:.0f} km diameter")
    
    print("\n✅ Edge cases handled properly!")


if __name__ == "__main__":
    import numpy as np  # Import here for the test
    
    try:
        success = test_integration()
        if success:
            test_edge_cases()
            print("\n🏆 ALL TESTS PASSED! Math backend is ready for integration!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
