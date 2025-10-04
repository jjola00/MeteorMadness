"""
Physical constants and configuration values foreroid impact calculations.
All values sourced from peer-reviewed literature and established models.
"""

# Physical Constants (SI units)
GRAVITATIONAL_CONSTANT = 6.67430e-11  # m^3 kg^-1 s^-2 (CODATA 2018)
EARTH_MASS_KG = 5.972e24  # kg
EARTH_RADIUS_M = 6.371e6  # m
EARTH_RADIUS_KM = 6371.0  # km
EARTH_SURFACE_GRAVITY = 9.80665  # m/s^2
ESCAPE_VELOCITY_EARTH_MS = 11180.0  # m/s

# Astronomical Constants
AU_M = 1.495978707e11  # m (astronomical unit)
GM_SUN = 1.32712440018e20  # m^3/s^2 (gravitational parameter of Sun)
GM_EARTH = 3.986004418e14  # m^3/s^2 (gravitational parameter of Earth)

# Asteroid Properties
DEFAULT_ASTEROID_DENSITY = 3000.0  # kg/m^3 (typical stony asteroid)
ASTEROID_DENSITY_RANGES = {
    'stony': (2500.0, 3500.0),      # S-type asteroids
    'metallic': (7000.0, 8000.0),   # M-type asteroids  
    'carbonaceous': (1500.0, 2500.0) # C-type asteroids
}

# Energy Conversion Factors
TNT_ENERGY_PER_KG = 4.184e6  # J/kg (energy density of TNT)
HIROSHIMA_EQUIVALENT_J = 6.3e13  # J (15 kilotons TNT equivalent)

# Crater Scaling Parameters
# Based on Holsapple & Housen (2007) and Collins et al. (2005)
CRATER_SCALING_CONSTANTS = {
    'simple': {
        'K1': 1.88,    # Crater diameter constant
        'K2': 0.78,    # Crater depth constant  
        'mu': 0.41,    # Scaling exponent
        'nu': 0.13     # Gravity scaling exponent
    },
    'complex': {
        'K1': 1.54,
        'K2': 0.13, 
        'mu': 0.22,
        'nu': 0.13
    }
}

# Seismic Parameters
SEISMIC_VELOCITY_P_WAVE = 6000.0  # m/s (P-wave velocity in crust)
SEISMIC_VELOCITY_S_WAVE = 3464.0  # m/s (S-wave velocity, Vp/Vs = 1.73)

# Ocean Properties
OCEAN_DEPTH_AVG_M = 3800.0  # m (average ocean depth)
SEAWATER_DENSITY_KG_M3 = 1025.0  # kg/m^3
SOUND_SPEED_WATER_MS = 1500.0  # m/s
TSUNAMI_WAVE_VELOCITY_MS = 200.0  # m/s (tsunami wave velocity in shallow water)

# Seismic Properties
SEISMIC_WAVE_VELOCITY_MS = 6000.0  # m/s (P-wave velocity in rock)
SEISMIC_P_WAVE_VELOCITY = 6100.0  # m/s (typical crustal P-wave velocity)
SEISMIC_VELOCITY_S_WAVE = 3464.0  # m/s (S-wave velocity, Vp/Vs = 1.73)

# Modified Mercalli Intensity Scale thresholds (in units of g)
MMI_THRESHOLDS = {
    10: 0.65,   # Extreme
    9: 0.34,    # Violent
    8: 0.18,    # Severe
    7: 0.092,   # Very strong
    6: 0.039,   # Strong
    5: 0.018,   # Moderate
    4: 0.0086,  # Light
    3: 0.0039,  # Weak
    2: 0.00175, # Very weak
    1: 0.0      # Not felt
}

# Environmental Effects Constants
TSUNAMI_EFFICIENCY_OCEAN = 0.5      # Energy transfer efficiency for ocean impacts
TSUNAMI_EFFICIENCY_LAND = 0.1       # Energy transfer efficiency for land impacts
TSUNAMI_DISSIPATION_LENGTH_KM = 5000  # Typical trans-oceanic dissipation scale

# Atmospheric Properties
ATMOSPHERIC_SCALE_HEIGHT_KM = 8.0  # km
ATMOSPHERIC_DENSITY_SEA_LEVEL = 1.225  # kg/m^3

# Impact Effect Scaling
# Based on nuclear weapons effects and asteroid impact research
THERMAL_RADIATION_FRACTION = 0.35  # Fraction of energy as thermal radiation
BLAST_WAVE_FRACTION = 0.50  # Fraction of energy as blast wave
SEISMIC_COUPLING_FRACTION = 0.15  # Fraction of energy as seismic waves

# Material Strength Parameters
ROCK_TENSILE_STRENGTH_PA = 1e7  # Pa (typical rock tensile strength)
CONCRETE_COMPRESSIVE_STRENGTH_PA = 3e7  # Pa
STEEL_YIELD_STRENGTH_PA = 2.5e8  # Pa

# Mitigation Strategy Constants
TYPICAL_IMPACTOR_MASS_KG = 1000.0  # kg (1 ton spacecraft)
TYPICAL_IMPACTOR_VELOCITY_KMS = 10.0  # km/s (relative velocity)
THRUST_EFFICIENCY_DEFAULT = 0.8  # Default thrust efficiency for spacecraft

# Deflection efficiency factors for different strategies
MOMENTUM_TRANSFER_EFFICIENCY = {
    'kinetic_impactor': 1.0,  # Perfect momentum transfer
    'nuclear_standoff': 10.0,  # 10x momentum enhancement from ejecta
    'nuclear_subsurface': 20.0,  # 20x enhancement from optimal coupling
    'gravity_tractor': 1.0,  # Continuous low thrust
    'ion_beam_shepherd': 1.2,  # Slight enhancement from plasma effects
}
