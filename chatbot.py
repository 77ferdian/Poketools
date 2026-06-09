import streamlit as st
from google import genai
from pokemon_utils import (
    get_pokemon_data, get_pokemon_species_data, get_evolution_chain,
    get_ability_data, get_move_data
)
from type_system import (
    TYPE_COLORS, get_type_color, build_effectiveness_matrix, STAT_NAMES
)
from calculations import get_stat_total

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """You are PokéChat, a friendly, enthusiastic, and highly knowledgeable Pokemon expert assistant embedded in a Pokemon analysis tool called "Poketools".

Your personality:
- You are passionate about Pokemon and love sharing knowledge
- You use Pokemon-related emojis naturally (🔥 ⚡ 💧 🌿 ❄️ 🐲 👻 etc.)
- You give concise but informative answers
- You can discuss competitive strategy, lore, trivia, type matchups, team building, and anything Pokemon-related
- When given live Pokemon data from PokéAPI, you incorporate it naturally into your responses
- You respond in the SAME LANGUAGE as the user's message (if they write in Indonesian, respond in Indonesian; if English, respond in English)

Your knowledge covers:
- All 9 generations of Pokemon (Gen 1 to Gen 9)
- Type effectiveness and matchups
- Competitive battling strategies (Smogon tiers, VGC, etc.)
- Pokemon abilities, natures, EVs/IVs, items
- Evolution methods and chains
- Pokemon lore, regions, and storylines
- Team building advice and synergy analysis

Rules:
- Keep responses concise (2-4 paragraphs max unless the user asks for detail)
- When discussing stats or type matchups, use clear formatting
- If you receive live PokéAPI data as context, use it to give accurate and up-to-date information
- If you don't know something specific, be honest about it
- Stay on topic — you are a Pokemon expert, not a general assistant
- If asked about non-Pokemon topics, politely redirect to Pokemon topics
"""

# ==================== QUICK ACTIONS ====================
QUICK_ACTIONS = [
    {"label": "🎲 Random Pokemon Fact", "prompt": "Tell me a cool random fact about a Pokemon!"},
    {"label": "⚡ Type Matchup Quiz", "prompt": "Give me a quick type matchup quiz question!"},
    {"label": "🏆 Competitive Tips", "prompt": "Give me a quick competitive battling tip for beginners."},
    {"label": "🔥 Best Starters", "prompt": "Who are the best starter Pokemon across all generations and why?"},
]


def _extract_pokemon_names(message: str) -> list:
    """Extract potential Pokemon names from a user message using simple heuristics."""
    import re
    words = re.findall(r'[a-zA-Z\-]+', message.lower())
    
    # Common Pokemon names that might appear in queries - we'll validate against PokéAPI
    potential_names = []
    skip_words = {
        'what', 'who', 'how', 'why', 'when', 'where', 'is', 'are', 'was', 'were',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'about', 'tell', 'me', 'show', 'give',
        'pokemon', 'type', 'stats', 'stat', 'ability', 'move', 'evolution',
        'compare', 'vs', 'versus', 'against', 'weak', 'weakness', 'strong',
        'best', 'worst', 'good', 'bad', 'can', 'does', 'do', 'have', 'has',
        'it', 'its', 'this', 'that', 'they', 'them', 'their', 'he', 'she',
        'competitive', 'team', 'build', 'counter', 'set', 'moveset',
        'apa', 'siapa', 'bagaimana', 'mengapa', 'kapan', 'dimana', 'dari',
        'dan', 'atau', 'tapi', 'di', 'ke', 'untuk', 'dengan', 'oleh',
        'itu', 'ini', 'yang', 'bisa', 'tidak', 'ya', 'ada', 'saya',
        'tipe', 'lemah', 'kuat', 'jurus', 'evolusi', 'statistik',
        'jelaskan', 'ceritakan', 'info', 'tentang', 'kenapa', 'gimana',
    }
    
    for word in words:
        if word not in skip_words and len(word) >= 3:
            potential_names.append(word)
    
    return potential_names[:3]  # Limit to 3 potential names


def _fetch_pokemon_context(pokemon_names: list) -> str:
    """Fetch PokéAPI data for detected Pokemon names and format as context."""
    context_parts = []
    
    for name in pokemon_names:
        data = get_pokemon_data(name)
        if data:
            types = [t['type']['name'].capitalize() for t in data['types']]
            stats = {STAT_NAMES.get(s['stat']['name'], s['stat']['name']): s['base_stat'] for s in data['stats']}
            abilities = [a['ability']['name'].capitalize() + (" (Hidden)" if a['is_hidden'] else "") for a in data['abilities']]
            total = get_stat_total(data['stats'])
            
            # Type effectiveness
            defending_types = [t['type']['name'] for t in data['types']]
            eff_matrix = build_effectiveness_matrix(defending_types)
            weak_to = [t.capitalize() for t, e in eff_matrix.items() if "2x" in e or "4x" in e]
            resists = [t.capitalize() for t, e in eff_matrix.items() if "0.5x" in e or "0.25x" in e]
            immune_to = [t.capitalize() for t, e in eff_matrix.items() if "0x" in e]
            
            context_parts.append(f"""
[LIVE DATA: {data['name'].capitalize()} #{data['id']}]
- Types: {', '.join(types)}
- Stats: {', '.join(f'{k}: {v}' for k, v in stats.items())} (Total: {total})
- Abilities: {', '.join(abilities)}
- Weak to: {', '.join(weak_to) if weak_to else 'None'}
- Resists: {', '.join(resists) if resists else 'None'}
- Immune to: {', '.join(immune_to) if immune_to else 'None'}
- Height: {data['height']/10}m, Weight: {data['weight']/10}kg
""")
    
    if context_parts:
        return "\n--- LIVE POKÉAPI DATA ---\n" + "\n".join(context_parts) + "\n--- END LIVE DATA ---\n"
    return ""


