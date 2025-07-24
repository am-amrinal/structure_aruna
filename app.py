import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Judul Aplikasi
st.title("🛩️ UAV Structure Analysis Dashboard")
st.markdown("""
Analyze spar, ribs, and composite skin contributions for UAV wings.
""")

# Sidebar Inputs
st.sidebar.header("Geometry & Load")
half_span = st.sidebar.number_input("Half Span Length (m)", value=1.3)
total_lift = st.sidebar.number_input("Total Lift Force (N)", value=1200)
chord_length = st.sidebar.number_input("Chord Length (m)", value=0.3)

st.sidebar.header("Spar 1 (Front)")
spar1_od = st.sidebar.number_input("Front Spar OD (mm)", value=20.0)
spar1_id = st.sidebar.number_input("Front Spar ID (mm)", value=18.0)

st.sidebar.header("Spar 2 (Rear)")
spar2_od = st.sidebar.number_input("Rear Spar OD (mm)", value=10.0)
spar2_id = st.sidebar.number_input("Rear Spar ID (mm)", value=8.0)

st.sidebar.header("Material")
E = st.sidebar.number_input("Young's Modulus (GPa)", value=140.0) * 1e9
material_density = st.sidebar.number_input("Material Density (g/cm³)", value=1.6) * 1000  # converted to kg/m³

st.sidebar.header("Ribs & Skin")
rib_spacing = st.sidebar.number_input("Rib Spacing (m)", value=0.15)
skin_thickness = st.sidebar.number_input("Skin Thickness (mm)", value=0.5) / 1000
skin_modulus = st.sidebar.number_input("Skin Modulus (GPa)", value=70.0) * 1e9

# Perhitungan
L = half_span
W = total_lift / 2
w = W / L

def moment_of_inertia_tube(od_mm, id_mm):
    od = od_mm / 1000
    id = id_mm / 1000
    return (np.pi / 64) * (od**4 - id**4)

I_spar1 = moment_of_inertia_tube(spar1_od, spar1_id)
I_spar2 = moment_of_inertia_tube(spar2_od, spar2_id)

# I skin sebagai dua layer atas & bawah
I_skin = (skin_thickness * chord_length**3) / 12
I_skin_eq = 2 * I_skin + 2 * (chord_length / 2)**2 * skin_thickness

I_total = I_spar1 + I_spar2 + I_skin_eq

# Defleksi maksimum
δ_max = (5 * w * L**4) / (384 * E * I_total)
δ_max_mm = δ_max * 1000
status_defleksi = "Aman" if δ_max_mm < 15 else "Berisiko"

# Tegangan lentur maksimum
max_bending_moment = w * L**2 / 2
y_max = (spar1_od / 2) / 1000
σ_max = (max_bending_moment * y_max) / I_total
status_bending = "Aman" if σ_max < 400e6 else "Berisiko"

# Tegangan geser kasar
shear_stress = W / (np.pi * (spar1_od / 1000)**2)
status_shear = "Aman" if shear_stress < 200e6 else "Berisiko"

# Estimasi Berat
num_ribs = int(L / rib_spacing) + 1
rib_weight = 0.05
ribs_weight = num_ribs * rib_weight

spar1_vol = np.pi * ((spar1_od/2)**2 - (spar1_id/2)**2) / 1e6 * L
spar2_vol = np.pi * ((spar2_od/2)**2 - (spar2_id/2)**2) / 1e6 * L
spar_weight = (spar1_vol + spar2_vol) * material_density

skin_area = chord_length * L * 2
skin_weight = skin_area * skin_thickness * material_density

total_weight = ribs_weight + spar_weight + skin_weight

# Output
st.subheader("📊 Structural Results")
st.metric("Max Bending Stress (Pa)", f"{σ_max:,.0f}")
st.metric("Tip Deflection (mm)", f"{δ_max_mm:.4f}")
st.metric("Shear Stress (Pa)", f"{shear_stress:,.0f}")
st.success(f"Status Defleksi: {status_defleksi}")

st.subheader("🧮 Combined Moment of Inertia")
st.markdown(f"""
- I Spar 1 = {I_spar1:.2e} m⁴  
- I Spar 2 = {I_spar2:.2e} m⁴  
- I Skin = {I_skin:.2e} m⁴  
- I Skin Eq = {I_skin_eq:.2e} m⁴  
- I Total = {I_total:.2e} m⁴
""")

# Grafik
x = np.linspace(0, L, 300)
moment = w * x * (L - x / 2)
delta_x = (w / (24 * E * I_total)) * x**2 * (6 * L**2 - 4 * L * x + x**2)
delta_x_mm = delta_x * 1000

fig1, ax1 = plt.subplots()
ax1.plot(x, moment)
ax1.set_title("Bending Moment Diagram")
ax1.set_xlabel("Wing Span (m)")
ax1.set_ylabel("Moment (Nm)")
st.pyplot(fig1)

fig2, ax2 = plt.subplots()
ax2.plot(x, delta_x_mm)
ax2.set_title("Deflection Curve")
ax2.set_xlabel("Wing Span (m)")
ax2.set_ylabel("Deflection (mm)")
st.pyplot(fig2)

# Estimasi Massa
st.subheader("📦 Mass Estimation")
st.markdown(f"""
- Rib Count = {num_ribs} pcs  
- Ribs Weight = {ribs_weight:.2f} kg  
- Spars Weight = {spar_weight:.2f} kg  
- Skin Weight = {skin_weight:.2f} kg  
- **Total Structure Weight** = {total_weight:.2f} kg
""")

# Export
st.subheader("📤 Export")
def convert_df_to_csv():
    csv = f"Max Stress, {σ_max}, Deflection, {δ_max_mm}, Shear Stress, {shear_stress}, Status, {status_defleksi}"
    return csv.encode('utf-8')
st.download_button("📥 Download CSV", convert_df_to_csv(), "analysis_result.csv")
