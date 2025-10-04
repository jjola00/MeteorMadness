"""
Sample environmental scenarios for development and testing.
Provides realistic asteroid impact scenarios with pre-calculated environmental effects.
"""

import json
from typing import Dict, Any, List
import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.impact import ImpactPhysics
from physics.environmental_effects import EnvironmentalEffectsProcessor


class SampleScenarios:
    """Generates and manages sample environmental scenarios."""
    
    def __init__(self):
        """Initialize the sample scenarios generator."""
        self.processor = EnvironmentalEffectsProcessor()
    
    def generate_tunguska_scenario(self) -> Dict[str, Any]:
        """
        Generate a Tunguska-like scenario (1908 event).
        50-60m asteroid, airburst at ~8km altitude.
        """
        # Impact parameters based on Tunguska research
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=50,
            velocity_ms=15000,
            impact_angle_degrees=30.0,  # Shallow angle
            include_atmospheric_entry=True
        )
        
        # Tunguska location (Siberia)
        impact_data['impact_location'] = {'lat': 60.8864, 'lon': 101.8961}
        
        # Calculate environmental effects (first 72 hours)
        temporal_effects = self.processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 72),
            time_resolution_hours=1.0
        )
        
        return {
            'name': 'Tunguska-like Event',
            'description': 'Small asteroid airburst similar to 1908 Tunguska event',
            'historical_reference': '1908 Tunguska event, Siberia',
            'impact_data': impact_data,
            'environmental_effects': temporal_effects,
            'key_characteristics': [
                'Airburst at ~8km altitude',
                'Flattened ~2000 km² of forest',
                'Seismic waves detected globally',
                'Atmospheric effects lasted days'
            ]
        }
    
    def generate_chelyabinsk_scenario(self) -> Dict[str, Any]:
        """
        Generate a Chelyabinsk-like scenario (2013 event).
        20m asteroid, airburst at ~30km altitude.
        """
        # Impact parameters based on Chelyabinsk research
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=20,
            velocity_ms=18000,
            impact_angle_degrees=18.0,  # Very shallow angle
            include_atmospheric_entry=True
        )
        
        # Chelyabinsk location (Russia)
        impact_data['impact_location'] = {'lat': 55.1644, 'lon': 61.4368}
        
        # Calculate environmental effects (first 24 hours)
        temporal_effects = self.processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 24),
            time_resolution_hours=0.5
        )
        
        return {
            'name': 'Chelyabinsk-like Event',
            'description': 'Small asteroid airburst similar to 2013 Chelyabinsk event',
            'historical_reference': '2013 Chelyabinsk meteor, Russia',
            'impact_data': impact_data,
            'environmental_effects': temporal_effects,
            'key_characteristics': [
                'Airburst at ~30km altitude',
                'Shockwave broke windows across city',
                'Over 1000 people injured by glass',
                'Bright flash visible for hundreds of km'
            ]
        }
    
    def generate_regional_impact_scenario(self) -> Dict[str, Any]:
        """
        Generate a regional impact scenario.
        200m asteroid, ground impact.
        """
        # Larger asteroid with ground impact
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=200,
            velocity_ms=20000,
            impact_angle_degrees=45.0,
            include_atmospheric_entry=True
        )
        
        # Hypothetical impact in Atlantic Ocean
        impact_data['impact_location'] = {'lat': 35.0, 'lon': -40.0}
        
        # Calculate environmental effects (first week)
        temporal_effects = self.processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 168),
            time_resolution_hours=2.0
        )
        
        return {
            'name': 'Regional Impact Event',
            'description': 'Medium-sized asteroid with regional consequences',
            'historical_reference': 'Hypothetical scenario based on impact models',
            'impact_data': impact_data,
            'environmental_effects': temporal_effects,
            'key_characteristics': [
                'Ground impact creates large crater',
                'Regional seismic effects',
                'Significant atmospheric disturbance',
                'Potential tsunami if ocean impact'
            ]
        }
    
    def generate_civilization_threat_scenario(self) -> Dict[str, Any]:
        """
        Generate a civilization-threatening scenario.
        1km asteroid, ground impact.
        """
        # Large asteroid - civilization threat
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=1000,
            velocity_ms=25000,
            impact_angle_degrees=60.0,
            include_atmospheric_entry=True
        )
        
        # Hypothetical impact on land
        impact_data['impact_location'] = {'lat': 40.0, 'lon': -100.0}  # Central US
        
        # Calculate environmental effects (first month)
        temporal_effects = self.processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 720),  # 30 days
            time_resolution_hours=6.0
        )
        
        return {
            'name': 'Civilization Threat Event',
            'description': 'Large asteroid impact with global consequences',
            'historical_reference': 'Similar to Chicxulub impact (66 million years ago)',
            'impact_data': impact_data,
            'environmental_effects': temporal_effects,
            'key_characteristics': [
                'Massive crater formation',
                'Global seismic effects',
                'Atmospheric dust injection',
                'Potential climate change',
                'Mass extinction potential'
            ]
        }
    
    def generate_ocean_impact_scenario(self) -> Dict[str, Any]:
        """
        Generate an ocean impact scenario with tsunami effects.
        500m asteroid, ocean impact.
        """
        # Medium-large asteroid in ocean
        impact_data = ImpactPhysics.complete_impact_analysis(
            diameter_m=500,
            velocity_ms=22000,
            impact_angle_degrees=45.0,
            include_atmospheric_entry=True
        )
        
        # Pacific Ocean impact
        impact_data['impact_location'] = {'lat': 20.0, 'lon': -150.0}
        
        # Calculate environmental effects (first 48 hours for tsunami propagation)
        temporal_effects = self.processor.calculate_temporal_effects(
            impact_data,
            time_range_hours=(0, 48),
            time_resolution_hours=1.0
        )
        
        return {
            'name': 'Ocean Impact Event',
            'description': 'Large asteroid impact in ocean with tsunami generation',
            'historical_reference': 'Hypothetical deep ocean impact scenario',
            'impact_data': impact_data,
            'environmental_effects': temporal_effects,
            'key_characteristics': [
                'Underwater crater formation',
                'Massive tsunami generation',
                'Trans-oceanic wave propagation',
                'Coastal devastation',
                'Atmospheric water vapor injection'
            ]
        }
    
    def get_all_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Get all available sample scenarios."""
        scenarios = {
            'tunguska': self.generate_tunguska_scenario(),
            'chelyabinsk': self.generate_chelyabinsk_scenario(),
            'regional': self.generate_regional_impact_scenario(),
            'civilization_threat': self.generate_civilization_threat_scenario(),
            'ocean_impact': self.generate_ocean_impact_scenario()
        }
        
        return scenarios
    
    def get_scenario_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of all available scenarios."""
        scenarios = self.get_all_scenarios()
        
        summary = []
        for key, scenario in scenarios.items():
            impact_data = scenario['impact_data']
            initial_params = impact_data.get('initial_parameters', {})
            
            summary.append({
                'id': key,
                'name': scenario['name'],
                'description': scenario['description'],
                'diameter_m': initial_params.get('diameter_m', 0),
                'velocity_ms': initial_params.get('velocity_ms', 0),
                'impact_location': impact_data.get('impact_location', {}),
                'energy_tnt_kt': impact_data.get('impact_energy', {}).get('effective_energy_tnt_kt', 0),
                'crater_diameter_km': impact_data.get('crater', {}).get('diameter_km', 0)
            })
        
        return summary
    
    def save_scenarios_to_json(self, filepath: str = None) -> str:
        """
        Save all scenarios to a JSON file for use by frontend.
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path to saved file
        """
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__),
                'sample_scenarios.json'
            )
        
        scenarios = self.get_all_scenarios()
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            else:
                return obj
        
        scenarios_json = convert_numpy(scenarios)
        
        with open(filepath, 'w') as f:
            json.dump(scenarios_json, f, indent=2)
        
        return filepath


def generate_sample_data():
    """Generate and save sample scenario data."""
    generator = SampleScenarios()
    
    # Generate all scenarios
    scenarios = generator.get_all_scenarios()
    
    # Save to JSON file
    filepath = generator.save_scenarios_to_json()
    print(f"Sample scenarios saved to: {filepath}")
    
    # Print summary
    summary = generator.get_scenario_summary()
    print("\nGenerated scenarios:")
    for scenario in summary:
        print(f"- {scenario['name']}: {scenario['diameter_m']}m asteroid, "
              f"{scenario['energy_tnt_kt']:.1f} kt TNT equivalent")
    
    return scenarios


if __name__ == '__main__':
    generate_sample_data()