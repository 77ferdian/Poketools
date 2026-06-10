# Poketools - Ultimate Pokemon Battle Arena ⚔️

Poketools is a premium, SaaS-grade Streamlit web application designed for competitive Pokemon players. It provides comprehensive tools for exploring Pokemon data, analyzing stats, simulating battles, and building optimized teams using data from the PokéAPI.

## Features ✨

*   **📚 Pokedex Database**: Search and explore any Pokemon's stats, abilities, move pool, and evolutionary line.
*   **⚔️ Battle Arena**: Compare two Pokemon side-by-side with interactive Radar and Bar charts. Run turn-by-turn battle simulations to predict the winner based on base stats, type advantages, and move power.
*   **⚡ Type Calculator**: Instantly calculate defensive weaknesses and offensive coverage for single or dual-type Pokemon.
*   **👥 Team Builder**: Construct a team of 6 Pokemon and analyze your team's overall stats, defensive vulnerabilities, and offensive coverage gaps using an interactive heatmap.
*   **📖 Move Browser**: Browse, filter, and search through all Pokemon moves by type, category, or power.
*   **🤖 PokéChat**: An AI-powered Pokemon expert chatbot using Google Gemini. Ask anything about Pokemon stats, type matchups, competitive strategies, lore, and trivia!

## Tech Stack 🛠️

*   **Python**: Core application logic.
*   **Streamlit**: Frontend framework for rapid UI development.
*   **Plotly**: Interactive data visualizations (Radar charts, Bar charts, Heatmaps).
*   **Pandas**: Data manipulation and aggregation.
*   **PokéAPI**: RESTful API for fetching up-to-date Pokemon data.
*   **FontAwesome & Google Fonts**: Premium iconography and typography (Outfit font).

## Installation & Setup 🚀

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/77ferdian/Poketools.git
    cd Poketools
    ```

2.  **Activate Virtual Environment (.venv):**
    Ensure you use the virtual environment so all dependencies (Streamlit, Plotly, etc.) are loaded correctly:
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **Windows (Command Prompt):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies (if not already installed):**
    ```bash
    pip install -r requirements.txt
    ```
    *(Or install manually if requirements.txt is not present: `pip install streamlit pandas plotly requests google-genai`)*

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## UI/UX Design Philosophy 🎨

Poketools is built with a modern, glassmorphism design language. It completely eschews system emojis in favor of high-fidelity vector icons (FontAwesome & Streamlit Material Icons) to provide a consistent, professional, and visually stunning experience across all devices.

## Disclaimer

This is a fan-made tool. Pokémon and Pokémon character names are trademarks of Nintendo.
