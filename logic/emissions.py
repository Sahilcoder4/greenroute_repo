import pandas as pd

# Load and normalize
df = pd.read_csv("data/glec_emission_factors_cleaned.csv")
print("DEBUG: Columns =", df.columns.tolist())
df["Vehicle Type"] = df["Vehicle Type"].str.lower().str.strip()
df["Fuel"] = df["Fuel"].str.lower().str.strip()
df["Region"] = df["Region"].str.lower().str.strip()  # ✅ Normalize Region too

def get_emission_factors(vehicle_type, fuel, region):
    vehicle_type = vehicle_type.lower().strip()
    fuel = fuel.lower().strip()
    region = region.lower().strip()

    # ✅ Apply Region Filter
    match = df[
        (df["Region"] == region) &
        (df["Vehicle Type"].str.contains(vehicle_type.split()[0], case=False)) &
        (df["Fuel"] == fuel)
    ]

    if match.empty:
        raise ValueError(f"No match found for: {vehicle_type} with fuel: {fuel} in region: {region}")

    row = match.iloc[0]

    if pd.isna(row["WTW (g CO2e/t-km)"]):
        wtw = float(row["WTT (g CO2e/t-km)"]) + float(row["TTW (g CO2e/t-km)"])
    else:
        wtw = float(row["WTW (g CO2e/t-km)"])

    return {
        "WTT": float(row["WTT (g CO2e/t-km)"]),
        "TTW": float(row["TTW (g CO2e/t-km)"]),
        "WTW": wtw
    }


def calculate_emissions(vehicle_type, fuel, distance_km, load_tons, region):
    factors = get_emission_factors(vehicle_type, fuel, region)

    emissions = {}
    for key, ef in factors.items():
        grams = ef * distance_km * load_tons  # g CO2e
        emissions[key] = round(grams / 1000, 2)  # kg CO2e

    return emissions

