import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="UAV Spar Structural Dashboard", page_icon="✈️")

st.title("✈️ UAV Structure Analysis Dashboard")
st.markdown("Analyze **spar**, **ribs**, and **composite skin** contributions for UAV wings.")

with st.sidebar:
    st.header("Geometry & Load")
    span = st.number_input("Half-Span Length (m)", value=1.3)
    total_force = st.number_input("Total Lift Force (N)", value=120.0)
    chord = st.number_input("Chord Length (m)", value=0.3)

    st.header("Spar 1 (Front)")
    od1 = st.number_input("Front Spar OD (mm)", value=20.0)
    id1 = st.number_input("Front Spar ID (mm)", value=18.0)

    st.header("Spar 2 (Rear)")
    od2 = st.number_input("Rear Spar OD (mm)", value=10.0)
    id2 = st.number_input("Rear Spar ID (mm)", value=8.0)

    st.header("Material")
    youngs_modulus = st.number_input("Young's Modulus (GPa)", value=140.0)
    density = st.number_input("Material Density (g/cm³)", value=1.6)

    st.header("Ribs & Skin")
    rib_spacing = st.number_input("Rib Spacing (m)", value=0.15)
    skin_thickness = st.number_input("Skin Thickness (mm)", value=0.5)
    skin_E = st.number_input("Skin Modulus (GPa)", value=70.0)

# === Calculations ===
def mm2_to_m4(mm4): return mm4 * 1e-12

def tube_inertia(od, id_):
    return (np.pi / 64) * (od**4 - id_**4)

def skin_inertia(b, t):
    return (b * t**3) / 12

# Spar inertia in mm^4
I1 = tube_inertia(od1, id1)
I2 = tube_inertia(od2, id2)

# Skin inertia (m converted to mm)
skin_width = chord * 1000  # mm
skin_t = skin_thickness    # mm
I_skin = skin_inertia(skin_width, skin_t)

# Adjust skin modulus to equivalent to spar modulus
n_mod = skin_E / youngs_modulus
I_skin_eq = I_skin * n_mod

I_total = I1 + I2 + I_skin_eq

L = span
F = total_force / 2  # Half-wing load
w = total_force / (2 * L)
E = youngs_modulus * 1e9

delta_max = (5 * w * L**4) / (384 * E * mm2_to_m4(I_total))  # m
stress_max = (F * L * (od1 / 2)) / mm2_to_m4(I_total)
shear_stress = F / (np.pi * ((od1 / 1000)**2 - (id1 / 1000)**2))

# Status
deflection_status = "✅ Aman" if delta_max*1000 < 20 else "⚠️ Berisiko"

col1, col2 = st.columns(2)
with col1:
    st.subheader("🧮 Structural Results")
    st.metric("Max Bending Stress (Pa)", f"{stress_max:,.0f}")
    st.metric("Tip Deflection (mm)", f"{delta_max*1000:.4f}")
    st.metric("Shear Stress (Pa)", f"{shear_stress:,.0f}")
    st.success(f"Status Defleksi: {deflection_status}")

with col2:
    st.subheader("📏 Combined Moment of Inertia")
    st.write(f"I Spar 1 = {I1:.2e} mm⁴")
    st.write(f"I Spar 2 = {I2:.2e} mm⁴")
    st.write(f"I Skin  = {I_skin:.2e} mm⁴")
    st.write(f"I Skin Eq = {I_skin_eq:.2e} mm⁴")
    st.write(f"I Total  = {I_total:.2e} mm⁴")

# === Visualization ===
x = np.linspace(0, L, 200)
M = F * (L - x)
delta = (F * x**2) * (3*L - x) / (6 * E * mm2_to_m4(I_total))

fig, ax = plt.subplots(1, 2, figsize=(10, 3))
ax[0].plot(x, M)
ax[0].set_title("Bending Moment Diagram")
ax[0].set_xlabel("Wing Span (m)")
ax[0].set_ylabel("Moment (Nm)")
ax[0].grid(True)

ax[1].plot(x, delta*1000)
ax[1].set_title("Deflection Curve")
ax[1].set_xlabel("Wing Span (m)")
ax[1].set_ylabel("Deflection (mm)")
ax[1].grid(True)

st.pyplot(fig)
