import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import plotly.graph_objs as go

# Constants
g = 9.81  # m/s^2

def tube_inertia(OD, ID):
    return (np.pi / 64) * (OD**4 - ID**4)

def tube_area(OD, ID):
    return (np.pi / 4) * (OD**2 - ID**2)

def calc_structure(params):
    L = params["half_span"]
    W = params["MTOW"]
    q = W * g / (2 * L)  # Uniform distributed load per half wing

    data = []
    total_weight = 0

    for i, spar in enumerate(params["spars"], 1):
        OD = spar["OD"] / 1000
        ID = spar["ID"] / 1000
        length = spar["length"]
        density = spar["density"]

        I = tube_inertia(OD, ID)
        A = tube_area(OD, ID)
        weight = A * length * density * 1000  # in grams

        E = spar["E"]

        sigma_max = (q * L**2) / (8 * I)
        tau_max = (q * L) / (2 * A)
        delta_max = (5 * q * L**4) / (384 * E * I)

        status_deflection = "Safe" if delta_max < 0.05 else "Too Much"
        status_stress = "Safe" if sigma_max < spar["max_stress"] else "Too High"
        status_shear = "Safe" if tau_max < spar["max_shear"] else "Too High"

        data.append({
            "Spar": f"Spar {i}",
            "Bending Stress (MPa)": sigma_max / 1e6,
            "Shear Stress (MPa)": tau_max / 1e6,
            "Max Deflection (mm)": delta_max * 1000,
            "Weight (g)": weight,
            "Deflection Status": status_deflection,
            "Stress Status": status_stress,
            "Shear Status": status_shear
        })

        total_weight += weight

    df = pd.DataFrame(data)
    df["Total Wing Weight (g)"] = total_weight + params["skin_weight"] + params["rib_weight"]
    return df

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="UAV Spar Structural Analysis Report", ln=1, align="C")

    pdf.set_font("Arial", size=10)
    col_width = pdf.w / 6
    pdf.ln(10)

    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()

    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, 10, str(round(row[col], 2)) if isinstance(row[col], float) else str(row[col]), border=1)
        pdf.ln()

    path = "uav_structure_report.pdf"
    pdf.output(path)
    return path

def main():
    st.title("UAV Spar Structure Analysis")

    params = {
        "MTOW": 12,  # kg
        "half_span": 1.3,  # m
        "skin_weight": 420,  # g
        "rib_weight": 200,   # g
        "spars": [
            {"OD": 20, "ID": 18, "length": 1.2, "density": 1.6, "E": 70e9, "max_stress": 600e6, "max_shear": 60e6},
            {"OD": 10, "ID": 8,  "length": 1.2, "density": 1.6, "E": 70e9, "max_stress": 600e6, "max_shear": 60e6},
            {"OD": 18, "ID": 16, "length": 1.2, "density": 1.6, "E": 70e9, "max_stress": 600e6, "max_shear": 60e6},
            {"OD": 8,  "ID": 6,  "length": 1.2, "density": 1.6, "E": 70e9, "max_stress": 600e6, "max_shear": 60e6},
        ]
    }

    df = calc_structure(params)
    st.dataframe(df)

    st.subheader("Line Charts")

    def plot_metric(y, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Spar"], y=df[y], mode='lines+markers', name=y))
        fig.update_layout(title=title, xaxis_title="Spar", yaxis_title=y)
        st.plotly_chart(fig)

    plot_metric("Max Deflection (mm)", "Deflection vs Spar")
    plot_metric("Bending Stress (MPa)", "Bending Stress vs Spar")
    plot_metric("Shear Stress (MPa)", "Shear Stress vs Spar")
    plot_metric("Weight (g)", "Weight vs Spar")

    if st.button("Export as PDF"):
        path = export_pdf(df)
        with open(path, "rb") as file:
            st.download_button("Download PDF", file, file_name="uav_structure_report.pdf")

if __name__ == "__main__":
    main()
