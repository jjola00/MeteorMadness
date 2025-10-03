"""
USGS data integration for geological and geographic data.
Handles topography, seismic zones, and tsunami risk areas.
"""

import requests
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
from typing import Dict, List, Tuple, Optional, Union
import warnings

try:
    from ..utils.conversions import validate_coordinates, EARTH_RADIUS_KM
except ImportError:
    # For direct execution - add project root to path
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    from backend.utils.conversions import validate_coordinates, EARTH_RADIUS_KM


class USGSDataHandler:
    """Handles USGS geological and geographic data integration."""
    
    # USGS API endpoints
    EARTHQUAKE_API = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    TSUNAMI_API = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    
    def __init__(self):
        """Initialize USGS data handler."""
        self.session = requests.Session()
        
        # Simplified geological data (in real implementation, this would come from USGS)
        self._initialize_geological_data()

    def _initialize_geological_data(self):
        """Initialize simplified geological data for demonstration."""
        # Major tectonic plate boundaries (simplified)
        self.plate_boundaries = [
            # Pacific Ring of Fire (simplified points)
            [(40, -125), (50, -130), (60, -140), (55, -160), (45, -170), (35, 140), (25, 120)],
            # Mid-Atlantic Ridge (simplified)
            [(60, -30), (45, -20), (30, -15), (0, -10), (-30, -5), (-50, 0)],
            # Mediterranean-Himalayan belt
            [(35, -10), (40, 20), (35, 40), (30, 60), (35, 80), (25, 90)]
        ]
        
        # Major seismic zones (lat, lon, radius_km, risk_level)
        self.seismic_zones = [
            # California
            (36.0, -120.0, 500, 'high'),
            # Japan
            (36.0, 138.0, 400, 'very_high'),
            # Turkey
            (39.0, 35.0, 300, 'high'),
            # Chile
            (-30.0, -71.0, 600, 'very_high'),
            # Alaska
            (61.0, -150.0, 400, 'high'),
            # Indonesia
            (-2.0, 120.0, 800, 'very_high'),
            # Iran
            (32.0, 53.0, 400, 'high'),
            # Greece
            (39.0, 22.0, 200, 'moderate'),
        ]
        
        # Coastal regions at tsunami risk
        self.tsunami_risk_zones = [
            # Pacific coastlines
            {'region': 'US West Coast', 'bounds': (32, 49, -125, -117), 'risk': 'high'},
            {'region': 'Japan', 'bounds': (30, 46, 129, 146), 'risk': 'very_high'},
            {'region': 'Chile Coast', 'bounds': (-56, -17, -76, -66), 'risk': 'very_high'},
            {'region': 'Alaska Coast', 'bounds': (54, 71, -170, -130), 'risk': 'high'},
            {'region': 'Indonesia', 'bounds': (-11, 6, 95, 141), 'risk': 'very_high'},
            # Atlantic coastlines (lower risk)
            {'region': 'US East Coast', 'bounds': (25, 45, -81, -66), 'risk': 'moderate'},
            {'region': 'Portugal', 'bounds': (37, 42, -10, -6), 'risk': 'moderate'},
        ]

    def get_elevation(self, latitude: float, longitude: float) -> Dict[str, any]:
        """
        Get elevation data for a point (simplified version).
        In real implementation, this would query USGS elevation services.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Dictionary with elevation data
        """
        if not validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates")
        
        # Simplified elevation model based on major geographic features
        # Real implementation would use USGS National Elevation Dataset
        
        elevation_m = 0  # Default sea level
        
        # Major mountain ranges (very simplified)
        mountain_ranges = [
            # Himalayas
            {'center': (28, 84), 'radius_deg': 8, 'max_elevation': 8000},
            # Andes
            {'center': (-15, -70), 'radius_deg': 5, 'max_elevation': 6000},
            # Rocky Mountains
            {'center': (45, -110), 'radius_deg': 8, 'max_elevation': 4000},
            # Alps
            {'center': (46, 8), 'radius_deg': 3, 'max_elevation': 4000},
        ]
        
        for mountain in mountain_ranges:
            center_lat, center_lon = mountain['center']
            distance = np.sqrt((latitude - center_lat)**2 + (longitude - center_lon)**2)
            if distance < mountain['radius_deg']:
                # Gaussian elevation profile
                elevation_m = max(elevation_m, 
                    mountain['max_elevation'] * np.exp(-distance**2 / (mountain['radius_deg']/3)**2))
        
        # Ocean depth (simplified)
        ocean_depth_m = 0
        if self._is_ocean_point(latitude, longitude):
            # Simplified ocean depth model
            # Deep ocean trenches
            trenches = [
                {'center': (11, 142), 'depth': 11000},  # Mariana Trench
                {'center': (-23, -71), 'depth': 8000},  # Peru-Chile Trench
            ]
            
            for trench in trenches:
                center_lat, center_lon = trench['center']
                distance = np.sqrt((latitude - center_lat)**2 + (longitude - center_lon)**2)
                if distance < 5:  # 5 degree radius
                    ocean_depth_m = max(ocean_depth_m, 
                        trench['depth'] * np.exp(-distance**2 / 2**2))
            
            if ocean_depth_m == 0:
                ocean_depth_m = 3800  # Average ocean depth
            
            elevation_m = -ocean_depth_m
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'elevation_m': elevation_m,
            'elevation_ft': elevation_m * 3.28084,
            'is_ocean': elevation_m < 0,
            'ocean_depth_m': abs(elevation_m) if elevation_m < 0 else 0
        }

    def _is_ocean_point(self, latitude: float, longitude: float) -> bool:
        """
        Simple ocean detection (placeholder for real coastline data).
        """
        # Very simplified - just check against major land masses
        land_regions = [
            # North America
            (-170, -50, 15, 75),
            # South America  
            (-85, -30, -60, 15),
            # Europe/Asia
            (-15, 180, 35, 80),
            # Africa
            (-20, 55, -40, 40),
            # Australia
            (110, 160, -45, -10),
        ]
        
        for lon_min, lon_max, lat_min, lat_max in land_regions:
            if lon_min <= longitude <= lon_max and lat_min <= latitude <= lat_max:
                return False
        
        return True

    def get_seismic_risk(self, latitude: float, longitude: float) -> Dict[str, any]:
        """
        Get seismic risk assessment for a location.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Dictionary with seismic risk data
        """
        if not validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates")
        
        # Find nearest seismic zone
        min_distance_km = float('inf')
        nearest_zone = None
        
        for zone_lat, zone_lon, radius_km, risk_level in self.seismic_zones:
            # Great circle distance approximation
            distance_km = self._haversine_distance(latitude, longitude, zone_lat, zone_lon)
            
            if distance_km < radius_km and distance_km < min_distance_km:
                min_distance_km = distance_km
                nearest_zone = {
                    'center_lat': zone_lat,
                    'center_lon': zone_lon,
                    'radius_km': radius_km,
                    'risk_level': risk_level,
                    'distance_km': distance_km
                }
        
        # Calculate risk score
        if nearest_zone:
            # Risk decreases with distance from zone center
            distance_factor = 1 - (nearest_zone['distance_km'] / nearest_zone['radius_km'])
            risk_levels = {'low': 1, 'moderate': 2, 'high': 3, 'very_high': 4}
            base_risk = risk_levels.get(nearest_zone['risk_level'], 1)
            risk_score = base_risk * distance_factor
        else:
            risk_score = 0.1  # Background seismic risk
            nearest_zone = {'risk_level': 'very_low', 'distance_km': float('inf')}
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'seismic_risk_score': max(0, min(4, risk_score)),
            'risk_level': nearest_zone.get('risk_level', 'very_low'),
            'distance_to_zone_km': nearest_zone.get('distance_km', float('inf')),
            'nearest_zone': nearest_zone
        }

    def get_tsunami_risk(self, latitude: float, longitude: float) -> Dict[str, any]:
        """
        Get tsunami risk assessment for a coastal location.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Dictionary with tsunami risk data
        """
        if not validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates")
        
        # Check if location is in a tsunami risk zone
        risk_assessment = {
            'latitude': latitude,
            'longitude': longitude,
            'is_coastal': False,
            'tsunami_risk_level': 'none',
            'risk_score': 0,
            'risk_region': None
        }
        
        for zone in self.tsunami_risk_zones:
            lat_min, lat_max, lon_min, lon_max = zone['bounds']
            
            if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
                risk_assessment.update({
                    'is_coastal': True,
                    'tsunami_risk_level': zone['risk'],
                    'risk_region': zone['region']
                })
                
                # Risk score based on level
                risk_scores = {'low': 1, 'moderate': 2, 'high': 3, 'very_high': 4}
                risk_assessment['risk_score'] = risk_scores.get(zone['risk'], 0)
                break
        
        # Additional risk factors
        elevation_data = self.get_elevation(latitude, longitude)
        if elevation_data['is_ocean']:
            risk_assessment['tsunami_risk_level'] = 'none'  # Ocean impacts generate tsunamis
            risk_assessment['risk_score'] = 0
        elif elevation_data['elevation_m'] > 100:
            # High elevation reduces tsunami risk
            risk_assessment['risk_score'] *= 0.5
        
        return risk_assessment

    def get_regional_geology(self, latitude: float, longitude: float, radius_km: float = 100) -> Dict[str, any]:
        """
        Get regional geological assessment around a point.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius for regional assessment
            
        Returns:
            Dictionary with regional geological data
        """
        if not validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates")
        
        # Sample points in the region
        n_samples = 20
        sample_points = []
        
        # Generate sample points in a circle
        for i in range(n_samples):
            angle = 2 * np.pi * i / n_samples
            # Convert radius to degrees (approximate)
            radius_deg = radius_km / 111.0  # Rough km to degree conversion
            
            sample_lat = latitude + radius_deg * np.cos(angle)
            sample_lon = longitude + radius_deg * np.sin(angle)
            
            if validate_coordinates(sample_lat, sample_lon):
                elevation = self.get_elevation(sample_lat, sample_lon)
                seismic = self.get_seismic_risk(sample_lat, sample_lon)
                tsunami = self.get_tsunami_risk(sample_lat, sample_lon)
                
                sample_points.append({
                    'latitude': sample_lat,
                    'longitude': sample_lon,
                    'elevation_m': elevation['elevation_m'],
                    'seismic_risk': seismic['seismic_risk_score'],
                    'tsunami_risk': tsunami['risk_score']
                })
        
        if not sample_points:
            return {'error': 'No valid sample points in region'}
        
        # Calculate regional statistics
        elevations = [p['elevation_m'] for p in sample_points]
        seismic_risks = [p['seismic_risk'] for p in sample_points]
        tsunami_risks = [p['tsunami_risk'] for p in sample_points]
        
        return {
            'center_latitude': latitude,
            'center_longitude': longitude,
            'radius_km': radius_km,
            'sample_count': len(sample_points),
            'elevation_stats': {
                'min_m': min(elevations),
                'max_m': max(elevations),
                'mean_m': np.mean(elevations),
                'std_m': np.std(elevations)
            },
            'seismic_risk_stats': {
                'min': min(seismic_risks),
                'max': max(seismic_risks),
                'mean': np.mean(seismic_risks),
                'std': np.std(seismic_risks)
            },
            'tsunami_risk_stats': {
                'min': min(tsunami_risks),
                'max': max(tsunami_risks),
                'mean': np.mean(tsunami_risks),
                'std': np.std(tsunami_risks)
            },
            'ocean_fraction': sum(1 for e in elevations if e < 0) / len(elevations),
            'sample_points': sample_points
        }

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance using Haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return EARTH_RADIUS_KM * c

    def get_impact_site_assessment(self, latitude: float, longitude: float) -> Dict[str, any]:
        """
        Complete geological assessment for an impact site.
        
        Args:
            latitude: Impact latitude
            longitude: Impact longitude
            
        Returns:
            Complete site assessment
        """
        assessment = {
            'impact_coordinates': (latitude, longitude),
            'coordinate_validation': validate_coordinates(latitude, longitude)
        }
        
        if not assessment['coordinate_validation']:
            assessment['error'] = 'Invalid coordinates'
            return assessment
        
        # Get all geological data
        assessment['elevation'] = self.get_elevation(latitude, longitude)
        assessment['seismic_risk'] = self.get_seismic_risk(latitude, longitude)
        assessment['tsunami_risk'] = self.get_tsunami_risk(latitude, longitude)
        assessment['regional_geology'] = self.get_regional_geology(latitude, longitude, 200)
        
        # Summary assessment
        impact_type = 'ocean' if assessment['elevation']['is_ocean'] else 'land'
        
        assessment['impact_summary'] = {
            'impact_type': impact_type,
            'elevation_m': assessment['elevation']['elevation_m'],
            'seismic_risk_level': assessment['seismic_risk']['risk_level'],
            'tsunami_generation_potential': 'high' if impact_type == 'ocean' else 'none',
            'local_tsunami_risk': assessment['tsunami_risk']['tsunami_risk_level'],
            'geological_complexity': 'complex' if assessment['regional_geology']['elevation_stats']['std_m'] > 1000 else 'simple'
        }
        
        return assessment


