import requests
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. User settings
# --------------------------------------------------

# Example location: near W22 / Virginia region
latitude = 38.03
longitude = -78.48

start_date = "20200101"
end_date = "20201231"

output_csv = "nasa_power_hydrology_data.csv"
output_plot = "daily_precipitation_plot.png"

# NASA POWER daily API
url = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Hydrology-relevant parameters
parameters = [
    "PRECTOTCORR",  # precipitation, mm/day
    "T2M",          # average temperature at 2 m, Celsius
    "T2M_MAX",      # max temperature at 2 m, Celsius
    "T2M_MIN"       # min temperature at 2 m, Celsius
]

params = {
    "parameters": ",".join(parameters),
    "community": "AG",
    "longitude": longitude,
    "latitude": latitude,
    "start": start_date,
    "end": end_date,
    "format": "JSON"
}

# --------------------------------------------------
# 2. Send API request
# --------------------------------------------------

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()

# --------------------------------------------------
# 3. Convert JSON response to pandas DataFrame
# --------------------------------------------------

parameter_data = data["properties"]["parameter"]

df = pd.DataFrame(parameter_data)

# Convert index from YYYYMMDD to datetime
df.index = pd.to_datetime(df.index, format="%Y%m%d")
df.index.name = "date"

# Rename columns for readability
df = df.rename(columns={
    "PRECTOTCORR": "precipitation_mm_day",
    "T2M": "temperature_mean_c",
    "T2M_MAX": "temperature_max_c",
    "T2M_MIN": "temperature_min_c"
})

# --------------------------------------------------
# 4. Save CSV
# --------------------------------------------------

df.to_csv(output_csv)
print(f"Saved CSV: {output_csv}")

# --------------------------------------------------
# 5. Basic hydrological summary
# --------------------------------------------------

annual_precip = df["precipitation_mm_day"].sum()
mean_temp = df["temperature_mean_c"].mean()
wet_days = (df["precipitation_mm_day"] > 1).sum()

print("Hydrological summary")
print("---------------------")
print(f"Annual precipitation: {annual_precip:.2f} mm")
print(f"Mean temperature: {mean_temp:.2f} °C")
print(f"Wet days > 1 mm: {wet_days}")

# --------------------------------------------------
# 6. Plot daily precipitation
# --------------------------------------------------

plt.figure(figsize=(12, 5))
plt.plot(df.index, df["precipitation_mm_day"])
plt.title("Daily Precipitation from NASA POWER API")
plt.xlabel("Date")
plt.ylabel("Precipitation (mm/day)")
plt.tight_layout()
plt.savefig(output_plot, dpi=300)
plt.show()

print(f"Saved plot: {output_plot}")