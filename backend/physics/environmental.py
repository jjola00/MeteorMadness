"""
Environmental impact modeling for asteroid impacts.
Handles tsunami generation, seismic effects, and atmospheric disturbances.
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
from scipy.interpolate import interp1d
from scipy.integrate import quad
from typing import Dict, List, Tuple, Optional, Union
import warnings

import sys
import os
# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversions import UnitConverter, EARTH_RADIUS_KM, validate_coordinates


class EnvironmentalEffects:
    """Handles environmental effects of asteroid impacts."""
    
    # Ocean and seismic constants
    OCEAN_DEPTH_AVG_M = 3800.0  # Average ocean depth
    SEISMIC_WAVE_VELOCITY_MS = 6000.0  # P-wave velocity in rock
    TSUNAMI_WAVE_VELOCITY_MS = 200.0  # Tsunami wave velocity (shallow water)
    
    # Earth properties
    EARTH_RADIUS_M = EARTH_RADIUS_KM * 1000.0
    EARTH_CIRCUMFERENCE_M = 2 * np.pi * EARTH_RADIUS_M

    @staticmethod
    def is_ocean_impact(latitude: float, longitude: float) -> bool:
        """
        Determine if impact coordinates are over ocean.
        This is a simplified version - real implementation would use coastline data.
        
        Args:
            latitude: Impact latitude in degrees
            longitude: Impact longitude in degrees
            
        Returns:
            True if impact is likely over ocean
        """
        if not validate_coordinates(latitude, longitude):
            return False
        
        # Simplified ocean detection based on major land masses
        # Real implementation would use detailed coastline/bathymetry data
        
        # Major continents (very simplified boundaries)
        land_regions = [
            # North America (approximate)
            (-170, -50, 15, 75),  # (lon_min, lon_max, lat_min, lat_max)
            # South America
            (-85, -30, -60, 15),
            # Europe/Asia
            (-15, 180, 35, 80),
            # Africa
            (-20, 55, -40, 40),
            # Australia
            (110, 160, -45, -10),
            # Antarctica (simplified)
            (-180, 180, -90, -60)
        ]
        
        for lon_min, lon_max, lat_min, lat_max in land_regions:
            # Handle longitude wraparound
            if lon_min < lon_max:
                if lon_min <= longitude <= lon_max and lat_min <= latitude <= lat_max:
                    return False
            else:  # Wraps around 180/-180
                if (longitude >= lon_min or longitude <= lon_max) and lat_min <= latitude <= lat_max:
                    return False
        
        return True  # Assume ocean if not clearly over land

    @staticmethod
    def tsunami_generation(
        impact_energy_j: float,
        water_depth_m: float = None,
        crater_diameter_m: float = None
    ) -> Dict[str, float]:
        """
        Model tsunami generation from ocean impact.
        Based on Ward & Asphaug (2000) and other tsunami impact studies.
        
        Args:
            impact_energy_j: Impact energy in Joules
            water_depth_m: Water depth at impact site
            crater_diameter_m: Crater diameter (if known)
            
        Returns:
            Dictionary with tsunami characteristics
        """
        if water_depth_m is None:
            water_depth_m = EnvironmentalEffects.OCEAN_DEPTH_AVG_M
        
        # Estimate crater diameter if not provided
        if crater_diameter_m is None:
            crater_info = ImpactPhysics.estimate_crater_size(impact_energy_j, target_density_kg_m3=1025)  # Seawater density
            crater_diameter_m = crater_info['diameter_m']
        
        # Tsunami amplitude scaling (simplified Ward & Asphaug model)
        # Initial wave amplitude ~ (crater_diameter / water_depth) * displacement
        
        # Displacement volume (hemisphere approximation)
        crater_radius_m = crater_diameter_m / 2.0
        displacement_volume_m3 = (2.0 / 3.0) * np.pi * crater_radius_m**3
        
        # Initial wave amplitude (order of magnitude estimate)
        if crater_diameter_m > water_depth_m:
            # Shallow water case - more efficient tsunami generation
            initial_amplitude_m = displacement_volume_m3 / (np.pi * crater_radius_m**2)
            efficiency_factor = 0.5  # More energy goes into horizontal waves
        else:
            # Deep water case - less efficient
            initial_amplitude_m = crater_diameter_m * 0.1  # Much smaller amplitude
            efficiency_factor = 0.1
        
        # Wave energy
        tsunami_energy_j = impact_energy_j * efficiency_factor
        
        # Characteristic wavelength (related to crater size and water depth)
        wavelength_m = max(2 * np.pi * crater_diameter_m, 4 * water_depth_m)
        
        # Wave period (shallow water approximation)
        wave_speed_ms = np.sqrt(9.81 * water_depth_m)  # Shallow water wave speed
        wave_period_s = wavelength_m / wave_speed_ms
        
        # Decay distance (very approximate)
        # Real tsunamis can travel across entire ocean basins
        decay_distance_km = np.sqrt(tsunami_energy_j / 1e15) * 1000  # Rough scaling
        
        return {
            'initial_amplitude_m': initial_amplitude_m,
            'crater_diameter_m': crater_diameter_m,
            'displacement_volume_m3': displacement_volume_m3,
            'tsunami_energy_j': tsunami_energy_j,
            'wavelength_m': wavelength_m,
            'wavelength_km': wavelength_m / 1000,
            'wave_period_s': wave_period_s,
            'wave_period_min': wave_period_s / 60,
            'initial_wave_speed_ms': wave_speed_ms,
            'initial_wave_speed_kmh': wave_speed_ms * 3.6,
            'decay_distance_km': decay_distance_km,
            'water_depth_m': water_depth_m,
            'efficiency_factor': efficiency_factor
        }

    @staticmethod
    def tsunami_propagation(
        tsunami_params: Dict[str, float],
        distances_km: np.ndarray,
        bathymetry_m: np.ndarray = None
    ) -> Dict[str, np.ndarray]:
        """
        Model tsunami wave propagation and amplitude decay.
        
        Args:
            tsunami_params: Output from tsunami_generation
            distances_km: Array of distances from impact site (km)
            bathymetry_m: Water depths along propagation path (optional)
            
        Returns:
            Dictionary with wave properties vs distance
        """
        if bathymetry_m is None:
            bathymetry_m = np.full_like(distances_km, EnvironmentalEffects.OCEAN_DEPTH_AVG_M)
        
        # Initial conditions
        initial_amplitude_m = tsunami_params['initial_amplitude_m']
        initial_energy_j = tsunami_params['tsunami_energy_j']
        
        # Distance array in meters
        distances_m = distances_km * 1000
        
        # Geometric spreading loss (cylindrical spreading)
        # Amplitude decreases as 1/sqrt(distance) for cylindrical waves
        geometric_factor = np.sqrt(distances_km[0] / np.maximum(distances_km, 0.1))
        
        # Bathymetry effects on wave speed and amplitude
        wave_speeds_ms = np.sqrt(9.81 * bathymetry_m)  # Shallow water approximation
        
        # Green's law: amplitude changes with depth
        # A₁/A₂ = (h₂/h₁)^(1/4) for long waves
        depth_factor = (bathymetry_m[0] / bathymetry_m) ** 0.25
        
        # Energy dissipation (simplified exponential decay)
        # Real tsunamis have complex dissipation mechanisms
        dissipation_length_km = 5000  # Typical trans-oceanic scale
        energy_factor = np.exp(-distances_km / dissipation_length_km)
        
        # Combined amplitude
        amplitudes_m = initial_amplitude_m * geometric_factor * depth_factor * np.sqrt(energy_factor)
        
        # Wave arrival times
        # Integrate travel time over variable bathymetry
        arrival_times_s = np.zeros_like(distances_km)
        for i in range(1, len(distances_km)):
            segment_distance_m = (distances_m[i] - distances_m[i-1])
            avg_speed_ms = (wave_speeds_ms[i] + wave_speeds_ms[i-1]) / 2
            arrival_times_s[i] = arrival_times_s[i-1] + segment_distance_m / avg_speed_ms
        
        # Wave periods (approximately constant for long waves)
        periods_s = np.full_like(distances_km, tsunami_params['wave_period_s'])
        
        return {
            'distances_km': distances_km,
            'amplitudes_m': amplitudes_m,
            'wave_speeds_ms': wave_speeds_ms,
            'wave_speeds_kmh': wave_speeds_ms * 3.6,
            'arrival_times_s': arrival_times_s,
            'arrival_times_h': arrival_times_s / 3600,
            'periods_s': periods_s,
            'bathymetry_m': bathymetry_m,
            'energy_remaining': energy_factor
        }

    @staticmethod
    def seismic_effects(
        impact_energy_j: float,
        impact_lat: float,
        impact_lon: float,
        observation_points: List[Tuple[float, float]]
    ) -> Dict[str, Union[float, List[float]]]:
        """
        Calculate seismic effects at various locations.
        
        Args:
            impact_energy_j: Impact energy in Joules
            impact_lat: Impact latitude
            impact_lon: Impact longitude
            observation_points: List of (lat, lon) tuples for seismic analysis
            
        Returns:
            Dictionary with seismic effects
        """
        # Estimate earthquake magnitude from energy
        # Gutenberg-Richter relation: log10(E) = 1.5*M + 4.8 (energy in Joules)
        if impact_energy_j > 0:
            magnitude = (np.log10(impact_energy_j) - 4.8) / 1.5
        else:
            magnitude = 0
        
        # Calculate distances to observation points
        impact_point = Point(impact_lon, impact_lat)
        
        results = {
            'magnitude': magnitude,
            'impact_coordinates': (impact_lat, impact_lon),
            'observation_points': observation_points,
            'distances_km': [],
            'travel_times_s': [],
            'peak_accelerations_g': [],
            'intensities_mmi': []  # Modified Mercalli Intensity
        }
        
        for obs_lat, obs_lon in observation_points:
            obs_point = Point(obs_lon, obs_lat)
            
            # Great circle distance (Haversine formula)
            distance_km = EnvironmentalEffects._haversine_distance(
                impact_lat, impact_lon, obs_lat, obs_lon
            )
            results['distances_km'].append(distance_km)
            
            # P-wave travel time (simplified)
            travel_time_s = (distance_km * 1000) / EnvironmentalEffects.SEISMIC_WAVE_VELOCITY_MS
            results['travel_times_s'].append(travel_time_s)
            
            # Peak ground acceleration (simplified attenuation)
            # Based on Boore-Atkinson Ground Motion Prediction Equation (simplified)
            if distance_km > 0:
                # Log acceleration decreases with distance and magnitude
                log_pga = magnitude - 3.5 * np.log10(distance_km) - 2.0
                pga_g = 10 ** log_pga  # in units of g
            else:
                pga_g = 10.0  # Very high acceleration at ground zero
            
            results['peak_accelerations_g'].append(max(pga_g, 0.001))  # Minimum detectable
            
            # Modified Mercalli Intensity (empirical relation to PGA)
            if pga_g >= 0.65:
                mmi = 10  # Extreme
            elif pga_g >= 0.34:
                mmi = 9   # Violent  
            elif pga_g >= 0.18:
                mmi = 8   # Severe
            elif pga_g >= 0.092:
                mmi = 7   # Very strong
            elif pga_g >= 0.039:
                mmi = 6   # Strong
            elif pga_g >= 0.017:
                mmi = 5   # Moderate
            elif pga_g >= 0.0092:
                mmi = 4   # Light
            elif pga_g >= 0.0017:
                mmi = 3   # Weak
            else:
                mmi = 2   # Not felt
            
            results['intensities_mmi'].append(mmi)
        
        return results

    @staticmethod
    def atmospheric_effects(
        impact_energy_j: float,
        impact_altitude_m: float = 0.0
    ) -> Dict[str, float]:
        """
        Estimate atmospheric effects from impact.
        
        Args:
            impact_energy_j: Impact energy in Joules
            impact_altitude_m: Impact altitude above sea level
            
        Returns:
            Dictionary with atmospheric effects
        """
        # TNT equivalent for scaling
        tnt_kt = UnitConverter.tnt_equivalent(impact_energy_j, 'TNT_kt')
        
        # Blast wave overpressure (Rankine-Hugoniot relations, simplified)
        # Peak overpressure at various distances
        
        # Thermal radiation effects
        thermal_energy_fraction = 0.35  # Typical fraction for nuclear weapons
        thermal_energy_j = impact_energy_j * thermal_energy_fraction
        
        # Fireball radius (scaled from nuclear weapons)
        fireball_radius_m = 50 * (tnt_kt ** 0.4)  # Rough scaling
        
        # Mushroom cloud height (if sufficient energy)
        if tnt_kt > 1:  # Significant atmospheric disturbance
            cloud_height_m = 12000 * (tnt_kt ** 0.25)  # Rough scaling
        else:
            cloud_height_m = 0
        
        # Atmospheric pressure wave travel time around Earth
        sound_speed_ms = 343  # At sea level
        pressure_wave_travel_time_s = EnvironmentalEffects.EARTH_CIRCUMFERENCE_M / sound_speed_ms
        
        return {
            'tnt_equivalent_kt': tnt_kt,
            'thermal_energy_j': thermal_energy_j,
            'thermal_energy_fraction': thermal_energy_fraction,
            'fireball_radius_m': fireball_radius_m,
            'fireball_radius_km': fireball_radius_m / 1000,
            'mushroom_cloud_height_m': cloud_height_m,
            'mushroom_cloud_height_km': cloud_height_m / 1000,
            'pressure_wave_travel_time_s': pressure_wave_travel_time_s,
            'pressure_wave_travel_time_h': pressure_wave_travel_time_s / 3600,
            'impact_altitude_m': impact_altitude_m
        }

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great circle distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates (degrees)
            lat2, lon2: Second point coordinates (degrees)
            
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return EARTH_RADIUS_KM * c

    @staticmethod
    def complete_environmental_analysis(
        impact_energy_j: float,
        impact_lat: float,
        impact_lon: float,
        observation_points: List[Tuple[float, float]] = None
    ) -> Dict[str, any]:
        """
        Complete environmental impact analysis.
        
        Args:
            impact_energy_j: Impact energy in Joules
            impact_lat: Impact latitude
            impact_lon: Impact longitude
            observation_points: Points for detailed analysis
            
        Returns:
            Complete environmental analysis
        """
        if observation_points is None:
            # Default observation points (major cities)
            observation_points = [
                (40.7128, -74.0060),  # New York
                (51.5074, -0.1278),   # London
                (35.6762, 139.6503),  # Tokyo
                (-33.8688, 151.2093), # Sydney
                (19.4326, -99.1332),  # Mexico City
            ]
        
        results = {}
        
        # Determine impact type
        is_ocean = EnvironmentalEffects.is_ocean_impact(impact_lat, impact_lon)
        results['impact_type'] = 'ocean' if is_ocean else 'land'
        results['impact_coordinates'] = (impact_lat, impact_lon)
        
        # Atmospheric effects (always present)
        atmospheric = EnvironmentalEffects.atmospheric_effects(impact_energy_j)
        results['atmospheric'] = atmospheric
        
        # Seismic effects (always present)
        seismic = EnvironmentalEffects.seismic_effects(
            impact_energy_j, impact_lat, impact_lon, observation_points
        )
        results['seismic'] = seismic
        
        # Tsunami effects (only for ocean impacts)
        if is_ocean:
            tsunami_gen = EnvironmentalEffects.tsunami_generation(impact_energy_j)
            results['tsunami_generation'] = tsunami_gen
            
            # Model tsunami propagation to nearby coasts
            distances_km = np.linspace(100, 5000, 50)  # 100 km to 5000 km
            tsunami_prop = EnvironmentalEffects.tsunami_propagation(
                tsunami_gen, distances_km
            )
            results['tsunami_propagation'] = tsunami_prop
        else:
            results['tsunami_generation'] = None
            results['tsunami_propagation'] = None
        
        return results


def run_environmental_test():
    """Test the environmental effects calculations."""
    print("🧪 Testing Environmental Effects Module")
    print("=" * 50)
    
    # Test parameters
    energy_j = 1e16  # 10 petajoules (~2.4 megatons TNT)
    impact_lat = 35.0  # Pacific Ocean
    impact_lon = -140.0
    
    print(f"Test case: {UnitConverter.tnt_equivalent(energy_j, 'TNT_Mt'):.1f} MT impact at ({impact_lat}, {impact_lon})")
    print()
    
    # Complete environmental analysis
    results = EnvironmentalEffects.complete_environmental_analysis(
        energy_j, impact_lat, impact_lon
    )
    
    # Print results
    print(f"Impact type: {results['impact_type']}")
    print()
    
    print("Atmospheric Effects:")
    atm = results['atmospheric']
    print(f"  Fireball radius: {atm['fireball_radius_km']:.1f} km")
    print(f"  Cloud height: {atm['mushroom_cloud_height_km']:.1f} km")
    print(f"  Pressure wave travel time: {atm['pressure_wave_travel_time_h']:.1f} hours")
    print()
    
    print("Seismic Effects:")
    seis = results['seismic']
    print(f"  Earthquake magnitude: {seis['magnitude']:.1f}")
    print(f"  Example distances: {seis['distances_km'][:3]} km")
    print(f"  Example intensities (MMI): {seis['intensities_mmi'][:3]}")
    print()
    
    if results['tsunami_generation']:
        print("Tsunami Effects:")
        tsu = results['tsunami_generation']
        print(f"  Initial amplitude: {tsu['initial_amplitude_m']:.1f} m")
        print(f"  Wavelength: {tsu['wavelength_km']:.1f} km")
        print(f"  Wave period: {tsu['wave_period_min']:.1f} minutes")
        print(f"  Initial wave speed: {tsu['initial_wave_speed_kmh']:.0f} km/h")
        
        prop = results['tsunami_propagation']
        print(f"  Max propagation distance: {np.max(prop['distances_km']):.0f} km")
        print(f"  Amplitude at 1000 km: {np.interp(1000, prop['distances_km'], prop['amplitudes_m']):.2f} m")
    
    print("\n🎉 Environmental effects test completed!")


if __name__ == "__main__":
    run_environmental_test()
