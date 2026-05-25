# Type effectiveness matrix (18x18)
TYPE_EFFECTIVENESS = {
    "normal": {"resist": [], "weak": ["fighting"], "immune": ["ghost"]},
    "fire": {"resist": ["fire", "grass", "ice", "bug", "steel", "fairy"], "weak": ["water", "ground", "rock"], "immune": []},
    "water": {"resist": ["fire", "water", "ice", "steel"], "weak": ["electric", "grass"], "immune": []},
    "electric": {"resist": ["flying", "steel", "electric"], "weak": ["ground"], "immune": []},
    "grass": {"resist": ["ground", "water", "grass", "electric"], "weak": ["fire", "ice", "poison", "flying", "bug"], "immune": []},
    "ice": {"resist": ["ice"], "weak": ["fire", "fighting", "rock", "steel"], "immune": []},
    "fighting": {"resist": ["rock", "bug", "dark"], "weak": ["flying", "psychic", "fairy"], "immune": []},
    "poison": {"resist": ["fighting", "poison", "bug", "grass"], "weak": ["ground", "psychic"], "immune": []},
    "ground": {"resist": ["poison", "rock"], "weak": ["water", "grass", "ice"], "immune": ["electric"]},
    "flying": {"resist": ["fighting", "bug", "grass"], "weak": ["electric", "ice", "rock"], "immune": []},
    "psychic": {"resist": ["fighting", "psychic"], "weak": ["bug", "ghost", "dark"], "immune": []},
    "bug": {"resist": ["fighting", "ground", "grass"], "weak": ["fire", "flying", "rock"], "immune": []},
    "rock": {"resist": ["normal", "flying", "poison", "fire"], "weak": ["water", "grass", "fighting", "ground", "steel"], "immune": []},
    "ghost": {"resist": ["poison", "bug"], "weak": ["ghost", "dark"], "immune": ["normal", "fighting"]},
    "dragon": {"resist": ["fire", "water", "grass", "electric"], "weak": ["ice", "dragon", "fairy"], "immune": []},
    "dark": {"resist": ["ghost", "dark"], "weak": ["fighting", "bug", "fairy"], "immune": ["psychic"]},
    "steel": {"resist": ["normal", "flying", "rock", "bug", "steel", "grass", "psychic", "ice", "dragon", "fairy"], "weak": ["fire", "fighting", "ground"], "immune": ["poison"]},
    "fairy": {"resist": ["fighting", "bug", "dark"], "weak": ["poison", "steel"], "immune": []},
}

TYPE_COLORS = {
    "normal": "#94a3b8", "fire": "#f97316", "water": "#3b82f6",
    "electric": "#eab308", "grass": "#22c55e", "ice": "#06b6d4", 
    "fighting": "#ef4444", "poison": "#a855f7", "ground": "#d97706", 
    "flying": "#818cf8", "psychic": "#ec4899", "bug": "#84cc16", 
    "rock": "#a8a29e", "ghost": "#6366f1", "dragon": "#8b5cf6", 
    "steel": "#64748b", "fairy": "#f472b6"
}

TYPE_EMOJIS = {
    "normal": "⚪", "fire": "🔥", "water": "💧",
    "electric": "⚡", "grass": "🌿", "ice": "❄️",
    "fighting": "🥊", "poison": "☠️", "ground": "🪨",
    "flying": "💨", "psychic": "🔮", "bug": "🐛",
    "rock": "🗿", "ghost": "👻", "dragon": "🐲",
    "steel": "⚙️", "fairy": "✨"
}

STAT_NAMES = {
    "hp": "HP", 
    "attack": "Attack", 
    "defense": "Defense",
    "sp-atk": "Sp. Attack", 
    "sp-def": "Sp. Defense", 
    "speed": "Speed"
}

def get_type_color(type_name: str) -> str:
    """Get hex color for Pokemon type"""
    return TYPE_COLORS.get(type_name.lower(), "#777777")

def get_type_effectiveness(attack_type: str, defend_type: str) -> str:
    """
    Returns effectiveness of attack_type against defend_type
    "2x" = super effective, "0.5x" = not very effective, "0x" = no effect, "1x" = neutral
    """
    attack_type = attack_type.lower()
    defend_type = defend_type.lower()
    
    defend_rules = TYPE_EFFECTIVENESS.get(defend_type, {})
    if attack_type in defend_rules.get("weak", []):
        return "2x"
    elif attack_type in defend_rules.get("resist", []):
        return "0.5x"
    elif attack_type in defend_rules.get("immune", []):
        return "0x"
    return "1x"

def build_effectiveness_matrix(defending_types: list) -> dict:
    """Build type effectiveness matrix for defending Pokemon"""
    matrix = {}
    all_types = list(TYPE_COLORS.keys())
    
    for attack_type in all_types:
        effectivenesses = []
        for defend_type in defending_types:
            effectiveness = get_type_effectiveness(attack_type, defend_type)
            effectivenesses.append(effectiveness)
        
        # For dual-type, combine (0x stays 0x, else multiply)
        if len(effectivenesses) == 1:
            combined = effectivenesses[0]
        else:
            if "0x" in effectivenesses:
                combined = "0x"
            elif "2x" in effectivenesses and "0.5x" in effectivenesses:
                combined = "1x"
            elif "2x" in effectivenesses and "2x" in effectivenesses:
                combined = "4x"
            elif "0.5x" in effectivenesses and "0.5x" in effectivenesses:
                combined = "0.25x"
            elif "2x" in effectivenesses:
                combined = "2x"
            elif "0.5x" in effectivenesses:
                combined = "0.5x"
            else:
                combined = "1x"
        
        matrix[attack_type] = combined
    
    return matrix
