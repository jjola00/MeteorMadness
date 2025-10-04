"""
Impact physics calculations for asteroid impact simulation.
Handles kinetic energy, crater formation, and immediate impact effects.
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, Tuple, Optional

from backend.utils.conversions import (
    UnitConverter, 
    kinetic_energy, 
    estimate_asteroid_mass,
    EARTH_RADIUS_KM
)


class ImpactPhysics:
    """Handles asteroid impact physics calculations."""
    
    # Import constants from configuration
    # TODO: When API integration is added, asteroid density can be determined from spectral classification
    def __init__(self):
        from config.constants import (
            DEFAULT_ASTEROID_DENSITY, EARTH_SURFACE_GRAVITY, CRATER_SCALING_CONSTANTS
        )
        self.DEFAULT_ASTEROID_DENSITY = DEFAULT_ASTEROID_DENSITY
        self.EARTH_GRAVITY = EARTH_SURFACE_GRAVITY  
        self.CRATER_SCALING_CONSTANTS = CRATER_SCALING_CONSTANTS

    @staticmethod
    def calculate_impact_energy(
        mass_kg: float,
        velocity_ms: float,
        angle_degrees: float = 45.0
    ) -> Dict[str, float]:
        """
        Calculate impact energy considering impact angle.
        
        Args:
            mass_kg: Asteroid mass in kg
            velocity_ms: Impact velocity in m/s
            angle_degrees: Impact angle from horizontal (45° is typical)
            
        Returns:
            Dictionary with energy values in different units
        """
        # Kinetic energy
        total_energy_j = kinetic_energy(mass_kg, velocity_ms)
        
        # Effective energy (accounting for impact angle)
        angle_rad = np.radians(angle_degrees)
        effective_energy_j = total_energy_j * np.sin(angle_rad)**2
        
        return {
            'total_energy_j': total_energy_j,
            'effective_energy_j': effective_energy_j,
            'total_energy_tnt_kt': UnitConverter.tnt_equivalent(total_energy_j, 'TNT_kt'),
            'effective_energy_tnt_kt': UnitConverter.tnt_equivalent(effective_energy_j, 'TNT_kt'),
            'total_energy_tnt_mt': UnitConverter.tnt_equivalent(total_energy_j, 'TNT_Mt'),
            'effective_energy_tnt_mt': UnitConverter.tnt_equivalent(effective_energy_j, 'TNT_Mt')
        }

    @staticmethod
    def estimate_crater_size(
        energy_j: float,
        target_density_kg_m3: float = 2500.0,
        gravity_ms2: float = None,
        impactor_density_kg_m3: float = None
    ) -> Dict[str, float]:
        """
        Estimate crater size using scaling relationships.
        
        Args:
            energy_j: Impact energy in Joules
            target_density_kg_m3: Target material density (default: 2500 kg/m³ for rock)
            gravity_ms2: Gravitational acceleration (default: Earth gravity)
            impactor_density_kg_m3: Impactor density (default: asteroid density)
            
        Returns:
            Dictionary with crater dimensions
        """
        if gravity_ms2 is None:
            from config.constants import EARTH_SURFACE_GRAVITY
            gravity_ms2 = EARTH_SURFACE_GRAVITY
        if impactor_density_kg_m3 is None:
            from config.constants import DEFAULT_ASTEROID_DENSITY
            impactor_density_kg_m3 = DEFAULT_ASTEROID_DENSITY
        
        # Determine crater type based on energy
        # Simple craters: < ~10^16 J, Complex craters: > ~10^16 J
        is_complex = energy_j > 1e16
        
        from config.constants import CRATER_SCALING_CONSTANTS
        constants = CRATER_SCALING_CONSTANTS['complex' if is_complex else 'simple']
        
        # Pi-scaling relationships
        # π₂ = (ρₜ/ρᵢ)^(1/3) * (g*D/V²)^ν
        # π₃ = D/d (crater diameter / impactor diameter)
        
        # For energy scaling: D = K₁ * (E/(ρₜ*g))^μ
        diameter_m = constants['K1'] * (energy_j / (target_density_kg_m3 * gravity_ms2)) ** constants['mu']
        
        # Depth-to-diameter ratios
        if is_complex:
            # Complex craters are shallower
            depth_to_diameter = 0.1  # Typical for complex craters
        else:
            # Simple craters
            depth_to_diameter = 0.2  # Typical for simple craters
        
        depth_m = diameter_m * depth_to_diameter
        
        # Rim height (typically 5-10% of crater diameter)
        rim_height_m = diameter_m * 0.05
        
        # Ejecta blanket radius (typically 2-3 times crater diameter)
        ejecta_radius_m = diameter_m * 2.5
        
        return {
            'diameter_m': diameter_m,
            'diameter_km': diameter_m / 1000.0,
            'depth_m': depth_m,
            'rim_height_m': rim_height_m,
            'ejecta_radius_m': ejecta_radius_m,
            'ejecta_radius_km': ejecta_radius_m / 1000.0,
            'crater_type': 'complex' if is_complex else 'simple',
            'volume_m3': (np.pi / 6) * diameter_m**2 * depth_m  # Approximate volume
        }

    @staticmethod
    def impact_effects_radius(energy_j: float) -> Dict[str, float]:
        """
        Estimate various impact effect radii.
        
        Args:
            energy_j: Impact energy in Joules
            
        Returns:
            Dictionary with effect radii in km
        """
        # TNT equivalent in kilotons
        tnt_kt = UnitConverter.tnt_equivalent(energy_j, 'TNT_kt')
        
        # Scaling relationships based on nuclear weapon effects
        # and asteroid impact research
        
        # Thermal radiation (3rd degree burns)
        thermal_radius_km = 0.4 * (tnt_kt ** 0.4)
        
        # Overpressure effects
        # 1 psi overpressure (window breakage)
        overpressure_1psi_km = 2.2 * (tnt_kt ** 0.33)
        
        # 5 psi overpressure (building damage)
        overpressure_5psi_km = 1.0 * (tnt_kt ** 0.33)
        
        # 20 psi overpressure (severe destruction)
        overpressure_20psi_km = 0.5 * (tnt_kt ** 0.33)
        
        # Seismic effects (Richter magnitude estimation)
        # Log(E) = 1.5*M + 4.8 (energy in Joules, M = Richter magnitude)
        if energy_j > 0:
            richter_magnitude = (np.log10(energy_j) - 4.8) / 1.5
            # Seismic damage radius (rough approximation)
            seismic_radius_km = 10 * (10 ** (richter_magnitude - 4))
        else:
            richter_magnitude = 0
            seismic_radius_km = 0
        
        return {
            'thermal_radius_km': max(thermal_radius_km, 0),
            'overpressure_1psi_km': max(overpressure_1psi_km, 0),
            'overpressure_5psi_km': max(overpressure_5psi_km, 0),
            'overpressure_20psi_km': max(overpressure_20psi_km, 0),
            'seismic_radius_km': max(seismic_radius_km, 0),
            'richter_magnitude': max(richter_magnitude, 0)
        }

    @staticmethod
    def atmospheric_entry_effects(
        diameter_m: float,
        velocity_ms: float,
        density_kg_m3: float = None,
        entry_angle_degrees: float = 45.0
    ) -> Dict[str, float]:
        """
        Calculate atmospheric entry effects and fragmentation.
        
        Args:
            diameter_m: Asteroid diameter in meters
            velocity_ms: Entry velocity in m/s
            density_kg_m3: Asteroid density
            entry_angle_degrees: Entry angle from horizontal
            
        Returns:
            Dictionary with atmospheric entry results
        """
        if density_kg_m3 is None:
            from config.constants import DEFAULT_ASTEROID_DENSITY
            density_kg_m3 = DEFAULT_ASTEROID_DENSITY
        
        mass_kg = estimate_asteroid_mass(diameter_m, density_kg_m3)
        
        # Atmospheric entry energy loss (simplified)
        # Based on meteoroid ablation models
        
        # Entry energy
        entry_energy_j = kinetic_energy(mass_kg, velocity_ms)
        
        # Ablation coefficient (depends on material and velocity)
        # Typical values: 0.01-0.1 s²/km² for stone meteoroids
        ablation_coeff = 0.05
        
        # Atmospheric scale height (km)
        scale_height_km = 8.0
        
        # Entry angle factor
        angle_rad = np.radians(entry_angle_degrees)
        path_factor = 1.0 / np.sin(angle_rad)
        
        # Simplified ablation model
        # Mass loss depends on velocity cubed and atmospheric density
        atmospheric_path_km = scale_height_km * path_factor
        
        # Estimate surviving fraction (very simplified)
        # Real models are much more complex
        if diameter_m < 10:  # Small asteroids
            surviving_fraction = 0.1  # Most burns up
        elif diameter_m < 100:  # Medium asteroids
            surviving_fraction = 0.5  # Partial survival
        else:  # Large asteroids
            surviving_fraction = 0.9  # Most survives
        
        surviving_mass_kg = mass_kg * surviving_fraction
        surviving_diameter_m = diameter_m * (surviving_fraction ** (1/3))
        
        # Final impact velocity (reduced by atmosphere)
        if diameter_m < 50:
            # Small objects reach terminal velocity
            from config.constants import EARTH_SURFACE_GRAVITY, ATMOSPHERIC_DENSITY_SEA_LEVEL
            terminal_velocity_ms = np.sqrt(2 * mass_kg * EARTH_SURFACE_GRAVITY / 
                                         (ATMOSPHERIC_DENSITY_SEA_LEVEL * np.pi * (diameter_m/2)**2 * 0.5))  # Simplified drag
            final_velocity_ms = min(velocity_ms * 0.7, terminal_velocity_ms)
        else:
            # Large objects retain most velocity
            final_velocity_ms = velocity_ms * 0.9
        
        final_energy_j = kinetic_energy(surviving_mass_kg, final_velocity_ms)
        
        return {
            'initial_mass_kg': mass_kg,
            'surviving_mass_kg': surviving_mass_kg,
            'mass_loss_fraction': 1 - surviving_fraction,
            'initial_diameter_m': diameter_m,
            'surviving_diameter_m': surviving_diameter_m,
            'initial_velocity_ms': velocity_ms,
            'final_velocity_ms': final_velocity_ms,
            'initial_energy_j': entry_energy_j,
            'final_energy_j': final_energy_j,
            'energy_loss_fraction': 1 - (final_energy_j / entry_energy_j),
            'atmospheric_path_km': atmospheric_path_km
        }

    @staticmethod
    def complete_impact_analysis(
        diameter_m: float,
        velocity_ms: float,
        impact_angle_degrees: float = 45.0,
        asteroid_density_kg_m3: float = None,
        target_density_kg_m3: float = 2500.0,
        include_atmospheric_entry: bool = True
    ) -> Dict[str, any]:
        """
        Complete impact analysis combining all effects.
        
        Args:
            diameter_m: Asteroid diameter in meters
            velocity_ms: Impact velocity in m/s
            impact_angle_degrees: Impact angle from horizontal
            asteroid_density_kg_m3: Asteroid density
            target_density_kg_m3: Target material density
            include_atmospheric_entry: Whether to model atmospheric entry
            
        Returns:
            Complete impact analysis dictionary
        """
        if asteroid_density_kg_m3 is None:
            from config.constants import DEFAULT_ASTEROID_DENSITY
            asteroid_density_kg_m3 = DEFAULT_ASTEROID_DENSITY
        
        results = {}
        
        # Initial parameters
        initial_mass_kg = estimate_asteroid_mass(diameter_m, asteroid_density_kg_m3)
        results['initial_parameters'] = {
            'diameter_m': diameter_m,
            'velocity_ms': velocity_ms,
            'mass_kg': initial_mass_kg,
            'impact_angle_degrees': impact_angle_degrees,
            'asteroid_density_kg_m3': asteroid_density_kg_m3
        }
        
        # Atmospheric entry (if enabled)
        if include_atmospheric_entry:
            entry_results = ImpactPhysics.atmospheric_entry_effects(
                diameter_m, velocity_ms, asteroid_density_kg_m3, impact_angle_degrees
            )
            results['atmospheric_entry'] = entry_results
            
            # Use surviving parameters for impact
            final_mass_kg = entry_results['surviving_mass_kg']
            final_velocity_ms = entry_results['final_velocity_ms']
        else:
            final_mass_kg = initial_mass_kg
            final_velocity_ms = velocity_ms
        
        # Impact energy
        energy_results = ImpactPhysics.calculate_impact_energy(
            final_mass_kg, final_velocity_ms, impact_angle_degrees
        )
        results['impact_energy'] = energy_results
        
        # Crater formation
        crater_results = ImpactPhysics.estimate_crater_size(
            energy_results['effective_energy_j'], target_density_kg_m3
        )
        results['crater'] = crater_results
        
        # Impact effects
        effects_results = ImpactPhysics.impact_effects_radius(
            energy_results['effective_energy_j']
        )
        results['effects'] = effects_results
        
        return results
