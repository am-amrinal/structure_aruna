# UAV Spar Structural Analysis Dashboard

This Streamlit app allows you to perform structural analysis of a UAV wing spar configuration using hollow carbon tubes and composite skins. It calculates bending stress, shear stress, maximum deflection, and weight estimation for each spar component. It also generates interactive line charts and provides export options.

---

## 📊 Features
- Input design parameters for multiple spars
- Structural analysis:
  - Bending Stress (σ)
  - Shear Stress (τ)
  - Maximum Bending Deflection (δₘₐₓ)
  - Total Weight Estimation (spar, ribs, skin)
- Visual line graphs comparing stress/deflection to safety limits
- Export results:
  - CSV Download
  - PDF Report (basic)
- Responsive dark-mode layout

---

## 🚀 How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
