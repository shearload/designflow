# wbinder 12.02.2026
# streamlit run MMC2.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Modular Asset Configurator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
    <style>
    .selection-banner {
        background-color: #2563eb;
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-container {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA CONSTANTS ---
SYSTEMS_DATA = [
    {"System": "Fully In-Situ Slabs", "Speed": 2, "Cost": 5, "Sustainability": 2, "Logistics": 5, "Quality": 2, "Short": "In-Situ Slab"},
    {"System": "Semi-Precast Slabs", "Speed": 3.5, "Cost": 4.5, "Sustainability": 2.5, "Logistics": 4, "Quality": 4, "Short": "Semi-Precast"},
    {"System": "Steel Beams with Hollowcore", "Speed": 4.5, "Cost": 3, "Sustainability": 4, "Logistics": 3, "Quality": 3.5, "Short": "Steel/Hollowcore"},
    {"System": "Prefabricated Timber Panels", "Speed": 4, "Cost": 3.5, "Sustainability": 5, "Logistics": 4.5, "Quality": 4, "Short": "Timber Panel"},
    {"System": "Volumetric Concrete Box", "Speed": 5, "Cost": 2, "Sustainability": 3, "Logistics": 1.5, "Quality": 5, "Short": "Concrete Box"},
    {"System": "Volumetric Steel Box", "Speed": 5, "Cost": 2, "Sustainability": 4, "Logistics": 2, "Quality": 5, "Short": "Steel Box"},
]
DF_MATRIX = pd.DataFrame(SYSTEMS_DATA)

# --- 3. SIDEBAR NAVIGATION & PARAMETERS ---
with st.sidebar:
    st.title("🏗️ Configurator")
    st.header("Building Parameters")
    
    max_h = st.slider("Max Building Height (Units)", 1, 6, 3, help="Max number of blocks stacked vertically.")
    target_gfa = st.slider("Target GFA (Total Blocks)", 1, 25, 12, help="Total number of modular units in the asset.")
    
    st.divider()
    st.info("💡 Adjust height and GFA to see how footprint area scales automatically.")

# --- 4. COMPUTATIONAL LOGIC (Building Generation) ---
def generate_building_layout(total_units, max_height):
    # Block Dimensions (1:3:1 Horizontal Ratio)
    W, L, H = 1, 3, 1
    
    # Calculate footprint requirements
    cols_count = int(np.ceil(total_units / max_height))
    grid_side = int(np.ceil(np.sqrt(cols_count)))
    
    coords = []
    placed = 0
    for i in range(grid_side):
        for j in range(grid_side):
            for k in range(max_height):
                if placed < total_units:
                    coords.append((i * W, j * L, k * H))
                    placed += 1
    return coords, (W, L, H), cols_count

block_coords, dims, footprint_area = generate_building_layout(target_gfa, max_h)

# --- 5. 3D VISUALIZATION ENGINE ---
def create_3d_viz(blocks, w, l, h):
    fig = go.Figure()
    
    for x, y, z in blocks:
        # Add Semi-transparent Volume
        fig.add_trace(go.Mesh3d(
            x=[x, x+w, x+w, x, x, x+w, x+w, x],
            y=[y, y, y+l, y+l, y, y, y+l, y+l],
            z=[z, z, z, z, z+h, z+h, z+h, z+h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.4, color='#cbd5e1', flatshading=True, showlegend=False, hoverinfo='none'
        ))

        # Add High-Contrast Wireframe
        lx, ly, lz = [], [], []
        edges = [
            ((0,0,0),(w,0,0)), ((w,0,0),(w,l,0)), ((w,l,0),(0,l,0)), ((0,l,0),(0,0,0)),
            ((0,0,h),(w,0,h)), ((w,0,h),(w,l,h)), ((w,l,h),(0,l,h)), ((0,l,h),(0,0,h)),
            ((0,0,0),(0,0,h)), ((w,0,0),(w,0,h)), ((w,l,0),(w,l,h)), ((0,l,0),(0,l,h))
        ]
        for s, e in edges:
            lx.extend([x+s[0], x+e[0], None]); ly.extend([y+s[1], y+e[1], None]); lz.extend([z+s[2], z+e[2], None])
        
        fig.add_trace(go.Scatter3d(
            x=lx, y=ly, z=lz, mode='lines', 
            line=dict(color='#1e293b', width=4), showlegend=False, hoverinfo='none'
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=550, paper_bgcolor='white',
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode='data', bgcolor='white',
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2), projection=dict(type='orthographic'))
        )
    )
    return fig

# --- 6. MAIN UI RENDERING ---
st.title("Modular Asset Visualizer")
st.markdown("Exploring spatial efficiency using **Modular Units** | Project: B+G wbinder | 12.02.26.")

# Top Row: 3D and Metrics
col_viz, col_metrics = st.columns([3, 1])

with col_viz:
    st.plotly_chart(create_3d_viz(block_coords, *dims), use_container_width=True)

with col_metrics:
    st.subheader("Asset Breakdown")
    st.metric("Total Modular Units", target_gfa)
    st.metric("Footprint Area", f"{footprint_area} units")
    st.metric("Total Height", f"{max_h} levels")
    st.divider()
    st.caption("Stack height to be verified with structural laod takedown.")

st.divider()

# --- 7. ANALYSIS MATRIX ---
st.header("Modular Systems Matrix")
st.caption("Comparative Structural Performance")

tab_perf, tab_logic = st.tabs(["📊 Performance Comparison", "⚖️ Selection Logic"])

with tab_perf:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("System Performance Scores")
        
        # # Performance Chart
        # fig_perf = go.Figure()
        # metrics = ["Speed", "Cost", "Logistics"]
        # colors = ["#3b82f6", "#10b981", "#f59e0b"]
        
        # for metric, color in zip(metrics, colors):
        #     fig_perf.add_trace(go.Bar(
        #         x=DF_MATRIX["Short"],
        #         y=DF_MATRIX[metric],
        #         name=metric,
        #         marker_color=color
        #     ))
            
        # fig_perf.update_layout(
        #     barmode='group',
        #     template='plotly_white',
        #     height=400,
        #     margin=dict(l=0, r=0, t=20, b=0),
        #     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        #     yaxis=dict(title="Score", range=[0, 5.5], gridcolor="#f1f5f9"),
        #     xaxis=dict(title="")
        # )
        # st.plotly_chart(fig_perf, use_container_width=True)
        
        # Numerical Values Table
        st.markdown("#### Numerical Matrix")
        st.dataframe(
            DF_MATRIX[["System", "Speed", "Cost", "Logistics", "Sustainability", "Quality"]],
            hide_index=True,
            use_container_width=True
        )
    
    with c2:
        st.subheader("System Spotlight")
        choice = st.selectbox("Select System", DF_MATRIX["System"].tolist(), index=1)
        row = DF_MATRIX[DF_MATRIX["System"] == choice].iloc[0]
        
        rad_cats = ['Speed', 'Cost', 'Sustainability', 'Logistics', 'Quality']
        rad_vals = [row[c] for c in rad_cats]
        
        fig_rad = go.Figure(go.Scatterpolar(
            r=rad_vals + [rad_vals[0]], theta=rad_cats + [rad_cats[0]],
            fill='toself', fillcolor='rgba(37, 99, 235, 0.3)', line_color='#2563eb'
        ))
        fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig_rad, use_container_width=True)

with tab_logic:
    st.markdown("""
        <div class="selection-banner">
            <h3>Final Recommendation: Semi-Precast System</h3>
            <p>Selected for optimal balance of <b>regional logistics</b> and <b>onsite speed</b>. 
            Reduces formwork labor by 60% compared to in-situ while avoiding the 'empty-air' transport 
            costs of full volumetric boxes.</p>
        </div>
    """, unsafe_allow_html=True)
    
    table_logic = {
        "System": ["Semi-Precast", "In-Situ Slab", "Steel/Hollowcore", "Volumetric"],
        "Strategic Benefit": ["Balance of Risk/Cost", "Low direct material cost", "Design Flexibility", "Max Speed/Zero Waste"],
        "Constraint": ["6m Span Limit", "Long Onsite Cycle", "Fire Protection Cost", "High Logistics Barrier"]
    }
    st.table(pd.DataFrame(table_logic))