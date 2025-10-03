from datetime import datetime, timedelta
import json
import os
import sys
from dotenv import load_dotenv


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print("Loaded .env file successfully.")
else:
    print("Warning: .env file not found.")


from services.asteroid_service import get_complete_asteroid_data
from clients.nasa_api import nasa_api_client

#ok guys, this is cache asteroid data script in case we decide go cache first for the demo and the fallback real api call!

def cache_asteroids():
    """
    Fetches and caches asteroid data for a fixed list of 10 famous asteroids.
    
    Returns:
        List of cached asteroid dictionaries.
    """
    # Famous near-Earth asteroids
    famous_asteroid_ids = [
        '2000433', '2099942', '2101955', '3542519', '2000001',
        '2000004', '2000010', '2000016', '2000021', '2000031'
    ]
    
    # Fetch complete data for all asteroids
    cached_asteroids = []
    
    for asteroid_id in famous_asteroid_ids:
        print(f"Fetching asteroid {asteroid_id}...")
        
        complete_data = get_complete_asteroid_data(asteroid_id)
        
        if complete_data:
            print(f"  ✓ Cached: {complete_data.get('name', 'Unknown')}")
            cached_asteroids.append(complete_data)
        else:
            print(f"  ⚠ Warning: Failed to fetch data for asteroid {asteroid_id}")
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to cache file
    cache_file = os.path.join(data_dir, "asteroids_cache.json")
    with open(cache_file, 'w') as f:
        json.dump(cached_asteroids, f, indent=2)
    
    print(f"\n✓ Successfully cached {len(cached_asteroids)} asteroids to {cache_file}")
    
    return cached_asteroids

if __name__ == "__main__":
    cache_asteroids()

