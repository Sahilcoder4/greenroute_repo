import json
import pandas as pd

def load_ocr_json(path="data/glec_raw_output.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_table_lines(raw_json):
    lines = []
    for page in raw_json['pages']:
        for block in page['blocks']:
            for line in block['lines']:
                text_line = " ".join([word['value'] for word in line['words']])
                lines.append(text_line)
    return lines

def parse_emission_table(lines):
    parsed_rows = []
    current_row = {}

    for line in lines:
        # Look for a line that starts a new row (vehicle category)
        if "Van" in line or "Truck" in line or "MGV" in line or "HGV" in line or "Carrier" in line:
            # Save previous row if it's filled
            if current_row:
                parsed_rows.append(current_row)
                current_row = {}

            current_row["Vehicle Type"] = line.strip()

        elif line.replace(".", "", 1).isdigit():
            value = float(line.strip())

            if "Fuel Intensity (kg/t-km)" not in current_row:
                current_row["Fuel Intensity (kg/t-km)"] = value
            elif "Fuel Intensity (l/t-km)" not in current_row:
                current_row["Fuel Intensity (l/t-km)"] = value
            elif "WTT (g CO2e/t-km)" not in current_row:
                current_row["WTT (g CO2e/t-km)"] = value
            elif "TTW (g CO2e/t-km)" not in current_row:
                current_row["TTW (g CO2e/t-km)"] = value
            elif "WTW (g CO2e/t-km)" not in current_row:
                current_row["WTW (g CO2e/t-km)"] = value

    # Save the last row
    if current_row:
        parsed_rows.append(current_row)

    return pd.DataFrame(parsed_rows)


def save_to_csv(df, path="data/glec_emission_factors_parsed.csv"):
    df.to_csv(path, index=False)
    print(f"Saved parsed table to: {path}")
