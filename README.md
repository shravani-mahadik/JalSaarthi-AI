# 🌾 JalSaarthi AI
### Smarter Irrigation. Better Farming. Sustainable Water.

JalSaarthi AI is a farmer-first, sensor-free irrigation decision-support prototype. It combines farmer-entered crop and field details with a seven-day weather forecast to estimate crop-water demand, rainfall contribution, irrigation depth and approximate farm water volume.

## Features
- Premium Streamlit dashboard and clear farmer workflow
- English / Marathi language toggle for main navigation and form labels
- 12 crop options, 5 soil categories and 4 growth stages
- Farm location search with location disambiguation
- Live 7-day weather: rainfall, temperature and FAO reference ET₀
- Offline demo mode using explicitly synthetic sample weather
- Daily crop demand, effective rainfall, net and gross irrigation estimates
- Irrigation method selection (drip, sprinkler, surface/furrow, other)
- Farm area and method-efficiency adjusted water volume in m³
- Short-term rainfall-deficit risk indication
- Crop-stage, soil and irrigation-method-aware recommendations
- Dashboard with latest session analyses (up to 10)
- CSV export and printable HTML farm report
- Automated unit tests for calculation engine

## Run on Windows
1. Extract the ZIP.
2. Open the `JalSaarthi_AI_Hackathon_Prototype` folder in VS Code.
3. Open Terminal in that folder and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If `py` is not recognised, use `python` to create the virtual environment. The app normally opens at `http://localhost:8501`.

### One-click Windows launcher
You can also double-click `RUN_JALSAARTHI.bat`. It creates the virtual environment if needed, installs dependencies and starts Streamlit.

## Run on macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Offline demonstration
On Farm Advisor, tick **Use built-in demo weather**. The sample dataset is synthetic and is provided only to demonstrate the interface when internet access is unavailable. It is not a live forecast and must never be presented as actual weather.

## Live weather source
- Geocoding: Open-Meteo Geocoding API
- Weather: Open-Meteo Forecast API, daily precipitation, maximum/minimum temperature and FAO reference evapotranspiration

No API key is required for this prototype. Check current Open-Meteo terms and attribution requirements before public/commercial deployment.

## Calculation method
- `ETc = ET₀ × Kc × growth-stage factor`
- `Effective rainfall = min(0.70 × forecast rainfall, ETc)`
- `Net irrigation = max(ETc − effective rainfall, 0)`
- `Gross irrigation = net irrigation ÷ assumed application efficiency`
- `Water volume (m³) = gross irrigation depth (mm) × area (ha) × 10`

The coefficients, stage factors and 70% effective-rainfall approximation are illustrative defaults for demonstrating the workflow. Soil type currently informs practical advice, not a fabricated soil-water measurement. Application-efficiency values are typical assumptions, not measured performance. The risk label is a simple seven-day rainfall/ET₀ heuristic, not a formal drought index.

## Test the calculation engine

```bash
python -m unittest discover -s tests -v
```

## Important limitations
This is an academic/hackathon prototype, not a certified agronomy product or autonomous irrigation controller. Actual irrigation depends on soil moisture, crop variety, rooting depth, sowing date, local crop coefficients, soil-water holding capacity, irrigation equipment, rainfall reliability and local recommendations. Validate all model parameters with agricultural experts and trusted regional data before field deployment.

## Project layout
```text
JalSaarthi_AI_Hackathon_Prototype/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_BRIEF.md
├── METHODOLOGY.md
├── HACKATHON_PITCH.md
├── TEST_CASES.md
├── RUN_JALSAARTHI.bat
├── jal_saarthi/
│   ├── __init__.py
│   ├── engine.py
│   └── weather.py
└── tests/
    └── test_engine.py
```

## Next steps for a production-grade solution
1. Calibrate crop coefficients and crop-stage factors with local agricultural experts and region-specific datasets.
2. Add root depth, sowing date, soil-water capacity and irrigation scheduling constraints.
3. Build a labelled regional dataset and compare a trained ML model against the ET₀ baseline with proper validation.
4. Add secure farmer accounts, saved farm profiles and seasonal history.
5. Add optional soil-moisture sensors, satellite observations and trusted local advisory feeds.
