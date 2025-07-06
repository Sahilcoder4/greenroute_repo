import folium

def plot_map(city_data):
    if not city_data:
        return folium.Map(location=[0, 0], zoom_start=2)

    start_lat, start_lon = city_data[0]["lat"], city_data[0]["lon"]
    m = folium.Map(location=[start_lat, start_lon], zoom_start=6)

    # Draw route line
    coords = [(c["lat"], c["lon"]) for c in city_data]
    folium.PolyLine(coords, color="blue", weight=4.5, opacity=0.8).add_to(m)

    # Add city markers
    for city in city_data:
        folium.Marker(
            location=[city["lat"], city["lon"]],
            tooltip=f"{city['city']}<br>CO₂ (Cumulative): {city['co2']} kg",
            icon=folium.Icon(color="green" if city["co2"] < 300 else "red")
        ).add_to(m)

    return m
