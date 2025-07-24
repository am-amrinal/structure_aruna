import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="UAV Spar Structure Analysis", layout="wide", page_icon="✈️", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        body, .stApp { background-color: #0e1117; color: white; }
        .sidebar .sidebar-content { background-color: #1c1f26; }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ UAV Spar Structural Analysis Dashboard")
st.markdown("Analyze bending stress, deflection, and safety factor for UAV carbon tube spars under distributed loads.")

with st.sidebar:
    st.header("Input Parameters")
    st.subheader("Aircraft")
    MTOW = st.number_input("Max Takeoff Weight (kg)", value=12.0)
    g = 9.81
    W = MTOW * g  # total weight in Newton

    st.subheader("Wing Geometry")
    L = st.number_input("Half Wing Span (m)", value=1.3)
    chord = st.number_input("Chord Length (m)", value=0.3)

    st.subheader("Spar Geometry & Material")
    OD = st.number_input("Outer Diameter (m)", value=0.020)
    ID = st.number_input("Inner Diameter (m)", value=0.018)
    E = st.number_input("Modulus of Elasticity (Pa)", value=70e9)
    density = st.number_input("Material Density (g/cm³)", value=1.6)

# Calculated values
I = (np.pi / 64) * (OD**4 - ID**4)  # Moment of inertia
A = (np.pi / 4) * (OD**2 - ID**2)   # Cross-sectional area
weight_spar = A * L * density * 1e6 / 1000  # in kg

w = W / (2 * L)  # distributed load per meter (half wing)

deflection_max = (5 * w * L**4) / (384 * E * I)

# Results
st.subheader("📊 Structural Analysis Result")
col1, col2, col3 = st.columns(3)
col1.metric("Moment of Inertia I (m⁴)", f"{I:.2e}")
col2.metric("Distributed Load w (N/m)", f"{w:.2f}")
col3.metric("Spar Weight (kg)", f"{weight_spar:.3f}")

st.write("### 📉 Maximum Deflection")
st.write(f"Deflection (center of beam): **{deflection_max*1000:.3f} mm**")

# Plot deflection shape
x = np.linspace(0, L, 200)
y = (5 * w * x**2 * (L**2 - x**2)) / (384 * E * I)
fig, ax = plt.subplots()
ax.plot(x, y * 1000, color='cyan', label='Deflection (mm)')
ax.set_xlabel('Span Position (m)')
ax.set_ylabel('Deflection (mm)')
ax.set_title('Wing Spar Deflection Profile')
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.caption("Built with ❤️ FORZA ROMA")
