# 🌱 GreenRoute – Intelligent CO₂ Emission Routing App

GreenRoute is a smart web application that helps users calculate and compare CO₂ emissions for trips between cities using real road data. It supports route optimization, fuel comparisons, region-specific emission standards, and visual heatmaps — all in one Streamlit app.

---

## 🚀 Features

### ✅ Route Planning with Optimization
- Calculates both baseline and optimized routes between two cities
- Uses OpenRouteService with OpenStreetMap
- Supports long trips with alternative route selection (`target_count=1`)

### ✅ CO₂ Emission Calculation (ISO 14083 + GLEC Compliant)
- Calculates **Well-to-Tank (WTT)**, **Tank-to-Wheel (TTW)**, and **Well-to-Wheel (WTW)** emissions
- Supports region-specific standards (Europe, North America, etc.)
- Vehicle + fuel type lookup from official GLEC Framework tables (pages 97–104)

### ✅ City-wise Emissions with Cumulative Logic
- Emission values shown at each city-like segment
- Hovering over markers shows cumulative CO₂ up to that point

### ✅ Fuel Comparison
- Compare selected fuel with other types (Diesel, Petrol, Electric, CNG, etc.)
- Visualized with an interactive bar chart

### ✅ Heatmap Visualization
- Dynamic CO₂ intensity heatmap overlaid on route using Folium

### ✅ Gemini AI Box (Generative AI)
- Ask contextual questions about the trip, emissions, vehicle type, or optimization
- Uses Google’s Gemini 1.5 Pro model

### ✅ Downloadable Trip Report
- Export full trip CO₂ breakdown as CSV
- Includes segment emissions, vehicle details, fuel, and region

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Folium
- **Backend:** Python
- **Routing API:** OpenRouteService
- **AI Integration:** Gemini (Google Generative AI)
- **Standards:** ISO 14083, GLEC Framework (2025)

---
## Notes

- openrouteservice → for routing

- google-generativeai → for Gemini box

- streamlit-folium → to render interactive map

- geopy (optional) → if you later use reverse geocoding

## Acknowledgements
- GLEC Framework v3.1 (March 2025)

- OpenRouteService

- Google Gemini AI

## 📦 Setup Instructions

1. Clone the repository or download the ZIP
2. Install dependencies:

```bash
pip install -r requirements.txt

