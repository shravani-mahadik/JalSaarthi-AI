# Methodology & System Architecture

## Workflow
Farmer inputs → location geocoding → weather retrieval → crop-water estimation → risk heuristic → recommendations → dashboard and export.

## Inputs
Crop, soil category, growth stage, farm location, farm area and irrigation method.

## Data retrieval
The place name is resolved to coordinates through Open-Meteo Geocoding. The coordinates are used to retrieve seven days of daily precipitation, maximum/minimum temperature and FAO reference evapotranspiration (ET₀).

## Estimation
Crop evapotranspiration is estimated from ET₀, a crop coefficient and a growth-stage factor. A simplified effective-rainfall credit is subtracted to estimate net irrigation. Gross irrigation is adjusted by an assumed method efficiency, then converted to farm volume.

## Equations
- `ETc = ET₀ × Kc × stage factor`
- `Effective rainfall = min(0.70 × rainfall, ETc)`
- `Net irrigation = max(ETc − effective rainfall, 0)`
- `Gross irrigation = net irrigation / application efficiency`
- `Volume (m³) = gross irrigation (mm) × area (ha) × 10`

## Risk indication
The app uses seven-day rainfall, average daily ET₀ and net irrigation estimate to assign Low, Moderate or High rainfall-deficit indication. It is a transparent heuristic, not a scientific drought index.

## Architecture
```text
+-------------------------+
| Farmer / Web Interface  |
| Streamlit + Marathi UI  |
+------------+------------+
             |
             v
+-------------------------+
| Farm Input Validation   |
+------------+------------+
             |
             v
+-------------------------+       +-------------------------+
| Location Geocoding      |------>| Open-Meteo Geocoding    |
+------------+------------+       +-------------------------+
             |
             v
+-------------------------+       +-------------------------+
| Weather Data Retrieval  |------>| Open-Meteo Forecast     |
+------------+------------+       +-------------------------+
             |
             v
+-------------------------+
| Water Estimation Engine |
| ETc / Rain / Irrigation |
+------------+------------+
             |
             v
+-------------------------+
| Risk & Recommendation  |
+------------+------------+
             |
             v
+-------------------------+
| Dashboard / CSV / HTML  |
+-------------------------+
```

## Limitations
Illustrative crop coefficients; simplified rainfall effectiveness; no measured soil moisture or root-zone water balance; no crop variety or rooting depth; forecast uncertainty; typical rather than measured irrigation efficiency; no validated ML model in the current prototype.

## Validation needed
Compare ETc and irrigation estimates with local agricultural recommendations, field observations and trusted crop/soil datasets. Record model errors and revise parameters with agronomist input before real-world use.
