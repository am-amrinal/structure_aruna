import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Title
st.set_page_config(page_title="UAV Spar Structure Analysis", layout="wide", page_icon="🚁")
st.title("UAV Wing Spar Structure Analysis")

# Sidebar Inputs
st.sidebar.header("Input Parameters")

# Constants
g = 9.81  # gravity [m/s^2]

# UAV and Spar Inputs
MTOW = st.sidebar.number_input("MTOW [kg]", value=12.0)
max_speed = st.sidebar.number_input("Max Speed [m/s]", value=36.0)
wing_span = st.sidebar.number_input("Total Wingspan [m]", value=2.6)
half_span = wing_span / 2
chord = st.sidebar.number_input("Chord Length [m]", value=0.3)

# Spar dimensions
st.sidebar.subheader("Spar Dimensions")
OD1 = st.sidebar.number_input("Front Spar OD [mm]", value=20) / 1000
ID1 = st.sidebar.number_input("Front Spar ID [mm]", value=18) / 1000
OD2 = st.sidebar.number_input("Rear Spar OD [mm]", value=10) / 1000
ID2 = st.sidebar.number_input("Rear Spar ID [mm]", value=8) / 1000
spar_length = st.sidebar.number_input("Spar Length [m]", value=1.2)

# Material properties
E = st.sidebar.number_input("Modulus of Elasticity E [GPa]", value=70.0) * 1e9
density = st.sidebar.number_input("Carbon Tube Density [g/cm^3]", value=1.6) * 1000  # kg/m3
skin_thickness = st.sidebar.number_input("Skin Thickness [mm]", value=0.5) / 1000

# Load Calculations
W = MTOW * g
F = W / 2  # Load per wing
w = F / half_span

# Moment of Inertia (circular tube): I = pi/64 * (OD^4 - ID^4)
I1 = (np.pi / 64) * (OD1**4 - ID1**4)
I2 = (np.pi / 64) * (OD2**4 - ID2**4)
I_skin = (1/12) * (skin_thickness * chord**3)  # approximate flat plate
I_total = I1 + I2 + I_skin

# Bending Deflection
delta_max = (5 * w * half_span**4) / (384 * E * I_total)

def check_status(val, limit):
    return "✅ Safe" if val < limit else "❌ Exceeds"

# Bending Stress and Shear Stress
c = OD1 / 2  # distance to outer fiber (largest tube)
M_max = (w * half_span**2) / 2
bending_stress = M_max * c / I_total
shear_stress = (3/2) * (F / (np.pi * (OD1**2 - ID1**2)))

# Allowable limits (can be adjusted)
bend_limit = 300e6  # 300 MPa
shear_limit = 60e6  # 60 MPa
deflect_limit = 0.05  # 5 cm

# Weight Calculation
volume_spar1 = np.pi * (OD1**2 - ID1**2) / 4 * spar_length
volume_spar2 = np.pi * (OD2**2 - ID2**2) / 4 * spar_length
mass_spar1 = volume_spar1 * density
mass_spar2 = volume_spar2 * density
mass_skin = chord * spar_length * skin_thickness * density
mass_ribs = 0.3  # estimate
mass_total = mass_spar1 + mass_spar2 + mass_skin + mass_ribs

# Display results
col1, col2 = st.columns(2)

with col1:
    st.metric("Deflection Max (m)", f"{delta_max:.4f}", check_status(delta_max, deflect_limit))
    st.metric("Bending Stress (MPa)", f"{bending_stress/1e6:.2f}", check_status(bending_stress, bend_limit))
    st.metric("Shear Stress (MPa)", f"{shear_stress/1e6:.2f}", check_status(shear_stress, shear_limit))

with col2:
    st.metric("Weight Front Spar (g)", f"{mass_spar1*1000:.1f}")
    st.metric("Weight Rear Spar (g)", f"{mass_spar2*1000:.1f}")
    st.metric("Weight Skin (g)", f"{mass_skin*1000:.1f}")
    st.metric("Est. Total Wing Weight (g)", f"{mass_total*1000:.1f}")

# Plotting
x = ["Deflection", "Bending Stress", "Shear Stress"]
y = [delta_max, bending_stress, shear_stress]
limits = [deflect_limit, bend_limit, shear_limit]
status = [check_status(delta_max, deflect_limit),
          check_status(bending_stress, bend_limit),
          check_status(shear_stress, shear_limit)]

fig, ax = plt.subplots()
ax.plot(x, y, marker='o', label='Value')
ax.plot(x, limits, linestyle='--', label='Limit')
for i, s in enumerate(status):
    ax.text(x[i], y[i], s, fontsize=10, color='green' if 'Safe' in s else 'red')
ax.set_ylabel("Value")
ax.set_title("Stress & Deflection vs Limit")
ax.legend()
st.pyplot(fig)

# Export to CSV
csv_data = pd.DataFrame({
    "Metric": x,
    "Value": y,
    "Limit": limits,
    "Status": status
})

csv = csv_data.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "spar_analysis.csv", "text/csv")

# Export to PDF
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="UAV Spar Structural Analysis", ln=True, align='C')
    for i in range(len(x)):
        pdf.cell(200, 10, txt=f"{x[i]}: {y[i]:.4f} | Limit: {limits[i]} | {status[i]}", ln=True)
    pdf.cell(200, 10, txt=f"Total Wing Mass: {mass_total*1000:.1f} g", ln=True)
    return pdf.output(dest='S').encode('latin1')

pdf_data = create_pdf()
st.download_button("Export to PDF", pdf_data, file_name="uav_spar_analysis.pdf")
