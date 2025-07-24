import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="UAV Spar Structural Analysis", layout="wide", page_icon="🛠️")
st.title("🛠️ UAV Spar Structural Analysis Dashboard")

st.markdown("""
This tool helps engineers analyze structural performance of UAV wing spars.
Given specifications, it calculates bending stress, deflection, and shear stress for front and rear spars.
""")

# --- INPUT PARAMETERS ---
st.sidebar.header("Wing & Spar Configuration")
MTOW = st.sidebar.number_input("Max Take-Off Weight (kg)", value=12.0)
speed = st.sidebar.number_input("Max Speed (m/s)", value=36.0)
wing_span = st.sidebar.number_input("Wingspan (m)", value=2.6)
chord = st.sidebar.number_input("Chord (m)", value=0.3)

half_span = wing_span / 2
lift_total = MTOW * 9.81  # Newton
lift_half = lift_total / 2  # Assume symmetric

st.sidebar.subheader("Spar 1 (Front)")
spar1_OD = st.sidebar.number_input("OD Front Spar (mm)", value=20) / 1000
spar1_ID = st.sidebar.number_input("ID Front Spar (mm)", value=18) / 1000

st.sidebar.subheader("Spar 2 (Rear)")
spar2_OD = st.sidebar.number_input("OD Rear Spar (mm)", value=10) / 1000
spar2_ID = st.sidebar.number_input("ID Rear Spar (mm)", value=8) / 1000

spar_length = st.sidebar.number_input("Spar Length (m)", value=1.2)
density = st.sidebar.number_input("Material Density (g/cm³)", value=1.6) * 1000  # kg/m³

# --- FUNCTION DEFINITIONS ---
def moment_of_inertia(OD, ID):
    return (np.pi / 64) * (OD**4 - ID**4)

def calc_deflection(F, L, E, I):
    return (F * L**3) / (3 * E * I)

def bending_stress(F, L, I, OD):
    c = OD / 2
    M = F * L
    return M * c / I

def shear_stress(F, A):
    return F / A

# --- CALCULATIONS ---
E = 70e9  # Young's modulus (Pa) assumed for carbon fiber
F = lift_half
L = half_span

# Spar 1 (Front)
I1 = moment_of_inertia(spar1_OD, spar1_ID)
stress1 = bending_stress(F, L, I1, spar1_OD)
deflection1 = calc_deflection(F, L, E, I1)
area1 = np.pi * (spar1_OD**2 - spar1_ID**2) / 4
shear1 = shear_stress(F, area1)

# Spar 2 (Rear)
I2 = moment_of_inertia(spar2_OD, spar2_ID)
stress2 = bending_stress(F, L, I2, spar2_OD)
deflection2 = calc_deflection(F, L, E, I2)
area2 = np.pi * (spar2_OD**2 - spar2_ID**2) / 4
shear2 = shear_stress(F, area2)

# --- DISPLAY RESULTS ---
col1, col2 = st.columns(2)

with col1:
    st.metric("Half Wing Load (N)", f"{F:.2f}")
    st.metric("Half Span (m)", f"{L:.2f}")
    st.metric("Young's Modulus (Pa)", f"{E:.1e}")

with col2:
    st.metric("Chord (m)", f"{chord:.3f}")
    st.metric("Total Lift (N)", f"{lift_total:.1f}")

st.subheader("📊 Spar Structural Analysis")
df = pd.DataFrame({
    "Spar": ["Front Spar (OD 20mm)", "Rear Spar (OD 10mm)"],
    "Moment of Inertia (m⁴)": [I1, I2],
    "Bending Stress (Pa)": [stress1, stress2],
    "Deflection at Tip (m)": [deflection1, deflection2],
    "Shear Stress (Pa)": [shear1, shear2],
    "Cross-sectional Area (m²)": [area1, area2],
})
st.dataframe(df.style.format({
    "Moment of Inertia (m⁴)": "{:.2e}",
    "Bending Stress (Pa)": "{:.2e}",
    "Deflection at Tip (m)": "{:.5f}",
    "Shear Stress (Pa)": "{:.2e}",
    "Cross-sectional Area (m²)": "{:.2e}"
}))

# --- PLOT ---
fig = go.Figure()
fig.add_trace(go.Bar(name='Bending Stress (Pa)', x=df['Spar'], y=df['Bending Stress (Pa)']))
fig.add_trace(go.Bar(name='Shear Stress (Pa)', x=df['Spar'], y=df['Shear Stress (Pa)']))
fig.update_layout(title="Stress Comparison", barmode='group', template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# --- WEIGHT ESTIMATION ---
weight1 = spar_length * area1 * density
weight2 = spar_length * area2 * density

total_weight = weight1 + weight2

st.success(f"Estimated Spar Weight Total: {total_weight:.2f} kg")