def run_usgs_test():
    """Test the USGS data integration."""
    print("🧪 Testing USGS Data Integration")
    print("=" * 40)
    
    # Initialize USGS handler
    usgs = USGSDataHandler()
    
    # Test locations
    test_locations = [
        (37.7749, -122.4194),  # San Francisco (seismic risk)
        (35.6762, 139.6503),   # Tokyo (tsunami risk)
        (40.7128, -74.0060),   # New York (low risk)
        (27.9881, 86.9250),    # Mount Everest (high elevation)
        (0, -160),             # Pacific Ocean
    ]
    
    location_names = ['San Francisco', 'Tokyo', 'New York', 'Mt. Everest', 'Pacific Ocean']
    
    for i, (lat, lon) in enumerate(test_locations):
        print(f"\n{i+1}. Testing {location_names[i]} ({lat}, {lon}):")
        
        try:
            # Get elevation
            elevation = usgs.get_elevation(lat, lon)
            print(f"   Elevation: {elevation['elevation_m']:.0f} m")
            
            # Get seismic risk
            seismic = usgs.get_seismic_risk(lat, lon)
            print(f"   Seismic risk: {seismic['risk_level']} (score: {seismic['seismic_risk_score']:.1f})")
            
            # Get tsunami risk
            tsunami = usgs.get_tsunami_risk(lat, lon)
            print(f"   Tsunami risk: {tsunami['tsunami_risk_level']} (score: {tsunami['risk_score']:.1f})")
            
            # Regional assessment for first location
            if i == 0:
                print(f"\n   Regional geology (100 km radius):")
                regional = usgs.get_regional_geology(lat, lon, 100)
                print(f"     Elevation range: {regional['elevation_stats']['min_m']:.0f} to {regional['elevation_stats']['max_m']:.0f} m")
                print(f"     Ocean fraction: {regional['ocean_fraction']:.1%}")
                print(f"     Avg seismic risk: {regional['seismic_risk_stats']['mean']:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 USGS data test completed!")


if __name__ == "__main__":
    run_usgs_test()
