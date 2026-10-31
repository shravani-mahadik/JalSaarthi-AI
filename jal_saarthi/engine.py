from html import escape
import pandas as pd

CROPS = {
    "Wheat": {"label": "Wheat", "kc": 1.00, "season": "Rabi"},
    "Rice": {"label": "Rice", "kc": 1.05, "season": "Kharif"},
    "Maize": {"label": "Maize", "kc": 1.00, "season": "Kharif / Rabi"},
    "Cotton": {"label": "Cotton", "kc": 1.00, "season": "Kharif"},
    "Sugarcane": {"label": "Sugarcane", "kc": 1.10, "season": "Year-round"},
    "Soybean": {"label": "Soybean", "kc": 0.95, "season": "Kharif"},
    "Tomato": {"label": "Tomato", "kc": 1.05, "season": "Year-round"},
    "Onion": {"label": "Onion", "kc": 0.95, "season": "Rabi"},
    "Groundnut": {"label": "Groundnut", "kc": 0.95, "season": "Kharif"},
    "Chickpea": {"label": "Chickpea", "kc": 0.85, "season": "Rabi"},
    "Sorghum": {"label": "Sorghum", "kc": 0.90, "season": "Kharif / Rabi"},
    "Pigeon pea": {"label": "Pigeon pea", "kc": 0.95, "season": "Kharif"},
}
STAGES = {
    "Initial": {"label": "Initial", "factor": 0.70},
    "Vegetative": {"label": "Vegetative", "factor": 1.00},
    "Flowering": {"label": "Flowering / reproductive", "factor": 1.15},
    "Maturity": {"label": "Maturity", "factor": 0.80},
}
SOILS = {
    "Sandy": {"label": "Sandy", "advice": "Sandy soils often drain quickly. Check moisture more frequently and consider smaller, appropriately timed applications."},
    "Loamy": {"label": "Loamy", "advice": "Loamy soils often provide a balance of drainage and water storage. Continue checking moisture at root depth."},
    "Clay": {"label": "Clay", "advice": "Clay soils can retain water for longer. Avoid over-irrigation and check for waterlogging."},
    "Black soil": {"label": "Black soil", "advice": "Black soils may store substantial moisture. Check field moisture and drainage before irrigating."},
    "Red soil": {"label": "Red soil", "advice": "Red-soil water retention varies by location and structure. Check root-zone moisture after rainfall and irrigation."},
}
IRRIGATION_METHODS = {
    "Drip": {"label": "Drip", "efficiency": 0.90},
    "Sprinkler": {"label": "Sprinkler", "efficiency": 0.75},
    "Surface / furrow": {"label": "Surface / furrow", "efficiency": 0.60},
    "Other / unknown": {"label": "Other / unknown", "efficiency": 0.65},
}

