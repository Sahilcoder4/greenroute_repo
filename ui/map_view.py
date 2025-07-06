import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



import os
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import pandas as pd
from io import StringIO
import setup_path  # ⬅️ This adds the root to path dynamically

from logic.routing import get_optimized_route

from logic.emissions import calculate_emissions
from logic.gemini_explainer import ask_gemini

# Initialize session state
if "route_data" not in st.session_state:
    st.session_state.route_data = None
    st.session_state.city_data = None
    st.session_state.total_distance_km = 0
    st.session_state.optimized = False

st.set_page_config(page_title="GreenRoute Map View", layout="wide")
st.title("🗺️ CO₂ Emission Map View")

# Inputs
start_city = st.text_input("Enter Start City")
end_city = st.text_input("Enter End City")
vehicle_type = st.selectbox("Vehicle Type", [
    "Van (<3.5t)",
    "Rigid truck (7.5t)",
    "Rigid truck (12t)",
    "Rigid truck (18t)",
    "Articulated truck (40t)",
    "HGV (>20t)",
    "Auto Carrier",
    "Refrigerated Truck",
    "Flatbed Truck",
    "General Cargo Truck"
])



fuel_type = st.selectbox("Fuel Type", [
    "Diesel",
    "Petrol",
    "CNG",
    "LNG",
    "Biodiesel",
    "Electric",
    "Hybrid"
])

region = st.selectbox("Region", [
    "Europe & South America", "North America", "China"])  # or from df["Region"].unique()


load_tons = st.slider("Load (tons)", 1.0, 40.0, 10.0)

# Generate Route
if st.button("Generate Route and Emissions"):
    try:
        route_data = get_optimized_route(start_city, end_city)

        # Use optimized if available
        selected_route = route_data["optimized"] if route_data["optimized"] else route_data["baseline"]
        st.session_state.optimized = route_data["optimized"] is not None

        route_coords = selected_route["coordinates"]
        total_distance_km = selected_route["distance_km"]

        sampled_coords = route_coords[::10] + [route_coords[-1]]
        segment_distance = round(total_distance_km / len(sampled_coords), 2)

        city_data = []
        cumulative = 0
        for idx, [lat, lon] in enumerate(sampled_coords):
            co2 = calculate_emissions(vehicle_type, fuel_type, segment_distance, load_tons, region)
            cumulative += co2["WTW"]
            city_data.append({
                "city": f"Point {idx+1}",
                "lat": lat,
                "lon": lon,
                "Vehicle Type": vehicle_type,
                "Fuel Type": fuel_type,
                "Region": region,
                "Segment Distance (km)": segment_distance,
                "WTT (kg)": round(co2["WTT"], 2),
                "TTW (kg)": round(co2["TTW"], 2),
                "WTW (kg)": round(co2["WTW"], 2),
                "co2": round(cumulative, 2)  # ✅ now shows cumulative!
            })

        
        st.session_state.route_data = route_data
        st.session_state.city_data = city_data
        st.session_state.total_distance_km = total_distance_km

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Map + Summary
if st.session_state.route_data and st.session_state.city_data:
    route_coords = st.session_state.route_data["optimized"]["coordinates"] if st.session_state.optimized else st.session_state.route_data["baseline"]["coordinates"]
    city_data = st.session_state.city_data
    total_distance_km = st.session_state.total_distance_km

    m = folium.Map(location=route_coords[len(route_coords)//2], zoom_start=7)
    folium.PolyLine(route_coords, color="blue", weight=4).add_to(m)

    for city in city_data:
        folium.Marker(
            location=[city["lat"], city["lon"]],
            tooltip=f"{city['city']}<br>CO₂: {city['co2']} KG",
            icon=folium.Icon(color="green" if city["co2"] < 300 else "red")
        ).add_to(m)

    HeatMap([[c["lat"], c["lon"], c["co2"]] for c in city_data], min_opacity=0.3, radius=20).add_to(m)

    st.subheader("🌍 Route + Heatmap View")
    folium_static(m)

    st.subheader("📊 Trip Summary")
    st.write(f"**Start:** {start_city}")
    st.write(f"**End:** {end_city}")
    st.write(f"**Total Distance:** {total_distance_km} km")
    st.write(f"**Vehicle:** {vehicle_type}")
    st.write(f"**Fuel:** {fuel_type}")
    st.write(f"**Load:** {load_tons} tons")
    st.write(f"**Estimated WTW CO₂ Emission:** {city_data[-1]['co2']} kg")

        # -------------------------------
    # ⚖️ Compare emissions by fuel
    # -------------------------------
    st.subheader("⚖️ CO₂ Comparison Across Fuel Types")
    fuel_options = ["diesel", "petrol", "cng", "lng", "electric"]
    other_fuels = [f for f in fuel_options if f != fuel_type.lower()]

    emissions_comparison = {}

    for alt_fuel in other_fuels:
        try:
            alt_emissions = sum([
                calculate_emissions(vehicle_type, alt_fuel, segment_distance, load_tons, region)["WTW"]
                for _ in city_data
            ])
            emissions_comparison[alt_fuel.title()] = round(alt_emissions, 2)
        except:
            emissions_comparison[alt_fuel.title()] = None
            # st.warning(f"No data for {vehicle_type} with {alt_fuel.title()}")

    # Show result as a bar chart
    # ✅ Store comparison results in session state
    st.session_state.emissions_comparison = emissions_comparison
    st.bar_chart({k: v for k, v in st.session_state.emissions_comparison.items() if v is not None})

    st.info(st.session_state.route_data["note"])

    if st.session_state.optimized:
        baseline_coords = st.session_state.route_data["baseline"]["coordinates"]
        baseline_distance = st.session_state.route_data["baseline"]["distance_km"]
        baseline_segments = baseline_coords[::10] + [baseline_coords[-1]]
        baseline_segment_distance = round(baseline_distance / len(baseline_segments), 2)

        # Recalculate baseline emissions freshly
        baseline_emissions = 0
        for _ in baseline_segments:
            co2 = calculate_emissions(vehicle_type, fuel_type, baseline_segment_distance, load_tons, region)
            baseline_emissions += co2["WTW"]

        # ✅ Use only final cumulative optimized emission
        optimized_emissions = city_data[-1]["co2"]

        savings = round((baseline_emissions - optimized_emissions) / baseline_emissions * 100, 2)
        st.success(f"🚀 Optimization saved {savings}% CO₂ vs baseline.")
    # === Show comparison chart always, even after rerun ===
    


# Gemini Panel
st.subheader("🤖 Ask GreenRoute AI (Gemini)")
user_question = st.text_input("Ask anything about this trip...")

if user_question and st.session_state.city_data:
    with st.spinner("Thinking..."):
        try:
            trip_context = (
                f"Vehicle: {vehicle_type}, Fuel: {fuel_type}, "
                f"Load: {load_tons} tons, Distance: {st.session_state.total_distance_km} km, "
                f"Total CO₂: {round(st.session_state.city_data[-1]['co2'], 2)} kg"
            )
            response = ask_gemini(user_question, trip_context)
            st.info(response)
        except Exception as e:
            st.error(f"Gemini error: {str(e)}")

# CSV Download
if st.session_state.city_data:
    df = pd.DataFrame(st.session_state.city_data)
    df["Vehicle"] = vehicle_type
    df["Fuel"] = fuel_type
    df["Load (tons)"] = load_tons
    df["Segment Distance (km)"] = round(st.session_state.total_distance_km / len(df), 2)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="📥 Download Trip Report (CSV)",
        data=csv_bytes,
        file_name="greenroute_trip_report.csv",
        mime="text/csv"
    )
