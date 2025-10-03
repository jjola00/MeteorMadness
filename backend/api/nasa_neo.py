"""
NASA Near-Earth Object (NEO) API integration.
Fetches real-time asteroid data for impact simulation.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import time

try:
    from ..utils.conversions import UnitConverter, estimate_asteroid_mass
except ImportError:
    # For direct execution - add project root to path
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    from backend.utils.conversions import UnitConverter, estimate_asteroid_mass


class NASANeoAPI:
    """NASA Near-Earth Object API client."""
    
    # API endpoints
    BASE_URL = "https://api.nasa.gov/neo/rest/v1"
    FEED_URL = f"{BASE_URL}/feed"
    NEO_LOOKUP_URL = f"{BASE_URL}/neo"
    STATS_URL = f"{BASE_URL}/stats"
    
    # Default API key (demo key with limited requests)
    DEFAULT_API_KEY = "DEMO_KEY"
    
    def __init__(self, api_key: str = None):
        """
        Initialize NASA NEO API client.
        
        Args:
            api_key: NASA API key (if None, tries to load from environment)
        """
        self.api_key = api_key or os.getenv('NASA_API_KEY', self.DEFAULT_API_KEY)
        self.session = requests.Session()
        self.session.params.update({'api_key': self.api_key})
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max

    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Make rate-limited API request.
        
        Args:
            url: API endpoint URL
            params: Additional parameters
            
        Returns:
            JSON response data
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self.request_count += 1
            self.last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"NASA API request failed: {e}")

    def get_neo_feed(
        self, 
        start_date: str = None, 
        end_date: str = None,
        detailed: bool = True
    ) -> Dict[str, any]:
        """
        Get NEO feed for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            detailed: Include detailed orbital data
            
        Returns:
            Dictionary with NEO feed data
        """
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if end_date is None:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'detailed': detailed
        }
        
        return self._make_request(self.FEED_URL, params)

    def get_neo_by_id(self, neo_id: str) -> Dict[str, any]:
        """
        Get detailed information for a specific NEO.
        
        Args:
            neo_id: NEO reference ID
            
        Returns:
            Dictionary with detailed NEO data
        """
        url = f"{self.NEO_LOOKUP_URL}/{neo_id}"
        return self._make_request(url)

    def search_neos(
        self,
        diameter_min_km: float = None,
        diameter_max_km: float = None,
        is_potentially_hazardous: bool = None,
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """
        Search for NEOs with specific criteria.
        Note: This uses the feed endpoint and filters results.
        
        Args:
            diameter_min_km: Minimum diameter in km
            diameter_max_km: Maximum diameter in km
            is_potentially_hazardous: Filter for potentially hazardous asteroids
            limit: Maximum number of results
            
        Returns:
            List of matching NEO dictionaries
        """
        # Get recent NEO data
        feed_data = self.get_neo_feed()
        
        all_neos = []
        for date_str, neos in feed_data.get('near_earth_objects', {}).items():
            all_neos.extend(neos)
        
        # Apply filters
        filtered_neos = []
        for neo in all_neos:
            # Diameter filter
            if diameter_min_km is not None or diameter_max_km is not None:
                diameter_km = neo.get('estimated_diameter', {}).get('kilometers', {})
                if diameter_km:
                    avg_diameter = (diameter_km.get('estimated_diameter_min', 0) + 
                                  diameter_km.get('estimated_diameter_max', 0)) / 2
                    
                    if diameter_min_km is not None and avg_diameter < diameter_min_km:
                        continue
                    if diameter_max_km is not None and avg_diameter > diameter_max_km:
                        continue
            
            # Hazardous filter
            if is_potentially_hazardous is not None:
                if neo.get('is_potentially_hazardous_asteroid') != is_potentially_hazardous:
                    continue
            
            filtered_neos.append(neo)
            
            if len(filtered_neos) >= limit:
                break
        
        return filtered_neos

    def parse_neo_data(self, neo_data: Dict[str, any]) -> Dict[str, any]:
        """
        Parse and standardize NEO data from API response.
        
        Args:
            neo_data: Raw NEO data from API
            
        Returns:
            Standardized NEO parameters
        """
        # Basic information
        parsed = {
            'id': neo_data.get('id'),
            'name': neo_data.get('name'),
            'designation': neo_data.get('designation'),
            'is_potentially_hazardous': neo_data.get('is_potentially_hazardous_asteroid', False),
            'absolute_magnitude': neo_data.get('absolute_magnitude_h')
        }
        
        # Diameter estimates
        diameter_data = neo_data.get('estimated_diameter', {})
        if 'kilometers' in diameter_data:
            km_data = diameter_data['kilometers']
            parsed['diameter_min_km'] = km_data.get('estimated_diameter_min')
            parsed['diameter_max_km'] = km_data.get('estimated_diameter_max')
            parsed['diameter_avg_km'] = (
                (km_data.get('estimated_diameter_min', 0) + 
                 km_data.get('estimated_diameter_max', 0)) / 2
            )
            parsed['diameter_avg_m'] = parsed['diameter_avg_km'] * 1000
        
        # Mass estimate (using average diameter)
        if parsed.get('diameter_avg_m'):
            parsed['estimated_mass_kg'] = estimate_asteroid_mass(parsed['diameter_avg_m'])
        
        # Close approach data
        close_approaches = neo_data.get('close_approach_data', [])
        if close_approaches:
            # Use the closest approach
            closest = min(close_approaches, 
                         key=lambda x: float(x.get('miss_distance', {}).get('kilometers', float('inf'))))
            
            parsed['close_approach'] = {
                'date': closest.get('close_approach_date'),
                'velocity_kms': float(closest.get('relative_velocity', {}).get('kilometers_per_second', 0)),
                'velocity_ms': float(closest.get('relative_velocity', {}).get('kilometers_per_second', 0)) * 1000,
                'miss_distance_km': float(closest.get('miss_distance', {}).get('kilometers', 0)),
                'miss_distance_au': float(closest.get('miss_distance', {}).get('astronomical', 0)),
                'miss_distance_lunar': float(closest.get('miss_distance', {}).get('lunar', 0)),
                'orbiting_body': closest.get('orbiting_body')
            }
        
        # Orbital elements (if available)
        orbital_data = neo_data.get('orbital_data', {})
        if orbital_data:
            parsed['orbital_elements'] = {
                'semi_major_axis_au': orbital_data.get('semi_major_axis'),
                'eccentricity': orbital_data.get('eccentricity'),
                'inclination_deg': orbital_data.get('inclination'),
                'ascending_node_longitude_deg': orbital_data.get('ascending_node_longitude'),
                'perihelion_argument_deg': orbital_data.get('perihelion_argument'),
                'mean_anomaly_deg': orbital_data.get('mean_anomaly'),
                'orbital_period_days': orbital_data.get('orbital_period'),
                'orbital_period_years': orbital_data.get('orbital_period') / 365.25 if orbital_data.get('orbital_period') else None,
                'perihelion_distance_au': orbital_data.get('perihelion_distance'),
                'aphelion_distance_au': orbital_data.get('aphelion_distance')
            }
        
        return parsed

    def get_impact_scenarios(self, count: int = 5) -> List[Dict[str, any]]:
        """
        Get realistic impact scenarios based on real NEO data.
        
        Args:
            count: Number of scenarios to generate
            
        Returns:
            List of impact scenario dictionaries
        """
        # Get potentially hazardous asteroids
        hazardous_neos = self.search_neos(
            is_potentially_hazardous=True,
            limit=count * 2  # Get extra to filter
        )
        
        scenarios = []
        for neo in hazardous_neos[:count]:
            parsed = self.parse_neo_data(neo)
            
            # Create impact scenario
            scenario = {
                'name': parsed.get('name', 'Unknown NEO'),
                'id': parsed.get('id'),
                'asteroid_data': parsed,
                'impact_parameters': {
                    'diameter_m': parsed.get('diameter_avg_m', 1000),
                    'mass_kg': parsed.get('estimated_mass_kg', estimate_asteroid_mass(1000)),
                    'velocity_ms': parsed.get('close_approach', {}).get('velocity_ms', 20000),
                    'impact_angle_deg': 45.0,  # Typical impact angle
                    'impact_probability': 0.001  # Very low for real NEOs
                }
            }
            
            # Add realistic impact coordinates (random)
            import random
            scenario['impact_coordinates'] = {
                'latitude': random.uniform(-60, 60),  # Avoid polar regions
                'longitude': random.uniform(-180, 180)
            }
            
            scenarios.append(scenario)
        
        return scenarios

    def get_neo_statistics(self) -> Dict[str, any]:
        """
        Get NEO population statistics from NASA.
        
        Returns:
            Dictionary with NEO statistics
        """
        return self._make_request(self.STATS_URL)


def run_nasa_api_test():
    """Test the NASA NEO API integration."""
    print("🧪 Testing NASA NEO API Integration")
    print("=" * 40)
    
    # Initialize API client
    api = NASANeoAPI()
    print(f"Using API key: {api.api_key[:8]}...")
    print()
    
    try:
        # Test 1: Get NEO feed
        print("1. Getting NEO feed for next 7 days...")
        feed = api.get_neo_feed()
        neo_count = feed.get('element_count', 0)
        print(f"   Found {neo_count} NEOs in the feed")
        
        # Test 2: Parse some NEO data
        if neo_count > 0:
            print("\n2. Parsing NEO data...")
            sample_neos = []
            for date_str, neos in feed.get('near_earth_objects', {}).items():
                sample_neos.extend(neos[:2])  # Get first 2 from each day
                if len(sample_neos) >= 3:
                    break
            
            for i, neo in enumerate(sample_neos[:3]):
                parsed = api.parse_neo_data(neo)
                print(f"   NEO {i+1}: {parsed.get('name')}")
                print(f"     Diameter: {parsed.get('diameter_avg_km', 'Unknown'):.3f} km")
                print(f"     Mass: {parsed.get('estimated_mass_kg', 0):.2e} kg")
                if parsed.get('close_approach'):
                    ca = parsed['close_approach']
                    print(f"     Approach: {ca.get('date')} at {ca.get('velocity_kms'):.1f} km/s")
        
        # Test 3: Search for potentially hazardous asteroids
        print("\n3. Searching for potentially hazardous asteroids...")
        hazardous = api.search_neos(is_potentially_hazardous=True, limit=3)
        print(f"   Found {len(hazardous)} potentially hazardous asteroids")
        
        for i, neo in enumerate(hazardous):
            parsed = api.parse_neo_data(neo)
            print(f"   PHA {i+1}: {parsed.get('name')}")
            print(f"     Diameter: {parsed.get('diameter_avg_km', 'Unknown'):.3f} km")
        
        # Test 4: Get statistics
        print("\n4. Getting NEO population statistics...")
        stats = api.get_neo_statistics()
        if 'near_earth_object_count' in stats:
            print(f"   Total known NEOs: {stats['near_earth_object_count']}")
        
        print(f"\n   Total API requests made: {api.request_count}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   This might be due to rate limiting or network issues")
    
    print("\n🎉 NASA API test completed!")


if __name__ == "__main__":
    run_nasa_api_test()
