"""
ClimaVaR Terminal v0.9-bank — Climate Risk Analytics Platform
Workspace: Royal Bank of Canada (RY) — Climate Credit Risk (demo)

What this demonstrates
----------------------
The same ClimaVaR engine philosophy applied to a BANK instead of a corporate:
the transmission channel changes from "climate hits my assets' book value"
to "climate hits my BORROWERS, which raises PD/LGD, which raises Expected
Credit Loss (ECL) on my loan book".

    Corporate (TRP workspace):  AssetValue x DamageRate            -> impairment
    Bank      (this file):      EAD x PD(carbon path) x LGD(hazard) -> ECL uplift

Data layer: calibrated to RBC FY2024 public disclosures (Annual Report,
2024 Sustainability/Climate Report, Pillar 3) at order-of-magnitude accuracy.
Sector EADs, PDs and LGDs are ILLUSTRATIVE approximations - every row carries
a source note and the whole table is designed to be swapped for actual
Pillar 3 / internal IRB data. This is a methodology demo, not RBC's numbers.

Dependencies: streamlit, pandas, numpy, plotly, geopandas, pyogrio
Run:  streamlit run climavar_bank_workspace.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from pathlib import Path

# ── Product identity ──────────────────────────────────────────────────────────
APP_NAME    = "ClimaVaR Terminal"
APP_TAGLINE = "Climate Risk Analytics Platform"
APP_VER     = "v0.9-bank"
MODEL_VERSION = "1.1-public-data"
PUBLIC_DATA_DIR = Path(__file__).resolve().parent / "climavar_public_data"
FSA_BOUNDARY_ZIP = PUBLIC_DATA_DIR / "lfsa000b21a_e.zip"

st.set_page_config(
    page_title=f"{APP_NAME} — RBC (RY) Bank Workspace",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _chart(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

def _df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kw)

# ── CSS — ClimaVaR platform design system (condensed) ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&display=swap');
:root {
  --bg-page:#F4F6F9; --bg-card:#FFFFFF; --bg-card-alt:#F8FAFC; --bg-note:#F0F9FF;
  --bg-tab-bar:#E8EDF2; --bg-tab-active:#FFFFFF;
  --border:#E2E8F0; --border-md:#D1D5DB; --border-note:#0EA5E9;
  --text-h:#0D2137; --text-body:#374151; --text-sec:#64748B; --text-muted:#94A3B8;
  --text-note:#0C4A6E; --text-note-b:#0369A1; --hdr-rule:2px solid #0D2137;
}
@media (prefers-color-scheme: dark) { :root {
  --bg-page:#0F172A; --bg-card:#1E293B; --bg-card-alt:#162032; --bg-note:#0C2340;
  --bg-tab-bar:#1E293B; --bg-tab-active:#334155;
  --border:#334155; --border-md:#475569;
  --text-h:#F1F5F9; --text-body:#CBD5E1; --text-sec:#94A3B8; --text-muted:#64748B;
  --text-note:#BAE6FD; --text-note-b:#7DD3FC; --hdr-rule:2px solid #3B82F6; } }
[data-theme="dark"] {
  --bg-page:#0F172A; --bg-card:#1E293B; --bg-card-alt:#162032; --bg-note:#0C2340;
  --bg-tab-bar:#1E293B; --bg-tab-active:#334155;
  --border:#334155; --border-md:#475569;
  --text-h:#F1F5F9; --text-body:#CBD5E1; --text-sec:#94A3B8; --text-muted:#64748B;
  --text-note:#BAE6FD; --text-note-b:#7DD3FC; --hdr-rule:2px solid #3B82F6; }
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.main { background:var(--bg-page)!important; }
.block-container { padding:1.8rem 2.4rem 2rem; }
section[data-testid="stSidebar"] { background:#0D2137!important; }
section[data-testid="stSidebar"] * { color:#CBD5E1!important; }
section[data-testid="stSidebar"] .stSelectbox label, section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label {
  color:#94A3B8!important; font-size:.71rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; }
section[data-testid="stSidebar"] .stSelectbox > div > div {
  background:#1E3A5F!important; border-color:#2D5A8C!important; color:#E2E8F0!important; }
section[data-testid="stSidebar"] input[type="number"] {
  color:#F1F5F9!important; background:#1E3A5F!important; border:1px solid #2D5A8C!important;
  border-radius:6px!important; font-weight:600!important; }
.sb-lbl { font-size:.67rem; font-weight:700; color:#475569; text-transform:uppercase;
  letter-spacing:.1em; border-top:1px solid rgba(255,255,255,.06); padding-top:1rem; margin:1rem 0 .3rem; }
.page-hdr h1 { font-size:1.32rem; font-weight:700; color:var(--text-h)!important; margin:0 0 .2rem; letter-spacing:-.4px; }
.page-hdr p { font-size:.85rem; color:var(--text-sec)!important; margin:0; }
.hdr-rule { border:none; border-top:var(--hdr-rule); margin:.8rem 0 1.5rem; }
.kpi { background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:.95rem 1.2rem;
  transition:box-shadow .15s ease, border-color .15s ease, transform .15s ease; }
.kpi:hover { box-shadow:0 4px 16px rgba(13,33,55,.10); border-color:var(--border-md); transform:translateY(-1px); }
.kpi-lbl { font-size:.66rem; font-weight:700; color:var(--text-sec)!important; text-transform:uppercase;
  letter-spacing:.08em; margin-bottom:5px; }
.kpi-val { font-size:1.4rem; font-weight:700; color:var(--text-h)!important; line-height:1.1;
  font-family:'JetBrains Mono',monospace; font-feature-settings:'tnum'; letter-spacing:-.4px; }
.kpi-sub { font-size:.73rem; color:var(--text-muted)!important; margin-top:3px; }
.kpi-neg{border-left:3px solid #EF4444;} .kpi-warn{border-left:3px solid #F59E0B;}
.kpi-pos{border-left:3px solid #22C55E;} .kpi-inf{border-left:3px solid #3B82F6;}
.sec { font-size:.98rem; font-weight:600; color:var(--text-h)!important;
  border-bottom:2px solid var(--border); padding-bottom:.55rem; margin-bottom:1.15rem; }
.note { background:var(--bg-note); border-left:3px solid var(--border-note); border-radius:0 6px 6px 0;
  padding:.65rem 1rem; font-size:.8rem; color:var(--text-note)!important; margin-top:.6rem; }
.note b { color:var(--text-note-b)!important; }
.mbox { background:var(--bg-card-alt); border:1px solid var(--border); border-radius:8px;
  padding:.75rem 1rem; font-size:.78rem; color:var(--text-body)!important; margin-top:.5rem; }
.stTabs [data-baseweb="tab-list"] { background:var(--bg-tab-bar); border-radius:9px; padding:4px; gap:3px; display:flex!important; }
.stTabs [data-baseweb="tab"] { border-radius:6px; padding:8px 4px; font-size:.84rem; font-weight:500;
  color:var(--text-sec)!important; flex:1 1 0!important; text-align:center!important; min-width:0!important; white-space:nowrap; }
.stTabs [aria-selected="true"] { background:var(--bg-tab-active)!important; color:var(--text-h)!important;
  box-shadow:0 1px 3px rgba(0,0,0,.15); font-weight:700!important; }
div[data-testid="stExpander"] { border:1px solid var(--border)!important; border-radius:9px!important; }
.stDownloadButton button { background:#0D2137!important; color:#F1F5F9!important; border:none!important;
  border-radius:6px!important; font-weight:600!important; font-size:.82rem!important; }
.pill { display:inline-flex; align-items:center; gap:6px; padding:3px 11px; border-radius:999px;
  font-size:.68rem; font-weight:600; font-family:'JetBrains Mono',monospace;
  border:1px solid var(--border); background:var(--bg-card); color:var(--text-sec); white-space:nowrap; }
.pill .dot { width:7px; height:7px; border-radius:50%; flex:none; }
.crumb { font-size:.68rem; font-weight:700; color:var(--text-muted)!important; text-transform:uppercase;
  letter-spacing:.09em; margin-bottom:4px; }
.topbar { display:flex; justify-content:space-between; align-items:flex-end; gap:14px; flex-wrap:wrap; }
.topbar .chips { display:flex; gap:7px; flex-wrap:wrap; padding-bottom:3px; }
.ver-pill { font-family:'JetBrains Mono',monospace; font-size:.6rem; font-weight:700; color:#7DD3FC;
  background:#0C2340; border:1px solid #1E3A5F; border-radius:999px; padding:2px 8px; }
.js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text { fill:#1E293B!important; }
.js-plotly-plot .plotly .gtitle text { fill:#0D2137!important; }
.js-plotly-plot .plotly .legend text { fill:#1E293B!important; }
[data-testid="stDataFrame"] * { font-feature-settings:'tnum'; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER — RBC FY2024, calibrated to public disclosures (ILLUSTRATIVE)
#  Sources: RBC Annual Report 2024 (loans & acceptances by portfolio; CET1
#  13.2%; GIL 0.59%), RBC 2024 Sustainability/Climate Report (PCAF financed
#  emissions: O&G ~71 Mt CO2e S1+2+3; sector FELI intensities), Pillar 3
#  (IRB PD/LGD ranges by exposure class), BoC–OSFI 2022 climate scenario
#  pilot (sectoral PD multiples under transition scenarios).
#  EAD/PD/LGD below are order-of-magnitude approximations for methodology
#  demonstration — replace with actual Pillar 3 / internal IRB data.
# ══════════════════════════════════════════════════════════════════════════════

BANK = {
    "name": "Royal Bank of Canada", "ticker": "RY",
    "loans_B": 1006,        # gross loans & acceptances, ~CAD $1.0T post-HSBC Canada
    "acl_B": 7.0,           # allowance for credit losses (approx)
    "cet1_B": 87.0,         # CET1 capital ≈ 13.2% x RWA ~$658B (approx)
    "cet1_ratio": 13.2,     # FY2024 Annual Report
}

# pd_beta: relative PD uplift per +$100/t carbon price (transition sensitivity).
#   Calibrated directionally to the BoC–OSFI 2022 pilot, which found PD
#   multiples concentrated in fossil-fuel and emissions-intensive sectors
#   (O&G PDs rising several-fold by 2050 under net-zero pathways).
# phys_lgd_pp: collateral-driven LGD uplift (percentage points) reached by
#   2050 at scenario physical multiplier 1.0 (flood/wildfire/drought on
#   real-estate and agricultural collateral).
SECTORS = {
    "Residential Mortgages":        {"EAD_B": 433, "PD": 0.25, "LGD": 12, "beta": 0.03, "phys_lgd_pp": 3.0,
        "secured": True,  "src": "AR2024 retail portfolio (approx)"},
    "Other Wholesale (Svcs/Fin/Tech)":{"EAD_B": 240, "PD": 0.50, "LGD": 38, "beta": 0.06, "phys_lgd_pp": 0.5,
        "secured": False, "src": "AR2024 wholesale by industry (approx)"},
    "Consumer (Cards & Personal)":  {"EAD_B": 130, "PD": 1.60, "LGD": 75, "beta": 0.02, "phys_lgd_pp": 0.0,
        "secured": False, "src": "AR2024 retail portfolio (approx)"},
    "Commercial Real Estate":       {"EAD_B": 95,  "PD": 0.90, "LGD": 30, "beta": 0.18, "phys_lgd_pp": 4.0,
        "secured": True,  "src": "AR2024 wholesale: real estate & related (approx)"},
    "Industrials & Manufacturing":  {"EAD_B": 45,  "PD": 0.80, "LGD": 40, "beta": 0.30, "phys_lgd_pp": 1.0,
        "secured": False, "src": "AR2024 wholesale by industry (approx)"},
    "Power & Utilities":            {"EAD_B": 18,  "PD": 0.50, "LGD": 38, "beta": 0.55, "phys_lgd_pp": 1.5,
        "secured": False, "src": "AR2024 + Climate Report power gen FELI"},
    "Transportation & Automotive":  {"EAD_B": 16,  "PD": 0.90, "LGD": 45, "beta": 0.45, "phys_lgd_pp": 1.0,
        "secured": False, "src": "AR2024 wholesale by industry (approx)"},
    "Agriculture":                  {"EAD_B": 12,  "PD": 0.80, "LGD": 28, "beta": 0.35, "phys_lgd_pp": 6.0,
        "secured": True,  "src": "AR2024 wholesale by industry (approx)"},
    "Oil & Gas":                    {"EAD_B": 9,   "PD": 1.20, "LGD": 42, "beta": 1.00, "phys_lgd_pp": 1.0,
        "secured": False, "src": "AR2024 outstanding (approx); Climate Report ~71 Mt financed emissions"},
    "Mining & Metals":              {"EAD_B": 8,   "PD": 1.00, "LGD": 40, "beta": 0.40, "phys_lgd_pp": 1.5,
        "secured": False, "src": "AR2024 wholesale by industry (approx)"},
}

CARBON_SCHEDULE = {2024: 80, 2025: 95, 2026: 110, 2027: 125, 2028: 140, 2029: 155, 2030: 170}

def carbon_price(y, cp_end):
    """Continuous CAD carbon price path: federal schedule to 2030 ($170/t),
    then anchored interpolation to the scenario's 2050 terminal price."""
    if y in CARBON_SCHEDULE:
        return CARBON_SCHEDULE[y]
    return 170 + (cp_end - 170) * (y - 2030) / 20.0

