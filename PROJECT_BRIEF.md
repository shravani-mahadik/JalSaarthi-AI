# JalSaarthi AI — Project Brief

## Project title
**JalSaarthi AI: Intelligent Crop Water Planning & Irrigation Assistant**

## Tagline
**Smarter Irrigation. Better Farming. Sustainable Water.**

## Problem
Farmers often struggle to decide when and how much to irrigate when weather is unpredictable. Over-irrigation wastes water and energy; under-irrigation can stress crops and affect productivity. Weather information alone is not always converted into clear farm-level action.

## Proposed solution
JalSaarthi AI is a sensor-free software assistant that accepts crop, soil, growth-stage, farm-area and location information, retrieves local weather forecasts, and converts the information into an estimated seven-day water plan. It provides daily crop-water demand, effective rainfall, net/gross irrigation estimates, an indicative rainfall-deficit risk level and water-saving guidance.

## Aim
To make weather-aware irrigation planning more accessible through a simple, explainable and low-cost digital assistant.

## Objectives
1. Capture farmer and farm information through a simple interface.
2. Retrieve location-specific forecast rainfall, temperature and reference ET₀.
3. Estimate crop-water demand and effective rainfall.
4. Estimate net irrigation depth and farm-level water volume.
5. Provide a transparent short-term rainfall-deficit indication.
6. Offer crop-stage, soil and irrigation-method-aware conservation tips.
7. Present the results in a dashboard and downloadable report.

## Current prototype scope
Selected crop and soil categories, four crop growth stages, live seven-day forecast, offline sample mode, irrigation method assumptions, water estimates, risk heuristic, recommendations, CSV/HTML exports and session dashboard.

## Technology
Python, Streamlit, Pandas, Requests, Open-Meteo Geocoding API and Forecast API.

## Innovation / value proposition
- No compulsory hardware or sensor installation in the initial version.
- Converts forecast data into a farm-area-adjusted irrigation planning estimate.
- Shows the assumptions behind water calculations instead of presenting an opaque number.
- Offers a Marathi interface option to improve accessibility.
- Provides an upgrade path to locally validated ML and optional IoT.

## Expected impact
The prototype demonstrates how accessible digital decision support can help farmers consider rainfall and crop-water demand before irrigating. Actual water savings or yield improvements must be established through field trials; they are not claimed by this prototype.

## Future scope
Regional agronomy calibration, local language voice assistant, farmer accounts, historical farm records, validated ML predictions, optional IoT soil-moisture sensing, satellite-based crop monitoring and expert advisory integration.
