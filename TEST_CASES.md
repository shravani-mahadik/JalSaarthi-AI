# Test Plan

Run the tests on the target laptop and record the actual outcomes. Do not claim live weather integration passed until it has been tested with an internet connection.

| ID | Scenario | Action | Expected outcome |
|---|---|---|---|
| TC-01 | Launch | `streamlit run app.py` | Home screen loads |
| TC-02 | Navigation | Open all sidebar pages | Each page renders |
| TC-03 | Marathi mode | Change language selector | Main navigation and farm form labels switch |
| TC-04 | Live location | Enter a valid village/town | Candidate location(s) are returned |
| TC-05 | Invalid location | Enter an unknown place | Clear not-found message |
| TC-06 | Live forecast | Generate live plan | Seven-day weather data is displayed |
| TC-07 | Offline demo | Tick demo weather and submit | Synthetic demo analysis is displayed and labelled |
| TC-08 | Water calculation | Generate plan with valid values | Non-negative daily estimates are displayed |
| TC-09 | Farm area scaling | Compare 1 ha and 2 ha | Water volume approximately doubles |
| TC-10 | Irrigation method | Compare drip and surface assumptions | Gross water volume changes with efficiency |
| TC-11 | CSV export | Download CSV | Daily analysis rows download |
| TC-12 | HTML report | Download report | Browser-openable report downloads |
| TC-13 | Session dashboard | Generate two plans and open Dashboard | Session history displays both |
| TC-14 | Network failure | Disable internet and use live mode | Friendly connection error; app remains usable |

## Calculation unit tests
Run:

```bash
python -m unittest discover -s tests -v
```

The included unit tests check non-negative irrigation estimates, farm-area scaling, efficiency behaviour and risk output.
