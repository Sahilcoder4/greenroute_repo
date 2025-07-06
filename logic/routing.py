
import openrouteservice
from opencage.geocoder import OpenCageGeocode
import streamlit as st

# Load secrets
ORS_API_KEY = st.secrets["ORS_API_KEY"]
OC_API_KEY = st.secrets["OPENCAGE_API_KEY"]

ors_client = openrouteservice.Client(key=ORS_API_KEY)
geocoder = OpenCageGeocode(OC_API_KEY)

def get_coordinates(city_name):
    results = geocoder.geocode(city_name, countrycode='in', limit=1)
    if not results:
        raise Exception(f"Could not geocode '{city_name}'. Try another city.")

    lat = results[0]['geometry']['lat']
    lng = results[0]['geometry']['lng']
    coords = [lng, lat]  # [lon, lat]

    st.write(f"📍 Geocoded {city_name}: {lat}, {lng}")

    try:
        snapped = ors_client.nearest(coordinates=coords)
        snapped_coords = snapped['coordinates']
        st.write(f"🔗 Snapped {city_name} to routable point: {snapped_coords}")
        return snapped_coords
    except Exception as e:
        st.warning(f"⚠️ Snapping failed for {city_name}. Using raw coordinates.")
        return coords

def extract_route_info(route):
    route_coords = [[lat, lon] for lon, lat in route["geometry"]["coordinates"]]
    distance_km = round(route["properties"]["segments"][0]["distance"] / 1000, 2)
    return {"coordinates": route_coords, "distance_km": distance_km}

def get_optimized_route(start_city, end_city):
    start_coords = get_coordinates(start_city)
    end_coords = get_coordinates(end_city)
    coords = [start_coords, end_coords]

    try:
        # Baseline
        baseline_result = ors_client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson'
        )
        baseline_route = extract_route_info(baseline_result["features"][0])

        # Try optimized route if long enough
        if baseline_route["distance_km"] >= 100:
            alt_result = ors_client.directions(
                coordinates=coords,
                profile='driving-car',
                format='geojson',
                alternative_routes={"share_factor": 0.6, "target_count": 1}
            )
            routes = alt_result["features"]
            if len(routes) >= 2:
                optimized_route = extract_route_info(routes[1])
                note = "✅ Optimized route applied (shorter alternative used)"
            else:
                optimized_route = None
                note = "⚠️ No alternative route found. Using baseline."
        else:
            optimized_route = None
            note = "ℹ️ Optimization skipped: trip is short or limited."

    except openrouteservice.exceptions.ApiError as e:
        optimized_route = None
        baseline_route = {"coordinates": coords, "distance_km": 0}
        note = f"❌ Routing failed: {e}. Using fallback baseline."

    return {
        "baseline": baseline_route,
        "optimized": optimized_route,
        "start": start_coords,
        "end": end_coords,
        "note": note
    }