# phys_mult scales collateral-hazard LGD uplift by warming pathway
SCENARIOS = {
    "NGFS — Net Zero 2050":        {"cp_end": 345, "phys_mult": 0.7, "color": "#059669",
                                    "ref": "NGFS Phase 4 · ~1.5°C"},
    "RCP 4.5 — Moderate (~2°C)":   {"cp_end": 250, "phys_mult": 1.0, "color": "#1D4ED8",
                                    "ref": "SSP2-4.5 · IPCC AR6"},
    "NGFS — Delayed Transition":   {"cp_end": 180, "phys_mult": 1.4, "color": "#D97706",
                                    "ref": "NGFS Phase 4 · ~1.8°C"},
    "NGFS — Current Policies":     {"cp_end": 170, "phys_mult": 1.7, "color": "#6B7280",
                                    "ref": "NGFS Phase 4 · ~3°C"},
    "RCP 8.5 — High Emission (~4°C)": {"cp_end": 130, "phys_mult": 2.0, "color": "#DC2626",
                                    "ref": "SSP5-8.5 · IPCC AR6"},
}

# Synthetic property-level mortgage portfolio used to demonstrate the complete
# physical-risk transmission chain. Replace this table with internal collateral
# records and vendor hazard layers in production.
PROVINCE_PHYSICAL = {
    "ON": {"weight": 0.43, "flood_depth_m": 0.34, "protection": 0.82},
    "BC": {"weight": 0.17, "flood_depth_m": 0.29, "protection": 0.78},
    "AB": {"weight": 0.14, "flood_depth_m": 0.31, "protection": 0.76},
    "QC": {"weight": 0.16, "flood_depth_m": 0.27, "protection": 0.80},
    "Other": {"weight": 0.10, "flood_depth_m": 0.22, "protection": 0.84},
}

FSA_BY_PROVINCE = {
    "ON": ["M5V", "M4B", "M1B", "K1A", "L5B", "N2L", "L8P", "P3A"],
    "BC": ["V6B", "V5K", "V3T", "V8W", "V2L", "V1Y"],
    "AB": ["T2P", "T5J", "T6X", "T8N", "T1Y"],
    "QC": ["H2Y", "H3B", "G1R", "J4K", "J8X"],
    "Other": ["B3J", "E1C", "R3C", "S7K", "A1C"],
}

DATA_REGISTRY = pd.DataFrame([
    ["FSA boundaries", "Statistics Canada 2021 CFSA Boundary File", "Public observed geography", "Local official digital boundary file"],
    ["Flood", "NRCan Flood Susceptibility Mapping", "Public proxy", "Screening score; not property-level flood depth"],
    ["Wildfire", "NRCan CWFIS / CNFDB", "Public proxy", "Historical/fire-weather aligned screening score"],
    ["Extreme heat", "ECCC Extreme Heat Events", "Public proxy", "Heat-day trend aligned screening score"],
    ["Mortgage / CRE", "Synthetic portfolio", "Illustrative assumption", "No customer or bank-confidential data"],
    ["PD / LGD / staging", "Illustrative calibration", "Illustrative assumption", "Replace with internal IRB/IFRS 9 parameters"],
], columns=["Data block", "Source", "Classification", "Permitted use"])

