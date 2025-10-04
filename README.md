# MeteorMadness: Asteroid Impact Simulator & Visualizer

MeteorMadness is a comprehensive Python-based application designed to simulate and visualize the potential effects of asteroid impacts on Earth. It combines real-world data from NASA and other scientific sources with a sophisticated physics engine to model everything from the initial impact energy to the subsequent environmental and societal consequences.

## Features

- **Real-Time Asteroid Data**: Integrates with the NASA Near-Earth Object (NEO) API to fetch data on real asteroids.
- **Detailed Impact Analysis**: Provides detailed context for any impact location on Earth, including:
  - **Terrain & Elevation**: Fetches elevation data to determine if an impact occurs on land or in the ocean, classifying the terrain from coastal lowlands to mountains.
  - **Population Density**: Estimates the population within a given radius of the impact to model potential human impact.
- **Physics-Based Modeling**: A core physics engine that calculates:
  - Impact energy and crater size.
  - Seismic effects, correlated with historical earthquake data.
  - Potential for tsunamis based on ocean depth.
- **Historical Data for Calibration**: Utilizes a rich set of reference data for model validation and comparison, including:
  - A database of significant historical earthquakes (M6.0+).
  - A catalog of well-documented historical impact events (e.g., Tunguska, Chicxulub).
  - A list of confirmed impact craters on Earth.
- **2D Visualization**: A browser-based 2D visualizer to plot impact scenarios and their effects on a world map.
- **REST API**: A Flask-based API to programmatically access asteroid and impact data.
- **Game Mode**: An interactive game mode where players can simulate planetary defense, launch asteroids, and progress through levels based on their score.

## Project Structure

The project is organized into several key directories:

- `/api`: Contains the Flask Blueprints that define the application's REST API endpoints.
- `/clients`: Houses the API clients used to communicate with external services (NASA, Open-Elevation, etc.).
- `/config`: Stores project-wide configuration and physical constants.
- `/data`: Contains all raw and processed reference data used by the application.
- `/physics`: The core physics engine for calculating impact effects.
- `/scripts`: A collection of utility scripts for downloading and processing reference data.
- `/services`: The business logic layer that orchestrates data fetching, processing, and analysis.
  - `/services/game`: Contains the core logic for the interactive game mode, including session management, defense simulation, and player progression.
- `/2dvisualisation`: The frontend code for the 2D impact visualizer.

## Getting Started

### Prerequisites

- Python 3.10+
- A virtual environment tool (e.g., `venv`)

### Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd MeteorMadness
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    *On Windows, use `venv\Scripts\activate`*

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**:
    Create a `.env` file in the project root. You will need to add your NASA API key to this file:
    ```
    NASA_API_KEY=your_nasa_api_key_here
    ```

5.  **Download Reference Data**:
    Run the one-time scripts to download the necessary reference datasets:
    ```bash
    python scripts/download_earthquake_data.py
    # Note: The population data script may be blocked; follow instructions in the script to manually download if needed.
    # python scripts/download_population_data.py 
    ```

### Running the Application

1.  **Start the Flask Server**:
    ```bash
    python app.py
    ```
    The API will be available at `http://127.0.0.1:5000`.

2.  **Launch the 2D Visualizer**:
    Open the `2dvisualisation/impact-visualizer-2d.html` file in your web browser.

## API Endpoints

### Simulation Endpoints

- `GET /api/asteroids`: Returns a list of cached asteroids.
- `GET /api/asteroids/current`: Returns asteroids approaching Earth in the next 7 days from the live NASA API.
- `GET /api/asteroids/<string:asteroid_id>`: Gets detailed data for a specific asteroid.
- `GET /api/elevation?lat=<lat>&lng=<lng>`: Provides detailed elevation and terrain context for a given coordinate.

### Game Mode Endpoints

- `POST /api/game/start`: Initializes a new game session and returns a unique `session_id`.
- `GET /api/game/asteroids-info`: Returns a list of the specific NASA asteroids used in the game's progression levels.
- `GET /api/game/<session_id>/stats`: Retrieves the current player statistics for a given session.
- `GET /api/game/<session_id>/unlocks`: Shows the asteroids and parameters the player has unlocked based on their level.
- `POST /api/game/<session_id>/launch`: Launches an asteroid. The planetary defense system will attempt to intercept it.
- `POST /api/game/<session_id>/impact`: If an asteroid is not deflected, this endpoint calculates the impact results and updates the player's score.

---
*This project is for educational and demonstrative purposes.*
