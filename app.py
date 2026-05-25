import streamlit as st
import pandas as pd

# Import helper modules
from pokemon_utils import (
    get_pokemon_data, get_pokemon_species_data, get_evolution_chain,
    get_pokemon_by_type, search_pokemon_by_generation, get_ability_data, get_move_data
)
from type_system import TYPE_COLORS, TYPE_EMOJIS, get_type_color, TYPE_EFFECTIVENESS, build_effectiveness_matrix, STAT_NAMES
from calculations import calculate_damage, calculate_ko_threshold, get_stat_total
from visualizations import (
    create_stat_radar_chart, create_type_effectiveness_heatmap,
    create_comparison_bar_chart, create_comparison_radar_chart,
    create_team_coverage_heatmap
)

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Ultimate Pokemon Battle Arena",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/9/98/International_Pok%C3%A9mon_logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism */
    .pokemon-card, .stat-box, .metric-container, .move-table {
        background: rgba(39, 39, 42, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .pokemon-card:hover, .stat-box:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 45px 0 rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .pokemon-card {
        border-left: 5px solid #ef4444;
    }
    
    .stat-box {
        border-top: 4px solid #3b82f6;
    }
    
    .metric-container {
        border-left: 4px solid #10b981;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc;
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Type Badges */
    .type-badge {
        padding: 6px 16px;
        border-radius: 20px;
        color: white;
        font-weight: 800;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        margin-right: 8px;
        margin-bottom: 8px;
        display: inline-block;
        text-transform: uppercase;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.2s ease, filter 0.2s ease;
    }

    .type-badge:hover {
        transform: scale(1.05) translateY(-2px);
        filter: brightness(1.1);
    }
    
    /* Headers */
    .header-title h2 {
        color: #f8fafc !important;
        font-weight: 800;
        background: linear-gradient(135deg, #ef4444, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: none !important;
        padding-bottom: 0;
        margin-bottom: 0;
    }
    
    .header-title {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 15px;
        margin-bottom: 30px;
    }

    /* Main App Header */
    .main-header {
        font-weight: 900 !important;
        font-size: 3rem !important;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        line-height: 1.2;
        letter-spacing: -1px;
    }

    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 1px;
        margin-bottom: 2rem;
    }
    
    /* Metrics Override */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    
    /* Text Inputs / Selectboxes */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #f8fafc !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #10b981, #3b82f6) !important;
        border-radius: 10px !important;
    }
    
    /* Custom Sidebar Navigation Buttons styling */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: rgba(30, 41, 59, 0.4) !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        padding: 12px 18px !important;
        transition: all 0.25s ease !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
        color: #f8fafc !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        font-weight: 800 !important;
    }
    
    /* Hide deploy button, but keep header toggle button and main menu */
    .stDeployButton {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for navigation page
# Initialize session state for navigation page
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Pokedex"

# ==================== SIDEBAR MENU ====================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/International_Pok%C3%A9mon_logo.svg", width=200)
    st.markdown("---")
    st.markdown("<p style='font-size: 0.9rem; font-weight: 800; color: #64748b; letter-spacing: 1.5px; margin-bottom: 15px;'><i class='fa-solid fa-gamepad'></i> MAIN MENU</p>", unsafe_allow_html=True)
    
    pages_config = {
        "Pokedex": ":material/search:",
        "Battle Arena": ":material/swords:",
        "Type Calculator": ":material/calculate:",
        "Team Builder": ":material/groups:",
        "Move Browser": ":material/menu_book:"
    }
    
    for page, icon in pages_config.items():
        is_active = st.session_state.current_page == page
        if st.button(
            page,
            key=f"sidebar_nav_{page}",
            icon=icon,
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_page = page
            st.rerun()

selected = st.session_state.current_page

# ==================== MAIN HEADER ====================
st.markdown("""
    <h1 class='main-header'><i class="fa-solid fa-bolt" style="color: #f59e0b;"></i> ULTIMATE POKEMON BATTLE ARENA <i class="fa-solid fa-bolt" style="color: #f59e0b;"></i></h1>
    <p class='sub-header'>Advanced Analysis Platform with Competitive Damage Calculations</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== PAGE 1: POKEDEX ====================
if selected == "Pokedex":
    st.markdown("<div class='header-title'><h2><i class='fa-solid fa-book-open'></i> Pokemon Pokedex Database</h2></div>", unsafe_allow_html=True)
    
    # Search & Filter Section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        pokemon_search = st.text_input("Search Pokemon Name:", placeholder="e.g., Charizard, Pikachu, Mewtwo")
    
    with col2:
        generation = st.selectbox("Generation:", range(1, 10), format_func=lambda x: f"Gen {x}")
    
    with col3:
        view_mode = st.radio("View:", ["Detail", "Grid"], horizontal=True)
    
    if pokemon_search:
        pokemon_data = get_pokemon_data(pokemon_search)
        species_data = get_pokemon_species_data(pokemon_search)
        
        if pokemon_data:
            # === MAIN POKEMON DISPLAY ===
            col_img, col_info = st.columns([1.2, 1.8])
            
            with col_img:
                img_url = pokemon_data['sprites']['other']['official-artwork']['front_default']
                if img_url:
                    st.image(img_url, use_container_width=True)
                else:
                    st.warning("No image available")
            
            with col_info:
                # Title & ID
                st.markdown(f"<h1 style='background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; font-weight: 900; font-size: 2.5rem;'>#{pokemon_data['id']} {pokemon_data['name'].upper()}</h1>", unsafe_allow_html=True)
                
                # Type Badges
                types = pokemon_data['types']
                type_badges = "".join([
                    f'<span class="type-badge" style="background-color: {get_type_color(t["type"]["name"])}">{t["type"]["name"].capitalize()}</span>'
                    for t in types
                ])
                st.markdown(type_badges, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Quick Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Height", f"{pokemon_data['height']/10}m")
                m2.metric("Weight", f"{pokemon_data['weight']/10}kg")
                m3.metric("Base Total", f"{get_stat_total(pokemon_data['stats'])}")
                
                # Audio cry
                if pokemon_data.get('cries', {}).get('latest'):
                    st.audio(pokemon_data['cries']['latest'], format="audio/wav")
            
            # === DETAIL TABS ===
            tab_stats, tab_moves, tab_abilities, tab_evol, tab_type = st.tabs([
                "Stats", "Moves", "Abilities", "Evolution", "Type Info"
            ])
            
            with tab_stats:
                st.markdown("### Base Statistics")
                stat_col1, stat_col2 = st.columns([2, 1.2])
                
                with stat_col1:
                    for stat in pokemon_data['stats']:
                        stat_name = STAT_NAMES.get(stat['stat']['name'], stat['stat']['name'])
                        stat_value = stat['base_stat']
                        col_s1, col_s2 = st.columns([1, 4])
                        with col_s1:
                            st.metric(stat_name, stat_value)
                        with col_s2:
                            st.progress(stat_value / 255)
                
                with stat_col2:
                    # Display stats as Radar Chart
                    fig_radar = create_stat_radar_chart(pokemon_data, pokemon_data['name'].capitalize())
                    st.plotly_chart(fig_radar, use_container_width=True)
            
            with tab_moves:
                st.markdown("### Moveset & Learnset")
                
                # Filter moves
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    move_type_filter = st.multiselect("Filter by Type:", list(TYPE_COLORS.keys()), key="pokedex_move_type_filter")
                with filter_col2:
                    move_method_filter = st.multiselect("Learn Method:", ["level-up", "machine", "egg", "tutor"], key="pokedex_move_method_filter")
                
                moves = pokemon_data.get('moves', [])
                if moves:
                    move_details = []
                    for move_info in moves:
                        method = ""
                        level = "-"
                        if move_info['version_group_details']:
                            method = move_info['version_group_details'][0]['move_learn_method']['name']
                            level = move_info['version_group_details'][0]['level_learned_at']
                        
                        # Filter by method
                        if move_method_filter and method not in move_method_filter:
                            continue
                            
                        move_name = move_info['move']['name']
                        move_type = "unknown"
                        
                        # Lazy fetch move data only if type filter is active
                        if move_type_filter:
                            m_data = get_move_data(move_name)
                            if m_data:
                                move_type = m_data.get('type', {}).get('name', 'unknown')
                            if move_type not in move_type_filter:
                                continue
                        
                        move_details.append({
                            "Move": move_name.capitalize(),
                            "Method": method.capitalize() if method else "-",
                            "Level": level if level else "-",
                            "Type": move_type.capitalize() if move_type != "unknown" else "-"
                        })
                        if len(move_details) >= 30: # Limit to 30 moves for performance
                            break
                    
                    if move_details:
                        df_moves = pd.DataFrame(move_details)
                        st.dataframe(df_moves, use_container_width=True, hide_index=True)
                    else:
                        st.info("Tidak ada jurus yang cocok dengan filter yang dipilih.")
                else:
                    st.info("No move data available")
            
            with tab_abilities:
                st.markdown("### Abilities & Hidden Ability")
                
                abilities = pokemon_data.get('abilities', [])
                for ability in abilities:
                    ability_name = ability['ability']['name'].capitalize()
                    is_hidden = ability.get('is_hidden', False)
                    
                    if is_hidden:
                        st.warning(f"**{ability_name}** (Hidden Ability)", icon=":material/lock:")
                    else:
                        st.info(f"⭐ **{ability_name}**")
                    
                    # Fetch and display actual ability details
                    ability_info = get_ability_data(ability['ability']['name'])
                    if ability_info:
                        effect_entries = ability_info.get('effect_entries', [])
                        description = "No description available."
                        for entry in effect_entries:
                            if entry.get('language', {}).get('name') == 'en':
                                description = entry.get('short_effect', entry.get('effect', ''))
                                break
                        st.markdown(f"<p style='color: #cbd5e1; font-size: 0.95rem; margin-left: 15px;'>{description}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #cbd5e1; font-size: 0.95rem; margin-left: 15px;'>Ability details not available.</p>", unsafe_allow_html=True)
            
            with tab_evol:
                st.markdown("### Evolution Chain")
                
                evolution_chain = get_evolution_chain(pokemon_search)
                if evolution_chain:
                    chain = evolution_chain['chain']
                    
                    def display_evolution_chain(chain_data, level=0):
                        indent = "→ " * level
                        species_name = chain_data['species']['name'].capitalize()
                        st.write(f"{indent}**{species_name}**")
                        
                        for evolution in chain_data.get('evolves_to', []):
                            display_evolution_chain(evolution, level + 1)
                    
                    display_evolution_chain(chain)
                else:
                    st.info("No evolution chain data available")
            
            with tab_type:
                st.markdown("### Type Effectiveness & Matchup Heatmap")
                
                defending_types = [t['type']['name'] for t in types]
                effectiveness = build_effectiveness_matrix(defending_types)
                
                # Display Heatmap
                fig_heatmap = create_type_effectiveness_heatmap(effectiveness, "Multiplier")
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Show what's super effective AGAINST this Pokemon
                weak_to = [t for t, eff in effectiveness.items() if "2x" in eff]
                resistant_to = [t for t, eff in effectiveness.items() if "0.5x" in eff]
                immune_to = [t for t, eff in effectiveness.items() if "0x" in eff]
                
                col_weak, col_resist, col_immune = st.columns(3)
                
                with col_weak:
                    st.markdown("**Weak To:**")
                    if weak_to:
                        for t in weak_to:
                            st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%;">{t.capitalize()}</span>', unsafe_allow_html=True)
                    else:
                        st.write("None")
                
                with col_resist:
                    st.markdown("**Resists:**")
                    if resistant_to:
                        for t in resistant_to:
                            st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%;">{t.capitalize()}</span>', unsafe_allow_html=True)
                    else:
                        st.write("None")
                
                with col_immune:
                    st.markdown("**Immune To:**")
                    if immune_to:
                        for t in immune_to:
                            st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%;">{t.capitalize()}</span>', unsafe_allow_html=True)
                    else:
                        st.write("None")
        
        else:
            st.error(f"Pokemon '{pokemon_search}' tidak ditemukan. Cek spelling!", icon=":material/error:")
    
    else:
        st.info("Masukkan nama Pokemon untuk mulai explore", icon=":material/ads_click:")

# ==================== PAGE 2: BATTLE ARENA ====================
elif selected == "Battle Arena":
    st.markdown("<div class='header-title'><h2><i class='fa-solid fa-khanda'></i> Advanced Battle Analysis</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-circle' style='color: #ef4444;'></i> Fighter 1 (Red Corner)</h3>", unsafe_allow_html=True)
        p1_name = st.text_input("Pokemon 1:", value="charizard", key="p1")
    
    with col2:
        st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-circle' style='color: #3b82f6;'></i> Fighter 2 (Blue Corner)</h3>", unsafe_allow_html=True)
        p2_name = st.text_input("Pokemon 2:", value="blastoise", key="p2")
    
    if p1_name and p2_name:
        data1 = get_pokemon_data(p1_name)
        data2 = get_pokemon_data(p2_name)
        
        if data1 and data2:
            # === BATTLE HEADER ===
            t1 = data1['types'][0]['type']['name']
            t2 = data2['types'][0]['type']['name']
            icon1 = f"https://raw.githubusercontent.com/duiker101/pokemon-type-svg-icons/master/icons/{t1}.svg"
            icon2 = f"https://raw.githubusercontent.com/duiker101/pokemon-type-svg-icons/master/icons/{t2}.svg"
            
            st.markdown("---")
            st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center; gap: 20px;'>
                <img src='{icon1}' style='width: 45px; height: 45px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4));' title='{t1.capitalize()}' />
                <h2 style='margin: 0; background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 2.5rem;'>VS</h2>
                <img src='{icon2}' style='width: 45px; height: 45px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4));' title='{t2.capitalize()}' />
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            # === MAIN COMPARISON ===
            col_p1, col_vs, col_p2 = st.columns([1.5, 0.5, 1.5])
            
            with col_p1:
                st.markdown(f"<h3 style='color: #ef4444; font-weight: 800;'>{data1['name'].upper()}</h3>", unsafe_allow_html=True)
                img1 = data1['sprites']['other']['official-artwork']['front_default']
                if img1:
                    st.image(img1, use_container_width=True)
                
                # Types
                types1 = [t['type']['name'] for t in data1['types']]
                for t in types1:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()}</span>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.metric("Base Total", get_stat_total(data1['stats']))
            
            with col_vs:
                st.markdown("<h1 style='text-align: center; margin-top: 80px; background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 3rem;'>VS</h1>", unsafe_allow_html=True)
                # Type matchup indicator
                types1 = [t['type']['name'] for t in data1['types']]
                types2 = [t['type']['name'] for t in data2['types']]
                eff1 = build_effectiveness_matrix(types1)
                eff2 = build_effectiveness_matrix(types2)
                
                # Count super-effective moves
                count1_super = sum(1 for e in eff1.values() if "2x" in e)
                count2_super = sum(1 for e in eff2.values() if "2x" in e)
                
                st.markdown(f"<p style='text-align: center; color: #aaa;'>P1 has {count1_super} super-effective types</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #aaa;'>P2 has {count2_super} super-effective types</p>", unsafe_allow_html=True)
            
            with col_p2:
                st.markdown(f"<h3 style='color: #3b82f6; font-weight: 800;'>{data2['name'].upper()}</h3>", unsafe_allow_html=True)
                img2 = data2['sprites']['other']['official-artwork']['front_default']
                if img2:
                    st.image(img2, use_container_width=True)
                
                # Types
                types2 = [t['type']['name'] for t in data2['types']]
                for t in types2:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()}</span>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.metric("Base Total", get_stat_total(data2['stats']))
            
            st.markdown("---")
            
            # === STAT COMPARISON CHARTS ===
            st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-chart-bar'></i> Stat Comparison</h3>", unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("##### <i class='fa-solid fa-chart-simple'></i> Stats Comparison Chart", unsafe_allow_html=True)
                fig_bar_comp = create_comparison_bar_chart(data1, data2)
                st.plotly_chart(fig_bar_comp, use_container_width=True)
            
            with col_chart2:
                st.markdown("##### <i class='fa-solid fa-network-wired'></i> Stats Radar Comparison", unsafe_allow_html=True)
                fig_radar_comp = create_comparison_radar_chart(data1, data2)
                st.plotly_chart(fig_radar_comp, use_container_width=True)
            
            # === STAT-BY-STAT BREAKDOWN ===
            st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-dumbbell'></i> Stat-by-Stat Analysis</h3>", unsafe_allow_html=True)
            
            stat_comparison = []
            for stat1, stat2 in zip(data1['stats'], data2['stats']):
                name = STAT_NAMES.get(stat1['stat']['name'], stat1['stat']['name'])
                val1 = stat1['base_stat']
                val2 = stat2['base_stat']
                diff = val1 - val2
                winner = "P1" if diff > 0 else ("P2" if diff < 0 else "TIE")
                
                stat_comparison.append({
                    "Stat": name,
                    "P1": val1,
                    "P2": val2,
                    "Difference": abs(diff),
                    "Advantage": winner
                })
            
            df_stats = pd.DataFrame(stat_comparison)
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
            
            # === TYPE MATCHUP ANALYSIS ===
            st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-bolt'></i> Type Matchup Details</h3>", unsafe_allow_html=True)
            
            col_match1, col_match2 = st.columns(2)
            
            with col_match1:
                st.markdown("**What beats P1 (Weak to):**")
                types1 = [t['type']['name'] for t in data1['types']]
                eff_matrix1 = build_effectiveness_matrix(types1)
                weak_to_p1 = [t for t, e in eff_matrix1.items() if "2x" in e]
                for t in weak_to_p1[:8]:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()}</span>', unsafe_allow_html=True)
            
            with col_match2:
                st.markdown("**What beats P2 (Weak to):**")
                types2 = [t['type']['name'] for t in data2['types']]
                eff_matrix2 = build_effectiveness_matrix(types2)
                weak_to_p2 = [t for t, e in eff_matrix2.items() if "2x" in e]
                for t in weak_to_p2[:8]:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()}</span>', unsafe_allow_html=True)
            
            # === DAMAGE CALCULATOR ===
            st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-calculator'></i> Advanced Damage Calculator</h3>", unsafe_allow_html=True)
            
            with st.expander("Configure Damage Calculation", icon=":material/settings:", expanded=False):
                calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
                
                with calc_col1:
                    attacker_level = st.slider("Attacker Level:", 1, 100, 50)
                    move_power = st.slider("Move Power:", 0, 200, 100)
                
                with calc_col2:
                    move_category = st.selectbox("Move Type:", ["Physical", "Special", "Status"])
                    stab = st.checkbox("STAB (Same Type Bonus)?", True)
                
                with calc_col3:
                    effectiveness = st.selectbox("Effectiveness:", ["0x", "0.5x", "1x", "2x", "4x"], index=2)
                    critical = st.checkbox("Critical Hit?", False)
                
                with calc_col4:
                    weather = st.selectbox("Weather:", ["Normal", "Sun", "Rain", "Hail"])
                    defender_hp = st.slider("Defender HP:", 1, 255, 100)
                
                # Calculate
                p1_stats = {s['stat']['name']: s['base_stat'] for s in data1['stats']}
                p2_stats = {s['stat']['name']: s['base_stat'] for s in data2['stats']}
                
                damage = calculate_damage(
                    attacker_level=attacker_level,
                    attacker_atk=p1_stats.get('attack', 100),
                    attacker_spatk=p1_stats.get('sp-atk', 100),
                    defender_def=p2_stats.get('defense', 100),
                    defender_spdef=p2_stats.get('sp-def', 100),
                    move_power=move_power,
                    move_category=move_category.lower(),
                    effectiveness=effectiveness,
                    stab=stab,
                    critical=critical
                )
                
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.metric("Min Damage", f"{damage[0]}")
                
                with result_col2:
                    st.metric("Max Damage", f"{damage[1]}")
                
                with result_col3:
                    min_pct = (damage[0] / defender_hp) * 100
                    max_pct = (damage[1] / defender_hp) * 100
                    st.metric("% of HP", f"{max_pct:.1f}%")
                
                # KO calculation
                ko_hits = calculate_ko_threshold(damage, defender_hp)
                st.info(f"**Guaranteed KO in: {ko_hits} hits**" if ko_hits != float('inf') else "Cannot KO", icon=":material/sports_martial_arts:")
            
            # === BATTLE SIMULATION & WINNER DETERMINATION ===
            st.markdown("---")
            st.markdown("<h3 style='background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 1.8rem; margin-bottom: 1.5rem;'><i class='fa-solid fa-trophy' style='color: #f59e0b;'></i> Battle Simulation & Winner Prediction</h3>", unsafe_allow_html=True)
            
            p1_name = data1['name'].capitalize()
            p2_name = data2['name'].capitalize()

            # Stats
            p1_stats = {s['stat']['name']: s['base_stat'] for s in data1['stats']}
            p2_stats = {s['stat']['name']: s['base_stat'] for s in data2['stats']}

            p1_hp = p1_stats.get('hp', 100)
            p1_atk = p1_stats.get('attack', 100)
            p1_def = p1_stats.get('defense', 100)
            p1_spa = p1_stats.get('sp-atk', 100)
            p1_spd = p1_stats.get('sp-def', 100)
            p1_spe = p1_stats.get('speed', 100)

            p2_hp = p2_stats.get('hp', 100)
            p2_atk = p2_stats.get('attack', 100)
            p2_def = p2_stats.get('defense', 100)
            p2_spa = p2_stats.get('sp-atk', 100)
            p2_spd = p2_stats.get('sp-def', 100)
            p2_spe = p2_stats.get('speed', 100)

            def estimate_stat(base, stat_type, level=50):
                if stat_type == "hp":
                    return int((2 * base + 31) * level / 100) + level + 10
                else:
                    return int(((2 * base + 31) * level / 100) + 5)

            p1_actual_hp = estimate_stat(p1_hp, "hp")
            p1_actual_atk = estimate_stat(p1_atk, "atk")
            p1_actual_def = estimate_stat(p1_def, "def")
            p1_actual_spa = estimate_stat(p1_spa, "spa")
            p1_actual_spd = estimate_stat(p1_spd, "spd")
            p1_actual_spe = estimate_stat(p1_spe, "spe")

            p2_actual_hp = estimate_stat(p2_hp, "hp")
            p2_actual_atk = estimate_stat(p2_atk, "atk")
            p2_actual_def = estimate_stat(p2_def, "def")
            p2_actual_spa = estimate_stat(p2_spa, "spa")
            p2_actual_spd = estimate_stat(p2_spd, "spd")
            p2_actual_spe = estimate_stat(p2_spe, "spe")

            eff_values = {"0x": 0.0, "0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "2x": 2.0, "4x": 4.0}
            all_types = list(TYPE_COLORS.keys())

            # Find P1's best attack against P2
            p1_best_dmg = 0
            p1_min_dmg = 0
            p1_max_dmg = 0
            p1_best_move_desc = ""
            for attack_type in all_types:
                is_stab = attack_type in [t['type']['name'] for t in data1['types']]
                power = 90 if is_stab else 80
                mult_str = build_effectiveness_matrix([t['type']['name'] for t in data2['types']]).get(attack_type, "1x")
                mult = eff_values.get(mult_str, 1.0)
                
                for cat in ["physical", "special"]:
                    dmg_tuple = calculate_damage(
                        attacker_level=50,
                        attacker_atk=p1_actual_atk,
                        attacker_spatk=p1_actual_spa,
                        defender_def=p2_actual_def,
                        defender_spdef=p2_actual_spd,
                        move_power=power,
                        move_category=cat,
                        effectiveness=mult_str,
                        stab=is_stab,
                        critical=False
                    )
                    avg_dmg = (dmg_tuple[0] + dmg_tuple[1]) / 2
                    if avg_dmg > p1_best_dmg:
                        p1_best_dmg = avg_dmg
                        p1_min_dmg = dmg_tuple[0]
                        p1_max_dmg = dmg_tuple[1]
                        p1_best_move_desc = f"{attack_type.capitalize()} ({cat.capitalize()})"

            # Find P2's best attack against P1
            p2_best_dmg = 0
            p2_min_dmg = 0
            p2_max_dmg = 0
            p2_best_move_desc = ""
            for attack_type in all_types:
                is_stab = attack_type in [t['type']['name'] for t in data2['types']]
                power = 90 if is_stab else 80
                mult_str = build_effectiveness_matrix([t['type']['name'] for t in data1['types']]).get(attack_type, "1x")
                mult = eff_values.get(mult_str, 1.0)
                
                for cat in ["physical", "special"]:
                    dmg_tuple = calculate_damage(
                        attacker_level=50,
                        attacker_atk=p2_actual_atk,
                        attacker_spatk=p2_actual_spa,
                        defender_def=p1_actual_def,
                        defender_spdef=p1_actual_spd,
                        move_power=power,
                        move_category=cat,
                        effectiveness=mult_str,
                        stab=is_stab,
                        critical=False
                    )
                    avg_dmg = (dmg_tuple[0] + dmg_tuple[1]) / 2
                    if avg_dmg > p2_best_dmg:
                        p2_best_dmg = avg_dmg
                        p2_min_dmg = dmg_tuple[0]
                        p2_max_dmg = dmg_tuple[1]
                        p2_best_move_desc = f"{attack_type.capitalize()} ({cat.capitalize()})"

            import math
            p1_hits_to_ko = math.ceil(p2_actual_hp / max(1, p1_max_dmg))
            p2_hits_to_ko = math.ceil(p1_actual_hp / max(1, p2_max_dmg))

            if p1_hits_to_ko < p2_hits_to_ko:
                winner = "P1"
                reason = f"<b>{p1_name}</b> menang karena dapat mengalahkan <b>{p2_name}</b> dalam jumlah giliran yang lebih sedikit ({p1_hits_to_ko} vs {p2_hits_to_ko} hit)."
            elif p2_hits_to_ko < p1_hits_to_ko:
                winner = "P2"
                reason = f"<b>{p2_name}</b> menang karena dapat mengalahkan <b>{p1_name}</b> dalam jumlah giliran yang lebih sedikit ({p2_hits_to_ko} vs {p1_hits_to_ko} hit)."
            else:
                if p1_actual_spe > p2_actual_spe:
                    winner = "P1"
                    reason = f"Kedua Pokemon membutuhkan {p1_hits_to_ko} hit, tetapi <b>{p1_name}</b> menang karena memiliki Speed yang lebih tinggi ({p1_actual_spe} vs {p2_actual_spe}) sehingga dapat menyerang terlebih dahulu."
                elif p2_actual_spe > p1_actual_spe:
                    winner = "P2"
                    reason = f"Kedua Pokemon membutuhkan {p2_hits_to_ko} hit, tetapi <b>{p2_name}</b> menang karena memiliki Speed yang lebih tinggi ({p2_actual_spe} vs {p1_actual_spe}) sehingga dapat menyerang terlebih dahulu."
                else:
                    winner = "TIE"
                    reason = f"Pertarungan SERI! Kedua Pokemon membutuhkan {p1_hits_to_ko} hit dan memiliki kecepatan Speed yang sama persis ({p1_actual_spe})."

            winner_display_name = p1_name.upper() if winner == "P1" else (p2_name.upper() if winner == "P2" else "NONE (TIE)")
            winner_color = "#ef4444" if winner == "P1" else ("#3b82f6" if winner == "P2" else "#94a3b8")

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border-radius: 16px; padding: 25px; border-left: 8px solid {winner_color}; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
                <h3 style="color: {winner_color}; margin-top: 0; font-weight: 900; letter-spacing: 1px; font-size: 1.8rem;"><i class='fa-solid fa-trophy' style='color: #f59e0b;'></i> BATTLE WINNER: {winner_display_name}</h3>
                <p style="font-size: 1.2rem; color: #f8fafc; line-height: 1.6; margin-bottom: 0;">{reason}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Turn-by-Turn Battle Simulation Log", icon=":material/history:", expanded=True):
                h1 = p1_actual_hp
                h2 = p2_actual_hp
                turn = 1
                
                st.markdown(f"**Status Tempur (Lv. 50):**")
                st.markdown(f"• **{p1_name}** - HP: `{h1}` | Atk/Spa: `{p1_actual_atk}/{p1_actual_spa}` | Def/Spd: `{p1_actual_def}/{p1_actual_spd}` | Spe: `{p1_actual_spe}`")
                st.markdown(f"• **{p2_name}** - HP: `{h2}` | Atk/Spa: `{p2_actual_atk}/{p2_actual_spa}` | Def/Spd: `{p2_actual_def}/{p2_actual_spd}` | Spe: `{p2_actual_spe}`")
                st.markdown("---")
                
                p1_first = p1_actual_spe >= p2_actual_spe
                
                while h1 > 0 and h2 > 0 and turn <= 10:
                    st.markdown(f"<i class='fa-solid fa-swords'></i> **[Turn {turn}]**", unsafe_allow_html=True)
                    if p1_first:
                        # P1 attacks P2
                        dmg1 = int(p1_best_dmg)
                        h2 = max(0, h2 - dmg1)
                        st.markdown(f"<i class='fa-solid fa-circle' style='color: #ef4444; font-size: 0.8rem;'></i> **{p1_name}** menggunakan *{p1_best_move_desc}* memberikan **{dmg1}** damage! (*{p2_name}* HP: `{h2}`)", unsafe_allow_html=True)
                        if h2 <= 0:
                            st.markdown(f"<i class='fa-solid fa-skull' style='color: #94a3b8;'></i> **{p2_name}** pingsan!", unsafe_allow_html=True)
                            break
                        
                        # P2 attacks P1
                        dmg2 = int(p2_best_dmg)
                        h1 = max(0, h1 - dmg2)
                        st.markdown(f"<i class='fa-solid fa-circle' style='color: #3b82f6; font-size: 0.8rem;'></i> **{p2_name}** menggunakan *{p2_best_move_desc}* memberikan **{dmg2}** damage! (*{p1_name}* HP: `{h1}`)", unsafe_allow_html=True)
                        if h1 <= 0:
                            st.markdown(f"<i class='fa-solid fa-skull' style='color: #94a3b8;'></i> **{p1_name}** pingsan!", unsafe_allow_html=True)
                            break
                    else:
                        # P2 attacks P1
                        dmg2 = int(p2_best_dmg)
                        h1 = max(0, h1 - dmg2)
                        st.markdown(f"<i class='fa-solid fa-circle' style='color: #3b82f6; font-size: 0.8rem;'></i> **{p2_name}** menggunakan *{p2_best_move_desc}* memberikan **{dmg2}** damage! (*{p1_name}* HP: `{h1}`)", unsafe_allow_html=True)
                        if h1 <= 0:
                            st.markdown(f"<i class='fa-solid fa-skull' style='color: #94a3b8;'></i> **{p1_name}** pingsan!", unsafe_allow_html=True)
                            break
                        
                        # P1 attacks P2
                        dmg1 = int(p1_best_dmg)
                        h2 = max(0, h2 - dmg1)
                        st.markdown(f"<i class='fa-solid fa-circle' style='color: #ef4444; font-size: 0.8rem;'></i> **{p1_name}** menggunakan *{p1_best_move_desc}* memberikan **{dmg1}** damage! (*{p2_name}* HP: `{h2}`)", unsafe_allow_html=True)
                        if h2 <= 0:
                            st.markdown(f"<i class='fa-solid fa-skull' style='color: #94a3b8;'></i> **{p2_name}** pingsan!", unsafe_allow_html=True)
                            break
                    turn += 1
                
                st.markdown("---")
                st.markdown("<i class='fa-solid fa-flag-checkered'></i> **Simulasi Selesai!**", unsafe_allow_html=True)

            st.success("Analisis pertempuran selesai!", icon=":material/check_circle:")
        
        else:
            st.error("One or both Pokemon not found", icon=":material/error:")

# ==================== PAGE 3: TYPE CALCULATOR ====================
elif selected == "Type Calculator":
    st.markdown("<div class='header-title'><h2><i class='fa-solid fa-bolt'></i> Type Effectiveness Calculator</h2></div>", unsafe_allow_html=True)
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600;'><i class='fa-solid fa-circle' style='color: #ef4444;'></i> Attacking Type</h3>", unsafe_allow_html=True)
        attack_type = st.selectbox("Select attacking move type:", sorted(TYPE_COLORS.keys()), key="attack_type")
    
    with col_calc2:
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 600;'><i class='fa-solid fa-circle' style='color: #3b82f6;'></i> Defending Pokemon/Types</h3>", unsafe_allow_html=True)
        defend_input_mode = st.radio("Input mode:", ["By Pokemon", "By Type"], horizontal=True)
        
        if defend_input_mode == "By Pokemon":
            defend_pokemon = st.text_input("Enter defending Pokemon:", "pikachu")
            if defend_pokemon:
                data = get_pokemon_data(defend_pokemon)
                if data:
                    defend_types = [t['type']['name'] for t in data['types']]
                    st.write(f"**Types: {', '.join([t.upper() for t in defend_types])}**")
                else:
                    st.error("Pokemon not found")
                    defend_types = []
        else:
            defend_types = st.multiselect(
                "Select defending types:",
                sorted(TYPE_COLORS.keys()),
                default=["water"],
                max_selections=2
            )
    
    if attack_type and defend_types:
        st.markdown("---")
        st.markdown("<h3 style='background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'><i class='fa-solid fa-chart-bar'></i> Effectiveness Result</h3>", unsafe_allow_html=True)
        
        # Calculate effectiveness
        results = {}
        for defend_type in defend_types:
            eff = build_effectiveness_matrix([defend_type])
            results[defend_type] = eff.get(attack_type, "1x")
        
        # Display results
        result_col1, result_col2, result_col3 = st.columns(3)
        
        # Super effective (2x)
        super_effective = [t for t, eff in results.items() if "2x" in eff]
        with result_col1:
            st.markdown("<h4 style='color: #ff6b6b;'><i class='fa-solid fa-circle-check' style='color: #10b981;'></i> Super Effective</h4>", unsafe_allow_html=True)
            if super_effective:
                for t in super_effective:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%; text-align: center;">2x damage</span>', unsafe_allow_html=True)
            else:
                st.write("None")
        
        # Neutral (1x)
        neutral = [t for t, eff in results.items() if "1x" in eff]
        with result_col2:
            st.markdown("<h4 style='color: #ffd93d;'><i class='fa-solid fa-circle-right' style='color: #64748b;'></i> Neutral</h4>", unsafe_allow_html=True)
            if neutral:
                for t in neutral:
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%; text-align: center;">1x damage</span>', unsafe_allow_html=True)
            else:
                st.write("None")
        
        # Not very effective (0.5x, 0.25x, 0x)
        not_effective = [t for t, eff in results.items() if "0" in eff or "0.5" in eff]
        with result_col3:
            st.markdown("<h4 style='color: #4ecdc4;'><i class='fa-solid fa-circle-xmark' style='color: #ef4444;'></i> Not Very Effective</h4>", unsafe_allow_html=True)
            if not_effective:
                for t in not_effective:
                    eff_val = results[t]
                    st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}; width: 100%; text-align: center;">{eff_val} damage</span>', unsafe_allow_html=True)
            else:
                st.write("None")
        
        st.markdown("---")
        
        # Full matrix
        st.markdown("### <i class='fa-solid fa-table'></i> Type Coverage Matrix", unsafe_allow_html=True)
        st.write(f"**{attack_type.upper()}** type moves against all defending types:")
        
        matrix_data = []
        all_types = sorted(TYPE_COLORS.keys())
        for defend_type in all_types:
            eff = build_effectiveness_matrix([defend_type]).get(attack_type, "1x")
            matrix_data.append({
                "Defending Type": defend_type.capitalize(),
                "Effectiveness": eff,
                "Damage": {"0x": "Immune", "0.25x": "Very Weak", "0.5x": "Not Very Effective", "1x": "Neutral", "2x": "Super Effective", "4x": "Ultra Effective"}.get(eff, "Unknown")
            })
        
        df_matrix = pd.DataFrame(matrix_data)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)

# ==================== PAGE 4: TEAM BUILDER ====================
elif selected == "Team Builder":
    st.markdown("<div class='header-title'><h2><i class='fa-solid fa-users'></i> Team Coverage Analyzer</h2></div>", unsafe_allow_html=True)
    
    st.info("Build a 6-Pokemon team and analyze offensive/defensive type coverage", icon=":material/push_pin:")
    
    team = []
    team_cols = st.columns(3)
    
    for i in range(6):
        col_idx = i % 3
        with team_cols[col_idx]:
            pokemon_name = st.text_input(f"Pokemon {i+1}:", value=["charizard", "blastoise", "venusaur", "pikachu", "mewtwo", "dragonite"][i] if i < 6 else "", key=f"team_{i}")
            if pokemon_name:
                data = get_pokemon_data(pokemon_name)
                if data:
                    team.append(data)
                    types = [t['type']['name'] for t in data['types']]
                    st.caption(f"✓ {data['name'].capitalize()} ({', '.join([t.upper() for t in types])})")
                else:
                    st.caption("✗ Not found")
    
    if len(team) > 0:
        st.markdown("---")
        st.markdown("<h3 style='font-size: 1.5rem; font-weight: 600;'><i class='fa-solid fa-chart-pie'></i> Team Analysis & Stats</h3>", unsafe_allow_html=True)
        
        # Display side-by-side: Radar chart of average stats and heatmap of coverage
        col_t1, col_t2 = st.columns([1.5, 2.5])
        
        with col_t1:
            st.markdown("##### <i class='fa-solid fa-network-wired'></i> Average Team Stats", unsafe_allow_html=True)
            # Calculate Average Team Stats
            avg_stats = []
            stat_keys = ['hp', 'attack', 'defense', 'sp-atk', 'sp-def', 'speed']
            for key in stat_keys:
                total_val = 0
                for p in team:
                    for s in p['stats']:
                        if s['stat']['name'] == key:
                            total_val += s['base_stat']
                avg_stats.append({
                    "stat": {"name": key},
                    "base_stat": int(total_val / len(team))
                })
                
            fake_team_pokemon = {
                "name": "Team Average",
                "types": [{"type": {"name": "normal"}}],
                "stats": avg_stats
            }
            fig_team_radar = create_stat_radar_chart(fake_team_pokemon, "Team Average Stats")
            st.plotly_chart(fig_team_radar, use_container_width=True)
            
        with col_t2:
            st.markdown("##### <i class='fa-solid fa-shield-halved'></i> Defense Coverage Heatmap", unsafe_allow_html=True)
            fig_team_heatmap = create_team_coverage_heatmap(team)
            st.plotly_chart(fig_team_heatmap, use_container_width=True)

        st.markdown("---")
        
        # Collect all types
        all_team_types = []
        for poke in team:
            for t in poke['types']:
                all_team_types.append(t['type']['name'])
        
        unique_types = set(all_team_types)
        
        st.markdown(f"**Team Type Coverage:** {', '.join([t.upper() for t in sorted(unique_types)])} ({len(unique_types)}/18 Types)")
        
        # Coverage analysis
        coverage_col1, coverage_col2 = st.columns(2)
        
        with coverage_col1:
            st.markdown("### Offensive Coverage (Can Attack)")
            can_attack = set()
            for poke in team:
                for t in poke['types']:
                    attack_type = t['type']['name']
                    # Check what this type is super-effective against
                    for target_type in TYPE_COLORS.keys():
                        eff = build_effectiveness_matrix([target_type]).get(attack_type, "1x")
                        if "2x" in eff:
                            can_attack.add(target_type)
            
            st.write(f"Can deal 2x damage to: {len(can_attack)}/18 types")
            for t in sorted(can_attack):
                st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()}</span>', unsafe_allow_html=True)
        
        with coverage_col2:
            st.markdown("### Defensive Coverage (Resistances)")
            resistances = {}
            for poke in team:
                for t in poke['types']:
                    defend_type = t['type']['name']
                    # Check what resists/is immune to each attacking type
                    for attack_type in TYPE_COLORS.keys():
                        eff = build_effectiveness_matrix([defend_type]).get(attack_type, "1x")
                        if "0" in eff or "0.5" in eff:
                            if attack_type not in resistances:
                                resistances[attack_type] = 0
                            resistances[attack_type] += 1
            
            st.write(f"Team has {len(resistances)}/18 type resistances")
            for t in sorted(resistances.keys()):
                st.markdown(f'<span class="type-badge" style="background-color: {get_type_color(t)}">{t.capitalize()} ({resistances[t]}x)</span>', unsafe_allow_html=True)

        st.markdown("---")
        # Recommendations Engine
        st.markdown("<h3 style='background: linear-gradient(135deg, #818cf8, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 1.5rem; margin-top: 15px;'><i class='fa-solid fa-lightbulb'></i> Strategic Recommendations</h3>", unsafe_allow_html=True)
        
        all_types = list(TYPE_COLORS.keys())
        uncovered_offensive_types = []
        for target_type in all_types:
            has_coverage = False
            for p in team:
                for t in p['types']:
                    eff = build_effectiveness_matrix([target_type]).get(t['type']['name'], "1x")
                    if "2x" in eff:
                        has_coverage = True
                        break
                if has_coverage:
                    break
            if not has_coverage:
                uncovered_offensive_types.append(target_type)
                
        vulnerable_defensive_types = []
        for attack_type in all_types:
            weak_count = 0
            resist_count = 0
            immune_count = 0
            for p in team:
                p_types = [t['type']['name'] for t in p['types']]
                eff_map = build_effectiveness_matrix(p_types)
                mult_str = eff_map.get(attack_type, "1x")
                if "2x" in mult_str or "4x" in mult_str:
                    weak_count += 1
                elif "0.5x" in mult_str or "0.25x" in mult_str:
                    resist_count += 1
                elif "0x" in mult_str:
                    immune_count += 1
            
            if weak_count >= 2 and resist_count == 0 and immune_count == 0:
                vulnerable_defensive_types.append(attack_type)
                
        type_suggestions = {
            "fire": ["Charizard", "Arcanine", "Volcarona"],
            "water": ["Gyarados", "Blastoise", "Starmie"],
            "grass": ["Venusaur", "Rillaboom", "Decidueye"],
            "electric": ["Jolteon", "Rotom-Wash", "Pikachu"],
            "ground": ["Garchomp", "Mamoswine", "Landorus"],
            "flying": ["Corviknight", "Salamence", "Aerodactyl"],
            "steel": ["Metagross", "Scizor", "Lucario"],
            "fairy": ["Togekiss", "Clefable", "Sylveon"],
            "dragon": ["Dragonite", "Hydreigon", "Garchomp"],
            "ghost": ["Gengar", "Dragapult", "Mimikyu"],
            "psychic": ["Alakazam", "Gardevoir", "Metagross"],
            "ice": ["Weavile", "Mamoswine", "Lapras"],
            "fighting": ["Machamp", "Lucario", "Conkeldurr"],
            "poison": ["Gengar", "Crobat", "Nidoking"],
            "rock": ["Tyranitar", "Aerodactyl", "Gigalith"],
            "bug": ["Scizor", "Volcarona", "Heracross"],
            "dark": ["Tyranitar", "Weavile", "Hydreigon"]
        }
        
        if not vulnerable_defensive_types and not uncovered_offensive_types:
            st.success("**Your team has excellent offensive and defensive coverage! No major gaps detected.**", icon=":material/stars:")
        else:
            if vulnerable_defensive_types:
                st.markdown("<h4 style='color: #ef4444; margin-top: 15px;'><i class='fa-solid fa-triangle-exclamation'></i> Defensive Vulnerabilities</h4>", unsafe_allow_html=True)
                st.write("Your team has multiple Pokemon weak to the following types, with no resistances or immunities to cover them:")
                for vt in vulnerable_defensive_types:
                    opts = ", ".join(type_suggestions.get(vt, ["Charizard", "Blastoise"]))
                    st.markdown(f"• **{vt.upper()}**: Consider adding a Fire, Grass, or Steel Pokemon depending on the weakness. Good options include: *{opts}*")
            
            if uncovered_offensive_types:
                st.markdown("<h4 style='color: #ffd93d; margin-top: 15px;'><i class='fa-solid fa-gavel'></i> Offensive Coverage Gaps</h4>", unsafe_allow_html=True)
                st.write("No Pokemon on your team can hit the following types super-effectively with their native STAB types:")
                gaps_str = ", ".join([f"**{gt.upper()}**" for gt in uncovered_offensive_types])
                st.markdown(f"• Gaps: {gaps_str}")

# ==================== PAGE 5: MOVE BROWSER ====================
else:  # "Move Browser"
    st.markdown("<div class='header-title'><h2><i class='fa-solid fa-book'></i> Pokemon Move Database</h2></div>", unsafe_allow_html=True)
    
    col_search, col_filter = st.columns(2)
    
    with col_search:
        pokemon_for_moves = st.text_input("Enter Pokemon name:", "charizard")
    
    with col_filter:
        move_type_filter = st.multiselect("Filter by move type:", sorted(TYPE_COLORS.keys()), key="browser_move_type_filter")
    
    if pokemon_for_moves:
        data = get_pokemon_data(pokemon_for_moves)
        
        if data:
            st.markdown(f"### {data['name'].upper()} - Available Moves")
            
            moves = data.get('moves', [])
            
            if moves:
                move_list = []
                for move_info in moves:
                    move_name = move_info['move']['name']
                    methods = []
                    level = "-"
                    
                    if move_info['version_group_details']:
                        detail = move_info['version_group_details'][0]
                        if detail['move_learn_method']['name']:
                            methods.append(detail['move_learn_method']['name'])
                        level = detail['level_learned_at'] if detail['level_learned_at'] > 0 else "-"
                    
                    move_type = "unknown"
                    if move_type_filter:
                        m_data = get_move_data(move_name)
                        if m_data:
                            move_type = m_data.get('type', {}).get('name', 'unknown')
                        if move_type not in move_type_filter:
                            continue
                    
                    move_list.append({
                        "Move": move_name.capitalize(),
                        "Learn Method": ", ".join(methods) if methods else "Unknown",
                        "Level": level,
                        "Type": move_type.capitalize() if move_type != "unknown" else "-"
                    })
                    if len(move_list) >= 40:
                        break
                
                if move_list:
                    df_moves = pd.DataFrame(move_list)
                    st.dataframe(df_moves, use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada jurus yang cocok dengan filter tipe.")
            else:
                st.info("No move data available")
        else:
            st.error("Pokemon not found")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <footer style='text-align: center; color: #666; font-size: 0.8em; margin-top: 40px;'>
    <p><i class="fa-solid fa-bolt" style="color: #f59e0b;"></i> <strong>Ultimate Pokemon Battle Arena</strong> | Powered by PokéAPI | Data & Analysis for Competitive Players</p>
    <p>Gen 1-9 Support | Advanced Damage Calculator | Type Effectiveness Matrix | Team Coverage Analysis | by Ferdian Information Systems</p>
    </footer>
    """, unsafe_allow_html=True)