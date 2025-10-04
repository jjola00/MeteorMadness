# Using real NASA Near-Earth Object data for authentic asteroid parameters
from typing import Dict, List, Any

LEVEL_THRESHOLDS: Dict[int, int] = {
    1: 0,
    2: 100000,
    3: 500000,
    4: 2000000,
    5: 10000000,
}

def get_level_from_kills(total_kills: int) -> int:
    """
    Determines the player's level based on their total kills.

    Args:
        total_kills (int): The total number of kills (score).

    Returns:
        int: The calculated level, from 1 to 6.
    """
    level = 1
    # Iterate through sorted level thresholds to find the current level
    for lvl, required_kills in sorted(LEVEL_THRESHOLDS.items(), reverse=True):
        if total_kills >= required_kills:
            level = lvl
            break
    return level

def get_level_unlocks(level: int) -> Dict[str, Any]:
    """
    Provides the unlocks and parameters for a given player level.

    Args:
        level (int): The player's current level.

    Returns:
        Dict[str, Any]: A dictionary containing level-specific unlocks.
    """
    if level == 1:
        return {
            "max_diameter_m": 100,
            "available_asteroids": ["custom_only"],
            "title": "Beginner",
            "description": "Start with small, custom-defined asteroids to learn the basics of impact simulation."
        }
    elif level == 2:
        return {
            "max_diameter_m": 300,
            "available_asteroids": ["2000433"], # Eros
            "title": "City Threat",
            "description": "Unlocks asteroid 433 Eros, large enough to pose a threat to a city."
        }
    elif level == 3:
        return {
            "max_diameter_m": 500,
            "available_asteroids": ["2000433", "2099942"], # Eros, Apophis
            "title": "Regional Devastator",
            "description": "Unlocks asteroid 99942 Apophis, capable of causing regional devastation."
        }
    elif level == 4:
        return {
            "max_diameter_m": 1000,
            "available_asteroids": ["2000433", "2099942", "2101955"], # Eros, Apophis, Bennu
            "title": "Continental Threat",
            "description": "Unlocks asteroid 101955 Bennu, a significant threat on a continental scale."
        }
    elif level >= 5:
        return {
            "max_diameter_m": float('inf'), # Unlimited
            "available_asteroids": ["all_cached"],
            "title": "Extinction Event",
            "description": "Unleash extinction-level events with no limits on asteroid size."
        }
    else:
        # Default to level 1 unlocks if an invalid level is provided
        return get_level_unlocks(1)
