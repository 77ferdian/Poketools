import math

def calculate_damage(
    attacker_level: int = 50,
    attacker_atk: int = 100,
    attacker_spatk: int = 100,
    defender_def: int = 100,
    defender_spdef: int = 100,
    move_power: int = 100,
    move_category: str = "physical",  # physical, special, status
    effectiveness: str = "1x",  # 0x, 0.25x, 0.5x, 1x, 2x, 4x
    stab: bool = False,
    critical: bool = False,
    weather: str = "normal",
    attacker_ability: str = None,
    defender_ability: str = None,
    item: str = None,
    ev_spread: dict = None,
    iv_spread: dict = None,
    nature_boost: dict = None
) -> tuple:
    """
    Calculate damage range with EV/IV/Nature/Ability support
    Returns: (min_damage, max_damage, damage_percentage)
    """
    
    if move_category == "status":
        return (0, 0, 0)
    
    # Parse effectiveness multiplier
    eff_map = {"0x": 0, "0.25x": 0.25, "0.5x": 0.5, "1x": 1, "2x": 2, "4x": 4}
    eff_multiplier = eff_map.get(effectiveness, 1)
    
    # Select stat based on category
    if move_category == "physical":
        attack_stat = attacker_atk
        defense_stat = defender_def
    else:  # special
        attack_stat = attacker_spatk
        defense_stat = defender_spdef
    
    # Apply EV spread (if provided)
    if ev_spread:
        if move_category == "physical" and "atk" in ev_spread:
            attack_stat += (ev_spread["atk"] // 4)
        elif move_category == "special" and "spa" in ev_spread:
            attack_stat += (ev_spread["spa"] // 4)
    
    # Apply IV spread (if provided)
    if iv_spread:
        if move_category == "physical" and "atk" in iv_spread:
            attack_stat += iv_spread["atk"]
        elif move_category == "special" and "spa" in iv_spread:
            attack_stat += iv_spread["spa"]
    
    # Apply nature boost (if provided)
    if nature_boost:
        if move_category == "physical" and nature_boost.get("boost_atk"):
            attack_stat = int(attack_stat * 1.1)
        elif move_category == "special" and nature_boost.get("boost_spa"):
            attack_stat = int(attack_stat * 1.1)
    
    # Base damage formula
    base_damage = (((2 * attacker_level / 5 + 2) * move_power * attack_stat / defense_stat) / 50 + 2)
    
    # Apply modifiers
    modifiers = 1.0
    
    # STAB (Same Type Attack Bonus)
    if stab:
        modifiers *= 1.5
    
    # Critical hit
    if critical:
        modifiers *= 1.5
    
    # Weather effects (simplified)
    if weather == "sun" and move_category == "special":
        modifiers *= 1.5  # Fire moves boost
    elif weather == "rain" and move_category == "special":
        modifiers *= 1.5  # Water moves boost
    
    # Type effectiveness
    modifiers *= eff_multiplier
    
    # Ability effects (simplified)
    if attacker_ability == "Adaptability" and stab:
        modifiers *= 2
    
    # Item effects (simplified)
    if item == "Assault Vest" and move_category == "special":
        modifiers *= 0.8  # Actually blocks, but for damage calc
    
    # Random roll (0.85 to 1.0)
    min_damage = int(base_damage * modifiers * 0.85)
    max_damage = int(base_damage * modifiers * 1.0)
    
    # Damage as percentage of defender HP
    min_percentage = (min_damage / defender_spdef) * 100  # Approximation
    max_percentage = (max_damage / defender_spdef) * 100
    
    return (max(0, min_damage), max_damage, (max(0, min_percentage), max_percentage))

def calculate_ko_threshold(damage: tuple, defender_hp: int = 100) -> int:
    """Calculate how many hits needed to KO"""
    min_damage, max_damage, _ = damage
    if max_damage == 0:
        return float('inf')
    return math.ceil(defender_hp / max_damage)

def get_stat_total(pokemon_stats: list) -> int:
    """Get total base stats"""
    return sum([stat['base_stat'] for stat in pokemon_stats])

def calculate_stat_rank(base_stat: int, max_possible: int = 255) -> float:
    """Calculate stat percentile (0-100)"""
    return (base_stat / max_possible) * 100
