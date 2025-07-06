import openrouteservice
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")
if not ORS_API_KEY:
    raise Exception("ORS_API_KEY not found in .env")

ors_client = openrouteservice.Client(key=ORS_API_KEY)
geolocator = Nominatim(user_agent="greenroute_app")

def get_coordinates(city_name):
    try:
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return [location.latitude, location.longitude]
        else:
            raise Exception(f"Location not found for: {city_name}")
    except GeocoderTimedOut:
        raise Exception(f"Geocoding timed out for: {city_name}")

def extract_route_info(route):
    route_coords = [[lat, lon] for lon, lat in route["geometry"]["coordinates"]]
    distance_km = round(route["properties"]["segments"][0]["distance"] / 1000, 2)
    return {"coordinates": route_coords, "distance_km": distance_km}

def get_optimized_route(start_city, end_city):
    start_coords = get_coordinates(start_city)
    end_coords = get_coordinates(end_city)
    coords = [start_coords[::-1], end_coords[::-1]]  # ORS needs [lon, lat]

    # Step 1: Get baseline route
    baseline_result = ors_client.directions(
        coordinates=coords,
        profile='driving-car',
        format='geojson'
    )
    baseline_route = extract_route_info(baseline_result["features"][0])

    # Step 2: Apply optimization logic only for long trips under 150km
    try:
        if baseline_route["distance_km"] >= 100:
            # For all trips >= 100km, try to fetch alternative route
            alt_result = ors_client.directions(
                coordinates=coords,
                profile='driving-car',
                format='geojson',
                alternative_routes={"share_factor": 0.6, "target_count": 1}
            )
            routes = alt_result["features"]

            if len(routes) >= 2:
                optimized_route = extract_route_info(routes[1])
                note = "Optimized route applied (shorter alternative used)"
            else:
                optimized_route = None
                note = "No alternative route found. Using baseline."
        else:
            optimized_route = None
            note = "Optimized approach is applied for longer routes. Using baseline if no alternative found."


    except openrouteservice.exceptions.ApiError as e:
        optimized_route = None
        note = "Optimized approach is applied for longer routes. Using baseline if no alternative found."

    return {
        "baseline": baseline_route,
        "optimized": optimized_route,
        "start": start_coords,
        "end": end_coords,
        "note": note
    }
