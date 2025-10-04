"""
Unit conversion utilities for Meteor Madness project.
Handles conversions between different unit systems to ensure consistency
across NASA API data, USGS datasets, and user inputs.
"""

import numpy as np
from typing import Union, Dict, Any
from astropy import units as u
from astropy import constants as const


class UnitConverter:
    """Handles unit conversions for asteroid impact calculations."""
    
    # Energy conversion factors (to Joules)
    ENERGY_CONVERSIONS = {
        'J': 1.0,
        'kJ': 1e3,
        'MJ': 1e6,
        'GJ': 1e9,
        'TJ': 1e12,
        'TNT_kg': 4.184e6,  # kg of TNT to Joules
        'TNT_kt': 4.184e12,  # kilotons of TNT to Joules
        'TNT_Mt': 4.184e18,  # megatons of TNT to Joules
        'cal': 4.184,
        'kcal': 4184,
        'kWh': 3.6e6,
    }
    
    # Distance conversion factors (to meters)
    DISTANCE_CONVERSIONS = {
        'm': 1.0,
        'km': 1000.0,
        'cm': 0.01,
        'mm': 0.001,
        'ft': 0.3048,
        'mi': 1609.344,
        'nmi': 1852.0,  # nautical miles
        'AU': 1.495978707e11,  # astronomical units
        'ly': 9.4607304725808e15,  # light years
    }
    
    # Velocity conversion factors (to m/s)
    VELOCITY_CONVERSIONS = {
        'm/s': 1.0,
        'km/s': 1000.0,
        'km/h': 1000.0 / 3600.0,
        'mph': 0.44704,
        'ft/s': 0.3048,
        'knots': 0.514444,
    }
    
    # Mass conversion factors (to kg)
    MASS_CONVERSIONS = {
        'kg': 1.0,
        'g': 0.001,
        't': 1000.0,  # metric tons
        'lb': 0.453592,
        'oz': 0.0283495,
        'solar_mass': 1.98847e30,
    }

    @staticmethod
    def convert_energy(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert energy between different units.
        
        Args:
            value: Energy value to convert
            from_unit: Source unit (J, kJ, MJ, GJ, TJ, TNT_kg, TNT_kt, TNT_Mt, etc.)
            to_unit: Target unit
            
        Returns:
            Converted energy value
            
        Examples:
            >>> UnitConverter.convert_energy(1, 'TNT_kt', 'J')
            4.184e12
            >>> UnitConverter.convert_energy(1e15, 'J', 'TNT_kt')
            0.239
        """
        if from_unit not in UnitConverter.ENERGY_CONVERSIONS:
            raise ValueError(f"Unknown energy unit: {from_unit}")
        if to_unit not in UnitConverter.ENERGY_CONVERSIONS:
            raise ValueError(f"Unknown energy unit: {to_unit}")
        
        # Convert to Joules first, then to target unit
        joules = value * UnitConverter.ENERGY_CONVERSIONS[from_unit]
        return joules / UnitConverter.ENERGY_CONVERSIONS[to_unit]

    @staticmethod
    def convert_distance(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert distance between different units.
        
        Args:
            value: Distance value to convert
            from_unit: Source unit (m, km, cm, ft, mi, AU, etc.)
            to_unit: Target unit
            
        Returns:
            Converted distance value
        """
        if from_unit not in UnitConverter.DISTANCE_CONVERSIONS:
            raise ValueError(f"Unknown distance unit: {from_unit}")
        if to_unit not in UnitConverter.DISTANCE_CONVERSIONS:
            raise ValueError(f"Unknown distance unit: {to_unit}")
        
        # Convert to meters first, then to target unit
        meters = value * UnitConverter.DISTANCE_CONVERSIONS[from_unit]
        return meters / UnitConverter.DISTANCE_CONVERSIONS[to_unit]

    @staticmethod
    def convert_velocity(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert velocity between different units.
        
        Args:
            value: Velocity value to convert
            from_unit: Source unit (m/s, km/s, km/h, mph, etc.)
            to_unit: Target unit
            
        Returns:
            Converted velocity value
        """
        if from_unit not in UnitConverter.VELOCITY_CONVERSIONS:
            raise ValueError(f"Unknown velocity unit: {from_unit}")
        if to_unit not in UnitConverter.VELOCITY_CONVERSIONS:
            raise ValueError(f"Unknown velocity unit: {to_unit}")
        
        # Convert to m/s first, then to target unit
        ms = value * UnitConverter.VELOCITY_CONVERSIONS[from_unit]
        return ms / UnitConverter.VELOCITY_CONVERSIONS[to_unit]

    @staticmethod
    def convert_mass(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert mass between different units.
        
        Args:
            value: Mass value to convert
            from_unit: Source unit (kg, g, t, lb, solar_mass, etc.)
            to_unit: Target unit
            
        Returns:
            Converted mass value
        """
        if from_unit not in UnitConverter.MASS_CONVERSIONS:
            raise ValueError(f"Unknown mass unit: {from_unit}")
        if to_unit not in UnitConverter.MASS_CONVERSIONS:
            raise ValueError(f"Unknown mass unit: {to_unit}")
        
        # Convert to kg first, then to target unit
        kg = value * UnitConverter.MASS_CONVERSIONS[from_unit]
        return kg / UnitConverter.MASS_CONVERSIONS[to_unit]

    @staticmethod
    def tnt_equivalent(energy_joules: float, unit: str = 'TNT_kt') -> float:
        """
        Convert energy in Joules to TNT equivalent.
        
        Args:
            energy_joules: Energy in Joules
            unit: TNT unit (TNT_kg, TNT_kt, TNT_Mt)
            
        Returns:
            TNT equivalent value
        """
        return UnitConverter.convert_energy(energy_joules, 'J', unit)

    @staticmethod
    def standardize_units(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize a dictionary of values to SI units (m, kg, m/s, J).
        
        Args:
            data: Dictionary with 'value', 'unit' pairs
            
        Returns:
            Dictionary with values converted to SI units
        """
        standardized = {}
        
        for key, item in data.items():
            if isinstance(item, dict) and 'value' in item and 'unit' in item:
                value = item['value']
                unit = item['unit']
                
                # Determine conversion type based on context
                if 'energy' in key.lower():
                    standardized[key] = {
                        'value': UnitConverter.convert_energy(value, unit, 'J'),
                        'unit': 'J'
                    }
                elif any(word in key.lower() for word in ['distance', 'radius', 'diameter', 'height']):
                    standardized[key] = {
                        'value': UnitConverter.convert_distance(value, unit, 'm'),
                        'unit': 'm'
                    }
                elif 'velocity' in key.lower() or 'speed' in key.lower():
                    standardized[key] = {
                        'value': UnitConverter.convert_velocity(value, unit, 'm/s'),
                        'unit': 'm/s'
                    }
                elif 'mass' in key.lower():
                    standardized[key] = {
                        'value': UnitConverter.convert_mass(value, unit, 'kg'),
                        'unit': 'kg'
                    }
                else:
                    # Keep original if type unknown
                    standardized[key] = item
            else:
                standardized[key] = item
                
        return standardized


def estimate_asteroid_mass(diameter_m: float, density_kg_m3: float = None) -> float:
    """
    Estimate asteroid mass from diameter assuming spherical shape.
    
    Args:
        diameter_m: Asteroid diameter in meters
        density_kg_m3: Asteroid density in kg/m³ (uses default if not provided)
        
    Returns:
        Estimated mass in kg
        
    TODO: When NASA NEO API is integrated, use actual density data from spectral classification
    """
    if density_kg_m3 is None:
        density_kg_m3 = DEFAULT_ASTEROID_DENSITY
        
    radius_m = diameter_m / 2.0
    volume_m3 = (4.0 / 3.0) * np.pi * radius_m**3
    return volume_m3 * density_kg_m3


def kinetic_energy(mass_kg: float, velocity_ms: float) -> float:
    """
    Calculate kinetic energy from mass and velocity.
    
    Args:
        mass_kg: Mass in kg
        velocity_ms: Velocity in m/s
        
    Returns:
        Kinetic energy in Joules
    """
    return 0.5 * mass_kg * velocity_ms**2


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        True if coordinates are valid
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


# Import constants from config
# TODO: When API integration is added, these constants can be made configurable
from config.constants import (
    EARTH_RADIUS_KM, EARTH_MASS_KG, GM_EARTH as GRAVITATIONAL_PARAMETER_EARTH,
    ESCAPE_VELOCITY_EARTH_MS, DEFAULT_ASTEROID_DENSITY
)
