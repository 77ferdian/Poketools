import streamlit as st
import requests
from typing import Dict, List, Optional

# Cache PokéAPI calls untuk performance
@st.cache_data(ttl=3600)
def get_pokemon_data(pokemon_name: str) -> Optional[Dict]:
    """Fetch Pokemon data from PokéAPI with caching"""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower().strip()}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_pokemon_species_data(pokemon_name: str) -> Optional[Dict]:
    """Fetch Pokemon species data (descriptions, evolution chain, etc.)"""
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower().strip()}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_move_data(move_name: str) -> Optional[Dict]:
    """Fetch move data from PokéAPI"""
    url = f"https://pokeapi.co/api/v2/move/{move_name.lower().strip()}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_ability_data(ability_name: str) -> Optional[Dict]:
    """Fetch ability data from PokéAPI"""
    url = f"https://pokeapi.co/api/v2/ability/{ability_name.lower().strip()}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def search_pokemon_by_generation(gen: int) -> List[Dict]:
    """Get all Pokemon from a specific generation"""
    url = f"https://pokeapi.co/api/v2/generation/{gen}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('pokemon_species', [])
    except:
        pass
    return []

@st.cache_data(ttl=3600)
def get_evolution_chain(pokemon_name: str) -> Optional[Dict]:
    """Get evolution chain for a Pokemon"""
    species_data = get_pokemon_species_data(pokemon_name)
    if not species_data or 'evolution_chain' not in species_data:
        return None
    
    chain_url = species_data['evolution_chain']['url']
    try:
        response = requests.get(chain_url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_pokemon_by_type(type_name: str) -> List[Dict]:
    """Get all Pokemon of a specific type"""
    url = f"https://pokeapi.co/api/v2/type/{type_name.lower().strip()}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('pokemon', [])
    except:
        pass
    return []

def parse_pokemon_name(pokemon_dict: Dict) -> str:
    """Extract clean Pokemon name from API response"""
    if isinstance(pokemon_dict, dict) and 'name' in pokemon_dict:
        return pokemon_dict['name'].capitalize()
    elif isinstance(pokemon_dict, dict) and 'pokemon' in pokemon_dict:
        return pokemon_dict['pokemon']['name'].capitalize()
    return str(pokemon_dict)