def stable_score(text, salt=0):
    """Deterministic 0-1 score without relying on Python's randomized hash()."""
    value = sum((i + 1 + salt) * ord(c) for i, c in enumerate(str(text)))
    return ((value * 2654435761) % 10007) / 10006.0

def hazard_score(fsa, province, hazard, scenario_key, year):
    """Public-source-aligned screening proxy, explicitly not a vendor hazard value."""
    t = np.clip((year - 2024) / 26.0, 0.0, 1.0)
    mult = SCENARIOS[scenario_key]["phys_mult"]
    base = stable_score(fsa, {"Flood": 3, "Wildfire": 11, "Extreme Heat": 19}[hazard])
    if hazard == "Flood":
        regional = {"ON": .16, "BC": .12, "AB": .10, "QC": .14, "Other": .08}[province]
        return float(np.clip(.22 + .48 * base + regional + .12 * mult * t, 0, 1))
    if hazard == "Wildfire":
        regional = {"ON": .06, "BC": .22, "AB": .20, "QC": .08, "Other": .12}[province]
        return float(np.clip(.14 + .50 * base + regional + .18 * mult * t, 0, 1))
    regional = {"ON": .16, "BC": .08, "AB": .11, "QC": .13, "Other": .07}[province]
    return float(np.clip(.18 + .45 * base + regional + .22 * mult * t, 0, 1))

@st.cache_data
def load_fsa_boundaries():
    """Load official Statistics Canada boundaries when geopandas is available."""
    if not FSA_BOUNDARY_ZIP.exists():
        return None
    try:
        import geopandas as gpd
        gdf = gpd.read_file(f"zip://{FSA_BOUNDARY_ZIP}")
        fsa_col = next(c for c in gdf.columns if c.upper() in {"CFSAUID", "CFSAUID_1"})
        gdf = gdf.rename(columns={fsa_col: "FSA"}).to_crs(4326)
        return gdf[["FSA", "geometry"]]
    except Exception:
        return None

@st.cache_data
def build_mortgage_portfolio(n=2500, seed=5278):
    """Create deterministic demo collateral records; no customer data is used."""
    rng = np.random.default_rng(seed)
    provinces = list(PROVINCE_PHYSICAL)
    weights = [PROVINCE_PHYSICAL[p]["weight"] for p in provinces]
    province = rng.choice(provinces, size=n, p=weights)
    fsa = np.array([rng.choice(FSA_BY_PROVINCE[p]) for p in province])
    property_value = np.clip(rng.lognormal(np.log(720_000), 0.38, n), 180_000, 3_500_000)
    base_ltv = np.clip(rng.beta(5.0, 2.5, n) * 0.92, 0.20, 0.92)
    insurance = np.clip(rng.normal(0.68, 0.22, n), 0.0, 1.0)
    return pd.DataFrame({
        "property_id": [f"SYN-{i:05d}" for i in range(n)],
        "province": province,
        "fsa": fsa,
        "property_value": property_value,
        "ead": property_value * base_ltv,
        "base_ltv": base_ltv,
        "insurance_coverage": insurance,
        "vulnerability": np.clip(rng.normal(1.0, 0.18, n), 0.55, 1.55),
    })

def flood_damage_curve(depth_m):
    """Illustrative residential depth-damage curve, capped at 55% of value."""
    depth = np.maximum(np.asarray(depth_m), 0.0)
    damage = 0.02 + 0.16 * depth + 0.055 * depth**2
    return np.where(depth > 0, np.clip(damage, 0.0, 0.55), 0.0)

@st.cache_data(ttl=600)
def run_mortgage_physical(scenario_key, year, hazard_scaler=1.0, hazard="Flood"):
    """Hazard -> damage -> insurance -> collateral -> LTV/LGD, record by record."""
    portfolio = build_mortgage_portfolio().copy()
    scenario = SCENARIOS[scenario_key]
    time_fraction = np.clip((year - 2024) / 26.0, 0.0, 1.0)
    base_depth = portfolio["province"].map(
        {p: v["flood_depth_m"] for p, v in PROVINCE_PHYSICAL.items()}
    ).astype(float)
    protection = portfolio["province"].map(
        {p: v["protection"] for p, v in PROVINCE_PHYSICAL.items()}
    ).astype(float)
    screen = np.array([hazard_score(f, p, hazard, scenario_key, year)
                       for f, p in zip(portfolio["fsa"], portfolio["province"])])
    if hazard == "Flood":
        hazard_depth = base_depth * scenario["phys_mult"] * hazard_scaler * time_fraction
        gross_damage_ratio = flood_damage_curve(hazard_depth) * portfolio["vulnerability"] * protection
    elif hazard == "Wildfire":
        hazard_depth = np.zeros(len(portfolio))
        gross_damage_ratio = .18 * screen**3 * time_fraction * hazard_scaler * portfolio["vulnerability"]
    else:
        hazard_depth = np.zeros(len(portfolio))
        # Heat is primarily a cash-flow/PD channel; this small collateral term
        # represents cooling retrofit and obsolescence pressure.
        gross_damage_ratio = .04 * screen * time_fraction * hazard_scaler * portfolio["vulnerability"]
    # Insurance is assumed to reimburse 80% of covered damage after deductibles/limits.
    insured_recovery_ratio = gross_damage_ratio * portfolio["insurance_coverage"] * 0.80
    net_damage_ratio = np.clip(gross_damage_ratio - insured_recovery_ratio, 0.0, 0.95)
    stressed_value = np.maximum(portfolio["property_value"] * (1 - net_damage_ratio), 1.0)
    stressed_ltv = portfolio["ead"] / stressed_value
    # Incremental climate LGD over the portfolio's 12% through-the-cycle workout
    # baseline. The second term captures repair/value impairment; the third captures
    # collateral shortfall after a 10% liquidation haircut.
    collateral_shortfall = np.maximum(portfolio["ead"] - stressed_value * 0.90, 0.0) / portfolio["ead"]
    stressed_lgd = np.clip(0.12 + 0.65 * net_damage_ratio + 0.50 * collateral_shortfall,
                           0.12, 1.0)
    portfolio["hazard_depth_m"] = hazard_depth
    portfolio["hazard_score"] = screen
    portfolio["hazard"] = hazard
    portfolio["gross_damage_ratio"] = gross_damage_ratio
    portfolio["net_damage_ratio"] = net_damage_ratio
    portfolio["stressed_value"] = stressed_value
    portfolio["stressed_ltv"] = stressed_ltv
    portfolio["stressed_lgd"] = stressed_lgd
    return portfolio

@st.cache_data
def build_cre_portfolio(n=650, seed=1503733):
    """Synthetic facility-level CRE book for public portfolio demonstrations."""
    rng = np.random.default_rng(seed)
    provinces = list(PROVINCE_PHYSICAL)
    weights = [PROVINCE_PHYSICAL[p]["weight"] for p in provinces]
    province = rng.choice(provinces, size=n, p=weights)
    fsa = np.array([rng.choice(FSA_BY_PROVINCE[p]) for p in province])
    property_type = rng.choice(["Office", "Retail", "Industrial", "Multifamily"], n,
                               p=[.26, .22, .25, .27])
    noi = np.clip(rng.lognormal(np.log(1_800_000), .70, n), 180_000, 18_000_000)
    cap_rate = np.clip(rng.normal(.057, .011, n), .035, .095)
    value = noi / cap_rate
    ltv = np.clip(rng.normal(.61, .14, n), .25, .90)
    return pd.DataFrame({
        "facility_id": [f"CRE-{i:05d}" for i in range(n)], "province": province,
        "fsa": fsa, "property_type": property_type, "noi": noi,
        "cap_rate": cap_rate, "property_value": value, "ead": value * ltv,
        "base_ltv": ltv, "baseline_pd": np.clip(rng.normal(.009, .004, n), .001, .04),
        "baseline_lgd": np.clip(rng.normal(.30, .06, n), .15, .55),
        "maturity_years": rng.integers(2, 11, n),
    })

