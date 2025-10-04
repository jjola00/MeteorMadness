import random
from typing import Dict, Any

def simulate_defense_attempt(asteroid_diameter_m: float, warning_time_days: float) -> Dict[str, Any]:
    """
    Simulates a planetary defense attempt against an asteroid.

    The simulation has two main phases: detection and deflection, both of which
    are probabilistic.

    Detection Probability Formula (based on warning time):
    - More than 180 days: 95%
    - More than 90 days: 80%
    - More than 30 days: 50%
    - 30 days or less: 20%

    Deflection Probability Formula (if detected, based on asteroid diameter):
    - Less than 100m: 85%
    - Less than 300m: 60%
    - Less than 500m: 40%
    - Less than 1000m: 15%
    - 1000m or more: 5%

    Args:
        asteroid_diameter_m (float): The diameter of the asteroid in meters.
        warning_time_days (float): The number of days of warning time before impact.

    Returns:
        Dict[str, Any]: A dictionary detailing the outcome of the defense attempt.
    """
    # 1. Calculate detection probability based on warning time
    if warning_time_days > 180:
        detection_prob = 0.95
    elif warning_time_days > 90:
        detection_prob = 0.8
    elif warning_time_days > 30:
        detection_prob = 0.5
    else:
        detection_prob = 0.2

    # Simulate detection using randomness
    if random.random() >= detection_prob:
        # 2. If not detected, return the result
        return {"detected": False, "deflected": False, "deflection_attempted": False, "method": None}

    # 3. If detected, calculate deflection probability based on diameter
    if asteroid_diameter_m < 100:
        deflection_prob = 0.85
    elif asteroid_diameter_m < 300:
        deflection_prob = 0.6
    elif asteroid_diameter_m < 500:
        deflection_prob = 0.4
    elif asteroid_diameter_m < 1000:
        deflection_prob = 0.15
    else:
        deflection_prob = 0.05

    # 4. Simulate deflection using randomness
    is_deflected = random.random() < deflection_prob
    method = None

    if is_deflected:
        method = random.choice(["kinetic_impactor", "gravity_tractor"])

    return {
        "detected": True,
        "deflection_attempted": True,
        "deflected": is_deflected,
        "method": method
    }
