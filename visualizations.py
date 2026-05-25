import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from type_system import TYPE_COLORS, STAT_NAMES

def hex_to_rgba(hex_str: str, alpha: float = 0.2) -> str:
    """Convert hex color code to rgba string for Plotly compatibility"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return hex_str

def create_stat_radar_chart(pokemon_data: dict, label: str) -> go.Figure:
    """Create radar chart for Pokemon stats"""
    stats = pokemon_data['stats']
    stat_names = [STAT_NAMES.get(s['stat']['name'], s['stat']['name']) for s in stats]
    stat_values = [s['base_stat'] for s in stats]
    
    # Radar chart requires the loop to be closed
    stat_names.append(stat_names[0])
    stat_values.append(stat_values[0])
    
    types = pokemon_data['types']
    primary_type = types[0]['type']['name'] if types else 'normal'
    color = TYPE_COLORS.get(primary_type, "#777777")
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=stat_values,
        theta=stat_names,
        fill='toself',
        name=label,
        line=dict(color=color, width=2),
        fillcolor=hex_to_rgba(color, 0.18)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 255], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        ),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=20, b=20),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_type_effectiveness_heatmap(effectiveness_matrix: dict, label: str = "Effectiveness") -> go.Figure:
    """Create heatmap for type effectiveness"""
    types = list(effectiveness_matrix.keys())
    
    # Map effectiveness to numeric values for heatmap
    eff_map = {"0x": 0.0, "0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "2x": 2.0, "4x": 4.0}
    values = [[eff_map.get(effectiveness_matrix[t], 1.0) for t in types]]
    
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=[t.capitalize() for t in types],
        y=[label],
        zmin=0.0,
        zmax=4.0,
        colorscale=[
            [0.0, "#18181b"],       # 0x (Zinc 900)
            [0.0625, "#34d399"],    # 0.25x (Emerald 400)
            [0.125, "#059669"],     # 0.5x (Emerald 600)
            [0.25, "#27272a"],      # 1x (Zinc 800)
            [0.5, "#f87171"],       # 2x (Red 400)
            [1.0, "#b91c1c"]        # 4x (Red 700)
        ],
        showscale=False,
        text=[[effectiveness_matrix[t] for t in types]],
        texttemplate="%{text}",
        ygap=2,
        xgap=2
    ))
    
    fig.update_layout(
        height=140,
        margin=dict(l=120, r=10, t=10, b=10),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_comparison_bar_chart(pokemon1: dict, pokemon2: dict) -> go.Figure:
    """Create comparison bar chart for two Pokemon"""
    stats1 = pokemon1['stats']
    stats2 = pokemon2['stats']
    
    stat_names = [STAT_NAMES.get(s['stat']['name'], s['stat']['name']) for s in stats1]
    values1 = [s['base_stat'] for s in stats1]
    values2 = [s['base_stat'] for s in stats2]
    
    types1 = pokemon1['types'][0]['type']['name'] if pokemon1['types'] else 'normal'
    types2 = pokemon2['types'][0]['type']['name'] if pokemon2['types'] else 'normal'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=stat_names,
        y=values1,
        name=pokemon1['name'].capitalize(),
        marker=dict(color=TYPE_COLORS.get(types1, "#777777")),
        marker_line_color="rgba(255,255,255,0.2)",
        marker_line_width=1
    ))
    fig.add_trace(go.Bar(
        x=stat_names,
        y=values2,
        name=pokemon2['name'].capitalize(),
        marker=dict(color=TYPE_COLORS.get(types2, "#777777")),
        marker_line_color="rgba(255,255,255,0.2)",
        marker_line_width=1
    ))
    
    fig.update_layout(
        barmode='group',
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_comparison_radar_chart(pokemon1: dict, pokemon2: dict) -> go.Figure:
    """Create comparison radar chart for two Pokemon"""
    stats1 = pokemon1['stats']
    stats2 = pokemon2['stats']
    
    stat_names = [STAT_NAMES.get(s['stat']['name'], s['stat']['name']) for s in stats1]
    values1 = [s['base_stat'] for s in stats1]
    values2 = [s['base_stat'] for s in stats2]
    
    # Close loops
    stat_names.append(stat_names[0])
    values1.append(values1[0])
    values2.append(values2[0])
    
    types1 = pokemon1['types'][0]['type']['name'] if pokemon1['types'] else 'normal'
    types2 = pokemon2['types'][0]['type']['name'] if pokemon2['types'] else 'normal'
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values1,
        theta=stat_names,
        fill='toself',
        name=pokemon1['name'].capitalize(),
        line=dict(color=TYPE_COLORS.get(types1, "#ef4444"), width=2),
        fillcolor=hex_to_rgba(TYPE_COLORS.get(types1, "#ef4444"), 0.15)
    ))
    fig.add_trace(go.Scatterpolar(
        r=values2,
        theta=stat_names,
        fill='toself',
        name=pokemon2['name'].capitalize(),
        line=dict(color=TYPE_COLORS.get(types2, "#3b82f6"), width=2),
        fillcolor=hex_to_rgba(TYPE_COLORS.get(types2, "#3b82f6"), 0.15)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 255], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        ),
        height=320,
        margin=dict(l=40, r=40, t=20, b=20),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_team_coverage_heatmap(team_data: list) -> go.Figure:
    """Create coverage matrix for a team (6 Pokemon)"""
    if not team_data:
        return go.Figure()
        
    all_types = sorted(list(TYPE_COLORS.keys()))
    pokemon_names = [p['name'].capitalize() for p in team_data]
    
    from type_system import build_effectiveness_matrix
    
    eff_values = {"0x": 0.0, "0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "2x": 2.0, "4x": 4.0}
    
    z_data = []
    for attack_type in all_types:
        row = []
        for p in team_data:
            p_types = [t['type']['name'] for t in p['types']]
            eff_map = build_effectiveness_matrix(p_types)
            mult_str = eff_map.get(attack_type, "1x")
            mult = eff_values.get(mult_str, 1.0)
            row.append(mult)
        z_data.append(row)
        
    text_data = []
    for r in z_data:
        text_row = []
        for val in r:
            if val == 0.0:
                text_row.append("0x")
            elif val == 0.25:
                text_row.append("0.25x")
            elif val == 0.5:
                text_row.append("0.5x")
            elif val == 1.0:
                text_row.append("-")
            elif val == 2.0:
                text_row.append("2x")
            elif val == 4.0:
                text_row.append("4x")
            else:
                text_row.append(f"{val}x")
        text_data.append(text_row)
        
    colorscale = [
        [0.0, "#18181b"],       # 0x (Zinc 900)
        [0.0625, "#34d399"],    # 0.25x (Emerald 400)
        [0.125, "#059669"],     # 0.5x (Emerald 600)
        [0.25, "#27272a"],      # 1x (Zinc 800)
        [0.5, "#f87171"],       # 2x (Red 400)
        [1.0, "#b91c1c"]        # 4x (Red 700)
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=pokemon_names,
        y=[t.capitalize() for t in all_types],
        text=text_data,
        texttemplate="%{text}",
        zmin=0.0,
        zmax=4.0,
        colorscale=colorscale,
        showscale=False,
        ygap=2,
        xgap=2
    ))
    
    fig.update_layout(
        height=520,
        margin=dict(l=100, r=20, t=10, b=20),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed")
    )
    return fig
