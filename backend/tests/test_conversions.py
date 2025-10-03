"""
Tests for the conversions utility module.
"""

import pytest
import numpy as np
from backend.utils.conversions import (
    UnitConverter, 
    estimate_asteroid_mass, 
    kinetic_energy, 
    validate_coordinates
)


class TestUnitConverter:
    """Test cases for UnitConverter class."""
    
    def test_energy_conversion_basic(self):
        """Test basic energy conversions."""
        # Test TNT equivalents
        assert abs(UnitConverter.convert_energy(1, 'TNT_kt', 'J') - 4.184e12) < 1e6
        assert abs(UnitConverter.convert_energy(4.184e12, 'J', 'TNT_kt') - 1.0) < 1e-6
        
        # Test simple conversions
        assert UnitConverter.convert_energy(1000, 'J', 'kJ') == 1.0
        assert UnitConverter.convert_energy(1, 'MJ', 'J') == 1e6
    
    def test_distance_conversion_basic(self):
        """Test basic distance conversions."""
        assert UnitConverter.convert_distance(1, 'km', 'm') == 1000.0
        assert UnitConverter.convert_distance(1000, 'm', 'km') == 1.0
        assert abs(UnitConverter.convert_distance(1, 'mi', 'km') - 1.609344) < 1e-6
    
    def test_velocity_conversion_basic(self):
        """Test basic velocity conversions."""
        assert UnitConverter.convert_velocity(1, 'km/s', 'm/s') == 1000.0
        assert UnitConverter.convert_velocity(3600, 'm/s', 'km/h') == 12960.0
    
    def test_mass_conversion_basic(self):
        """Test basic mass conversions."""
        assert UnitConverter.convert_mass(1, 't', 'kg') == 1000.0
        assert UnitConverter.convert_mass(1000, 'g', 'kg') == 1.0
    
    def test_invalid_units(self):
        """Test error handling for invalid units."""
        with pytest.raises(ValueError):
            UnitConverter.convert_energy(1, 'invalid_unit', 'J')
        
        with pytest.raises(ValueError):
            UnitConverter.convert_distance(1, 'km', 'invalid_unit')
    
    def test_tnt_equivalent(self):
        """Test TNT equivalent calculation."""
        # 1 kiloton TNT = 4.184e12 J
        energy_j = 4.184e12
        tnt_kt = UnitConverter.tnt_equivalent(energy_j, 'TNT_kt')
        assert abs(tnt_kt - 1.0) < 1e-6
    
    def test_standardize_units(self):
        """Test unit standardization."""
        data = {
            'impact_energy': {'value': 1, 'unit': 'TNT_kt'},
            'asteroid_diameter': {'value': 1, 'unit': 'km'},
            'impact_velocity': {'value': 20, 'unit': 'km/s'},
            'asteroid_mass': {'value': 1, 'unit': 't'}
        }
        
        standardized = UnitConverter.standardize_units(data)
        
        assert standardized['impact_energy']['unit'] == 'J'
        assert standardized['asteroid_diameter']['unit'] == 'm'
        assert standardized['impact_velocity']['unit'] == 'm/s'
        assert standardized['asteroid_mass']['unit'] == 'kg'
        
        # Check values
        assert abs(standardized['impact_energy']['value'] - 4.184e12) < 1e6
        assert standardized['asteroid_diameter']['value'] == 1000.0
        assert standardized['impact_velocity']['value'] == 20000.0
        assert standardized['asteroid_mass']['value'] == 1000.0


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_estimate_asteroid_mass(self):
        """Test asteroid mass estimation."""
        # 1 km diameter asteroid with default density
        diameter_m = 1000.0
        mass_kg = estimate_asteroid_mass(diameter_m)
        
        # Volume = (4/3) * π * (500)³ ≈ 5.236e8 m³
        # Mass = Volume * 3000 kg/m³ ≈ 1.57e12 kg
        expected_mass = (4/3) * np.pi * (500**3) * 3000
        assert abs(mass_kg - expected_mass) < 1e9
    
    def test_kinetic_energy(self):
        """Test kinetic energy calculation."""
        mass_kg = 1000.0  # 1 ton
        velocity_ms = 20000.0  # 20 km/s
        
        energy_j = kinetic_energy(mass_kg, velocity_ms)
        expected_energy = 0.5 * mass_kg * velocity_ms**2
        
        assert energy_j == expected_energy
        assert energy_j == 2e11  # 200 GJ
    
    def test_validate_coordinates(self):
        """Test coordinate validation."""
        # Valid coordinates
        assert validate_coordinates(0, 0) == True
        assert validate_coordinates(45.0, -122.0) == True
        assert validate_coordinates(-90, 180) == True
        assert validate_coordinates(90, -180) == True
        
        # Invalid coordinates
        assert validate_coordinates(91, 0) == False
        assert validate_coordinates(-91, 0) == False
        assert validate_coordinates(0, 181) == False
        assert validate_coordinates(0, -181) == False


def run_basic_tests():
    """Run basic tests without pytest."""
    print("🧪 Testing Conversions Module")
    print("=" * 40)
    
    # Test energy conversion
    energy_j = UnitConverter.convert_energy(1, 'TNT_kt', 'J')
    print(f"✅ 1 kiloton TNT = {energy_j:.2e} J")
    
    # Test distance conversion
    meters = UnitConverter.convert_distance(1, 'km', 'm')
    print(f"✅ 1 km = {meters} m")
    
    # Test asteroid mass estimation
    mass_kg = estimate_asteroid_mass(1000)
    print(f"✅ 1 km asteroid mass = {mass_kg:.2e} kg")
    
    # Test kinetic energy
    energy_j = kinetic_energy(1000, 20000)
    print(f"✅ 1 ton at 20 km/s = {energy_j:.2e} J")
    
    # Test coordinate validation
    assert validate_coordinates(45.0, -122.0) == True
    assert validate_coordinates(91, 0) == False
    print("✅ Coordinate validation working")
    
    print("\n🎉 All basic tests passed!")


if __name__ == "__main__":
    run_basic_tests()