def build_daily_plan(daily, crop, soil, stage, area_ha, efficiency):
    """Build a daily planning estimate using ETc and a simplified rainfall credit.

    ETc = ET0 × crop coefficient × growth-stage factor.
    Effective rainfall = min(70% of rainfall, ETc).
    Gross depth adjusts the net estimate by assumed application efficiency.
    """
    if crop not in CROPS or soil not in SOILS or stage not in STAGES:
        raise ValueError("Unsupported crop, soil or growth stage.")
    if area_ha <= 0:
        raise ValueError("Farm area must be greater than zero.")
    if not 0 < efficiency <= 1:
        raise ValueError("Irrigation efficiency must be between 0 and 1.")
    n = len(daily["time"])
    required = ["temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "et0_fao_evapotranspiration"]
    if any(len(daily[k]) != n for k in required):
        raise ValueError("Weather series have inconsistent lengths.")

    kc = CROPS[crop]["kc"]
    stage_factor = STAGES[stage]["factor"]
    rows = []
    for i, day in enumerate(daily["time"]):
        et0 = max(float(daily["et0_fao_evapotranspiration"][i] or 0), 0)
        rain = max(float(daily["precipitation_sum"][i] or 0), 0)
        etc = et0 * kc * stage_factor
        effective_rain = min(rain * 0.70, etc)
        net = max(etc - effective_rain, 0)
        gross = net / efficiency
        rows.append({
            "Date": day,
            "Max temperature (°C)": round(float(daily["temperature_2m_max"][i]), 1),
            "Min temperature (°C)": round(float(daily["temperature_2m_min"][i]), 1),
            "Rainfall (mm)": round(rain, 2),
            "Reference ET₀ (mm)": round(et0, 2),
            "Crop demand (mm)": round(etc, 2),
            "Effective rainfall (mm)": round(effective_rain, 2),
            "Net irrigation (mm)": round(net, 2),
            "Gross irrigation (mm)": round(gross, 2),
            "Estimated water volume (m³)": round(gross * area_ha * 10, 2),
        })
    return pd.DataFrame(rows)

def summarize_plan(df, area_ha):
    return {
        "rainfall_mm": float(df["Rainfall (mm)"].sum()),
        "crop_demand_mm": float(df["Crop demand (mm)"].sum()),
        "effective_rain_mm": float(df["Effective rainfall (mm)"].sum()),
        "net_irrigation_mm": float(df["Net irrigation (mm)"].sum()),
        "gross_irrigation_mm": float(df["Gross irrigation (mm)"].sum()),
        "gross_volume_m3": float(df["Estimated water volume (m³)"].sum()),
        "area_ha": float(area_ha),
    }

def assess_drought_risk(df):
    rain_total = float(df["Rainfall (mm)"].sum())
    avg_et0 = float(df["Reference ET₀ (mm)"].mean())
    net_total = float(df["Net irrigation (mm)"].sum())
    if rain_total < 10 and avg_et0 >= 5:
        return "High", "Very limited forecast rainfall with relatively high atmospheric evaporative demand."
    if rain_total < 25 and (avg_et0 >= 4 or net_total >= 15):
        return "Moderate", "Some rainfall is forecast, but the estimated crop-water deficit may still require attention."
    return "Low", "The forecast does not currently indicate a strong seven-day rainfall deficit."

def build_recommendations(crop, soil, stage, method, df, risk):
    total_net = float(df["Net irrigation (mm)"].sum())
    wet_days = df.loc[df["Rainfall (mm)"] >= 5, "Date"].tolist()
    priority_days = df.nlargest(3, "Net irrigation (mm)")["Date"].tolist()
    if total_net < 2:
        schedule = "Forecast rainfall may cover most of the estimated short-term demand. Do not irrigate automatically; inspect root-zone soil moisture and confirm field need first."
    else:
        schedule = (
            f"The seven-day net irrigation estimate is {total_net:.1f} mm. "
            f"Prioritise field-moisture checks on {', '.join(priority_days)}. "
            "If irrigation is needed, split it into suitable applications based on root-zone moisture and the crop's condition."
        )
    if wet_days:
        schedule += f" Rainfall of at least 5 mm is forecast on: {', '.join(wet_days)}; reassess the plan after rain."
    tips = [
        "Check soil moisture in the crop root zone before every irrigation; a weather forecast cannot measure actual field moisture.",
        "Avoid unnecessary irrigation before useful rainfall, while ensuring the crop does not experience moisture stress.",
        f"For the selected {method.lower()} system, maintain equipment and repair leaks to reduce water losses.",
        "Where suitable, use mulch and timely weed control to reduce avoidable soil-water loss.",
        SOILS[soil]["advice"],
    ]
    if stage == "Flowering":
        tips.insert(0, "Flowering/reproductive growth can be sensitive to water stress. Monitor the crop and field moisture closely during this stage.")
    if risk == "High":
        tips.insert(0, "The forecast indicates a high short-term rainfall-deficit signal. Inspect the field promptly and seek local agricultural guidance for irrigation timing.")
    if crop == "Rice":
        tips.append("Rice water management depends strongly on establishment method and local practice; follow regionally recommended water-saving rice practices.")
    return {"schedule": schedule, "tips": tips}

def make_report_html(result):
    s = result["summary"]
    df_html = result["daily"].to_html(index=False, border=0, classes="data")
    safe = lambda x: escape(str(x))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>JalSaarthi AI Farm Water Plan</title>
<style>
body{{font-family:Arial,sans-serif;margin:34px;color:#20372b;line-height:1.5}}
header{{background:#174d35;color:white;padding:24px;border-radius:14px}}
h1{{margin:0}} .sub{{opacity:.9}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0}}
.card{{background:#eef5ef;padding:14px;border-radius:10px}} table{{border-collapse:collapse;width:100%;font-size:12px}}
th{{background:#1d6845;color:white}} td,th{{padding:8px;border:1px solid #d8e2da;text-align:left}}
.note{{background:#fff8e6;padding:14px;border-left:4px solid #d5a52b;margin-top:18px}}
@media print{{body{{margin:12mm}}}}
</style></head><body>
<header><h1>🌾 JalSaarthi AI</h1><div class="sub">Smarter Irrigation. Better Farming. Sustainable Water.</div>
<div>Farm Water Planning Report</div></header>
<p><b>Location:</b> {safe(result['location'])}<br>
<b>Crop:</b> {safe(result['crop'])} &nbsp; <b>Soil:</b> {safe(result['soil'])} &nbsp; <b>Stage:</b> {safe(result['stage'])}<br>
<b>Area:</b> {result['area']:.2f} ha &nbsp; <b>Irrigation:</b> {safe(result['method'])}<br>
<b>Generated:</b> {safe(result['generated'])} &nbsp; <b>Source:</b> {safe(result['source'])}</p>
<div class="grid">
<div class="card"><b>Forecast rainfall</b><br>{s['rainfall_mm']:.1f} mm</div>
<div class="card"><b>Crop demand estimate</b><br>{s['crop_demand_mm']:.1f} mm</div>
<div class="card"><b>Net irrigation estimate</b><br>{s['net_irrigation_mm']:.1f} mm</div>
<div class="card"><b>Gross water volume</b><br>{s['gross_volume_m3']:.1f} m³</div>
<div class="card"><b>Rainfall-deficit risk</b><br>{safe(result['risk'])}</div>
<div class="card"><b>Method</b><br>{safe(result['method'])}</div></div>
<h2>Irrigation planning note</h2><p>{safe(result['advice']['schedule'])}</p>
<h2>Water-saving recommendations</h2><ul>{''.join('<li>'+safe(x)+'</li>' for x in result['advice']['tips'])}</ul>
<h2>Seven-day detail</h2>{df_html}
<div class="note"><b>Important:</b> Educational decision-support estimate only. Coefficients and rainfall effectiveness are simplified assumptions, not locally validated agronomic prescriptions. Verify field moisture and consult local agricultural experts. Do not apply the entire weekly estimate at once.</div>
<p><small>Weather provider: Open-Meteo. Forecasts can change.</small></p></body></html>"""