def _initialize_gemini_client():
    """Initialize Gemini client using Streamlit secrets."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return None


def chat_with_gemini(user_message: str, chat_history: list) -> str:
    """Send a message to Gemini with Pokemon context enrichment."""
    client = _initialize_gemini_client()
    if not client:
        return "⚠️ Gemini API key belum di-setup. Tambahkan key di `.streamlit/secrets.toml`."
    
    # Extract Pokemon names and fetch live data
    pokemon_names = _extract_pokemon_names(user_message)
    pokemon_context = _fetch_pokemon_context(pokemon_names)
    
    # Build conversation history for Gemini
    contents = []
    
    # Add recent chat history (last 10 messages for context window management)
    recent_history = chat_history[-10:]
    for msg in recent_history:
        if msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        else:
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
    
    # Build the current user message with optional Pokemon context
    enriched_message = user_message
    if pokemon_context:
        enriched_message = f"{user_message}\n\n{pokemon_context}"
    
    contents.append({"role": "user", "parts": [{"text": enriched_message}]})
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.8,
                    "max_output_tokens": 1024,
                }
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            is_transient = any(code in err_msg for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"])
            if is_transient and attempt < max_retries - 1:
                import time
                time.sleep(2 * (attempt + 1))
                continue
            return f"⚠️ Error saat menghubungi Gemini: {err_msg}"


def render_pokechat_page():
    """Render the PokéChat page with full chat interface."""
    
    st.markdown("""<div class='header-title'><h2><i class='fa-solid fa-robot'></i> PokéChat — Your Pokemon Expert</h2></div>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #94a3b8; font-size: 1.05rem; margin-top: -15px; margin-bottom: 20px;'>
        <i class='fa-solid fa-circle-info' style='color: #818cf8;'></i> 
        Tanya apapun seputar Pokemon — stats, type matchups, strategi competitive, lore, trivia, dan lainnya!
    </p>""", unsafe_allow_html=True)
    
    # Initialize chat history in session state
    if "pokechat_messages" not in st.session_state:
        st.session_state.pokechat_messages = []
    
    # Quick Actions Row
    st.markdown("""<p style='font-size: 0.85rem; font-weight: 700; color: #64748b; letter-spacing: 1px; margin-bottom: 8px;'>
        <i class='fa-solid fa-bolt'></i> QUICK ACTIONS
    </p>""", unsafe_allow_html=True)
    
    quick_cols = st.columns(len(QUICK_ACTIONS))
    for i, action in enumerate(QUICK_ACTIONS):
        with quick_cols[i]:
            if st.button(action["label"], key=f"quick_{i}", use_container_width=True):
                st.session_state.pokechat_messages.append({"role": "user", "content": action["prompt"]})
                with st.spinner("PokéChat sedang berpikir..."):
                    response = chat_with_gemini(action["prompt"], st.session_state.pokechat_messages)
                st.session_state.pokechat_messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    st.markdown("---")
    
    # Chat Display Area
    chat_container = st.container(height=480)
    
    with chat_container:
        if not st.session_state.pokechat_messages:
            # Welcome message
            st.markdown("""
            <div class="chat-welcome">
                <div style="font-size: 3rem; margin-bottom: 10px;">🤖</div>
                <h3 style="background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin-bottom: 8px;">
                    Halo, Trainer!
                </h3>
                <p style="color: #94a3b8; font-size: 1rem; max-width: 500px; margin: 0 auto;">
                    Saya PokéChat, asisten Pokemon kamu. Tanyakan apapun seputar Pokemon — 
                    dari stats dan type matchups hingga strategi competitive dan trivia!
                </p>
                <div style="margin-top: 20px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                    <span class="type-badge" style="background-color: #6366f1; font-size: 0.75rem;">"Stats Garchomp"</span>
                    <span class="type-badge" style="background-color: #ec4899; font-size: 0.75rem;">"Counter untuk Tyranitar?"</span>
                    <span class="type-badge" style="background-color: #f97316; font-size: 0.75rem;">"Best Fire types Gen 1"</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Render chat messages
            for msg in st.session_state.pokechat_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-msg-user">
                        <div class="chat-bubble-user">
                            <span class="chat-sender-user"><i class="fa-solid fa-user"></i> You</span>
                            {msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-msg-bot">
                        <div class="chat-bubble-bot">
                            <span class="chat-sender-bot"><i class="fa-solid fa-robot"></i> PokéChat</span>
                            {msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat Input
    st.markdown("")  # spacing
    
    input_col, clear_col = st.columns([5, 1])
    
    with input_col:
        user_input = st.chat_input("Tanya sesuatu tentang Pokemon...", key="pokechat_input")
    
    with clear_col:
        if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
            st.session_state.pokechat_messages = []
            st.rerun()
    
    # Process user input
    if user_input:
        st.session_state.pokechat_messages.append({"role": "user", "content": user_input})
        with st.spinner("PokéChat sedang berpikir... 🤔"):
            response = chat_with_gemini(user_input, st.session_state.pokechat_messages)
        st.session_state.pokechat_messages.append({"role": "assistant", "content": response})
        st.rerun()
