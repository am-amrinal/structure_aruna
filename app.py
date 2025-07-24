import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="UAV Structure Analysis")

st.title("✈️ UAV Structure Analysis Dashboard")
st.markdown("Analyze **spar**, **ribs**, and **composite skin** contributions for UAV wings.")

with st.sidebar:
    st.header("Geometry & Load")
    span = st.number_input("Half-Span Length (m)", value=1.3)
    total_force = st.number_input("Total Lift Force (N)", value=120.0)
    chord = st.number_input("Chord Length (m)", value=0.3)

    st.header("Spar 1 (Front)")
    spar1_od = st.number_input("Front Spar OD (mm)", value=20.0)
    spar1_id = st.number_input("Front Spar ID (mm)", value=18.0)

    st.header("Spar 2 (Rear)")
    spar2_od = st.number_input("Rear Spar OD (mm)", value=10.0)
    spar2_id = st.number_input("Rear Spar ID (mm)", value=8.0)

    st.header("Material")
    spar_E = st.number_input("Spar Young's Modulus (GPa)", value=140.0)
    spar_density = st.number_input("Spar Density (g/cm³)", value=1.6)

    st.header("Skin Contribution")
    skin_thickness = st.number_input("Skin Thickness (mm)", value=0.5)
    skin_E = st.number_input("Skin Young's Modulus (GPa)", value=70.0)
    skin_effective_height = st.number_input("Effective Height from Neutral Axis (mm)", value=15.0)

# Moment of inertia for circular tube (mm^4)
def moment_of_inertia_tube(od_mm, id_mm):
    return (np.pi / 64) * (od_mm**4 - id_mm**4)

# Moment of inertia for skin (as 2 flanges)
def moment_of_inertia_skin(t_mm, b_mm, h_mm):
    return 2 * b_mm * t_mm * (h_mm**2)

# === CALCULATION ===
F = total_force / 2  # N, half wing load
L = span  # m
E_spar = spar_E * 1e9  # GPa to Pa
E_skin = skin_E * 1e9

# Convert I to m^4
I_spar1 = moment_of_inertia_tube(spar1_od, spar1_id) * 1e-12
I_spar2 = moment_of_inertia_tube(spar2_od, spar2_id) * 1e-12
I_skin = moment_of_inertia_skin(skin_thickness, chord * 1000, skin_effective_height) * 1e-12

I_total = I_spar1 + I_spar2 + I_skin
E_equiv = (E_spar * (I_spar1 + I_spar2) + E_skin * I_skin) / I_total

# Max Deflection using uniform load assumption (conservative)
w = F / L  # N/m
delta_max = (5 * w * L**4) / (384 * E_equiv * I_total)  # m

# Display Results
st.subheader("🧮 Structural Results")
st.metric("Tip Deflection (mm)", f"{delta_max*1000:.4f}")
status = "✅ Aman" if delta_max*1000 < 15 else "⚠️ Berisiko"
st.markdown(f"**Status**: {status}")

st.subheader("📏 Moment of Inertia")
st.write(f"I Spar 1 = {I_spar1:.2e} m⁴")
st.write(f"I Spar 2 = {I_spar2:.2e} m⁴")
st.write(f"I Skin   = {I_skin:.2e} m⁴")
st.write(f"**I Total**  = {I_total:.2e} m⁴")

# Plotting
x = np.linspace(0, L, 200)
deflection_curve = (5 * w * x**4) / (384 * E_equiv * I_total)

fig, ax = plt.subplots()
ax.plot(x, deflection_curve * 1000)
ax.set_title("Deflection Curve")
ax.set_xlabel("Span (m)")
ax.set_ylabel("Deflection (mm)")
ax.grid(True)
st.pyplot(fig)
