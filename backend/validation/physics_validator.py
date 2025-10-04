"""
Scientific validation of physics calculations against historical asteroid impact events.

This module validates the Meteor Madness physics engine against well-documented 
historical events including Tunguska (1908), Chelyabinsk (2013), Chicxulub (66 MYA),
and Meteor Crater Arizona. All calculations are compared against peer-reviewed
scientific literature to ensure accuracy.

Classes:
    ScientificValidator: Main validation class with historical event data and methods

Functions:
    run_scientific_validation(): Entry point for validation suite
"""

import sys
import os
# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.impact import ImpactPhysics
from physics.environmental import EnvironmentalEffects
from physics.orbital import OrbitalMechanics
from config.constants import *

import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings


class ScientificValidator:
    """Validates physics calculations against known events and scientific literature."""
    
    # Known historical events with documented parameters
    HISTORICAL_EVENTS = {
        'tunguska_1908': {
            'date': '1908-06-30',
            'location': {'lat': 60.886, 'lon': 101.894},
            'estimated_diameter_m': 60.0,  # Range: 50-80m
            'estimated_velocity_kms': 27.0,  # Range: 15-30 km/s
            'estimated_energy_mt': 15.0,  # 10-30 megatons TNT
            'airburst_altitude_km': 8.0,  # 5-10 km altitude
            'flattened_area_km2': 2150,  # Trees flattened over 2150 km²
            'event_type': 'airburst',
            'source': 'Boslough & Crawford (2008), Collins et al. (2005)'
        },
        
        'chelyabinsk_2013': {
            'date': '2013-02-15',
            'location': {'lat': 55.1540, 'lon': 61.4291},
            'estimated_diameter_m': 19.0,  # Well constrained: 17-20m
            'estimated_velocity_kms': 19.16,  # Very precise from observations
            'estimated_energy_mt': 0.5,  # 440-500 kilotons TNT
            'airburst_altitude_km': 29.7,  # Well documented
            'injuries': 1491,  # From glass breakage
            'windows_broken': 7200,  # Buildings affected
            'event_type': 'airburst',
            'source': 'Popova et al. (2013), Brown et al. (2013)'
        },
        
        'chicxulub_66mya': {
            'date': '66 million years ago',
            'location': {'lat': 21.4, 'lon': -82.0},
            'estimated_diameter_m': 10000.0,  # 10-15 km diameter
            'estimated_velocity_kms': 20.0,  # Typical asteroid velocity
            'estimated_energy_mt': 100000000.0,  # 100 million megatons
            'crater_diameter_km': 150.0,  # Measured crater diameter
            'crater_depth_km': 20.0,  # Original depth (now filled)
            'event_type': 'surface_impact',
            'source': 'Schulte et al. (2010), Artemieva & Morgan (2009)'
        },
        
        'meteor_crater_arizona': {
            'date': '~50,000 years ago',
            'location': {'lat': 35.0274, 'lon': -111.0224},
            'estimated_diameter_m': 50.0,  # Iron meteorite
            'estimated_velocity_kms': 12.8,  # Relatively slow impact
            'estimated_energy_mt': 10.0,  # 2.5-10 megatons
            'crater_diameter_km': 1.186,  # Measured: 1186m diameter
            'crater_depth_m': 170,  # Current depth (partially filled)
            'event_type': 'surface_impact',
            'source': 'Melosh & Collins (2005), Shoemaker (1963)'
        }
    }

    @staticmethod
    def validate_tunguska_event() -> Dict[str, any]:
        """
        Validate calculations against the 1908 Tunguska event.
        This is the largest documented airburst in modern history.
        """
        print("🔬 Validating against Tunguska Event (1908)")
        print("=" * 50)
        
        event = ScientificValidator.HISTORICAL_EVENTS['tunguska_1908']
        
        # Input parameters
        diameter_m = event['estimated_diameter_m']
        velocity_ms = event['estimated_velocity_kms'] * 1000
        impact_angle_deg = 30  # Estimated shallow angle
        
        print(f"Event Parameters:")
        print(f"  Diameter: {diameter_m} m")
        print(f"  Velocity: {event['estimated_velocity_kms']} km/s")
        print(f"  Expected Energy: {event['estimated_energy_mt']} MT TNT")
        print()
        
        # Calculate using our physics
        results = ImpactPhysics.complete_impact_analysis(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            impact_angle_degrees=impact_angle_deg,
            target_density_kg_m3=DEFAULT_ASTEROID_DENSITY,
            calculate_atmospheric_entry=True
        )
        
        # Extract key results
        calculated_energy_j = results['impact_energy']['total_energy_j']
        calculated_energy_mt = calculated_energy_j / (TNT_ENERGY_PER_KG * 1e9)  # Convert to megatons
        
        print(f"Our Calculations:")
        print(f"  Impact Energy: {calculated_energy_mt:.1f} MT TNT")
        print(f"  Kinetic Energy: {results['impact_energy']['kinetic_energy_j']:.2e} J")
        print(f"  Hiroshima Equivalent: {results['impact_energy']['hiroshima_equivalent']:.1f}x")
        
        # Atmospheric entry effects
        atm_entry = results['atmospheric_entry']
        print(f"  Entry Effects:")
        print(f"    Peak deceleration: {atm_entry['peak_deceleration_g']:.1f} g")
        print(f"    Fragmentation altitude: {atm_entry['fragmentation_altitude_km']:.1f} km")
        print(f"    Surviving mass fraction: {atm_entry['surviving_mass_fraction']:.3f}")
        
        # Blast effects
        blast_effects = results['blast_effects']
        print(f"  Blast Effects:")
        print(f"    1 psi overpressure radius: {blast_effects['overpressure_1psi_radius_km']:.1f} km")
        print(f"    Thermal radius (1st deg burns): {blast_effects['thermal_radius_km']:.1f} km")
        
        # Validation assessment
        energy_match = abs(calculated_energy_mt - event['estimated_energy_mt']) / event['estimated_energy_mt']
        
        print(f"\n📊 Validation Results:")
        print(f"  Expected: {event['estimated_energy_mt']} MT")
        print(f"  Calculated: {calculated_energy_mt:.1f} MT")
        print(f"  Error: {energy_match*100:.1f}%")
        
        validation_passed = energy_match < 0.5  # Within 50% is good for this complex event
        print(f"  Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"  Source: {event['source']}")
        
        return {
            'event': 'tunguska_1908',
            'expected_energy_mt': event['estimated_energy_mt'],
            'calculated_energy_mt': calculated_energy_mt,
            'error_percentage': energy_match * 100,
            'validation_passed': validation_passed,
            'full_results': results
        }

    @staticmethod
    def validate_chelyabinsk_event() -> Dict[str, any]:
        """
        Validate calculations against the 2013 Chelyabinsk meteor.
        This is the best-documented asteroid airburst in history.
        """
        print("\n🔬 Validating against Chelyabinsk Event (2013)")
        print("=" * 50)
        
        event = ScientificValidator.HISTORICAL_EVENTS['chelyabinsk_2013']
        
        # Input parameters (very well constrained)
        diameter_m = event['estimated_diameter_m']
        velocity_ms = event['estimated_velocity_kms'] * 1000
        impact_angle_deg = 18  # Shallow angle, well documented
        
        print(f"Event Parameters:")
        print(f"  Diameter: {diameter_m} m")
        print(f"  Velocity: {event['estimated_velocity_kms']} km/s")
        print(f"  Expected Energy: {event['estimated_energy_mt']} MT TNT")
        print(f"  Airburst Altitude: {event['airburst_altitude_km']} km")
        print()
        
        # Calculate using our physics
        results = ImpactPhysics.complete_impact_analysis(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            impact_angle_degrees=impact_angle_deg,
            target_density_kg_m3=3300,  # Ordinary chondrite density
            calculate_atmospheric_entry=True
        )
        
        # Extract key results
        calculated_energy_j = results['impact_energy']['total_energy_j']
        calculated_energy_mt = calculated_energy_j / (TNT_ENERGY_PER_KG * 1e9)
        
        print(f"Our Calculations:")
        print(f"  Impact Energy: {calculated_energy_mt:.2f} MT TNT")
        print(f"  Kinetic Energy: {results['impact_energy']['kinetic_energy_j']:.2e} J")
        
        # Atmospheric entry validation
        atm_entry = results['atmospheric_entry']
        expected_altitude = event['airburst_altitude_km']
        calculated_altitude = atm_entry['fragmentation_altitude_km']
        
        print(f"  Atmospheric Entry:")
        print(f"    Expected airburst altitude: {expected_altitude} km")
        print(f"    Calculated fragmentation: {calculated_altitude:.1f} km")
        print(f"    Peak deceleration: {atm_entry['peak_deceleration_g']:.1f} g")
        
        # Validation assessment
        energy_match = abs(calculated_energy_mt - event['estimated_energy_mt']) / event['estimated_energy_mt']
        altitude_match = abs(calculated_altitude - expected_altitude) / expected_altitude
        
        print(f"\n📊 Validation Results:")
        print(f"  Energy - Expected: {event['estimated_energy_mt']} MT, Calculated: {calculated_energy_mt:.2f} MT")
        print(f"  Energy Error: {energy_match*100:.1f}%")
        print(f"  Altitude Error: {altitude_match*100:.1f}%")
        
        validation_passed = energy_match < 0.3 and altitude_match < 0.5  # High accuracy expected
        print(f"  Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"  Source: {event['source']}")
        
        return {
            'event': 'chelyabinsk_2013',
            'expected_energy_mt': event['estimated_energy_mt'],
            'calculated_energy_mt': calculated_energy_mt,
            'energy_error_percentage': energy_match * 100,
            'altitude_error_percentage': altitude_match * 100,
            'validation_passed': validation_passed,
            'full_results': results
        }

    @staticmethod
    def validate_chicxulub_impact() -> Dict[str, any]:
        """
        Validate calculations against the Chicxulub impact (K-Pg extinction event).
        This tests our calculations at the extreme high-energy end.
        """
        print("\n🔬 Validating against Chicxulub Impact (66 MYA)")
        print("=" * 50)
        
        event = ScientificValidator.HISTORICAL_EVENTS['chicxulub_66mya']
        
        # Input parameters
        diameter_m = event['estimated_diameter_m']
        velocity_ms = event['estimated_velocity_kms'] * 1000
        impact_angle_deg = 60  # Estimated non-vertical impact
        
        print(f"Event Parameters:")
        print(f"  Diameter: {diameter_m/1000} km")
        print(f"  Velocity: {event['estimated_velocity_kms']} km/s")
        print(f"  Expected Energy: {event['estimated_energy_mt']:,.0f} MT TNT")
        print(f"  Expected Crater: {event['crater_diameter_km']} km diameter")
        print()
        
        # Calculate using our physics
        results = ImpactPhysics.complete_impact_analysis(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            impact_angle_degrees=impact_angle_deg,
            target_density_kg_m3=DEFAULT_ASTEROID_DENSITY
        )
        
        # Extract key results
        calculated_energy_j = results['impact_energy']['total_energy_j']
        calculated_energy_mt = calculated_energy_j / (TNT_ENERGY_PER_KG * 1e9)
        crater_results = results['crater_formation']
        
        print(f"Our Calculations:")
        print(f"  Impact Energy: {calculated_energy_mt:,.0f} MT TNT")
        print(f"  Crater Diameter: {crater_results['diameter_km']:.1f} km")
        print(f"  Crater Depth: {crater_results['depth_m']/1000:.1f} km")
        print(f"  Crater Type: {crater_results['crater_type']}")
        
        # Global effects
        print(f"  Global Effects:")
        print(f"    Hiroshima Equivalent: {results['impact_energy']['hiroshima_equivalent']:,.0f}x")
        print(f"    Seismic Magnitude: ~9+ (global)")
        
        # Validation assessment
        energy_match = abs(calculated_energy_mt - event['estimated_energy_mt']) / event['estimated_energy_mt']
        crater_match = abs(crater_results['diameter_km'] - event['crater_diameter_km']) / event['crater_diameter_km']
        
        print(f"\n📊 Validation Results:")
        print(f"  Energy - Expected: {event['estimated_energy_mt']:,.0f} MT, Calculated: {calculated_energy_mt:,.0f} MT")
        print(f"  Energy Error: {energy_match*100:.1f}%")
        print(f"  Crater - Expected: {event['crater_diameter_km']} km, Calculated: {crater_results['diameter_km']:.1f} km")
        print(f"  Crater Error: {crater_match*100:.1f}%")
        
        validation_passed = energy_match < 0.5 and crater_match < 0.3  # Large uncertainties for ancient event
        print(f"  Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"  Source: {event['source']}")
        
        return {
            'event': 'chicxulub_66mya',
            'expected_energy_mt': event['estimated_energy_mt'],
            'calculated_energy_mt': calculated_energy_mt,
            'expected_crater_km': event['crater_diameter_km'],
            'calculated_crater_km': crater_results['diameter_km'],
            'energy_error_percentage': energy_match * 100,
            'crater_error_percentage': crater_match * 100,
            'validation_passed': validation_passed,
            'full_results': results
        }

    @staticmethod
    def validate_meteor_crater_arizona() -> Dict[str, any]:
        """
        Validate calculations against Meteor Crater, Arizona.
        This is the best-preserved impact crater on Earth.
        """
        print("\n🔬 Validating against Meteor Crater, Arizona (~50,000 years ago)")
        print("=" * 50)
        
        event = ScientificValidator.HISTORICAL_EVENTS['meteor_crater_arizona']
        
        # Input parameters
        diameter_m = event['estimated_diameter_m']
        velocity_ms = event['estimated_velocity_kms'] * 1000
        impact_angle_deg = 45  # Estimated
        
        print(f"Event Parameters:")
        print(f"  Meteorite Diameter: {diameter_m} m (iron)")
        print(f"  Velocity: {event['estimated_velocity_kms']} km/s")
        print(f"  Expected Crater: {event['crater_diameter_km']*1000} m diameter")
        print()
        
        # Calculate using our physics (iron meteorite density)
        results = ImpactPhysics.complete_impact_analysis(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            impact_angle_degrees=impact_angle_deg,
            target_density_kg_m3=7800  # Iron meteorite density
        )
        
        # Extract results
        calculated_energy_j = results['impact_energy']['total_energy_j']
        calculated_energy_mt = calculated_energy_j / (TNT_ENERGY_PER_KG * 1e9)
        crater_results = results['crater_formation']
        
        print(f"Our Calculations:")
        print(f"  Impact Energy: {calculated_energy_mt:.1f} MT TNT")
        print(f"  Crater Diameter: {crater_results['diameter_m']:,.0f} m")
        print(f"  Crater Depth: {crater_results['depth_m']:.0f} m")
        print(f"  Crater Type: {crater_results['crater_type']}")
        
        # Validation assessment
        expected_crater_m = event['crater_diameter_km'] * 1000
        crater_match = abs(crater_results['diameter_m'] - expected_crater_m) / expected_crater_m
        
        print(f"\n📊 Validation Results:")
        print(f"  Crater - Expected: {expected_crater_m:,.0f} m, Calculated: {crater_results['diameter_m']:,.0f} m")
        print(f"  Crater Error: {crater_match*100:.1f}%")
        
        validation_passed = crater_match < 0.4  # Within 40% for this complex scenario
        print(f"  Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"  Source: {event['source']}")
        
        return {
            'event': 'meteor_crater_arizona',
            'expected_crater_m': expected_crater_m,
            'calculated_crater_m': crater_results['diameter_m'],
            'crater_error_percentage': crater_match * 100,
            'validation_passed': validation_passed,
            'full_results': results
        }

    @staticmethod
    def run_complete_validation() -> Dict[str, any]:
        """
        Run complete scientific validation against all known events.
        Returns comprehensive validation report.
        """
        print("🧪 SCIENTIFIC VALIDATION SUITE")
        print("Testing physics calculations against known asteroid impact events")
        print("=" * 70)
        
        validation_results = []
        
        # Run all validation tests
        validation_results.append(ScientificValidator.validate_tunguska_event())
        validation_results.append(ScientificValidator.validate_chelyabinsk_event())
        validation_results.append(ScientificValidator.validate_chicxulub_impact())
        validation_results.append(ScientificValidator.validate_meteor_crater_arizona())
        
        # Summary statistics
        total_tests = len(validation_results)
        passed_tests = sum(1 for result in validation_results if result['validation_passed'])
        
        print(f"\n🎯 VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        overall_status = "✅ PHYSICS VALIDATED" if passed_tests == total_tests else "⚠️ SOME ISSUES FOUND"
        print(f"Overall Status: {overall_status}")
        
        if passed_tests == total_tests:
            print("\n🎉 All physics calculations validated against known events!")
            print("   Your math backend is scientifically accurate and ready for use.")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} validation(s) failed.")
            print("   Review calculations and consider model improvements.")
        
        print(f"\n📚 Scientific References:")
        for event_key, event_data in ScientificValidator.HISTORICAL_EVENTS.items():
            print(f"   {event_key}: {event_data['source']}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'individual_results': validation_results,
            'overall_passed': passed_tests == total_tests
        }


def run_scientific_validation():
    """Entry point for running scientific validation."""
    return ScientificValidator.run_complete_validation()


if __name__ == "__main__":
    run_scientific_validation()
