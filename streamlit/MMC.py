#wbinder 11.02.2026
#streamlit run MMC.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Modular Systems Matrix",
    page_icon="🏗️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .selection-banner {
        background-color: #2563eb;
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Data Definition
data = [
    {"System": "Fully In-Situ Slabs", "Speed": 2, "Cost": 5, "Sustainability": 2, "Logistics": 5, "Quality": 2, "Short": "In-Situ Slab"},
    {"System": "Semi-Precast Slabs", "Speed": 3.5, "Cost": 4.5, "Sustainability": 2.5, "Logistics": 4, "Quality": 4, "Short": "Semi-Precast"},
    {"System": "Steel Beams with Hollowcore", "Speed": 4.5, "Cost": 3, "Sustainability": 4, "Logistics": 3, "Quality": 3.5, "Short": "Steel/Hollowcore"},
    {"System": "Prefabricated Timber Panels", "Speed": 4, "Cost": 3.5, "Sustainability": 5, "Logistics": 4.5, "Quality": 4, "Short": "Timber Panel"},
    {"System": "Volumetric Concrete Box", "Speed": 5, "Cost": 2, "Sustainability": 3, "Logistics": 1.5, "Quality": 5, "Short": "Concrete Box"},
    {"System": "Volumetric Steel Box", "Speed": 5, "Cost": 2, "Sustainability": 4, "Logistics": 2, "Quality": 5, "Short": "Steel Box"},
]

df = pd.DataFrame(data)

# Header
st.title("Modular Systems Matrix")
st.caption("Comparative analysis of structural solutions and final selection. B+G wbinder. 11.02.2026")

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("System Performance Scores (1-5)")
    
    # Prepare data for Matplotlib Bar Chart
    metrics = ["Speed", "Cost", "Logistics"]
    labels = df["Short"].tolist()
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    rects1 = ax.bar(x - width, df["Speed"], width, label='Speed', color="#3b82f6")
    rects2 = ax.bar(x, df["Cost"], width, label='Cost', color="#10b981")
    rects3 = ax.bar(x + width, df["Logistics"], width, label='Logistics', color="#f59e0b")
    
    ax.set_ylabel('Score')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 5.5)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("System Spotlight")
    selected_name = st.selectbox("Select System", df["System"].tolist(), index=1)
    selected_row = df[df["System"] == selected_name].iloc[0]

    # Matplotlib Radar Chart
    categories = ['Speed', 'Cost', 'Sustainability', 'Logistics', 'Quality']
    values = [selected_row[cat] for cat in categories]
    num_vars = len(categories)
    
    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig_radar, ax_radar = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax_radar.fill(angles, values, color='#3b82f6', alpha=0.4)
    ax_radar.plot(angles, values, color='#2563eb', linewidth=2)
    
    ax_radar.set_yticklabels([])
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(categories)
    ax_radar.set_ylim(0, 5)
    
    st.pyplot(fig_radar)

# Final Selection Banner
st.markdown(f"""
    <div class="selection-banner">
        <h2 style="color: white; margin-top: 0;">Final Solution: Precast Beams with Semi-Precast Slabs</h2>
        <p style="font-size: 1.1rem; opacity: 0.9;">
            This system has been selected as the optimal choice. It offers the best balance of regional 
            <b>cost-effectiveness</b> while achieving a <b>30-40% reduction in onsite time</b> compared 
            to fully in-situ slabs. By utilizing precast beams and sacrificial formwork (planks), 
            the project maximizes safety and speed without the high logistical premium of volumetric modular units.
        </p>
    </div>
""", unsafe_allow_html=True)

# Logic Summary Table
st.subheader("Selection Logic Summary")
table_data = {
    "System": ["Semi-Precast Slabs", "In-Situ Slab", "Steel/Hollowcore", "Volumetric Boxes"],
    "Primary Benefit": ["Balanced Speed/Cost/Risk", "Lowest direct cost", "High span & disassembly", "Maximum Speed & Quality"],
    "Key Trade-off": ["Limited span (6m)", "Slowest onsite delivery", "High regional material cost", "Highest logistics & cost barriers"]
}
st.table(pd.DataFrame(table_data))

st.info("💡 Note: Cost scores represent economic viability (Higher = More Affordable).")