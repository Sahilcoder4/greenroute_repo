
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from logic.emissions import calculate_emissions
from logic.routing import get_optimized_route
from logic.map_utils import plot_map
from logic.gemini_explainer import ask_gemini

# UI
st.set_page_config(page_title="GreenRoute", layout="wide")
st.title("🌱 GreenRoute – Intelligent CO₂ Emission Routing")

with st.sidebar:
    st.subheader("Trip Details")
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

    # load_tons = st.number_input("Load (tons)", min_value=1.0, value=10.0)
    load_tons = st.slider("Load (tons)", 1.0, 40.0, 10.0)
    go = st.button("🚗 Generate Route & Emissions")

# Trigger
if go:
    with st.spinner("Calculating route and emissions..."):
        st.session_state.route_data = get_optimized_route(start_city, end_city)
        st.session_state.optimized = st.session_state.route_data["optimized"] is not None

        # Use optimized or fallback to baseline
        coords = st.session_state.route_data["optimized"]["coordinates"] if st.session_state.optimized else st.session_state.route_data["baseline"]["coordinates"]
        total_distance_km = st.session_state.route_data["optimized"]["distance_km"] if st.session_state.optimized else st.session_state.route_data["baseline"]["distance_km"]

        sampled_coords = coords[::10] + [coords[-1]]
        segment_distance = round(total_distance_km / len(sampled_coords), 2)
        st.session_state.segment_distance = segment_distance

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
                "co2": round(cumulative, 2)  # for map marker
            })

        st.session_state.city_data = city_data

        # Map
        m = plot_map(city_data)
        st_data = st_folium(m, width=900, height=500)

        # Trip Summary
        st.subheader("📊 Trip Summary")
        st.write(f"**Start:** {start_city}")
        st.write(f"**End:** {end_city}")
        st.write(f"**Total Distance:** {total_distance_km} km")
        st.write(f"**Vehicle:** {vehicle_type}")
        st.write(f"**Fuel:** {fuel_type}")
        st.write(f"**Load:** {load_tons} tons")
        st.write(f"**Estimated WTW CO₂ Emission:** {city_data[-1]['co2']} kg")

        st.info(st.session_state.route_data["note"])

        # Baseline vs Optimized savings
        if st.session_state.optimized:
            baseline_coords = st.session_state.route_data["baseline"]["coordinates"]
            baseline_distance = st.session_state.route_data["baseline"]["distance_km"]
            baseline_segments = baseline_coords[::10] + [baseline_coords[-1]]
            baseline_segment_distance = round(baseline_distance / len(baseline_segments), 2)

            baseline_emissions = 0
            for _ in baseline_segments:
                co2 = calculate_emissions(vehicle_type, fuel_type, baseline_segment_distance, load_tons, region)
                baseline_emissions += co2["WTW"]

            optimized_emissions = city_data[-1]["co2"]
            savings = round((baseline_emissions - optimized_emissions) / baseline_emissions * 100, 2)
            st.success(f"🚀 Optimization saved {savings}% CO₂ vs baseline.")

        # Store fuel comparison for persistence
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

        st.session_state.emissions_comparison = emissions_comparison

        # CSV Download
        df = pd.DataFrame(city_data)
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Trip CO₂ Report", csv, "greenroute_emissions.csv", "text/csv")

# Always show fuel comparison if available
if "emissions_comparison" in st.session_state and st.session_state.emissions_comparison:
    st.subheader("⚖️ CO₂ Comparison Across Fuel Types")
    filtered = {k: v for k, v in st.session_state.emissions_comparison.items() if v is not None}
    if filtered:
        st.bar_chart(filtered)
    else:
        st.info("No valid emission data available for alternative fuels.")

# Gemini AI box
if "city_data" in st.session_state and st.session_state.city_data:
    st.subheader("🤖 Ask GreenRoute AI (Gemini)")
    prompt = st.text_input("Ask about your trip, route, or emissions:")
    if prompt:
        total = st.session_state.city_data[-1]["co2"]
        chat_input = f"""
        Trip from {start_city} to {end_city}
        Vehicle: {vehicle_type}, Fuel: {fuel_type}, Load: {load_tons} tons
        Region: {region}, Total Distance: {total_distance_km} km
        Total CO₂: {round(total, 2)} kg

        Question: {prompt}
        """
        response = ask_gemini(chat_input)
        st.write("🧠 Gemini Response:")
        st.markdown(response)
