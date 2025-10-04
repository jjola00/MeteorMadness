"""
Orbital mechanics calculations for asteroid trajectory prediction and mitigation.
Handles Keplerian orbital elements, trajectory propagation, and deflection scenarios.
"""

import numpy as np
from astropy import units as u
from astropy import constants as const
from astropy.time import Time
from astropy.coordinates import (
    solar_system_ephemeris, 
    get_body_barycentric_posvel,
    CartesianRepresentation,
    CartesianDifferential,
    ICRS
)
from astropy.coordinates.builtin_frames import GCRS
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Optional, Union
import warnings

import sys
import os
# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import GM_SUN, GM_EARTH, EARTH_RADIUS_M, AU_M

from backend.utils.conversions import UnitConverter, validate_coordinates


class OrbitalMechanics:
    """Handles orbital mechanics calculations for asteroids."""
    
    def __init__(self):
        """Initialize with constants from configuration."""
        # TODO: When NASA NEO API is integrated, these can be updated with latest ephemeris data
        self.GM_SUN = GM_SUN
        self.GM_EARTH = GM_EARTH
        self.EARTH_RADIUS_M = EARTH_RADIUS_M
        self.AU_M = AU_M

    @staticmethod
    def keplerian_to_cartesian(
        a: float, e: float, i: float, raan: float, 
        arg_per: float, true_anomaly: float,
        gm: float = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert Keplerian orbital elements to Cartesian position and velocity.
        
        Args:
            a: Semi-major axis (m)
            e: Eccentricity
            i: Inclination (degrees)
            raan: Right Ascension of Ascending Node (degrees)
            arg_per: Argument of Periapsis (degrees)
            true_anomaly: True Anomaly (degrees)
            gm: Gravitational parameter (default: Sun)
            
        Returns:
            Tuple of (position_vector, velocity_vector) in meters and m/s
        """
        if gm is None:
            from config.constants import GM_SUN
            gm = GM_SUN
        
        # Convert angles to radians
        i_rad = np.radians(i)
        raan_rad = np.radians(raan)
        arg_per_rad = np.radians(arg_per)
        nu_rad = np.radians(true_anomaly)
        
        # Distance and velocity in orbital plane
        r = a * (1 - e**2) / (1 + e * np.cos(nu_rad))
        h = np.sqrt(gm * a * (1 - e**2))  # Specific angular momentum
        
        # Position in orbital plane
        x_orb = r * np.cos(nu_rad)
        y_orb = r * np.sin(nu_rad)
        z_orb = 0
        
        # Velocity in orbital plane
        vx_orb = -(gm / h) * np.sin(nu_rad)
        vy_orb = (gm / h) * (e + np.cos(nu_rad))
        vz_orb = 0
        
        # Rotation matrices
        # Rotation about z-axis by -raan
        cos_raan = np.cos(-raan_rad)
        sin_raan = np.sin(-raan_rad)
        R1 = np.array([
            [cos_raan, -sin_raan, 0],
            [sin_raan, cos_raan, 0],
            [0, 0, 1]
        ])
        
        # Rotation about x-axis by -i
        cos_i = np.cos(-i_rad)
        sin_i = np.sin(-i_rad)
        R2 = np.array([
            [1, 0, 0],
            [0, cos_i, -sin_i],
            [0, sin_i, cos_i]
        ])
        
        # Rotation about z-axis by -arg_per
        cos_arg = np.cos(-arg_per_rad)
        sin_arg = np.sin(-arg_per_rad)
        R3 = np.array([
            [cos_arg, -sin_arg, 0],
            [sin_arg, cos_arg, 0],
            [0, 0, 1]
        ])
        
        # Combined rotation matrix
        R = R1 @ R2 @ R3
        
        # Transform to inertial frame
        r_vec = R @ np.array([x_orb, y_orb, z_orb])
        v_vec = R @ np.array([vx_orb, vy_orb, vz_orb])
        
        return r_vec, v_vec

    @staticmethod
    def cartesian_to_keplerian(
        r_vec: np.ndarray, v_vec: np.ndarray, gm: float = None
    ) -> Dict[str, float]:
        """
        Convert Cartesian position and velocity to Keplerian elements.
        
        Args:
            r_vec: Position vector (m)
            v_vec: Velocity vector (m/s)
            gm: Gravitational parameter (default: Sun)
            
        Returns:
            Dictionary with Keplerian elements
        """
        if gm is None:
            from config.constants import GM_SUN
            gm = GM_SUN
        
        r = np.linalg.norm(r_vec)
        v = np.linalg.norm(v_vec)
        
        # Specific energy
        energy = v**2 / 2 - gm / r
        
        # Semi-major axis
        a = -gm / (2 * energy)
        
        # Angular momentum vector
        h_vec = np.cross(r_vec, v_vec)
        h = np.linalg.norm(h_vec)
        
        # Eccentricity vector
        e_vec = np.cross(v_vec, h_vec) / gm - r_vec / r
        e = np.linalg.norm(e_vec)
        
        # Inclination
        i = np.degrees(np.arccos(h_vec[2] / h))
        
        # Node vector
        n_vec = np.cross([0, 0, 1], h_vec)
        n = np.linalg.norm(n_vec)
        
        # Right ascension of ascending node
        if n > 1e-10:
            raan = np.degrees(np.arccos(n_vec[0] / n))
            if n_vec[1] < 0:
                raan = 360 - raan
        else:
            raan = 0
        
        # Argument of periapsis
        if n > 1e-10 and e > 1e-10:
            arg_per = np.degrees(np.arccos(np.dot(n_vec, e_vec) / (n * e)))
            if e_vec[2] < 0:
                arg_per = 360 - arg_per
        else:
            arg_per = 0
        
        # True anomaly
        if e > 1e-10:
            true_anomaly = np.degrees(np.arccos(np.dot(e_vec, r_vec) / (e * r)))
            if np.dot(r_vec, v_vec) < 0:
                true_anomaly = 360 - true_anomaly
        else:
            true_anomaly = 0
        
        return {
            'semi_major_axis_m': a,
            'semi_major_axis_au': a / AU_M,
            'eccentricity': e,
            'inclination_deg': i,
            'raan_deg': raan,
            'arg_periapsis_deg': arg_per,
            'true_anomaly_deg': true_anomaly,
            'period_s': 2 * np.pi * np.sqrt(a**3 / gm),
            'period_years': 2 * np.pi * np.sqrt(a**3 / gm) / (365.25 * 24 * 3600)
        }

    @staticmethod
    def propagate_orbit(
        initial_state: np.ndarray,
        time_span_s: float,
        n_points: int = 100,
        gm: float = None,
        include_perturbations: bool = False
    ) -> Dict[str, np.ndarray]:
        """
        Propagate orbital motion over time using numerical integration.
        
        Args:
            initial_state: [x, y, z, vx, vy, vz] in meters and m/s
            time_span_s: Time span for propagation (seconds)
            n_points: Number of points in trajectory
            gm: Gravitational parameter
            include_perturbations: Include Earth gravity perturbations
            
        Returns:
            Dictionary with time, position, and velocity arrays
        """
        if gm is None:
            from config.constants import GM_SUN
            gm = GM_SUN
        
        def orbital_dynamics(t, state):
            """Two-body dynamics with optional perturbations."""
            r_vec = state[:3]
            v_vec = state[3:]
            r = np.linalg.norm(r_vec)
            
            # Primary gravitational acceleration (Sun)
            a_primary = -gm * r_vec / r**3
            
            # Optional Earth perturbation (simplified)
            a_perturbation = np.zeros(3)
            if include_perturbations:
                # This is a very simplified Earth perturbation
                # Real implementation would use full planetary positions
                earth_distance = 1.5e11  # Approximate Earth distance
                from config.constants import GM_EARTH
                earth_gm = GM_EARTH
                a_perturbation = -earth_gm * r_vec / earth_distance**3
            
            total_acceleration = a_primary + a_perturbation
            
            return np.concatenate([v_vec, total_acceleration])
        
        # Time points
        t_eval = np.linspace(0, time_span_s, n_points)
        
        # Solve ODE
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            solution = solve_ivp(
                orbital_dynamics,
                [0, time_span_s],
                initial_state,
                t_eval=t_eval,
                method='RK45',
                rtol=1e-8,
                atol=1e-10
            )
        
        if not solution.success:
            raise RuntimeError(f"Orbit propagation failed: {solution.message}")
        
        positions = solution.y[:3, :].T  # Shape: (n_points, 3)
        velocities = solution.y[3:, :].T  # Shape: (n_points, 3)
        
        return {
            'time_s': solution.t,
            'time_days': solution.t / (24 * 3600),
            'positions_m': positions,
            'velocities_ms': velocities,
            'distances_au': np.linalg.norm(positions, axis=1) / AU_M
        }

    @staticmethod
    def earth_impact_probability(
        trajectory: Dict[str, np.ndarray],
        earth_soi_radius_m: float = None
    ) -> Dict[str, Union[bool, float, int]]:
        """
        Check if trajectory intersects Earth's sphere of influence.
        
        Args:
            trajectory: Output from propagate_orbit
            earth_soi_radius_m: Earth's sphere of influence radius
            
        Returns:
            Dictionary with impact analysis
        """
        if earth_soi_radius_m is None:
            # Earth's Hill sphere radius (simplified)
            earth_soi_radius_m = EARTH_RADIUS_M * 100  # ~600,000 km
        
        positions = trajectory['positions_m']
        times = trajectory['time_s']
        
        # Calculate distances from Earth (assuming Earth at origin for simplification)
        # In reality, you'd need Earth's position at each time
        distances = np.linalg.norm(positions, axis=1)
        
        # Find minimum approach
        min_distance_idx = np.argmin(distances)
        min_distance_m = distances[min_distance_idx]
        min_distance_time_s = times[min_distance_idx]
        
        # Check for impact
        impact_detected = min_distance_m < earth_soi_radius_m
        
        # If close approach, estimate impact parameters
        if impact_detected and min_distance_m < EARTH_RADIUS_M * 10:
            # Estimate impact velocity (simplified)
            velocity_at_approach = trajectory['velocities_ms'][min_distance_idx]
            impact_velocity_ms = np.linalg.norm(velocity_at_approach)
            
            # Estimate impact coordinates (very simplified)
            # Real calculation would account for Earth's rotation and precise geometry
            position_at_approach = positions[min_distance_idx]
            # Convert to spherical coordinates for Earth surface
            lat = np.degrees(np.arcsin(position_at_approach[2] / min_distance_m))
            lon = np.degrees(np.arctan2(position_at_approach[1], position_at_approach[0]))
            
            # Ensure valid coordinates
            lat = np.clip(lat, -90, 90)
            lon = ((lon + 180) % 360) - 180
        else:
            impact_velocity_ms = None
            lat = None
            lon = None
        
        return {
            'impact_detected': impact_detected,
            'min_distance_m': min_distance_m,
            'min_distance_km': min_distance_m / 1000,
            'min_distance_earth_radii': min_distance_m / EARTH_RADIUS_M,
            'time_to_closest_approach_s': min_distance_time_s,
            'time_to_closest_approach_days': min_distance_time_s / (24 * 3600),
            'impact_velocity_ms': impact_velocity_ms,
            'impact_velocity_kms': impact_velocity_ms / 1000 if impact_velocity_ms else None,
            'impact_latitude': lat,
            'impact_longitude': lon,
            'impact_coordinates_valid': validate_coordinates(lat, lon) if lat is not None else False
        }

    @staticmethod
    def deflection_delta_v(
        mass_kg: float,
        impactor_mass_kg: float,
        impact_velocity_ms: float,
        deflection_efficiency: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate velocity change from kinetic impactor deflection.
        
        Args:
            mass_kg: Asteroid mass (kg)
            impactor_mass_kg: Impactor spacecraft mass (kg)
            impact_velocity_ms: Relative impact velocity (m/s)
            deflection_efficiency: Momentum transfer efficiency (0-1)
            
        Returns:
            Dictionary with deflection results
        """
        # Momentum transfer (conservation of momentum)
        initial_momentum = impactor_mass_kg * impact_velocity_ms
        transferred_momentum = initial_momentum * deflection_efficiency
        
        # Velocity change of asteroid
        delta_v_ms = transferred_momentum / mass_kg
        
        # Energy considerations
        impactor_energy_j = 0.5 * impactor_mass_kg * impact_velocity_ms**2
        
        return {
            'delta_v_ms': delta_v_ms,
            'delta_v_kms': delta_v_ms / 1000,
            'momentum_transfer_kg_ms': transferred_momentum,
            'impactor_energy_j': impactor_energy_j,
            'impactor_energy_tnt_kg': UnitConverter.tnt_equivalent(impactor_energy_j, 'TNT_kg'),
            'deflection_efficiency': deflection_efficiency,
            'mass_ratio': impactor_mass_kg / mass_kg
        }
