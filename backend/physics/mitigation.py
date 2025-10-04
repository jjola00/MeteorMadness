"""
Mitigation strategy calculations for asteroid deflection scenarios.
Handles kinetic impactors, gravity tractors, and other deflection methods.
"""

import numpy as np
from astropy import units as u
from astropy import constants as const
from scipy.optimize import minimize_scalar
from typing import Dict, List, Tuple, Optional, Union
import warnings

import sys
import os
# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversions import UnitConverter
from config.constants import (
    EARTH_RADIUS_M, AU_M, TYPICAL_IMPACTOR_MASS_KG, TYPICAL_IMPACTOR_VELOCITY_KMS,
    THRUST_EFFICIENCY_DEFAULT, MOMENTUM_TRANSFER_EFFICIENCY
)


class MitigationStrategies:
    """Handles asteroid deflection and mitigation calculations."""

    @staticmethod
    def deflection_timing_analysis(
        orbital_period_years: float,
        time_to_impact_years: float,
        deflection_delta_v_ms: float
    ) -> Dict[str, float]:
        """
        Analyze how deflection timing affects the final deflection distance.
        
        Args:
            orbital_period_years: Asteroid orbital period
            time_to_impact_years: Time remaining until Earth impact
            deflection_delta_v_ms: Velocity change from deflection (m/s)
            
        Returns:
            Dictionary with timing analysis results
        """
        # Convert to consistent units
        period_s = orbital_period_years * 365.25 * 24 * 3600
        time_to_impact_s = time_to_impact_years * 365.25 * 24 * 3600
        
        # Semi-major axis change (for circular orbit approximation)
        # δa/a ≈ 2δv/v for small velocity changes
        orbital_velocity_ms = 2 * np.pi * AU_M / period_s  # Rough estimate
        relative_sma_change = 2 * deflection_delta_v_ms / orbital_velocity_ms
        
        # Position change accumulates over time
        # For a deflection applied tangentially, the position change grows approximately linearly
        # Δr ≈ (3/2) * δa * n * t, where n is mean motion and t is time
        mean_motion_rad_s = 2 * np.pi / period_s
        
        # Final deflection distance (order of magnitude estimate)
        deflection_distance_m = (3/2) * relative_sma_change * 1.5e11 * mean_motion_rad_s * time_to_impact_s
        
        # Alternative calculation: linearized orbital mechanics
        # Δr ≈ Δv * t for tangential velocity changes (very simplified)
        linear_deflection_m = deflection_delta_v_ms * time_to_impact_s
        
        # Use the more conservative estimate
        final_deflection_m = min(abs(deflection_distance_m), linear_deflection_m)
        
        # Express in Earth radii for context
        earth_radius_m = EARTH_RADIUS_M
        deflection_earth_radii = final_deflection_m / earth_radius_m
        
        return {
            'deflection_delta_v_ms': deflection_delta_v_ms,
            'deflection_delta_v_kms': deflection_delta_v_ms / 1000,
            'time_to_impact_years': time_to_impact_years,
            'time_to_impact_days': time_to_impact_years * 365.25,
            'orbital_period_years': orbital_period_years,
            'final_deflection_m': final_deflection_m,
            'final_deflection_km': final_deflection_m / 1000,
            'deflection_earth_radii': deflection_earth_radii,
            'orbital_velocity_ms': orbital_velocity_ms,
            'orbital_velocity_kms': orbital_velocity_ms / 1000,
            'relative_sma_change': relative_sma_change
        }

    @staticmethod
    def kinetic_impactor_mission(
        asteroid_mass_kg: float,
        asteroid_velocity_ms: float,
        impactor_mass_kg: float = None,
        impactor_velocity_ms: float = None,
        impact_angle_degrees: float = 0.0,
        momentum_enhancement: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate kinetic impactor mission parameters.
        
        Args:
            asteroid_mass_kg: Target asteroid mass
            asteroid_velocity_ms: Asteroid orbital velocity
            impactor_mass_kg: Impactor spacecraft mass
            impactor_velocity_ms: Impactor velocity relative to asteroid
            impact_angle_degrees: Impact angle (0 = head-on)
            momentum_enhancement: β factor from ejecta (typically 1-5)
            
        Returns:
            Dictionary with mission results
        """
        if impactor_mass_kg is None:
            impactor_mass_kg = MitigationStrategies.TYPICAL_IMPACTOR_MASS_KG
        if impactor_velocity_ms is None:
            impactor_velocity_ms = MitigationStrategies.TYPICAL_IMPACTOR_VELOCITY_KMS * 1000
        
        # Impact angle correction
        angle_rad = np.radians(impact_angle_degrees)
        effective_velocity_ms = impactor_velocity_ms * np.cos(angle_rad)
        
        # Momentum transfer with enhancement factor
        momentum_transfer = impactor_mass_kg * effective_velocity_ms * momentum_enhancement
        
        # Velocity change of asteroid
        delta_v_ms = momentum_transfer / asteroid_mass_kg
        
        # Energy delivered to asteroid
        impactor_energy_j = 0.5 * impactor_mass_kg * impactor_velocity_ms**2
        
        # Mass ratio
        mass_ratio = impactor_mass_kg / asteroid_mass_kg
        
        # Mission efficiency metrics
        momentum_per_kg = delta_v_ms / (impactor_mass_kg / asteroid_mass_kg)
        energy_efficiency = delta_v_ms / np.sqrt(2 * impactor_energy_j / asteroid_mass_kg)
        
        return {
            'impactor_mass_kg': impactor_mass_kg,
            'impactor_velocity_ms': impactor_velocity_ms,
            'impactor_velocity_kms': impactor_velocity_ms / 1000,
            'effective_velocity_ms': effective_velocity_ms,
            'impact_angle_degrees': impact_angle_degrees,
            'momentum_enhancement': momentum_enhancement,
            'momentum_transfer_kg_ms': momentum_transfer,
            'delta_v_ms': delta_v_ms,
            'delta_v_kms': delta_v_ms / 1000,
            'delta_v_mm_s': delta_v_ms * 1000,  # Often expressed in mm/s
            'impactor_energy_j': impactor_energy_j,
            'impactor_energy_tnt_kg': UnitConverter.tnt_equivalent(impactor_energy_j, 'TNT_kg'),
            'mass_ratio': mass_ratio,
            'momentum_per_kg_efficiency': momentum_per_kg,
            'energy_efficiency': energy_efficiency
        }

    @staticmethod
    def gravity_tractor_mission(
        asteroid_mass_kg: float,
        tractor_mass_kg: float,
        orbital_distance_m: float,
        mission_duration_years: float,
        thrust_efficiency: float = THRUST_EFFICIENCY_DEFAULT
    ) -> Dict[str, float]:
        """
        Calculate gravity tractor mission parameters.
        
        Args:
            asteroid_mass_kg: Target asteroid mass
            tractor_mass_kg: Gravity tractor spacecraft mass
            orbital_distance_m: Distance between spacecraft and asteroid
            mission_duration_years: Duration of gravitational pull
            thrust_efficiency: Fraction of time thrusting (accounting for orbit mechanics)
            
        Returns:
            Dictionary with gravity tractor results
        """
        # Gravitational force between spacecraft and asteroid
        G = const.G.to(u.m**3 / (u.kg * u.s**2)).value
        gravitational_force_n = G * tractor_mass_kg * asteroid_mass_kg / orbital_distance_m**2
        
        # Acceleration of asteroid
        acceleration_ms2 = gravitational_force_n / asteroid_mass_kg
        
        # Mission duration in seconds
        mission_duration_s = mission_duration_years * 365.25 * 24 * 3600
        effective_duration_s = mission_duration_s * thrust_efficiency
        
        # Velocity change (constant acceleration)
        delta_v_ms = acceleration_ms2 * effective_duration_s
        
        # Distance traveled during acceleration (rough estimate)
        deflection_distance_m = 0.5 * acceleration_ms2 * effective_duration_s**2
        
        # Fuel requirements (very rough estimate for ion propulsion)
        # Assumes specific impulse of 3000s and need to maintain position
        specific_impulse_s = 3000
        exhaust_velocity_ms = specific_impulse_s * 9.81
        
        # Thrust needed to maintain position against asteroid gravity
        required_thrust_n = gravitational_force_n
        mass_flow_rate_kg_s = required_thrust_n / exhaust_velocity_ms
        total_propellant_kg = mass_flow_rate_kg_s * effective_duration_s
        
        return {
            'tractor_mass_kg': tractor_mass_kg,
            'orbital_distance_m': orbital_distance_m,
            'orbital_distance_km': orbital_distance_m / 1000,
            'mission_duration_years': mission_duration_years,
            'mission_duration_days': mission_duration_years * 365.25,
            'effective_duration_s': effective_duration_s,
            'gravitational_force_n': gravitational_force_n,
            'acceleration_ms2': acceleration_ms2,
            'delta_v_ms': delta_v_ms,
            'delta_v_kms': delta_v_ms / 1000,
            'delta_v_mm_s': delta_v_ms * 1000,
            'deflection_distance_m': deflection_distance_m,
            'deflection_distance_km': deflection_distance_m / 1000,
            'required_thrust_n': required_thrust_n,
            'propellant_mass_kg': total_propellant_kg,
            'propellant_fraction': total_propellant_kg / tractor_mass_kg,
            'thrust_efficiency': thrust_efficiency
        }

    @staticmethod
    def nuclear_deflection(
        asteroid_mass_kg: float,
        asteroid_diameter_m: float,
        nuclear_yield_kt: float,
        detonation_distance_m: float = None,
        subsurface_depth_m: float = None
    ) -> Dict[str, float]:
        """
        Calculate nuclear deflection mission parameters.
        
        Args:
            asteroid_mass_kg: Target asteroid mass
            asteroid_diameter_m: Asteroid diameter
            nuclear_yield_kt: Nuclear device yield in kilotons
            detonation_distance_m: Distance for standoff detonation (if applicable)
            subsurface_depth_m: Burial depth for subsurface detonation (if applicable)
            
        Returns:
            Dictionary with nuclear deflection results
        """
        # Convert yield to energy
        nuclear_energy_j = UnitConverter.convert_energy(nuclear_yield_kt, 'TNT_kt', 'J')
        
        # Determine detonation type
        if subsurface_depth_m is not None:
            detonation_type = 'subsurface'
            momentum_enhancement = MitigationStrategies.MOMENTUM_TRANSFER_EFFICIENCY['nuclear_subsurface']
            # For subsurface, effective distance is burial depth
            effective_distance_m = subsurface_depth_m
        elif detonation_distance_m is not None:
            detonation_type = 'standoff'
            momentum_enhancement = MitigationStrategies.MOMENTUM_TRANSFER_EFFICIENCY['nuclear_standoff']
            effective_distance_m = detonation_distance_m
        else:
            # Default to standoff at 1 asteroid radius
            detonation_type = 'standoff'
            momentum_enhancement = MitigationStrategies.MOMENTUM_TRANSFER_EFFICIENCY['nuclear_standoff']
            effective_distance_m = asteroid_diameter_m / 2
        
        # Energy coupling efficiency (depends on detonation type and distance)
        if detonation_type == 'subsurface':
            # Much higher coupling for buried charges
            coupling_efficiency = 0.5  # 50% of energy goes into acceleration
        else:
            # Standoff detonation - lower coupling due to energy dispersion
            # Inverse square law for energy density
            asteroid_cross_section_m2 = np.pi * (asteroid_diameter_m / 2)**2
            sphere_area_m2 = 4 * np.pi * effective_distance_m**2
            geometric_efficiency = asteroid_cross_section_m2 / sphere_area_m2
            coupling_efficiency = geometric_efficiency * 0.1  # 10% base coupling
        
        # Effective energy transferred to asteroid
        transferred_energy_j = nuclear_energy_j * coupling_efficiency
        
        # Estimate velocity change using momentum-energy relationship
        # Assumes energy goes into kinetic energy of ejected material
        # Conservation of momentum: m_ejecta * v_ejecta = m_asteroid * delta_v
        # Kinetic energy of ejecta: E = 0.5 * m_ejecta * v_ejecta^2
        
        # Assume 10% of asteroid mass is accelerated (rough estimate)
        ejecta_fraction = 0.1
        ejecta_mass_kg = asteroid_mass_kg * ejecta_fraction
        
        # Ejecta velocity from energy
        ejecta_velocity_ms = np.sqrt(2 * transferred_energy_j / ejecta_mass_kg)
        
        # Asteroid velocity change from momentum conservation
        delta_v_ms = (ejecta_mass_kg * ejecta_velocity_ms) / asteroid_mass_kg * momentum_enhancement
        
        # Alternative calculation: direct impulse estimate
        # Impulse = sqrt(2 * m * E) for explosive events
        impulse_ns = np.sqrt(2 * asteroid_mass_kg * transferred_energy_j)
        delta_v_impulse_ms = impulse_ns / asteroid_mass_kg
        
        # Use the more conservative estimate
        delta_v_final_ms = min(delta_v_ms, delta_v_impulse_ms)
        
        return {
            'nuclear_yield_kt': nuclear_yield_kt,
            'nuclear_energy_j': nuclear_energy_j,
            'detonation_type': detonation_type,
            'effective_distance_m': effective_distance_m,
            'effective_distance_km': effective_distance_m / 1000,
            'momentum_enhancement': momentum_enhancement,
            'coupling_efficiency': coupling_efficiency,
            'transferred_energy_j': transferred_energy_j,
            'ejecta_fraction': ejecta_fraction,
            'ejecta_mass_kg': ejecta_mass_kg,
            'ejecta_velocity_ms': ejecta_velocity_ms,
            'ejecta_velocity_kms': ejecta_velocity_ms / 1000,
            'delta_v_ms': delta_v_final_ms,
            'delta_v_kms': delta_v_final_ms / 1000,
            'delta_v_mm_s': delta_v_final_ms * 1000,
            'impulse_ns': impulse_ns
        }

    @staticmethod
    def mission_comparison(
        asteroid_params: Dict[str, float],
        orbital_params: Dict[str, float],
        mission_scenarios: List[Dict[str, any]] = None
    ) -> Dict[str, any]:
        """
        Compare different mitigation strategies for a given asteroid threat.
        
        Args:
            asteroid_params: Dictionary with asteroid properties
            orbital_params: Dictionary with orbital parameters
            mission_scenarios: List of mission scenario dictionaries
            
        Returns:
            Comparison results
        """
        if mission_scenarios is None:
            # Default mission scenarios
            mission_scenarios = [
                {
                    'type': 'kinetic_impactor',
                    'params': {
                        'impactor_mass_kg': 1000,
                        'impactor_velocity_ms': 10000,
                        'momentum_enhancement': 2.0
                    }
                },
                {
                    'type': 'gravity_tractor',
                    'params': {
                        'tractor_mass_kg': 2000,
                        'orbital_distance_m': 100,
                        'mission_duration_years': 5
                    }
                },
                {
                    'type': 'nuclear_standoff',
                    'params': {
                        'nuclear_yield_kt': 100,
                        'detonation_distance_m': asteroid_params.get('diameter_m', 1000) / 2
                    }
                }
            ]
        
        results = {
            'asteroid_parameters': asteroid_params,
            'orbital_parameters': orbital_params,
            'mission_results': {},
            'comparison_metrics': {}
        }
        
        # Calculate each mission scenario
        for scenario in mission_scenarios:
            mission_type = scenario['type']
            params = scenario['params']
            
            if mission_type == 'kinetic_impactor':
                mission_result = MitigationStrategies.kinetic_impactor_mission(
                    asteroid_params['mass_kg'],
                    asteroid_params.get('velocity_ms', 20000),
                    **params
                )
            elif mission_type == 'gravity_tractor':
                mission_result = MitigationStrategies.gravity_tractor_mission(
                    asteroid_params['mass_kg'],
                    **params
                )
            elif mission_type in ['nuclear_standoff', 'nuclear_subsurface']:
                mission_result = MitigationStrategies.nuclear_deflection(
                    asteroid_params['mass_kg'],
                    asteroid_params.get('diameter_m', 1000),
                    **params
                )
            else:
                continue
            
            # Add timing analysis
            timing_result = MitigationStrategies.deflection_timing_analysis(
                orbital_params.get('period_years', 2.0),
                orbital_params.get('time_to_impact_years', 10.0),
                mission_result['delta_v_ms']
            )
            
            mission_result.update(timing_result)
            results['mission_results'][mission_type] = mission_result
        
        # Comparison metrics
        delta_vs = [result['delta_v_ms'] for result in results['mission_results'].values()]
        deflections = [result['final_deflection_km'] for result in results['mission_results'].values()]
        
        if delta_vs:
            results['comparison_metrics'] = {
                'max_delta_v_ms': max(delta_vs),
                'min_delta_v_ms': min(delta_vs),
                'max_deflection_km': max(deflections),
                'min_deflection_km': min(deflections),
                'best_strategy': max(results['mission_results'].keys(), 
                                   key=lambda k: results['mission_results'][k]['final_deflection_km'])
            }
        
        return results


# TODO: Add API integration endpoints for mitigation strategy analysis
