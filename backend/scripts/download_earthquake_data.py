"""
This script performs a one-time download of historical earthquake data from the
USGS API. This data serves as a reference for physics calculations, allowing
us to model the seismic effects of an asteroid impact by correlating impact
energy with historical earthquake magnitudes and their observed effects.

The downloaded data is intended to be committed to the repository.
"""
import requests
import pandas as pd
import json
import os
from typing import Dict

# The base URL for the USGS Earthquake API
USGS_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "reference_data")

def download_significant_earthquakes() -> pd.DataFrame:
    """
    Downloads significant historical earthquake data from the USGS.

    This function queries the USGS API for earthquakes with a magnitude of 6.0
    or greater, dating back to 1974. It saves the data to a CSV file and
    prints a summary.

    Returns:
        A pandas DataFrame containing the earthquake data, or an empty
        DataFrame if the download fails.
    """
    params = {
        "format": "csv",
        "starttime": "1974-01-01",
        "minmagnitude": 6.0,
        "orderby": "time"
    }
    
    print("Downloading significant earthquake data from USGS (since 1974, M6.0+)...")
    
    try:
        response = requests.get(USGS_API_URL, params=params, timeout=30)
        response.raise_for_status()

        # Save the raw data to a CSV file
        csv_path = os.path.join(DATA_DIR, "earthquakes_historical.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Load into pandas DataFrame
        df = pd.read_csv(csv_path)
        
        # Print summary
        print(f"✓ Successfully downloaded and saved {len(df)} earthquakes to {csv_path}")
        print("\n--- Data Summary ---")
        print(f"Magnitude Range: {df['mag'].min():.1f} - {df['mag'].max():.1f}")
        
        # Display 5 largest magnitude earthquakes as "deadliest" proxy
        print("\nTop 5 Largest Magnitude Earthquakes:")
        print(df.nlargest(5, 'mag')[['time', 'mag', 'place']])
        print("--------------------")

        return df

    except requests.exceptions.RequestException as e:
        print(f"⚠ Error downloading earthquake data: {e}")
        return pd.DataFrame()

def create_magnitude_effects_table() -> Dict:
    """
    Creates a lookup table for estimated earthquake effects by magnitude.

    This function defines bins for earthquake magnitudes and assigns estimated
    radii for felt area and damage, along with a qualitative description.
    This table is used by the physics model to estimate impact consequences.

    Returns:
        A dictionary containing the magnitude effects lookup table.
    """
    print("\nCreating magnitude effects lookup table...")
    
    # This is a simplified model. In a real scenario, these values would be
    # derived from complex geological and structural engineering models.
    effects_table = {
        "6.0-6.5": {
            "description": "Strong Earthquake",
            "felt_radius_km": 250,
            "damage_radius_km": 50
        },
        "6.5-7.0": {
            "description": "Major Earthquake",
            "felt_radius_km": 400,
            "damage_radius_km": 100
        },
        "7.0-7.5": {
            "description": "Major Earthquake",
            "felt_radius_km": 600,
            "damage_radius_km": 150
        },
        "7.5-8.0": {
            "description": "Great Earthquake",
            "felt_radius_km": 800,
            "damage_radius_km": 250
        },
        "8.0+": {
            "description": "Great Earthquake",
            "felt_radius_km": 1200,
            "damage_radius_km": 400
        }
    }
    
    json_path = os.path.join(DATA_DIR, "magnitude_effects.json")
    with open(json_path, 'w') as f:
        json.dump(effects_table, f, indent=2)
        
    print(f"✓ Successfully created and saved magnitude effects table to {json_path}")
    
    return effects_table

def main():
    """
    Main function to orchestrate the download and processing of earthquake data.
    """
    print("--- Starting Earthquake Data Setup ---")
    
    # Ensure the reference data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Execute the main steps
    df = download_significant_earthquakes()
    
    if not df.empty:
        create_magnitude_effects_table()
        print("\n--- Earthquake Data Setup Complete ---")
    else:
        print("\n--- Earthquake Data Setup Failed ---")

if __name__ == "__main__":
    main()