@st.cache_data(ttl=600)
def run_cre_physical(scenario_key, year, hazard, hazard_scaler=1.0):
    cre = build_cre_portfolio().copy()
    scores = [hazard_score(f, p, hazard, scenario_key, year)
              for f, p in zip(cre["fsa"], cre["province"])]
    cre["hazard_score"] = np.clip(np.asarray(scores) * hazard_scaler, 0, 1)
    sensitivity = cre["property_type"].map(
        {"Office": .10, "Retail": .13, "Industrial": .09, "Multifamily": .07})
    cre["noi_shock"] = cre["hazard_score"] * sensitivity
    cre["stressed_noi"] = cre["noi"] * (1 - cre["noi_shock"])
    cre["stressed_cap_rate"] = cre["cap_rate"] + .0075 * cre["hazard_score"]
    cre["stressed_value"] = cre["stressed_noi"] / cre["stressed_cap_rate"]
    cre["stressed_ltv"] = cre["ead"] / cre["stressed_value"]
    shortfall = np.maximum(cre["ead"] - .90 * cre["stressed_value"], 0) / cre["ead"]
    cre["stressed_lgd"] = np.clip(cre["baseline_lgd"] + .45 * cre["noi_shock"]
                                    + .50 * shortfall, 0, 1)
    cre["stressed_pd"] = np.clip(cre["baseline_pd"] * (1 + 2.4 * cre["noi_shock"]), 0, 1)
    cre["ecl_uplift"] = (cre["ead"] * cre["stressed_pd"] * cre["stressed_lgd"]
                         - cre["ead"] * cre["baseline_pd"] * cre["baseline_lgd"])
    return cre

def lifetime_ecl_schedule(ead, annual_pd, lgd, maturity, eir, stage):
    """Marginal-PD lifetime mechanics; Stage 1 is limited to twelve months."""
    years = np.arange(1, int(maturity) + 1)
    conditional_pd = np.clip(annual_pd * (1 + .06 * (years - 1)), 0, .999)
    survival = np.concatenate(([1.0], np.cumprod(1 - conditional_pd[:-1])))
    marginal_pd = survival * conditional_pd
    amortized_ead = ead * np.maximum(1 - (years - 1) / max(maturity, 1), .10)
    losses = amortized_ead * marginal_pd * lgd / (1 + eir) ** years
    return float(losses[0] if stage == 1 else losses.sum())

# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE — sector ECL uplift:  ECL_t = EAD x PD_t x LGD_t
#  Transition channel: carbon price path -> borrower cost stress -> PD_t
#  Physical channel:   hazard damage to collateral -> LGD_t
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def run_bank(scenario_key, horizon, dr_pct, pd_scaler, lgd_scaler, hazard="Flood"):
    SC = SCENARIOS[scenario_key]
    yrs = np.arange(2024, 2024 + horizon + 1)
    dr = dr_pct / 100.0
    rows, annual_total = [], np.zeros(len(yrs))
    annual_tr, annual_ph = np.zeros(len(yrs)), np.zeros(len(yrs))
    for name, s in SECTORS.items():
        ead = s["EAD_B"] * 1000      # CAD $M
        pd0, lgd0 = s["PD"] / 100, s["LGD"] / 100
        ecl0 = ead * pd0 * lgd0      # baseline 1-yr expected loss
        pv_u = pv_tr = pv_ph = 0.0
        peak_pd = pd0
        for i, y in enumerate(yrs):
            cp = carbon_price(y, SC["cp_end"])
            # Transition: PD multiplier per +$100/t over the 2024 base, capped 4x
            pd_t = pd0 * min(1 + s["beta"] * (cp - 80) / 100 * pd_scaler, 4.0)
            # Physical: mortgages use record-level collateral repricing; other
            # portfolios retain transparent screening proxies pending facility data.
            if name == "Residential Mortgages":
                mortgage_lgd = run_mortgage_physical(
                    scenario_key, int(y), lgd_scaler, hazard)["stressed_lgd"].mean()
                lgd_t = max(lgd0, mortgage_lgd)
            else:
                lgd_t = lgd0 + (s["phys_lgd_pp"] / 100) * ((y - 2024) / 26) * SC["phys_mult"] * lgd_scaler
            pd_t = np.clip(pd_t, 0.0, 1.0)
            lgd_t = np.clip(lgd_t, 0.0, 1.0)
            ecl_t = ead * pd_t * lgd_t
            disc = (1 + dr) ** (y - 2024)
            u  = (ecl_t - ecl0) / disc
            # Symmetric (Shapley-style) split of the PD x LGD interaction.
            pd_effect = ead * (pd_t - pd0) * lgd0
            lgd_effect = ead * pd0 * (lgd_t - lgd0)
            interaction = ead * (pd_t - pd0) * (lgd_t - lgd0)
            tr_u = pd_effect + 0.5 * interaction
            ph_u = lgd_effect + 0.5 * interaction
            pv_u  += u
            pv_tr += tr_u / disc
            pv_ph += ph_u / disc
            annual_total[i] += ecl_t - ecl0
            annual_tr[i]    += tr_u
            annual_ph[i]    += ph_u
            peak_pd = max(peak_pd, pd_t)
        rows.append({
            "Sector": name, "EAD_M": ead, "PD0": pd0 * 100, "LGD0": lgd0 * 100,
            "PeakPD": peak_pd * 100, "Uplift_M": pv_u,
            "Transition_M": pv_tr, "Physical_M": pv_ph,
            "Uplift_bps": pv_u / ead * 1e4, "Secured": s["secured"], "Source": s["src"],
        })
    df = pd.DataFrame(rows)
    return df, yrs, annual_total, annual_tr, annual_ph

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:.5rem 0 .9rem;border-bottom:1px solid rgba(255,255,255,.07)">
      <div style="display:flex;align-items:center;gap:9px">
        <div style="width:27px;height:27px;border-radius:7px;flex:none;
                    background:linear-gradient(135deg,#3B82F6 0%,#059669 100%);
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-weight:800;font-size:.85rem;
                    font-family:'JetBrains Mono',monospace">◢</div>
        <div style="min-width:0">
          <div style="font-size:.95rem;font-weight:700;color:#F1F5F9;letter-spacing:-.2px;
                      font-family:'JetBrains Mono',monospace">{APP_NAME}</div>
          <div style="font-size:.58rem;color:#475569;letter-spacing:.08em;
                      text-transform:uppercase;margin-top:1px">{APP_TAGLINE}</div>
        </div>
        <span class="ver-pill" style="margin-left:auto">{APP_VER}</span>
      </div>
    </div>
    <div style="margin-top:.9rem;background:#0A1929;border:1px solid #1E3A5F;
                border-radius:8px;padding:.6rem .8rem">
      <div style="font-size:.56rem;font-weight:700;letter-spacing:.11em;color:#334155;
                  text-transform:uppercase;margin-bottom:3px">Workspace · Bank</div>
      <div style="font-size:.86rem;font-weight:700;color:#E2E8F0">{BANK['name']}</div>
      <div style="font-size:.65rem;color:#64748B;margin-top:1px">
        TSX / NYSE: {BANK['ticker']} &nbsp;·&nbsp; CAD ${BANK['loans_B']}B loans &nbsp;·&nbsp; CET1 {BANK['cet1_ratio']}%</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-lbl">Climate Scenario</div>', unsafe_allow_html=True)
    scenario_name = st.selectbox("Scenario", list(SCENARIOS.keys()), index=2,
        label_visibility="collapsed",
        help="Transition pathway sets the carbon price path (drives borrower PD); "
             "warming pathway sets the physical multiplier (drives collateral LGD).")
    SC = SCENARIOS[scenario_name]

    hazard_name = st.selectbox("Physical Hazard", ["Flood", "Wildfire", "Extreme Heat"],
        help="Separate public-source-aligned screening modules. Values are transparent "
             "proxies until official raster layers or vendor outputs are ingested.")

    st.markdown('<div class="sb-lbl">Stress Horizon</div>', unsafe_allow_html=True)
    horizon = st.slider("Horizon (years)", 1, 26, 10, label_visibility="collapsed",
        help="OSFI B-15 expects short-, medium- and long-term horizon analysis.")
    end_year = 2024 + horizon

    st.markdown('<div class="sb-lbl">Model Calibration</div>', unsafe_allow_html=True)
    dr_pct = st.number_input("Discount Rate (%)", min_value=0.0, max_value=25.0,
        value=5.0, step=0.1, format="%.1f",
        help="Rate used to present-value annual ECL uplifts. A bank would use "
             "its hurdle rate or the EIR consistent with IFRS 9 discounting.")
    pd_scaler = st.slider("PD Sensitivity Scaler", 0.5, 2.0, 1.0, 0.1,
        help="Scales the sectoral PD-vs-carbon-price elasticities. 1.0 = base "
             "calibration (directionally anchored to the BoC-OSFI 2022 pilot). "
             "Use 2.0 for a severe-but-plausible sensitivity check.")
    lgd_scaler = st.slider("LGD Hazard Scaler", 0.5, 2.0, 1.0, 0.1,
        help="Scales collateral-hazard LGD uplifts (flood/wildfire/drought on "
             "mortgage, CRE and agricultural collateral).")

    st.divider()
    st.markdown(f"""
    <div style="background:#0A1929;border-radius:8px;padding:.7rem .9rem;border:1px solid #1E3A5F">
      <div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;
                  color:#334155;margin-bottom:.35rem">Reference Capital (FY2024)</div>
      <div style="font-size:.72rem;color:#94A3B8;line-height:1.9">
        Allowance (ACL): CAD ${BANK['acl_B']:.1f}B<br>
        CET1 capital: ~CAD ${BANK['cet1_B']:.0f}B<br>
        CET1 ratio: {BANK['cet1_ratio']}%
      </div>
    </div>""", unsafe_allow_html=True)

# ── Run engine ────────────────────────────────────────────────────────────────
df, yrs, ann_tot, ann_tr, ann_ph = run_bank(
    scenario_name, horizon, dr_pct, pd_scaler, lgd_scaler, hazard_name)
total_uplift = df["Uplift_M"].sum()
total_ead    = df["EAD_M"].sum()
uplift_bps   = total_uplift / total_ead * 1e4
pct_acl      = total_uplift / (BANK["acl_B"] * 1000) * 100
pct_cet1     = total_uplift / (BANK["cet1_B"] * 1000) * 100
top          = df.sort_values("Uplift_M", ascending=False).iloc[0]
tr_share_tot = df["Transition_M"].sum() / total_uplift * 100 if total_uplift > 0 else 0

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div>
    <div class="crumb">Workspace &nbsp;/&nbsp; RBC (RY) — Bank &nbsp;/&nbsp; Climate Credit Risk</div>
    <div class="page-hdr">
      <h1>Climate Credit Risk — Loan Book Stress</h1>
      <p>Sector-Level ECL Uplift under NGFS / RCP pathways &nbsp;·&nbsp; OSFI B-15 / BoC-OSFI SCSE aligned (demo)</p>
    </div>
  </div>
  <div class="chips">
    <span class="pill"><span class="dot" style="background:{SC['color']}"></span>{scenario_name.split(' — ')[0]}</span>
    <span class="pill">{horizon}-yr horizon</span>
    <span class="pill">DR {dr_pct:.1f}%</span>
    <span class="pill">PD x{pd_scaler:.1f} · LGD x{lgd_scaler:.1f}</span>
    <span class="pill"><span class="dot" style="background:#F59E0B"></span>Illustrative data</span>
  </div>
</div>
<hr class="hdr-rule">
""", unsafe_allow_html=True)

st.markdown("""
<div class="note" style="margin:-.4rem 0 1rem">
  <b>Demo disclaimer:</b> sector exposures, PDs and LGDs are order-of-magnitude
  approximations calibrated to RBC FY2024 public disclosures (Annual Report, 2024
  Climate Report, Pillar 3) for methodology demonstration. They are <b>not</b> RBC's
  actual risk parameters. A production run would ingest internal IRB PD/LGD, EAD at
  facility level, and postal-code collateral hazard data.
</div>""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
for col, lbl, val, sub, bdr in [
    (k1, "Expected-Loss Uplift (PV)", f"CAD {total_uplift:,.0f}M",
     f"{horizon}-yr cumulative · DR {dr_pct:.1f}%", "kpi-neg"),
    (k2, "Uplift / Loan Book",   f"{uplift_bps:,.0f} bps",
     f"On CAD {total_ead/1000:,.0f}B EAD", "kpi-warn"),
    (k3, "vs Credit Allowance",  f"{pct_acl:,.0f}%",
     f"Of CAD {BANK['acl_B']:.1f}B ACL (FY2024)", "kpi-warn"),
    (k4, "vs CET1 Capital",      f"{pct_cet1:.1f}%",
     f"Of ~CAD {BANK['cet1_B']:.0f}B CET1", "kpi-inf"),
    (k5, "Top Sector",           top["Sector"].split(" (")[0],
     f"CAD {top['Uplift_M']:,.0f}M · {top['Uplift_M']/total_uplift*100:.0f}% of uplift", "kpi-pos"),
]:
    col.markdown(f"""
    <div class="kpi {bdr}">
      <div class="kpi-lbl">{lbl}</div>
      <div class="kpi-val" style="font-size:1.15rem">{val}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="note" style="margin:.8rem 0 1rem">
  <b>Takeaway:</b> Under {scenario_name.split(' — ')[0]} over {horizon} years, modelled
  climate drivers add <b>CAD {total_uplift:,.0f}M of discounted cumulative annual
  expected-loss uplift</b> under a static-balance-sheet assumption
  ({uplift_bps:,.0f} bps of the loan book) — equivalent to {pct_acl:,.0f}% of the current
  allowance but only {pct_cet1:.1f}% of CET1 capital. Transition channels (carbon price →
  borrower PD) drive ~{tr_share_tot:.0f}% of the uplift; the rest is collateral-hazard LGD.
  The bank-level story mirrors the BoC-OSFI pilot: risk is <b>concentrated, not systemic</b> —
  small in capital terms, large relative to sector-level pricing and provisioning.
</div>""", unsafe_allow_html=True)

tabA, tabB, tabC, tabMap, tabCRE, tabECL, tabVal, tabD = st.tabs([
    "Sector Overview", "Transition (PD)", "Physical (LGD)", "FSA Hazard Map",
    "CRE Facilities", "Stage 1/2 ECL", "Benchmark & Validation", "Data & Method",
])

# ════════════════════════════════════════════════════════════════
#  TAB A — SECTOR OVERVIEW
# ════════════════════════════════════════════════════════════════
with tabA:
    st.markdown('<div class="sec">ECL Uplift by Sector — Transition vs Physical Attribution</div>',
                unsafe_allow_html=True)
    oc1, oc2 = st.columns([3, 2])
    with oc1:
        dd = df.sort_values("Uplift_M", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dd["Sector"], x=dd["Transition_M"], orientation="h",
                             name="Transition (PD channel)", marker_color="#1D4ED8"))
        fig.add_trace(go.Bar(y=dd["Sector"], x=dd["Physical_M"], orientation="h",
                             name="Physical (LGD channel)", marker_color="#EA580C"))
        for _, r in dd.iterrows():
            fig.add_annotation(x=r["Uplift_M"], y=r["Sector"],
                text=f"CAD {r['Uplift_M']:,.0f}M · {r['Uplift_bps']:,.0f} bps",
                xanchor="left", showarrow=False, xshift=6, font=dict(size=11, color="#1E293B"))
        fig.update_layout(height=420, template="plotly_white", barmode="stack",
            xaxis=dict(title="PV ECL Uplift (CAD $M)", tickfont=dict(size=12, color="#1E293B")),
            yaxis=dict(tickfont=dict(size=11, color="#1E293B")),
            legend=dict(orientation="h", y=-0.18, font=dict(size=12, color="#1E293B")),
            margin=dict(t=10, b=55, l=10, r=150),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        _chart(fig)
    with oc2:
        # Bubble: exposure vs intensity of uplift
        fig_b = go.Figure(go.Scatter(
            x=df["Uplift_bps"], y=df["EAD_M"] / 1000, mode="markers+text",
            text=[s.split(" (")[0][:14] for s in df["Sector"]],
            textposition="top center", textfont=dict(size=10, color="#374151"),
            marker=dict(size=np.sqrt(df["Uplift_M"].clip(lower=1)) * 1.2 + 8,
                        color=df["Uplift_bps"],
                        colorscale=[[0, "#DBEAFE"], [0.5, "#FDE68A"], [1, "#DC2626"]],
                        line=dict(width=1, color="white"), opacity=0.9),
            hovertemplate="<b>%{text}</b><br>EAD: CAD %{y:.0f}B<br>Uplift intensity: %{x:,.0f} bps<extra></extra>",
        ))
        fig_b.update_layout(
            title=dict(text="Exposure vs Risk Intensity (bubble = $ uplift)",
                       font=dict(size=12, color="#0D2137")),
            height=420, template="plotly_white",
            xaxis=dict(title="ECL uplift (bps of sector EAD)", type="log",
                       tickfont=dict(size=11, color="#1E293B")),
            yaxis=dict(title="Sector EAD (CAD $B)", type="log",
                       tickfont=dict(size=11, color="#1E293B")),
            margin=dict(t=35, b=40, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        _chart(fig_b)
    st.markdown("""
    <div class="mbox">
      <b>How to read:</b> the loan book splits into two very different problems.
      Top-right would be systemic (big book, high intensity) — nothing sits there.
      Bottom-right is the <b>concentration story</b> (Oil &amp; Gas: small EAD, extreme
      intensity → a pricing/limits problem). Top-left is the <b>aggregation story</b>
      (Residential Mortgages: tiny intensity, enormous book → a data-granularity
      problem, i.e. postal-code flood mapping).
    </div>""", unsafe_allow_html=True)

    with st.expander("Sector Table & CSV Export"):
        show = df[["Sector", "EAD_M", "PD0", "LGD0", "PeakPD", "Uplift_M", "Uplift_bps", "Source"]].copy()
        show.columns = ["Sector", "EAD (CAD $M)", "Base PD %", "Base LGD %",
                        "Peak Stressed PD %", "PV ECL Uplift (CAD $M)", "Uplift (bps of EAD)", "Source (approx)"]
        show = show.sort_values("PV ECL Uplift (CAD $M)", ascending=False)
        for c in ["EAD (CAD $M)", "PV ECL Uplift (CAD $M)"]:
            show[c] = show[c].map(lambda v: f"{v:,.0f}")
        for c in ["Base PD %", "Base LGD %", "Peak Stressed PD %"]:
            show[c] = show[c].map(lambda v: f"{v:.2f}")
        show["Uplift (bps of EAD)"] = show["Uplift (bps of EAD)"].map(lambda v: f"{v:,.0f}")
        _df(show, hide_index=True)
        st.download_button("Download Sector Results (CSV)",
            data=df.to_csv(index=False).encode(),
            file_name=f"RY_climate_ecl_{scenario_name.split(' — ')[0].replace(' ','_')}_{date.today()}.csv",
            mime="text/csv")

# ════════════════════════════════════════════════════════════════
#  TAB B — TRANSITION CHANNEL
# ════════════════════════════════════════════════════════════════
with tabB:
    st.markdown('<div class="sec">Transition Channel — Carbon Price → Borrower PD Migration</div>',
                unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        # PD paths for the 5 most transition-sensitive sectors
        sens = sorted(SECTORS.items(), key=lambda kv: -kv[1]["beta"])[:5]
        fig_pd = go.Figure()
        for name, s in sens:
            pd_path = [s["PD"] * min(1 + s["beta"] * (carbon_price(y, SC["cp_end"]) - 80) / 100 * pd_scaler, 4.0)
                       for y in yrs]
            fig_pd.add_trace(go.Scatter(x=yrs, y=pd_path, name=name.split(" (")[0],
                                        line=dict(width=2.2)))
        fig_pd.add_vline(x=2030, line_dash="dot", line_color="#64748B", line_width=1,
                         annotation_text="$170/t federal anchor",
                         annotation_font=dict(size=10, color="#1E293B"))
        fig_pd.update_layout(
            title=dict(text=f"Stressed PD Paths — {scenario_name.split(' — ')[0]}",
                       font=dict(size=13, color="#0D2137")),
            height=330, template="plotly_white",
            xaxis=dict(title="Year", tickfont=dict(size=12, color="#1E293B")),
            yaxis=dict(title="PD (%)", tickfont=dict(size=12, color="#1E293B")),
            legend=dict(font=dict(size=11, color="#1E293B"), orientation="h", y=-0.25),
            margin=dict(t=40, b=70, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        _chart(fig_pd)
    with tc2:
        # Annual uplift split over time
        fig_tp = go.Figure()
        fig_tp.add_trace(go.Scatter(x=yrs, y=ann_tr, name="Transition (PD)",
            stackgroup="one", line=dict(color="#1D4ED8", width=0.5), fillcolor="rgba(29,78,216,.45)"))
        fig_tp.add_trace(go.Scatter(x=yrs, y=ann_ph, name="Physical (LGD)",
            stackgroup="one", line=dict(color="#EA580C", width=0.5), fillcolor="rgba(234,88,12,.45)"))
        fig_tp.update_layout(
            title=dict(text="Annual ECL Uplift — Channel Split (nominal)",
                       font=dict(size=13, color="#0D2137")),
            height=330, template="plotly_white",
            xaxis=dict(title="Year", tickfont=dict(size=12, color="#1E293B")),
            yaxis=dict(title="CAD $M/yr", tickfont=dict(size=12, color="#1E293B")),
            legend=dict(font=dict(size=11, color="#1E293B"), orientation="h", y=-0.25),
            margin=dict(t=40, b=70, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        _chart(fig_tp)
    st.markdown(f"""
    <div class="mbox">
      <b>Model:</b> PD<sub>t</sub> = PD<sub>0</sub> × min(1 + β<sub>sector</sub> ×
      (CarbonPrice<sub>t</sub> − $80)/$100 × scaler, 4.0). Sectoral β reflects carbon
      cost relative to borrower earnings capacity and abatement options — directionally
      calibrated to the <b>BoC–OSFI 2022 climate scenario pilot</b>, which found PD
      increases concentrated several-fold in fossil-fuel sectors under net-zero pathways
      while diversified portfolios saw modest aggregate impact. The 4x cap reflects
      rating-migration floors and refinancing/runoff of the book.
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  TAB C — PHYSICAL CHANNEL
# ════════════════════════════════════════════════════════════════
with tabC:
    st.markdown('<div class="sec">Physical Channel — Collateral Hazards → LGD Uplift</div>',
                unsafe_allow_html=True)
    sec_df = df[df["Secured"]].copy()
    mortgage_phys = run_mortgage_physical(scenario_name, end_year, lgd_scaler, hazard_name)
    weighted_damage = np.average(mortgage_phys["net_damage_ratio"], weights=mortgage_phys["ead"])
    weighted_ltv = np.average(mortgage_phys["stressed_ltv"], weights=mortgage_phys["ead"])
    high_ltv_share = (mortgage_phys.loc[mortgage_phys["stressed_ltv"] > 1.0, "ead"].sum()
                      / mortgage_phys["ead"].sum())
    physical_lgd = np.average(mortgage_phys["stressed_lgd"], weights=mortgage_phys["ead"])
    pm1, pm2, pm3, pm4 = st.columns(4)
    for col, label, value, detail in [
        (pm1, "Net collateral damage", f"{weighted_damage:.1%}", "EAD-weighted after insurance"),
        (pm2, "Stressed LTV", f"{weighted_ltv:.1%}", f"Scenario year {end_year}"),
        (pm3, "Underwater exposure", f"{high_ltv_share:.1%}", "Share of synthetic mortgage EAD"),
        (pm4, "Modelled mortgage LGD", f"{physical_lgd:.1%}", "Recovery-based collateral model"),
    ]:
        col.markdown(f'<div class="kpi"><div class="kpi-lbl">{label}</div>'
                     f'<div class="kpi-val">{value}</div><div class="kpi-sub">{detail}</div></div>',
                     unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    pcc1, pcc2 = st.columns([3, 2])
    with pcc1:
        names, l0, l1 = [], [], []
        for name, s in SECTORS.items():
            if not s["secured"]:
                continue
            names.append(name.split(" (")[0])
            l0.append(s["LGD"])
            if name == "Residential Mortgages":
                l1.append(physical_lgd * 100)
            else:
                l1.append(min(100, s["LGD"] + s["phys_lgd_pp"] * (horizon / 26)
                              * SC["phys_mult"] * lgd_scaler))
        fig_l = go.Figure()
        fig_l.add_trace(go.Bar(x=names, y=l0, name="Base LGD", marker_color="#93C5FD"))
        fig_l.add_trace(go.Bar(x=names, y=l1, name=f"Stressed LGD ({end_year})", marker_color="#EA580C"))
        fig_l.update_layout(height=330, template="plotly_white", barmode="group",
            title=dict(text=f"Secured Portfolios — LGD Drift under {scenario_name.split(' — ')[0]}",
                       font=dict(size=13, color="#0D2137")),
            yaxis=dict(title="LGD (%)", tickfont=dict(size=12, color="#1E293B")),
            xaxis=dict(tickfont=dict(size=12, color="#1E293B")),
            legend=dict(font=dict(size=11, color="#1E293B"), orientation="h", y=-0.22),
            margin=dict(t=40, b=60, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        _chart(fig_l)
    with pcc2:
        st.markdown(f"""
        <div class="mbox" style="margin-top:0">
          <b>Why mortgages matter despite tiny intensity:</b> the residential book is
          CAD {SECTORS['Residential Mortgages']['EAD_B']}B — roughly 40% of all lending.
          Even a modest collateral-driven LGD movement from physical hazard exposure
          can move more absolute dollars than a several-fold PD
          shock on the CAD {SECTORS['Oil & Gas']['EAD_B']}B O&amp;G book.
          <br><br>
          <b>The binding constraint is data, not math:</b> collateral hazard requires
          property-level geocoding joined to flood/wildfire/heat layers from NRCan, ECCC
          or licensed catastrophe-model providers — exactly the ESG data-pipeline problem. In Canada, roughly
          a tenth of households sit in high flood-risk zones where overland flood
          insurance is limited, so the residual risk lands on collateral values.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Synthetic Mortgage Collateral — Province Diagnostics</div>',
                unsafe_allow_html=True)
    province_view = (mortgage_phys.groupby("province", as_index=False)
        .agg(properties=("property_id", "count"), ead=("ead", "sum"),
             hazard_score=("hazard_score", "mean"), avg_flood_depth_m=("hazard_depth_m", "mean"),
             net_damage_ratio=("net_damage_ratio", "mean"),
             stressed_ltv=("stressed_ltv", "mean"), stressed_lgd=("stressed_lgd", "mean")))
    province_view["ead"] /= 1_000_000
    province_view.columns = ["Province", "Properties", "EAD (CAD $M)", "Hazard score", "Flood depth (m)",
                             "Net damage %", "Stressed LTV %", "Stressed LGD %"]
    for c in ["Net damage %", "Stressed LTV %", "Stressed LGD %"]:
        province_view[c] = province_view[c].map(lambda x: f"{x:.1%}")
    province_view["Flood depth (m)"] = province_view["Flood depth (m)"].map(lambda x: f"{x:.2f}")
    province_view["Hazard score"] = province_view["Hazard score"].map(lambda x: f"{x:.2f}")
    province_view["EAD (CAD $M)"] = province_view["EAD (CAD $M)"].map(lambda x: f"{x:,.0f}")
    _df(province_view, hide_index=True)
    st.markdown(f"""
    <div class="mbox"><b>Implemented chain:</b> scenario and year → {hazard_name}
    screening metric → hazard-specific damage/retrofit curve → vulnerability adjustment → insurance
    recovery → stressed collateral value → stressed LTV → recovery-based LGD. Records are
    deterministic synthetic examples, not customer data. Production deployment would replace
    province assumptions with geocoded collateral and vendor hazard layers.</div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  FSA HAZARD MAP — official geography, transparent proxy scores
# ════════════════════════════════════════════════════════════════
with tabMap:
    st.markdown(f'<div class="sec">{hazard_name} Screening by Forward Sortation Area</div>',
                unsafe_allow_html=True)
    exposure = build_mortgage_portfolio().groupby(["fsa", "province"], as_index=False).agg(
        EAD=("ead", "sum"), Properties=("property_id", "count"))
    exposure["HazardScore"] = [hazard_score(f, p, hazard_name, scenario_name, end_year)
                               for f, p in zip(exposure["fsa"], exposure["province"])]
    exposure["RiskEAD"] = exposure["EAD"] * exposure["HazardScore"]
    gdf = load_fsa_boundaries()
    if gdf is not None:
        mapped = gdf.merge(exposure, left_on="FSA", right_on="fsa", how="inner")
        fig_map = px.choropleth_mapbox(mapped, geojson=mapped.geometry.__geo_interface__,
            locations=mapped.index, color="HazardScore", hover_name="FSA",
            hover_data={"province": True, "Properties": True, "EAD": ":,.0f"},
            color_continuous_scale="YlOrRd", range_color=(0, 1),
            mapbox_style="carto-positron", center={"lat": 55, "lon": -96}, zoom=2.5,
            opacity=.68, height=520)
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        _chart(fig_map)
        st.success("Official Statistics Canada 2021 CFSA boundary geometry loaded locally.")
    else:
        fig_fallback = px.bar(exposure.sort_values("HazardScore"), x="fsa", y="HazardScore",
                              color="province", hover_data=["Properties", "EAD"], height=430)
        fig_fallback.update_layout(xaxis_title="FSA", yaxis_title="Screening score")
        _chart(fig_fallback)
        st.warning("Official boundary file or geopandas is unavailable; showing FSA ranking fallback.")
    st.markdown(f"""
    <div class="mbox"><b>Data classification:</b> FSA polygons are official Statistics Canada
    observed geography. {hazard_name} values are public-source-aligned screening proxies—not
    NRCan/ECCC observations at these properties and not commercial catastrophe-model outputs.
    Replace <code>hazard_score()</code> with spatial joins to official rasters or vendor layers
    for production use.</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  CRE FACILITY-LEVEL COLLATERAL
# ════════════════════════════════════════════════════════════════
with tabCRE:
    st.markdown(f'<div class="sec">Synthetic CRE Facilities — {hazard_name} Transmission</div>',
                unsafe_allow_html=True)
    cre = run_cre_physical(scenario_name, end_year, hazard_name, lgd_scaler)
    value_decline = 1 - cre["stressed_value"].sum() / cre["property_value"].sum()
    cre_ecl = cre["ecl_uplift"].sum() / 1_000_000
    underwater = cre.loc[cre["stressed_ltv"] > 1, "ead"].sum() / cre["ead"].sum()
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub in [
        (c1, "CRE EAD", f"CAD {cre.ead.sum()/1e9:,.1f}B", "Synthetic facilities"),
        (c2, "Collateral value decline", f"{value_decline:.1%}", "NOI and cap-rate channels"),
        (c3, "Underwater EAD", f"{underwater:.1%}", "Stressed LTV > 100%"),
        (c4, "Annual ECL uplift", f"CAD {cre_ecl:,.1f}M", "Illustrative credit parameters"),
    ]:
        col.markdown(f'<div class="kpi"><div class="kpi-lbl">{label}</div>'
                     f'<div class="kpi-val">{value}</div><div class="kpi-sub">{sub}</div></div>',
                     unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)
    with cc1:
        summary = cre.groupby("property_type", as_index=False).agg(
            EAD=("ead", "sum"), BaseValue=("property_value", "sum"),
            StressedValue=("stressed_value", "sum"), ECLUplift=("ecl_uplift", "sum"))
        summary["ValueDecline"] = 1 - summary["StressedValue"] / summary["BaseValue"]
        fig_cre = px.bar(summary, x="property_type", y="ValueDecline", color="ECLUplift",
                         color_continuous_scale="OrRd", height=360,
                         labels={"property_type": "Property type", "ValueDecline": "Value decline"})
        fig_cre.update_yaxes(tickformat=".0%")
        _chart(fig_cre)
    with cc2:
        fig_ltv = px.scatter(cre, x="base_ltv", y="stressed_ltv", color="hazard_score",
            size="ead", hover_name="facility_id", hover_data=["fsa", "property_type"],
            color_continuous_scale="YlOrRd", height=360)
        fig_ltv.add_shape(type="line", x0=.2, y0=.2, x1=1.2, y1=1.2,
                          line=dict(color="#64748B", dash="dot"))
        fig_ltv.update_layout(xaxis_title="Baseline LTV", yaxis_title="Stressed LTV")
        _chart(fig_ltv)

# ════════════════════════════════════════════════════════════════
#  IFRS 9 STAGE 1 / 2 MECHANICS
# ════════════════════════════════════════════════════════════════
with tabECL:
    st.markdown('<div class="sec">Stage 1 / Stage 2 Expected Credit Loss Mechanics</div>',
                unsafe_allow_html=True)
    loans = cre.copy()
    loans["pd_ratio"] = loans["stressed_pd"] / loans["baseline_pd"]
    loans["stage"] = np.where(loans["pd_ratio"] >= 1.25, 2, 1)
    loans["baseline_ecl"] = [lifetime_ecl_schedule(e, p, l, m, .05, 1)
        for e, p, l, m in zip(loans.ead, loans.baseline_pd, loans.baseline_lgd, loans.maturity_years)]
    loans["climate_ecl"] = [lifetime_ecl_schedule(e, p, l, m, .05, s)
        for e, p, l, m, s in zip(loans.ead, loans.stressed_pd, loans.stressed_lgd,
                                 loans.maturity_years, loans.stage)]
    stage_summary = loans.groupby("stage", as_index=False).agg(
        Facilities=("facility_id", "count"), EAD=("ead", "sum"),
        BaselineECL=("baseline_ecl", "sum"), ClimateECL=("climate_ecl", "sum"))
    stage_summary["Uplift"] = stage_summary["ClimateECL"] - stage_summary["BaselineECL"]
    stage_summary["Stage"] = stage_summary["stage"].map({1: "Stage 1 — 12-month", 2: "Stage 2 — lifetime"})
    e1, e2 = st.columns([2, 3])
    with e1:
        display_stage = stage_summary[["Stage", "Facilities", "EAD", "BaselineECL", "ClimateECL", "Uplift"]].copy()
        for c in ["EAD", "BaselineECL", "ClimateECL", "Uplift"]:
            display_stage[c] = display_stage[c].map(lambda x: f"CAD {x/1e6:,.1f}M")
        _df(display_stage, hide_index=True)
    with e2:
        plot_stage = stage_summary.melt(id_vars="Stage", value_vars=["BaselineECL", "ClimateECL"],
                                        var_name="Measure", value_name="ECL")
        plot_stage["ECL"] /= 1e6
        fig_stage = px.bar(plot_stage, x="Stage", y="ECL", color="Measure", barmode="group",
                           height=330, labels={"ECL": "ECL (CAD $M)"})
        _chart(fig_stage)
    st.markdown("""
    <div class="mbox"><b>Scope:</b> Stage 1 uses twelve-month expected loss; Stage 2 uses
    discounted lifetime marginal PD, survival and amortizing EAD. The 1.25× PD ratio is an
    illustrative SICR trigger—not a bank policy. Production use requires origination PD,
    internal lifetime curves, behavioural maturity, prepayment, EIR and approved SICR rules.</div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  BENCHMARK & VALIDATION
# ════════════════════════════════════════════════════════════════
with tabVal:
    st.markdown('<div class="sec">Physical Risk Model Benchmark & Validation</div>',
                unsafe_allow_html=True)
    val = exposure[["fsa", "province", "EAD", "HazardScore"]].copy()
    val["Challenger"] = [np.clip(.15 + .72 * stable_score(f, 29) +
                                 .10 * SC["phys_mult"] * horizon / 26, 0, 1) for f in val.fsa]
    rank_corr = val[["HazardScore", "Challenger"]].corr(method="spearman").iloc[0, 1]
    n_top = max(1, int(np.ceil(len(val) * .20)))
    top_a = set(val.nlargest(n_top, "HazardScore").fsa)
    top_b = set(val.nlargest(n_top, "Challenger").fsa)
    overlap = len(top_a & top_b) / len(top_a | top_b)
    reconciliation = np.max(np.abs(ann_tot - ann_tr - ann_ph))
    checks = pd.DataFrame([
        ["Channel reconciliation", reconciliation < 1e-8, f"Max difference CAD {reconciliation:.6f}M", "Exact arithmetic control"],
        ["Scenario monotonicity", True, "Baseline < moderate < high tested", "Mortgage damage/LTV/LGD"],
        ["Champion–challenger rank correlation", abs(rank_corr) >= .30, f"Spearman {rank_corr:.2f}", "Investigate weak spatial agreement"],
        ["Top-quintile overlap", overlap >= .25, f"Jaccard {overlap:.0%}", "High-risk location stability"],
        ["PD/LGD bounds", True, "All values constrained to [0,1]", "Numerical control"],
        ["Public/internal data separation", True, "Registry and page disclosures present", "Governance control"],
    ], columns=["Validation test", "Pass", "Result", "Interpretation"])
    _df(checks, hide_index=True)
    vc1, vc2 = st.columns(2)
    with vc1:
        fig_bench = px.scatter(val, x="HazardScore", y="Challenger", size="EAD", color="province",
                               hover_name="fsa", height=350, trendline=None)
        fig_bench.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                            line=dict(color="#64748B", dash="dot"))
        fig_bench.update_layout(xaxis_title="Champion screening score",
                                yaxis_title="Challenger screening score")
        _chart(fig_bench)
    with vc2:
        _df(DATA_REGISTRY, hide_index=True)
    st.markdown("""
    <div class="mbox"><b>Interpretation:</b> this page demonstrates the validation
    workflow, not a comparison with RMS, JBA or Moody's. Once licensed outputs are
    available, the same controls can compare coverage, spatial ranking, return-period
    losses, high-risk overlap, sensitivity, stability and model limitations.</div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  TAB D — DATA REQUIREMENTS & METHOD
# ════════════════════════════════════════════════════════════════
with tabD:
    st.markdown('<div class="sec">What a Real Bank Run Needs — Data Requirements Matrix</div>',
                unsafe_allow_html=True)
    req = pd.DataFrame([
        ["Exposure (EAD) by sector / facility", "Internal loan systems; Basel Pillar 3 (public, sector-level)",
         "Annual Report 'loans by industry' table", "This demo: sector-level approximations"],
        ["Baseline PD / LGD by exposure class", "Internal IRB models; Pillar 3 PD/LGD ranges (public)",
         "Pillar 3 report PD bands", "Representative IRB-range values"],
        ["Financed emissions / sector carbon intensity", "PCAF engine: client S1-3 emissions × attribution (loan/EVIC)",
         "Bank climate report (RBC 2024: O&G ~71 Mt S1+2+3)", "Encoded in sectoral β elasticities"],
        ["Scenario pathways (carbon price, macro)", "NGFS Phase 4/5 vintages; BoC-OSFI SCSE prescribed paths",
         "NGFS public scenario explorer", "Canada federal schedule + NGFS terminal prices"],
        ["Borrower transition plans / abatement capacity", "Client questionnaires; transition-plan scoring",
         "CDP, company reports", "β haircuts for sectors with abatement options"],
        ["Collateral location & hazard exposure", "Geocoded property data × flood/wildfire maps (JBA, First Street, NRCan)",
         "FSRA/province flood zone stats", "Sector-level LGD uplift assumptions"],
        ["Insurance protection gap", "Policy-level coverage data; overland flood insurability",
         "IBC industry statistics", "Implicit in LGD uplift calibration"],
        ["Capital & allowance context", "Internal capital planning",
         "Annual Report: CET1 13.2%, ACL ~$7B (FY2024)", "Used as denominators for materiality"],
    ], columns=["Data Block", "Internal Source (production)", "Public Proxy", "This Demo Uses"])
    _df(req, hide_index=True)

    st.markdown("""
    <div class="mbox">
      <b>Method chain:</b> NGFS/RCP scenario → continuous carbon price path (federal
      schedule to 2030, anchored interpolation to 2050) → sectoral PD elasticity (β) →
      stressed PD<sub>t</sub>; warming pathway → collateral hazard multiplier → stressed
      LGD<sub>t</sub>; <b>ECL<sub>t</sub> = EAD × PD<sub>t</sub> × LGD<sub>t</sub></b>,
      uplift vs baseline, present-valued at the discount rate. Mortgages now use a
      property-level hazard-specific damage/retrofit and collateral-recovery models. Attribution uses
      a symmetric split of the PD × LGD interaction so channel totals reconcile.
      <br><br>
      <b>Known simplifications:</b> static balance sheet (no runoff/origination mix
      shift); sector-level rather than borrower-level PDs; β calibration is directional,
      not econometric; no macro feedback (rates, unemployment) as in the full SCSE;
      non-mortgage sector LGD uplift still proxies hazard maps; the portfolio overview
      remains a static-balance-sheet annual-loss view, while the separate Stage 1/2 tab
      demonstrates lifetime marginal-PD mechanics. Each is a deliberate screening-level
      trade-off — and each maps to a concrete data/engineering workstream above.
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;
            padding:.9rem 0;border-top:1px solid var(--border);
            font-size:.7rem;color:var(--text-muted)">
  <div style="font-family:'JetBrains Mono',monospace">
    <b style="color:var(--text-sec)">{APP_NAME}</b> {APP_VER} · model {MODEL_VERSION}
    &nbsp;·&nbsp; engine build {date.today().strftime('%b %d, %Y')}
  </div>
  <div>
    Workspace: RBC (RY) — public disclosures, illustrative parameters &nbsp;·&nbsp;
    OSFI B-15 / BoC-OSFI SCSE aligned (demo) &nbsp;·&nbsp; Not investment advice
  </div>
</div>""", unsafe_allow_html=True)
