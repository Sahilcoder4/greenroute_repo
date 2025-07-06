import sys
import os
import streamlit as st
import pandas as pd

# ✅ Add root folder to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.emissions import calculate_emissions, df as emissions_df

st.set_page_config(page_title="GreenRoute Emissions Calculator", layout="centered")

st.title("🚛 GreenRoute CO₂ Emission Estimator")
st.markdown("Estimate WTT, TTW and WTW CO₂ emissions using GLEC Framework + ISO 14083 standards.")

# Get available vehicle types
vehicle_options = sorted(emissions_df["Vehicle Type"].dropna().unique())
vehicle_type = st.selectbox("Select Vehicle Type", vehicle_options)

# Filter fuels based on selected vehicle
filtered_fuels = emissions_df[emissions_df["Vehicle Type"] == vehicle_type]["Fuel"].unique()
fuel_type = st.selectbox("Select Fuel Type", filtered_fuels)

# Distance & Load inputs
distance_km = st.number_input("Trip Distance (in km)", min_value=1, max_value=5000, value=300)
load_tons = st.number_input("Load Weight (in tonnes)", min_value=0.1, max_value=100.0, value=10.0, step=0.1)

# Trigger emission calculation
if st.button("Calculate Emissions"):
    try:
        results = calculate_emissions(vehicle_type, fuel_type, distance_km, load_tons)
        
        st.success("✅ Emissions Calculated Successfully!")
        st.metric("📦 Load", f"{load_tons} tons")
        st.metric("🛣️ Distance", f"{distance_km} km")

        st.subheader("💨 CO₂ Emissions Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("WTT", f"{results['WTT']} kg")
        col2.metric("TTW", f"{results['TTW']} kg")
        col3.metric("WTW", f"{results['WTW']} kg")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
