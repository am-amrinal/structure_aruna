import streamlit as st
import numpy as np

st.set_page_config(page_title="UAV Spar Structure Analysis", layout="wide", page_icon="🛩️")

st.title("🛩️ UAV Spar Structure Analysis Dashboard")

with st.sidebar:
    st.header("Input Parameters")

    MTOW = st.number_input("MTOW (kg)", value=12.0)
    wingspan = st.number_input("Wingspan (m)", value=2.6)
    half_span = wingspan / 2
    chord = st.number_input("Chord Length (m)", value=0.3)
    spar1_pos = st.slider("Front Spar Position (% chord)", 0, 100, 30) / 100
    spar2_pos = st.slider("Rear Spar Position (% chord)", 0, 100, 65) / 100

    g = 9.81
    total_force = MTOW * g
    half_force = total_force / 2

    L = st.number_input("Spar Length (m)", value=1.2)

    st.subheader("Spar 1 - Front")
    od1 = st.number_input("Outer Diameter Spar 1 (mm)", value=20.0) / 1000
    id1 = st.number_input("Inner Diameter Spar 1 (mm)", value=18.0) / 1000

    st.subheader("Spar 2 - Rear")
    od2 = st.number_input("Outer Diameter Spar 2 (mm)", value=10.0) / 1000
    id2 = st.number_input("Inner Diameter Spar 2 (mm)", value=8.0) / 1000

    st.subheader("Composite Skin")
    skin_thk = st.number_input("Skin Thickness (mm)", value=0.5) / 1000
    skin_E = st.number_input("Skin Modulus E (GPa)", value=25.0) * 1e9

    E = st.number_input("Spar Modulus E (GPa)", value=70.0) * 1e9  # typical for carbon fiber
    density = st.number_input("Material Density (g/cm³)", value=1.6) * 1000  # kg/m³

# Spar moment of inertia
def I_tube(od, id):
    return (np.pi / 64) * (od**4 - id**4)

I1 = I_tube(od1, id1)
I2 = I_tube(od2, id2)

# Assume spar spacing equals full chord distance
spar_spacing = abs(spar2_pos - spar1_pos) * chord

# Composite skin moment of inertia approximation (as two flanges)
I_skin = 2 * (skin_thk * spar_spacing * (0.5 * spar_spacing)**2)

# Total I
I_total = I1 + I2 + I_skin

# Distributed load for half wing
w = half_force / L

# Deflection using beam formula: δ = (5wL⁴) / (384EI)
delta_max = (5 * w * L**4) / (384 * (E * (I1 + I2) + skin_E * I_skin))

# Spar weight
vol1 = np.pi * (od1**2 - id1**2) / 4 * L
vol2 = np.pi * (od2**2 - id2**2) / 4 * L
mass1 = vol1 * density
mass2 = vol2 * density

st.subheader("🧮 Results")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Lift Force (Half Wing)", f"{half_force:.2f} N")
    st.metric("Bending Deflection (δ_max)", f"{delta_max*1000:.2f} mm")
with col2:
    st.metric("Spar 1 Mass", f"{mass1:.2f} kg")
    st.metric("Spar 2 Mass", f"{mass2:.2f} kg")

st.caption("Deflection formula: δ_max = (5wL⁴)/(384EI), assuming uniformly distributed load.")
