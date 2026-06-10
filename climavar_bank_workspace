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

Run:  streamlit run climavar_bank_workspace.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

# ── Product identity ──────────────────────────────────────────────────────────
APP_NAME    = "ClimaVaR Terminal"
APP_TAGLINE = "Climate Risk Analytics Platform"
APP_VER     = "v0.9-bank"

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

# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE — sector ECL uplift:  ECL_t = EAD x PD_t x LGD_t
#  Transition channel: carbon price path -> borrower cost stress -> PD_t
#  Physical channel:   hazard damage to collateral -> LGD_t
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def run_bank(scenario_key, horizon, dr_pct, pd_scaler, lgd_scaler):
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
            # Physical: collateral LGD drift toward 2050 uplift, scenario-scaled
            lgd_t = lgd0 + (s["phys_lgd_pp"] / 100) * ((y - 2024) / 26) * SC["phys_mult"] * lgd_scaler
            ecl_t = ead * pd_t * lgd_t
            ecl_tr = ead * pd_t * lgd0          # transition-only counterfactual
            ecl_ph = ead * pd0 * lgd_t          # physical-only counterfactual
            disc = (1 + dr) ** (y - 2024)
            u  = (ecl_t - ecl0) / disc
            pv_u  += u
            pv_tr += (ecl_tr - ecl0) / disc
            pv_ph += (ecl_ph - ecl0) / disc
            annual_total[i] += ecl_t - ecl0
            annual_tr[i]    += ecl_tr - ecl0
            annual_ph[i]    += ecl_ph - ecl0
            peak_pd = max(peak_pd, pd_t)
        # Normalize attribution (cross-term split pro-rata)
        attr = pv_tr + pv_ph
        tr_share = pv_tr / attr if attr > 0 else 0.5
        rows.append({
            "Sector": name, "EAD_M": ead, "PD0": pd0 * 100, "LGD0": lgd0 * 100,
            "PeakPD": peak_pd * 100, "Uplift_M": pv_u,
            "Transition_M": pv_u * tr_share, "Physical_M": pv_u * (1 - tr_share),
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

    st.markdown('<div class="sb-lbl">Stress Horizon</div>', unsafe_allow_html=True)
    horizon = st.slider("Horizon (years)", 1, 26, 10, label_visibility="collapsed",
        help="OSFI B-15 expects short-, medium- and long-term horizon analysis.")
    end_year = 2024 + horizon

    st.markdown('<div class="sb-lbl">Model Calibration</div>', unsafe_allow_html=True)
    dr_pct = st.number_input("Discount Rate (%)", value=5.0, step=0.1, format="%.1f",
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
df, yrs, ann_tot, ann_tr, ann_ph = run_bank(scenario_name, horizon, dr_pct, pd_scaler, lgd_scaler)
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
    (k1, "ECL Uplift (PV)",      f"CAD {total_uplift:,.0f}M",
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
  climate drivers add <b>CAD {total_uplift:,.0f}M of present-value expected credit loss</b>
  ({uplift_bps:,.0f} bps of the loan book) — equivalent to {pct_acl:,.0f}% of the current
  allowance but only {pct_cet1:.1f}% of CET1 capital. Transition channels (carbon price →
  borrower PD) drive ~{tr_share_tot:.0f}% of the uplift; the rest is collateral-hazard LGD.
  The bank-level story mirrors the BoC-OSFI pilot: risk is <b>concentrated, not systemic</b> —
  small in capital terms, large relative to sector-level pricing and provisioning.
</div>""", unsafe_allow_html=True)

tabA, tabB, tabC, tabD = st.tabs([
    "Sector Overview", "Transition Channel (PD)", "Physical Channel (LGD)", "Data Requirements & Method",
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
    pcc1, pcc2 = st.columns([3, 2])
    with pcc1:
        names, l0, l1 = [], [], []
        for name, s in SECTORS.items():
            if not s["secured"]:
                continue
            names.append(name.split(" (")[0])
            l0.append(s["LGD"])
            l1.append(s["LGD"] + s["phys_lgd_pp"] * (horizon / 26) * SC["phys_mult"] * lgd_scaler)
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
          A {SECTORS['Residential Mortgages']['phys_lgd_pp']:.0f}pp LGD drift from
          uninsured flood exposure moves more absolute dollars than a several-fold PD
          shock on the CAD {SECTORS['Oil & Gas']['EAD_B']}B O&amp;G book.
          <br><br>
          <b>The binding constraint is data, not math:</b> collateral hazard requires
          property-level geocoding joined to flood/wildfire maps (e.g. JBA, First
          Street, NRCan) — exactly the ESG data-pipeline problem. In Canada, roughly
          a tenth of households sit in high flood-risk zones where overland flood
          insurance is limited, so the residual risk lands on collateral values.
        </div>""", unsafe_allow_html=True)

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
      uplift vs baseline, present-valued at the discount rate. Attribution splits the
      uplift pro-rata between PD-only and LGD-only counterfactuals.
      <br><br>
      <b>Known simplifications:</b> static balance sheet (no runoff/origination mix
      shift); sector-level rather than borrower-level PDs; β calibration is directional,
      not econometric; no macro feedback (rates, unemployment) as in the full SCSE;
      LGD uplift proxies hazard maps rather than computing them; 1-yr ECL each year
      rather than full IFRS 9 lifetime staging. Each is a deliberate screening-level
      trade-off — and each maps to a concrete data/engineering workstream above.
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;
            padding:.9rem 0;border-top:1px solid var(--border);
            font-size:.7rem;color:var(--text-muted)">
  <div style="font-family:'JetBrains Mono',monospace">
    <b style="color:var(--text-sec)">{APP_NAME}</b> {APP_VER}
    &nbsp;·&nbsp; engine build {date.today().strftime('%b %d, %Y')}
  </div>
  <div>
    Workspace: RBC (RY) — public disclosures, illustrative parameters &nbsp;·&nbsp;
    OSFI B-15 / BoC-OSFI SCSE aligned (demo) &nbsp;·&nbsp; Not investment advice
  </div>
</div>""", unsafe_allow_html=True)
