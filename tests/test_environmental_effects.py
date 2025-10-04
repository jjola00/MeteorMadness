"""
Unit tests for environmental effects calculations.
Tests the physics accuracy and API functionality.
"""

import unittest
import numpy as np
import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.environmental_effects import (
    EnvironmentalEffectsProcessor, SeismicEffects, AtmosphericEffects,
    ThermalEffects, DebrisEffects, InfrastructureEffects
)
from physics.impact import ImpactPhysics


class TestEnvironmentalEffectsProcessor(unittest.TestCase):
    """Test the main environmental effects processor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = EnvironmentalEffectsProcessor()
        
        # Sample impact data for testing
        self.sample_impact_data = {
            'impact_energy': {'effective_energy_j': 1e15},
            'crater': {
                'volume_m3': 1e9,
                'ejecta_radius_km': 50
            },
            'effects': {
                'overpressure_1psi_km': 100,
                'overpressure_5psi_km': 50,
                'overpressure_20psi_km': 20
            },
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_calculate_temporal_effects_basic(self):
        """Test basic temporal effects calculation."""
        results = self.processor.calculate_temporal_effects(
            self.sample_impact_data,
            time_range_hours=(0, 24),
            time_resolution_hours=1.0
        )
        
        # Check structure
        self.assertIn('time_hours', results)
        self.assertIn('effects', results)
        self.assertIn('impact_location', results)
        
        # Check time array
        self.assertEqual(len(results['time_hours']), 24)
        self.assertEqual(results['time_hours'][0], 0.0)
        self.assertEqual(results['time_hours'][-1], 23.0)
        
        # Check that all effect types are present
        expected_effects = ['seismic', 'atmospheric', 'thermal', 'debris', 'infrastructure']
        for effect_type in expected_effects:
            self.assertIn(effect_type, results['effects'])
    
    def test_calculate_temporal_effects_subset(self):
        """Test temporal effects calculation with subset of effect types."""
        results = self.processor.calculate_temporal_effects(
            self.sample_impact_data,
            time_range_hours=(0, 12),
            time_resolution_hours=2.0,
            effect_types=['seismic', 'thermal']
        )
        
        # Check that only requested effects are present
        self.assertEqual(len(results['effects']), 2)
        self.assertIn('seismic', results['effects'])
        self.assertIn('thermal', results['effects'])
        self.assertNotIn('atmospheric', results['effects'])
    
    def test_get_effect_at_time(self):
        """Test getting effects at specific time and location."""
        location = (41.0, -73.0)  # Near impact site
        time_hours = 2.0
        
        results = self.processor.get_effect_at_time(
            self.sample_impact_data,
            time_hours,
            location
        )
        
        # Check structure
        self.assertIn('time_hours', results)
        self.assertIn('location', results)
        self.assertIn('effects', results)
        
        # Check values
        self.assertEqual(results['time_hours'], time_hours)
        self.assertEqual(results['location']['lat'], location[0])
        self.assertEqual(results['location']['lon'], location[1])
        
        # Check that effects are calculated
        for effect_type in self.processor.effect_types.keys():
            self.assertIn(effect_type, results['effects'])


class TestSeismicEffects(unittest.TestCase):
    """Test seismic effects calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.seismic = SeismicEffects()
        self.sample_impact_data = {
            'impact_energy': {'effective_energy_j': 1e15},
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_temporal_evolution(self):
        """Test seismic temporal evolution calculation."""
        time_hours = np.array([0, 1, 2, 6, 12, 24])
        
        results = self.seismic.calculate_temporal_evolution(
            self.sample_impact_data, time_hours
        )
        
        # Check structure
        self.assertIn('magnitude', results)
        self.assertIn('distances_km', results)
        self.assertIn('p_wave_arrival_hours', results)
        self.assertIn('s_wave_arrival_hours', results)
        self.assertIn('intensity_grid', results)
        
        # Check magnitude calculation
        self.assertGreater(results['magnitude'], 0)
        self.assertLess(results['magnitude'], 15)  # Reasonable upper bound
        
        # Check wave arrival times
        p_arrivals = results['p_wave_arrival_hours']
        s_arrivals = results['s_wave_arrival_hours']
        
        # S-waves should arrive after P-waves
        for i in range(len(p_arrivals)):
            self.assertLessEqual(p_arrivals[i], s_arrivals[i])
        
        # Check intensity grid dimensions
        self.assertEqual(len(results['intensity_grid']), len(time_hours))
        self.assertEqual(len(results['intensity_grid'][0]), len(results['distances_km']))
    
    def test_intensity_at_location_time(self):
        """Test seismic intensity at specific location and time."""
        location = (41.0, -73.0)  # ~100 km from impact
        time_hours = 1.0
        
        results = self.seismic.get_intensity_at_location_time(
            self.sample_impact_data, location, time_hours
        )
        
        # Check structure
        self.assertIn('intensity', results)
        self.assertIn('magnitude', results)
        self.assertIn('distance_km', results)
        self.assertIn('p_wave_arrival_hours', results)
        self.assertIn('s_wave_arrival_hours', results)
        
        # Check values
        self.assertGreaterEqual(results['intensity'], 0)
        self.assertGreater(results['distance_km'], 0)
        self.assertLess(results['distance_km'], 200)  # Should be reasonable distance
    
    def test_distance_calculation(self):
        """Test great circle distance calculation."""
        # Test known distance (approximately)
        loc1 = (40.7128, -74.0060)  # New York
        loc2 = (34.0522, -118.2437)  # Los Angeles
        
        distance = self.seismic._calculate_distance(loc1, loc2)
        
        # Should be approximately 3944 km
        self.assertGreater(distance, 3900)
        self.assertLess(distance, 4000)


class TestAtmosphericEffects(unittest.TestCase):
    """Test atmospheric effects calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.atmospheric = AtmosphericEffects()
        self.sample_impact_data = {
            'impact_energy': {'effective_energy_j': 1e15},
            'crater': {'volume_m3': 1e9},
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_temporal_evolution(self):
        """Test atmospheric temporal evolution."""
        time_hours = np.array([0, 6, 12, 24, 48, 72])
        
        results = self.atmospheric.calculate_temporal_evolution(
            self.sample_impact_data, time_hours
        )
        
        # Check structure
        self.assertIn('total_dust_mass_kg', results)
        self.assertIn('atmospheric_energy_j', results)
        self.assertIn('timeline', results)
        
        # Check timeline data
        timeline = results['timeline']
        self.assertEqual(len(timeline), len(time_hours))
        
        # Check that dust concentration decreases over time
        concentrations = [t['dust_concentration_kg_m3'] for t in timeline]
        for i in range(1, len(concentrations)):
            self.assertLessEqual(concentrations[i], concentrations[i-1])
    
    def test_intensity_at_location_time(self):
        """Test atmospheric intensity at location and time."""
        location = (40.5, -74.2)  # Near impact site
        time_hours = 12.0
        
        results = self.atmospheric.get_intensity_at_location_time(
            self.sample_impact_data, location, time_hours
        )
        
        # Check structure
        self.assertIn('dust_concentration_kg_m3', results)
        self.assertIn('temperature_change_c', results)
        self.assertIn('air_quality_index', results)
        self.assertIn('in_affected_area', results)
        
        # Check values
        self.assertGreaterEqual(results['dust_concentration_kg_m3'], 0)
        self.assertLessEqual(results['temperature_change_c'], 0)  # Should be cooling
        self.assertGreaterEqual(results['air_quality_index'], 0)
        self.assertLessEqual(results['air_quality_index'], 500)


class TestThermalEffects(unittest.TestCase):
    """Test thermal effects calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.thermal = ThermalEffects()
        self.sample_impact_data = {
            'impact_energy': {'effective_energy_j': 1e15},
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_temporal_evolution(self):
        """Test thermal temporal evolution."""
        time_hours = np.array([0, 0.1, 0.5, 1, 6, 12])
        
        results = self.thermal.calculate_temporal_evolution(
            self.sample_impact_data, time_hours
        )
        
        # Check structure
        self.assertIn('thermal_energy_j', results)
        self.assertIn('timeline', results)
        
        # Check that thermal effects peak early and decay
        timeline = results['timeline']
        intensities = [t['intensity_fraction'] for t in timeline]
        
        # Peak should be at or near the beginning
        max_intensity_index = intensities.index(max(intensities))
        self.assertLessEqual(max_intensity_index, 1)  # Should be in first two time steps
    
    def test_intensity_at_location_time(self):
        """Test thermal intensity at location and time."""
        location = (40.1, -74.1)  # Close to impact
        time_hours = 0.1  # Peak thermal time
        
        results = self.thermal.get_intensity_at_location_time(
            self.sample_impact_data, location, time_hours
        )
        
        # Check structure
        self.assertIn('intensity', results)
        self.assertIn('temperature_k', results)
        self.assertIn('thermal_radius_km', results)
        
        # Check values
        self.assertGreaterEqual(results['intensity'], 0)
        self.assertLessEqual(results['intensity'], 1)
        self.assertGreaterEqual(results['temperature_k'], 300)  # At least ambient


class TestDebrisEffects(unittest.TestCase):
    """Test debris effects calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.debris = DebrisEffects()
        self.sample_impact_data = {
            'crater': {
                'volume_m3': 1e9,
                'ejecta_radius_km': 50
            },
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_temporal_evolution(self):
        """Test debris temporal evolution."""
        time_hours = np.array([0, 0.1, 0.3, 0.5, 1, 2])
        
        results = self.debris.calculate_temporal_evolution(
            self.sample_impact_data, time_hours
        )
        
        # Check structure
        self.assertIn('total_debris_mass_kg', results)
        self.assertIn('ejecta_radius_km', results)
        self.assertIn('timeline', results)
        
        # Check that debris effects are strongest early
        timeline = results['timeline']
        intensities = [t['debris_intensity'] for t in timeline]
        
        # Should decrease over time in first 0.5 hours
        for i in range(1, min(3, len(intensities))):
            if time_hours[i] <= 0.5:
                self.assertLessEqual(intensities[i], intensities[i-1])


class TestInfrastructureEffects(unittest.TestCase):
    """Test infrastructure effects calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.infrastructure = InfrastructureEffects()
        self.sample_impact_data = {
            'effects': {
                'overpressure_1psi_km': 100,
                'overpressure_5psi_km': 50,
                'overpressure_20psi_km': 20
            },
            'impact_location': {'lat': 40.0, 'lon': -74.0}
        }
    
    def test_temporal_evolution(self):
        """Test infrastructure temporal evolution."""
        time_hours = np.array([0, 1, 12, 24, 48, 168])
        
        results = self.infrastructure.calculate_temporal_evolution(
            self.sample_impact_data, time_hours
        )
        
        # Check structure
        self.assertIn('initial_severe_radius_km', results)
        self.assertIn('timeline', results)
        
        # Check that damage initially increases then decreases (recovery)
        timeline = results['timeline']
        severe_radii = [t['severe_damage_radius_km'] for t in timeline]
        
        # Should have some variation over time
        self.assertNotEqual(severe_radii[0], severe_radii[-1])
    
    def test_intensity_at_location_time(self):
        """Test infrastructure intensity at location and time."""
        location = (40.1, -74.1)  # Close to impact
        time_hours = 12.0
        
        results = self.infrastructure.get_intensity_at_location_time(
            self.sample_impact_data, location, time_hours
        )
        
        # Check structure
        self.assertIn('damage_level', results)
        self.assertIn('infrastructure_damage_fraction', results)
        self.assertIn('power_outage', results)
        
        # Check damage level is valid
        valid_levels = ['none', 'light', 'moderate', 'severe']
        self.assertIn(results['damage_level'], valid_levels)
        
        # Check damage fraction is valid
        self.assertGreaterEqual(results['infrastructure_damage_fraction'], 0)
        self.assertLessEqual(results['infrastructure_damage_fraction'], 1)


class TestIntegration(unittest.TestCase):
    """Integration tests using real impact data."""
    
    def test_complete_workflow(self):
        """Test complete workflow from impact to environmental effects."""
        # Generate realistic impact data
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=200,
            velocity_ms=20000,
            impact_angle_degrees=45.0,
            include_atmospheric_entry=True
        )
        
        # Add impact location
        impact_data['impact_location'] = {'lat': 40.7128, 'lon': -74.0060}
        
        # Calculate environmental effects
        processor = EnvironmentalEffectsProcessor()
        
        results = processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 48),
            time_resolution_hours=2.0
        )
        
        # Verify results structure
        self.assertIn('time_hours', results)
        self.assertIn('effects', results)
        
        # Verify all effect types are present
        expected_effects = ['seismic', 'atmospheric', 'thermal', 'debris', 'infrastructure']
        for effect_type in expected_effects:
            self.assertIn(effect_type, results['effects'])
        
        # Test point effects
        point_results = processor.get_effect_at_time(
            impact_data,
            time_hours=6.0,
            location=(41.0, -73.0)
        )
        
        self.assertIn('effects', point_results)
        self.assertEqual(point_results['time_hours'], 6.0)


if __name__ == '__main__':
    unittest.main()