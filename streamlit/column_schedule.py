"""
Wyeth Binder
Bollinger + Grohmann

Run Program with following command:

streamlit run column_schedule.py

"""
import io
import streamlit as st
import pandas as pd
import math
import numpy as np

# Set page title and icon
st.set_page_config(page_title="Column Schedule", page_icon=":heart:")

# Page title and description
st.title("Automated Column Schedule Tool")
st.markdown("")
st.markdown("")
st.markdown("v0.1 Concept WIP | Written by: Wyeth Binder | Verified by: Name, Surname")
st.markdown("")

st.markdown("This is a Streamlit app to generate a column schedule report from RFEM data and preprocess for Revit drawings.")

#st.image("icon.png", caption="column image")

# User input - Sidebar
user_input_text = st.sidebar.text_input("Enter project name:", "VIE23 P017")
user_input_rfem = st.sidebar.text_input("RFEM model name and version:", "BG_Building Model East_wbinder_v1")


st.subheader("Input RFEM data")

uploaded = st.file_uploader("Upload RFEM input (.xlsx)", type=["xlsx"])

DEFAULT_ROWS = 8
default_df = pd.DataFrame(
    {
        "Column_ID": [f"C{i+1}" for i in range(DEFAULT_ROWS)],
        "Shape": ["RECT"] * DEFAULT_ROWS,           # RECT or CIRC
        "b_mm": [300] * DEFAULT_ROWS,               # for RECT
        "h_mm": [300] * DEFAULT_ROWS,               # for RECT
        "D_mm": [None] * DEFAULT_ROWS,              # for CIRC
        "NEd_kN": [1200] * DEFAULT_ROWS,            # design axial load (example)
        "fck_MPa": [30] * DEFAULT_ROWS,             # concrete strength (example)
        "cover_mm": [40] * DEFAULT_ROWS,            # nominal cover (example)
    }
)

st.subheader("Manual input (used only if no upload)")
manual_df = st.data_editor(
    default_df,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
)

def read_uploaded_xlsx(file) -> pd.DataFrame:
    """
    Expects columns similar to the manual input:
    Column_ID, Shape, b_mm, h_mm, D_mm, NEd_kN, fck_MPa, cover_mm
    """
    df = pd.read_excel(file)

    # Normalize column names (basic)
    df.columns = [c.strip() for c in df.columns]

    required = ["Column_ID", "Shape", "NEd_kN", "fck_MPa", "cover_mm"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column '{c}' in uploaded file.")

    # Ensure optional geometry columns exist
    for c in ["b_mm", "h_mm", "D_mm"]:
        if c not in df.columns:
            df[c] = None

    return df

if uploaded is not None:
    try:
        input_df = read_uploaded_xlsx(uploaded)
        st.success("Using uploaded Excel data (overrides manual input).")
    except Exception as e:
        st.error(f"Could not read uploaded file: {e}")
        st.info("Falling back to manual input.")
        input_df = manual_df.copy()
else:
    input_df = manual_df.copy()

# Basic cleanup
input_df["Shape"] = input_df["Shape"].astype(str).str.upper().str.strip()

st.subheader("Input data being used")
st.dataframe(input_df, use_container_width=True)

# ----------------------------------------
# 2) Reinforcement / schedule generation
# ----------------------------------------
st.subheader("Reinforcement rules / assumptions")

st.markdown(
    """
- Minimum longitudinal bars:
  - **RECT/SQUARE**: 4 bars minimum
  - **CIRC**: 6 bars minimum  
- Minimum longitudinal bar diameter: **12 mm**  
These minimum detailing requirements are taken from the provided guidance note. [1]
"""
)

bar_diams = st.multiselect(
    "Allowed bar diameters (mm)",
    options=[10, 12, 14, 16, 20, 25, 32, 40],
    default=[12, 16, 20, 25],
)
if not bar_diams:
    st.stop()

default_bar_diam = st.selectbox("Default chosen bar diameter (mm)", options=sorted(bar_diams), index=0)

def min_bars_for_shape(shape: str) -> int:
    # From context: min 4 in square, 6 in circular [1].
    if shape in ("CIRC", "CIRCULAR", "ROUND"):
        return 6
    # Treat RECT/SQUARE and unknowns as 4
    return 4

def area_of_bar_mm2(d_mm: float) -> float:
    return math.pi * (d_mm ** 2) / 4.0

def section_area_concrete_mm2(row) -> float:
    shape = row["Shape"]
    if shape in ("CIRC", "CIRCULAR", "ROUND"):
        D = row.get("D_mm", None)
        if pd.isna(D) or D is None:
            return float("nan")
        return math.pi * (float(D) ** 2) / 4.0
    else:
        b = row.get("b_mm", None)
        h = row.get("h_mm", None)
        if pd.isna(b) or pd.isna(h) or b is None or h is None:
            return float("nan")
        return float(b) * float(h)

def design_reinf_for_row(row, chosen_d_mm: float):
    shape = row["Shape"]
    n_min = min_bars_for_shape(shape)

    # Minimum bar diameter 12mm per context [1]
    d_mm = max(float(chosen_d_mm), 12.0)

    # Placeholder: just provide minimum detailing reinforcement.
    n_bars = n_min
    As_mm2 = n_bars * area_of_bar_mm2(d_mm)

    return n_bars, d_mm, As_mm2

generate = st.button("Generate column schedule")

if generate:
    out = input_df.copy()

    # Compute geometry area
    out["Ac_mm2"] = out.apply(section_area_concrete_mm2, axis=1)

    # Compute reinforcement
    results = out.apply(lambda r: design_reinf_for_row(r, default_bar_diam), axis=1, result_type="expand")
    results.columns = ["n_bars", "bar_diam_mm", "As_provided_mm2"]
    out = pd.concat([out, results], axis=1)

    # Simple notes / validation
    notes = []
    for _, r in out.iterrows():
        shape = r["Shape"]
        if shape in ("CIRC", "CIRCULAR", "ROUND"):
            if pd.isna(r.get("D_mm")):
                notes.append("Missing D_mm for circular column")
            else:
                notes.append("")
        else:
            if pd.isna(r.get("b_mm")) or pd.isna(r.get("h_mm")):
                notes.append("Missing b_mm/h_mm for rectangular column")
            else:
                notes.append("")
    out["Notes"] = notes

    st.subheader("Generated column schedule")
    st.dataframe(out, use_container_width=True)

    # Export to Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        out.to_excel(writer, index=False, sheet_name="Column_Schedule")
    buf.seek(0)

    st.download_button(
        "Download schedule as Excel",
        data=buf,
        file_name="column_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Footer
st.markdown("---")
st.markdown("W. Binder, 2026")

