import streamlit as st
import pandas as pd
from datetime import datetime
from jal_saarthi.weather import search_locations, fetch_forecast, demo_forecast
from jal_saarthi.engine import (
    CROPS, SOILS, STAGES, IRRIGATION_METHODS,
    build_daily_plan, assess_drought_risk, build_recommendations,
    summarize_plan, make_report_html
)

st.set_page_config(
    page_title="JalSaarthi AI | Smart Irrigation",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.block-container {max-width:1450px;padding-top:1.3rem;padding-bottom:2.5rem;}
.hero {padding:2.1rem 2.2rem;border-radius:22px;color:#fff;
background:linear-gradient(120deg,#102f25 0%,#17613e 55%,#65a477 100%);margin-bottom:1.25rem;}
.hero .eyebrow {font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;font-weight:700;opacity:.82;}
.hero h1 {font-family:'Manrope',sans-serif;font-size:2.65rem;line-height:1.12;margin:.45rem 0;}
.hero p {font-size:1.05rem;margin:0;opacity:.92;}
.pill {display:inline-block;border:1px solid rgba(255,255,255,.35);border-radius:20px;padding:5px 11px;margin:12px 5px 0 0;font-size:.78rem;}
.section-kicker {font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#43845a;font-weight:800;}
.info-card {border:1px solid rgba(90,130,100,.22);border-radius:15px;padding:15px 16px;height:100%;}
.tip-card {border:1px solid rgba(90,130,100,.22);border-radius:12px;padding:12px 14px;margin:.4rem 0;}
div[data-testid="stMetric"] {background:rgba(38,112,69,.06);border:1px solid rgba(80,130,90,.12);padding:12px 14px;border-radius:14px;}
div.stButton>button[kind="primary"],button[kind="primaryFormSubmit"] {background:#17613e;border-color:#17613e;}
.small-muted {color:#718078;font-size:.84rem;}
[data-testid="stSidebar"] {border-right:1px solid rgba(100,130,100,.15);}
</style>
""", unsafe_allow_html=True)

LANG = {
    "English": {
        "nav": "Navigation", "home": "Overview", "advisor": "Farm Advisor",
        "dashboard": "Farm Dashboard", "profile": "Farm Profile",
        "analyze": "Generate Smart Water Plan", "crop": "Crop",
        "soil": "Soil type", "stage": "Growth stage", "location": "Farm location",
        "area": "Farm area (hectares)", "method": "Irrigation method",
        "date": "Sowing date (optional)", "demo": "Use built-in demo weather (works offline)",
        "intro": "Your farm's water companion", "tagline": "Smarter Irrigation. Better Farming. Sustainable Water.",
    },
    "मराठी": {
        "nav": "नेव्हिगेशन", "home": "मुख्यपृष्ठ", "advisor": "शेत सल्लागार",
        "dashboard": "शेत डॅशबोर्ड", "profile": "शेत माहिती",
        "analyze": "स्मार्ट पाणी नियोजन तयार करा", "crop": "पीक",
        "soil": "मातीचा प्रकार", "stage": "पिकाची वाढीची अवस्था",
        "location": "शेताचे ठिकाण", "area": "शेताचे क्षेत्रफळ (हेक्टर)",
        "method": "सिंचन पद्धत", "date": "पेरणीची तारीख (ऐच्छिक)",
        "demo": "डेमो हवामान वापरा (ऑफलाइन उपलब्ध)",
        "intro": "तुमच्या शेताचा पाणी व्यवस्थापन साथीदार",
        "tagline": "स्मार्ट सिंचन. उत्तम शेती. शाश्वत पाणी.",
    },
}

def t(key):
    return LANG[st.session_state.get("language", "English")].get(key, key)

def render_home():
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">Climate-smart agriculture · Decision support</div>
      <h1>🌾 JalSaarthi AI</h1>
      <p>{t('tagline')}</p>
      <span class="pill">Sensor-free prototype</span>
      <span class="pill">7-day weather intelligence</span>
      <span class="pill">Farmer-first design</span>
    </div>
    """, unsafe_allow_html=True)
    st.write(
        "JalSaarthi AI turns crop, soil and local weather information into a practical "
        "water-planning view. It estimates crop-water demand, accounts for forecast rainfall, "
        "and helps farmers decide when to inspect fields and consider irrigation."
    )
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Hardware needed", "No")
    k2.metric("Forecast horizon", "7 days")
    k3.metric("Core output", "Water plan")
    k4.metric("Interface", "English / मराठी")
    st.markdown("### From farm details to informed decisions")
    cols = st.columns(4)
    flow = [
        ("01 · Farm profile", "Crop, soil, growth stage, area and location."),
        ("02 · Weather intelligence", "Rainfall, temperature and reference ET₀."),
        ("03 · Water engine", "Crop demand, effective rainfall and irrigation estimate."),
        ("04 · Actionable guidance", "Daily plan, risk indicator and conservation tips."),
    ]
    for c, (title, desc) in zip(cols, flow):
        with c:
            st.markdown(f'<div class="info-card"><b>{title}</b><p class="small-muted">{desc}</p></div>', unsafe_allow_html=True)
    st.markdown("### What makes JalSaarthi AI useful?")
    a, b = st.columns(2)
    with a:
        st.markdown("- No sensor purchase required for the first version\n- Location-specific seven-day weather forecast\n- Transparent water calculations and assumptions")
    with b:
        st.markdown("- Irrigation volume scaled to farm size and method\n- Marathi interface option\n- Downloadable farm plan for sharing")
    st.info(
        "Responsible-use note: JalSaarthi AI is an academic decision-support prototype. "
        "Its coefficients and rainfall assumptions are illustrative, not locally calibrated "
        "agronomic prescriptions. Verify soil moisture and consult local agricultural experts."
    )

def render_advisor():
    st.title("🌱 " + t("advisor"))
    st.caption("Enter the farm details below. You can use live weather or the clearly labelled offline demo dataset.")
    with st.form("farm_form", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            crop = st.selectbox(t("crop"), list(CROPS.keys()), format_func=lambda x: CROPS[x]["label"])
            soil = st.selectbox(t("soil"), list(SOILS.keys()), format_func=lambda x: SOILS[x]["label"])
            stage = st.selectbox(t("stage"), list(STAGES.keys()), format_func=lambda x: STAGES[x]["label"])
            method = st.selectbox(t("method"), list(IRRIGATION_METHODS.keys()),
                                  format_func=lambda x: IRRIGATION_METHODS[x]["label"])
        with right:
            location = st.text_input(t("location"), "Loni, Maharashtra",
                                     help="Enter the farm's village, town or district.")
            area = st.number_input(t("area"), min_value=0.01, max_value=10000.0,
                                   value=1.0, step=0.1)
            sowing_date = st.date_input(t("date"), value=None)
            demo = st.checkbox(t("demo"), value=False)
        submitted = st.form_submit_button(t("analyze"), type="primary", use_container_width=True)

    if not submitted:
        st.markdown("#### Before generating a plan")
        st.caption("Live mode requires internet access. Offline demo mode uses sample weather and must not be treated as a real forecast.")
        return
    if not demo and not location.strip():
        st.error("Please enter the farm location.")
        return

    try:
        with st.spinner("Preparing your farm water plan..."):
            if demo:
                weather_data = demo_forecast()
                location_label = "Demo farm · Sample weather (not live)"
                source = "Offline demonstration dataset"
            else:
                places = search_locations(location.strip())
                if not places:
                    st.error("Location not found. Try a nearby village, town or district.")
                    return
                # Geocoder ranks likely matches. Use its top result to keep the
                # form submission flow stable; the resolved place is shown below.
                selected = places[0]
                weather_data = fetch_forecast(selected["lat"], selected["lon"], selected["timezone"])
                location_label = selected["label"]
                source = "Open-Meteo live forecast"
            daily = build_daily_plan(
                weather_data["daily"], crop, soil, stage, area,
                IRRIGATION_METHODS[method]["efficiency"]
            )
            risk, risk_reason = assess_drought_risk(daily)
            advice = build_recommendations(crop, soil, stage, method, daily, risk)
            summary = summarize_plan(daily, area)
            result = {
                "location": location_label, "source": source,
                "crop": crop, "soil": soil, "stage": stage, "method": method,
                "area": area, "sowing_date": str(sowing_date) if sowing_date else "Not provided",
                "generated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "daily": daily, "risk": risk, "risk_reason": risk_reason,
                "advice": advice, "summary": summary,
            }
            st.session_state["latest_plan"] = result
            st.session_state.setdefault("plan_history", []).insert(0, result)
            st.session_state["plan_history"] = st.session_state["plan_history"][:10]
    except Exception as exc:
        st.error(f"Unable to generate the plan: {exc}")
        st.caption("Check the internet connection or use offline demo mode to explore the prototype.")
        return
    render_results(result)

def render_results(r):
    s, df = r["summary"], r["daily"]
    st.success(f"Water plan generated for **{r['location']}**")
    st.caption(f"{r['crop']} · {r['soil']} · {r['stage']} · {r['area']:.2f} ha · {r['method']} · {r['generated']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("7-day rainfall", f"{s['rainfall_mm']:.1f} mm")
    m2.metric("Crop water demand", f"{s['crop_demand_mm']:.1f} mm")
    m3.metric("Net irrigation need", f"{s['net_irrigation_mm']:.1f} mm")
    m4.metric("Rainfall-deficit risk", r["risk"])
    st.markdown("### 💧 Recommended irrigation plan")
    st.write(r["advice"]["schedule"])
    st.info(
        f"Estimated gross irrigation volume: **{s['gross_volume_m3']:,.1f} m³ over 7 days** "
        f"for {r['area']:.2f} ha, using the typical {IRRIGATION_METHODS[r['method']]['efficiency']:.0%} "
        "application-efficiency assumption for the selected method. Do not apply the full weekly volume at once."
    )
    st.markdown("### ⚠️ Short-term drought-risk indication")
    st.write(f"**{r['risk']} risk:** {r['risk_reason']}")
    st.markdown("### 🌿 Crop-care and water-saving recommendations")
    for tip in r["advice"]["tips"]:
        st.markdown(f'<div class="tip-card">🌱 {tip}</div>', unsafe_allow_html=True)
    st.markdown("### 📅 Seven-day weather and irrigation schedule")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("### 📈 Rainfall vs crop water demand")
    chart = df.set_index("Date")[["Rainfall (mm)", "Crop demand (mm)", "Net irrigation (mm)"]]
    st.line_chart(chart, use_container_width=True)
    st.download_button(
        "⬇️ Download detailed plan (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="JalSaarthi_AI_water_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )
    html = make_report_html(r)
    st.download_button(
        "🧾 Download shareable farm report (HTML)",
        data=html.encode("utf-8"),
        file_name="JalSaarthi_AI_farm_report.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption(f"Data source: {r['source']}. Forecasts and estimates may change.")

def render_dashboard():
    st.title("📊 " + t("dashboard"))
    history = st.session_state.get("plan_history", [])
    if not history:
        st.info("No farm plans have been generated in this session. Open Farm Advisor to create your first plan.")
    else:
        st.metric("Plans generated this session", len(history))
        rows = []
        for p in history:
            rows.append({
                "Generated": p["generated"], "Location": p["location"],
                "Crop": CROPS[p["crop"]]["label"], "Area (ha)": p["area"],
                "Net irrigation (mm)": p["summary"]["net_irrigation_mm"],
                "Water volume (m³)": p["summary"]["gross_volume_m3"],
                "Risk": p["risk"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if st.button("Clear session history"):
            st.session_state["plan_history"] = []
            st.session_state.pop("latest_plan", None)
            st.rerun()
    st.markdown("### 🚀 Product roadmap")
    st.markdown("""
    - **Regional intelligence:** locally validated crop coefficients, soil-water capacity and district-level agronomy datasets.
    - **Farmer access:** Marathi voice assistant, low-bandwidth mobile experience and saved farm profiles.
    - **Precision agriculture:** optional soil-moisture IoT sensors and satellite-derived crop indicators.
    - **AI/ML upgrade:** train and validate crop-water prediction models using labelled regional data; compare against the ET₀ baseline.
    - **Ecosystem:** agricultural university/KVK expert review and integration of trusted local advisories.
    """)

st.sidebar.markdown("# 🌾 JalSaarthi AI")
st.sidebar.caption("Your smart irrigation companion")
language = st.sidebar.selectbox("Language / भाषा", ["English", "मराठी"])
st.session_state["language"] = language
page = st.sidebar.radio(t("nav"), [t("home"), t("advisor"), t("dashboard")])
st.sidebar.divider()
st.sidebar.markdown("**Built for sustainable farming**")
st.sidebar.caption("Sensor-free · Weather-aware · Explainable estimates")
st.sidebar.caption("Hackathon prototype v1.0")

if page == t("home"):
    render_home()
elif page == t("advisor"):
    render_advisor()
else:
    render_dashboard()

st.markdown("---")
st.caption("JalSaarthi AI · Smarter Irrigation. Better Farming. Sustainable Water.")
