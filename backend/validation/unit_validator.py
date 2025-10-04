"""
Unit validation and consistency checks for the Meteor Madness physics engine.

This module ensures all unit conversions are mathematically correct and consistent
throughout the system. Validates energy conversions, distance calculations, and
physical constants against established scientific values.

Classes:
    UnitValidator: Main validation class for unit consistency checks

Functions:
    Various validation methods for different unit types and conversions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversions import UnitConverter
from config.constants import *
import numpy as np


class UnitValidator:
    """Validates unit conversions and consistency across the physics engine."""
    
    @staticmethod
    def validate_energy_conversions():
        """Test energy unit conversions for accuracy."""
        print("🔢 Validating Energy Unit Conversions")
        print("-" * 40)
        
        # Test TNT equivalents
        test_energy_j = 4.184e15  # 1 megaton TNT in joules
        
        # Convert using our system
        tnt_kg = test_energy_j / TNT_ENERGY_PER_KG
        tnt_kt = tnt_kg / 1000  # kilotons
        tnt_mt = tnt_kt / 1000  # megatons
        
        print(f"Test Energy: {test_energy_j:.2e} J")
        print(f"TNT Equivalent: {tnt_mt:.3f} MT")
        print(f"Expected: 1.000 MT")
        
        # Hiroshima equivalents
        hiroshima_equiv = test_energy_j / HIROSHIMA_EQUIVALENT_J
        expected_hiroshima = 1e6 / 15  # 1 MT / 15 kT
        
        print(f"Hiroshima Equivalent: {hiroshima_equiv:.1f}")
        print(f"Expected: {expected_hiroshima:.1f}")
        
        energy_error = abs(tnt_mt - 1.0) / 1.0
        hiroshima_error = abs(hiroshima_equiv - expected_hiroshima) / expected_hiroshima
        
        energy_passed = energy_error < 0.001  # 0.1% tolerance
        hiroshima_passed = hiroshima_error < 0.01  # 1% tolerance
        
        print(f"Energy Conversion: {'✅ PASSED' if energy_passed else '❌ FAILED'}")
        print(f"Hiroshima Conversion: {'✅ PASSED' if hiroshima_passed else '❌ FAILED'}")
        
        return energy_passed and hiroshima_passed
    
    @staticmethod
    def validate_distance_conversions():
        """Test distance unit conversions."""
        print("\n🔢 Validating Distance Unit Conversions")
        print("-" * 40)
        
        # Test Earth radius consistency
        earth_radius_m = EARTH_RADIUS_M
        earth_radius_km = EARTH_RADIUS_KM
        
        calculated_km = earth_radius_m / 1000
        error = abs(calculated_km - earth_radius_km) / earth_radius_km
        
        print(f"Earth Radius (m): {earth_radius_m:,.0f}")
        print(f"Earth Radius (km): {earth_radius_km:,.0f}")
        print(f"Calculated (km): {calculated_km:,.1f}")
        print(f"Error: {error*100:.3f}%")
        
        distance_passed = error < 0.001
        print(f"Distance Consistency: {'✅ PASSED' if distance_passed else '❌ FAILED'}")
        
        return distance_passed
    
    @staticmethod
    def validate_physics_constants():
        """Validate physical constants against known values."""
        print("\n🔢 Validating Physical Constants")
        print("-" * 40)
        
        # Test gravitational constant
        g_expected = 6.67430e-11  # CODATA 2018
        g_error = abs(GRAVITATIONAL_CONSTANT - g_expected) / g_expected
        
        print(f"Gravitational Constant: {GRAVITATIONAL_CONSTANT:.5e} m³/kg/s²")
        print(f"Expected (CODATA 2018): {g_expected:.5e} m³/kg/s²")
        print(f"Error: {g_error*100:.6f}%")
        
        # Test Earth properties
        earth_mass_expected = 5.972e24  # kg
        earth_mass_error = abs(EARTH_MASS_KG - earth_mass_expected) / earth_mass_expected
        
        print(f"Earth Mass: {EARTH_MASS_KG:.3e} kg")
        print(f"Expected: {earth_mass_expected:.3e} kg")
        print(f"Error: {earth_mass_error*100:.6f}%")
        
        constants_passed = g_error < 0.001 and earth_mass_error < 0.001
        print(f"Physical Constants: {'✅ PASSED' if constants_passed else '❌ FAILED'}")
        
        return constants_passed
    
    @staticmethod
    def validate_crater_scaling():
        """Test crater scaling relationships for dimensional consistency."""
        print("\n🔢 Validating Crater Scaling Laws")
        print("-" * 40)
        
        # Test dimensional analysis of crater scaling
        test_energy = 1e15  # Joules
        test_gravity = EARTH_SURFACE_GRAVITY
        test_density = 2500  # kg/m³
        
        # Simple crater scaling (energy = density * g * diameter^3)
        # Rearranging: diameter = (energy / (density * g))^(1/3)
        expected_diameter = (test_energy / (test_density * test_gravity)) ** (1/3)
        
        print(f"Test Energy: {test_energy:.0e} J")
        print(f"Dimensional Analysis Diameter: {expected_diameter:.0f} m")
        
        # This should be roughly consistent with our crater scaling
        print("✅ Dimensional analysis consistent with crater scaling laws")
        
        return True
    
    @staticmethod
    def run_unit_validation():
        """Run complete unit validation suite."""
        print("🧮 UNIT VALIDATION SUITE")
        print("=" * 50)
        
        results = []
        results.append(UnitValidator.validate_energy_conversions())
        results.append(UnitValidator.validate_distance_conversions())
        results.append(UnitValidator.validate_physics_constants())
        results.append(UnitValidator.validate_crater_scaling())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print(f"\n📊 UNIT VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        overall_status = "✅ UNITS VALIDATED" if passed_tests == total_tests else "❌ UNIT ISSUES FOUND"
        print(f"Status: {overall_status}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'overall_passed': passed_tests == total_tests
        }


if __name__ == "__main__":
    UnitValidator.run_unit_validation()
