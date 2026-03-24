import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

st.set_page_config(
    page_title="SemiTrack India",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Data ────────────────────────────────────────────────────────────────────
YEARS = list(range(1995, 2025))
REAL  = [0.870,0.511,0.707,0.680,0.846,0.842,0.805,0.803,0.935,0.948,1.017,1.229,1.399,0.933,2.286,2.398,2.529,2.411,1.633,1.362,1.738,1.823,2.672,6.701,8.789,7.068,9.866,11.81,12.73,14.60]
NOM   = [0.237,0.154,0.230,0.246,0.322,0.336,0.339,0.358,0.447,0.490,0.565,0.741,0.930,0.694,1.851,2.152,2.560,2.721,1.997,1.763,1.738,1.892,2.883,7.561,10.34,8.511,12.59,16.51,19.01,23.05]
CHINA = [0.78,0.72,1.61,3.04,2.61,2.97,2.94,5.27,5.15,6.88,9.80,9.49,18.3,17.2,22.3,18.5,18.4,18.4,24.0,27.4,32.7,33.5,27.7,33.2,35.5,34.5,35.7,31.6,53.5,45.8]
HHI   = [0.051,0.084,0.079,0.062,0.062,0.058,0.058,0.046,0.039,0.041,0.041,0.041,0.044,0.077,0.052,0.090,0.059,0.056,0.082,0.089,0.117,0.120,0.118,0.210,0.219,0.188,0.225,0.183,0.321,0.291]
HS8   = [0.228,0.148,0.220,0.233,0.314,0.317,0.314,0.334,0.419,0.459,0.531,0.680,0.841,0.536,1.721,1.885,2.420,2.671,1.944,1.687,1.652,1.765,2.683,7.420,10.20,8.421,12.45,16.33,18.68,22.86]
HS3   = [0.009,0.006,0.010,0.014,0.008,0.019,0.026,0.024,0.028,0.030,0.034,0.061,0.088,0.158,0.130,0.267,0.139,0.049,0.053,0.076,0.085,0.128,0.201,0.141,0.138,0.089,0.141,0.181,0.331,0.189]
YOY   = [None,-41.3,38.4,-3.8,24.4,-0.4,-4.4,-0.3,16.4,1.5,7.3,20.8,13.8,-33.3,144.9,4.9,5.4,-4.7,-32.3,-16.6,27.6,4.9,46.6,150.8,31.2,-19.6,39.6,19.7,7.8,14.6]
FC_YEARS = [2025,2026,2027]; FC_VALS = [13.93,14.16,14.08]; FC_LO = [9.89,10.03,9.98]; FC_HI = [19.62,19.98,19.85]

NON_CHINA = [round(100-c, 2) for c in CHINA]
HS8_SHARE = [round(HS8[i]/NOM[i]*100, 2) for i in range(len(YEARS))]
HS3_SHARE = [round(HS3[i]/NOM[i]*100, 2) for i in range(len(YEARS))]
REAL_IDX  = [round(r/REAL[22]*100,1) for r in REAL]
NOM_IDX   = [round(n/NOM[22]*100,1)  for n in NOM]

COUNTRIES = [
    {"name":"China","share":45.8,"val":10.56,"risk":9.0,"level":"Critical"},
    {"name":"Taiwan","share":25.7,"val":5.92,"risk":8.5,"level":"Critical"},
    {"name":"South Korea","share":15.0,"val":3.47,"risk":4.5,"level":"Moderate"},
    {"name":"Japan","share":2.6,"val":0.60,"risk":3.0,"level":"Low"},
    {"name":"Malaysia","share":2.2,"val":0.51,"risk":4.0,"level":"Moderate"},
    {"name":"Singapore","share":2.1,"val":0.48,"risk":3.0,"level":"Low"},
    {"name":"Other","share":1.6,"val":0.36,"risk":5.0,"level":"High"},
    {"name":"Israel","share":0.8,"val":0.18,"risk":5.0,"level":"High"},
    {"name":"Hong Kong","share":0.8,"val":0.18,"risk":7.0,"level":"High"},
    {"name":"Philippines","share":0.7,"val":0.16,"risk":3.0,"level":"Low"},
]

VOLATILITY = []
for i in range(len(YEARS)):
    if i < 2:
        VOLATILITY.append(None)
    else:
        vals = [v for v in YOY[max(1,i-2):i+1] if v is not None]
        if vals:
            mean = sum(vals)/len(vals)
            var = sum((v-mean)**2 for v in vals)/len(vals)
            VOLATILITY.append(round(var**0.5, 2))
        else:
            VOLATILITY.append(None)

# ─── CSS ─────────────────────────────────────────────────────────────────────
# ENHANCED: All changes are CSS-only. No logic, data, or chart code modified.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:        #f0f2f8;
  --surface:   #ffffff;
  --border:    #e4e8f0;
  --border2:   #c8d0e0;
  --accent:    #1a56db;
  --accent-lt: #eff4ff;
  --danger:    #c81e1e;
  --danger-lt: #fdf2f2;
  --warn:      #c05621;
  --warn-lt:   #fffbf0;
  --ok:        #057a55;
  --ok-lt:     #f0fdf9;
  --text:      #111827;
  --text2:     #4b5563;
  --text3:     #9ca3af;
  --navy:      #0f1f3d;

  /* ENHANCED: Shadow system */
  --shadow-xs:  0 1px 2px rgba(15,31,61,.04), 0 1px 3px rgba(15,31,61,.06);
  --shadow-sm:  0 2px 6px rgba(15,31,61,.06), 0 1px 3px rgba(15,31,61,.05);
  --shadow-md:  0 4px 14px rgba(15,31,61,.09), 0 2px 6px rgba(15,31,61,.06);
  --shadow-lg:  0 8px 28px rgba(15,31,61,.12), 0 3px 8px rgba(15,31,61,.07);

  /* ENHANCED: Spacing scale */
  --space-xs:  8px;
  --space-sm:  14px;
  --space-md:  24px;
  --space-lg:  36px;
  --space-xl:  52px;

  /* ENHANCED: Border radius scale */
  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  16px;
  --radius-xl:  20px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}

/* hide default streamlit chrome */
[data-testid="stHeader"],
[data-testid="stSidebar"],
footer { display: none !important; }

[data-testid="stMainBlockContainer"],
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Outer wrapper ── */
.outer-wrap {
  max-width: 1300px;
  margin: 0 auto;
  /* ENHANCED: Improved padding with more bottom breathing room */
  padding: 0 40px 80px;
}

/* ── Top navbar — ENHANCED: backdrop-blur + refined shadow ── */
.navbar {
  background: rgba(15,31,61,.97);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,.07);
  /* ENHANCED: subtle bottom shadow for depth */
  box-shadow: 0 2px 16px rgba(0,0,0,.18);
  padding: 0 40px;
  display: flex;
  align-items: stretch;
  /* ENHANCED: slightly taller for better proportion */
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-inner {
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-icon {
  width: 34px; height: 34px;
  background: var(--accent);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
  /* ENHANCED: glow on icon */
  box-shadow: 0 0 14px rgba(26,86,219,.45);
}
.nav-title {
  font-family: 'DM Serif Display', serif;
  font-size: 18px;
  color: #ffffff;
  letter-spacing: .2px;
}
.nav-sub {
  font-size: 10px;
  color: #7a8fbb;
  letter-spacing: .9px;
  text-transform: uppercase;
  margin-top: 1px;
}
.nav-pills {
  display: flex;
  gap: 8px;
  align-items: center;
}
.nav-pill {
  font-size: 10px;
  padding: 5px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,.07);
  color: #8899bb;
  border: 1px solid rgba(255,255,255,.09);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: .3px;
  /* ENHANCED: smooth hover */
  transition: background .2s, color .2s, border-color .2s;
}
.nav-pill:hover {
  background: rgba(255,255,255,.13);
  color: #c4d0ee;
  border-color: rgba(255,255,255,.16);
}

/* ── Tab panel top padding — ENHANCED ── */
.stTabs [data-baseweb="tab-panel"] {
  padding: 0 !important;
  /* ENHANCED: add top breathing room after tab bar */
  padding-top: 0 !important;
}

/* ── Page header — ENHANCED spacing ── */
.page-head {
  /* ENHANCED: more generous top + bottom padding */
  padding: 36px 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
}
.page-head-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
}
.page-eyebrow {
  font-size: 10px;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 7px;
  /* ENHANCED: slight opacity animation placeholder for future */
  opacity: .85;
}
.page-h1 {
  font-family: 'DM Serif Display', serif;
  /* ENHANCED: larger heading for stronger hierarchy */
  font-size: 32px;
  line-height: 1.1;
  color: var(--text);
  margin: 0;
  letter-spacing: -.3px;
}
.page-sub {
  font-size: 13.5px;
  color: var(--text2);
  line-height: 1.7;
  margin-top: 8px;
  max-width: 74ch;
}
.data-badge {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text3);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 6px 12px;
  white-space: nowrap;
  box-shadow: var(--shadow-xs);
}

/* ── KPI strip — ENHANCED: shadow + hover + refined spacing ── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.kpi-strip.cols4 { grid-template-columns: repeat(4, 1fr); }
.kpi-strip.cols3 { grid-template-columns: repeat(3, 1fr); }

.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  /* ENHANCED: more generous padding */
  padding: 20px 22px 18px;
  position: relative;
  overflow: hidden;
  /* ENHANCED: layered shadow for lift */
  box-shadow: var(--shadow-sm);
  /* ENHANCED: smooth hover transition */
  transition: box-shadow .22s ease, transform .18s ease, border-color .18s ease;
}
.kpi:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--border2);
}
.kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  /* ENHANCED: slightly thicker accent bar */
  height: 4px;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.kpi.blue::before  { background: linear-gradient(90deg, var(--accent), #4f85f5); }
.kpi.red::before   { background: linear-gradient(90deg, var(--danger), #e84c4c); }
.kpi.amber::before { background: linear-gradient(90deg, var(--warn), #e07840); }
.kpi.green::before { background: linear-gradient(90deg, var(--ok), #2ea87a); }
.kpi.slate::before { background: linear-gradient(90deg, #9ca3af, #c4ccd8); }

.kpi-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  /* ENHANCED: slightly darker for better legibility */
  color: #7a8698;
  font-weight: 600;
  /* ENHANCED: more space below label */
  margin-bottom: 10px;
}
.kpi-val {
  font-family: 'DM Serif Display', serif;
  /* ENHANCED: slightly tuned size for balance */
  font-size: 30px;
  line-height: 1;
  color: var(--text);
}
.kpi.blue .kpi-val  { color: var(--accent); }
.kpi.red .kpi-val   { color: var(--danger); }
.kpi.amber .kpi-val { color: var(--warn); }
.kpi.green .kpi-val { color: var(--ok); }

.kpi-sub {
  /* ENHANCED: more breathing room above sub-label */
  margin-top: 9px;
  font-size: 11.5px;
  color: var(--text2);
  line-height: 1.55;
  /* ENHANCED: visual separator line */
  padding-top: 9px;
  border-top: 1px solid var(--border);
}

/* ── Card — ENHANCED: shadow tiers, hover, refined radius ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  /* ENHANCED: more generous padding */
  padding: 24px 26px;
  margin-bottom: 0;
  /* ENHANCED: card shadow */
  box-shadow: var(--shadow-sm);
  transition: box-shadow .22s ease;
}
.card:hover {
  box-shadow: var(--shadow-md);
}
.card-title {
  font-family: 'DM Serif Display', serif;
  /* ENHANCED: slightly larger card title */
  font-size: 18px;
  color: var(--text);
  margin: 0 0 4px;
  letter-spacing: -.1px;
}
.card-sub {
  font-size: 12.5px;
  color: var(--text3);
  /* ENHANCED: more space before divider */
  margin-bottom: 16px;
  line-height: 1.55;
}
.card-divider {
  height: 1px;
  background: var(--border);
  /* ENHANCED: refined divider spacing */
  margin: 14px 0 20px;
  opacity: .8;
}

/* ── Section head — ENHANCED spacing ── */
.sec-head {
  /* ENHANCED: more top margin so sections breathe apart */
  margin-top: 8px;
  margin-bottom: 20px;
}
.sec-tag {
  font-size: 10px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 6px;
  opacity: .85;
}
.sec-h2 {
  font-family: 'DM Serif Display', serif;
  /* ENHANCED: stronger section heading */
  font-size: 24px;
  color: var(--text);
  margin: 0 0 6px;
  line-height: 1.14;
  letter-spacing: -.2px;
}
.sec-p {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.7;
  max-width: 74ch;
  margin: 0;
}

/* ── Callout — ENHANCED: shadow + better spacing ── */
.callout {
  border-radius: var(--radius-sm);
  /* ENHANCED: more padding */
  padding: 13px 16px;
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--text2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  background: var(--accent-lt);
  /* ENHANCED: more top margin from chart */
  margin-top: 14px;
  box-shadow: var(--shadow-xs);
}
.callout.red   { border-left-color: var(--danger); background: var(--danger-lt); }
.callout.amber { border-left-color: var(--warn);   background: var(--warn-lt); }
.callout.green { border-left-color: var(--ok);     background: var(--ok-lt); }
.callout strong { color: var(--text); }
.callout-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 6px;
}
.callout.red   .callout-label { color: var(--danger); }
.callout.amber .callout-label { color: var(--warn); }
.callout.green .callout-label { color: var(--ok); }

/* ── Summary grid — ENHANCED: responsive + shadow ── */
.sum-grid {
  display: grid;
  /* ENHANCED: min-width prevents collapse at mid-viewport */
  grid-template-columns: repeat(5, minmax(160px, 1fr));
  gap: 14px;
  margin-top: 16px;
}
.sum-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  /* ENHANCED: more padding */
  padding: 16px 16px;
  box-shadow: var(--shadow-xs);
  transition: box-shadow .2s ease, transform .18s ease;
}
.sum-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.sum-kicker {
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text3);
  font-weight: 600;
  margin-bottom: 7px;
}
.sum-strong {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}
.sum-copy {
  font-size: 12px;
  color: var(--text2);
  line-height: 1.6;
}

/* ── Hero 2-col — ENHANCED: better proportions + shadow ── */
.hero-grid {
  display: grid;
  /* ENHANCED: more balanced ratio */
  grid-template-columns: 1.25fr 1fr;
  gap: 22px;
  margin-bottom: 28px;
}
.hero-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  /* ENHANCED: more generous padding */
  padding: 28px 30px;
  /* ENHANCED: elevated shadow for hero prominence */
  box-shadow: var(--shadow-md);
  transition: box-shadow .22s ease;
}
.hero-card:hover {
  box-shadow: var(--shadow-lg);
}
.hero-h {
  font-family: 'DM Serif Display', serif;
  /* ENHANCED: bolder hero heading */
  font-size: 26px;
  line-height: 1.18;
  color: var(--text);
  margin: 0 0 14px;
  letter-spacing: -.25px;
}
.hero-p {
  font-size: 13.5px;
  line-height: 1.78;
  color: var(--text2);
}
.stat-quad {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stat-q {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  /* ENHANCED: more padding */
  padding: 15px 16px;
  box-shadow: var(--shadow-xs);
  transition: box-shadow .18s;
}
.stat-q:hover {
  box-shadow: var(--shadow-sm);
}
.sq-label { font-size: 10px; text-transform: uppercase; letter-spacing: .9px; color: var(--text3); font-weight: 600; margin-bottom: 7px; }
.sq-val { font-family: 'DM Serif Display', serif; font-size: 28px; color: var(--accent); line-height: 1; }
.sq-copy { font-size: 11.5px; color: var(--text2); line-height: 1.55; margin-top: 6px; }

/* ── Timeline — ENHANCED ── */
.tl { margin-top: 16px; }
.tl-row {
  display: grid;
  grid-template-columns: 52px 1fr;
  gap: 14px;
  align-items: start;
  /* ENHANCED: more vertical padding between rows */
  padding: 12px 0;
  border-top: 1px solid var(--border);
}
.tl-row:first-child { border-top: none; padding-top: 0; }
.tl-yr {
  background: var(--accent-lt);
  color: var(--accent);
  border: 1px solid #c3d9fd;
  border-radius: var(--radius-sm);
  /* ENHANCED: bolder year badge */
  font-size: 11.5px;
  font-weight: 700;
  text-align: center;
  padding: 6px 0;
  font-family: 'JetBrains Mono', monospace;
}
.tl-txt { font-size: 12.5px; line-height: 1.7; color: var(--text2); }

/* ── Risk table — ENHANCED: row hover transition ── */
.rtable { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.rtable th {
  padding: 10px 12px;
  border-bottom: 2px solid var(--border2);
  text-align: left;
  font-size: 10px;
  letter-spacing: .8px;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 600;
}
.rtable td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  vertical-align: middle;
}
/* ENHANCED: smooth hover transition on table rows */
.rtable tbody tr {
  transition: background .15s ease;
}
.rtable tbody tr:hover td { background: #f4f6fc; }
.rtable tfoot td {
  font-weight: 600;
  background: var(--bg);
  border-top: 2px solid var(--border2);
  font-size: 13px;
  padding: 12px;
}
/* ENHANCED: pill-shaped badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 11px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .4px;
  text-transform: uppercase;
}
.b-crit { background: #fde8e8; color: #9b1c1c; }
.b-high { background: #fef3c7; color: #92400e; }
.b-mod  { background: #e1effe; color: #1e429f; }
.b-low  { background: #def7ec; color: #03543f; }

/* ── Regime table — ENHANCED ── */
.reg-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.reg-tbl th { padding: 10px 12px; border-bottom: 2px solid var(--border2); font-size: 10px; text-transform: uppercase; letter-spacing: .8px; color: var(--text3); font-weight: 600; }
.reg-tbl td { padding: 11px 12px; border-bottom: 1px solid var(--border); color: var(--text2); }
.reg-tbl tbody tr { transition: background .15s ease; }
.reg-tbl tbody tr:hover td { background: #f4f6fc; }
.reg-tbl .hl { color: var(--accent); font-weight: 600; }

/* ── Policy list — ENHANCED ── */
.plist { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.plist li {
  padding: 13px 15px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--bg);
  font-size: 12.5px;
  line-height: 1.7;
  color: var(--text2);
  /* ENHANCED: smooth hover */
  transition: background .18s, border-color .18s, box-shadow .18s;
  box-shadow: var(--shadow-xs);
}
.plist li:hover {
  background: #eef1f8;
  border-color: var(--border2);
  box-shadow: var(--shadow-sm);
}
.plist li strong { color: var(--text); }

/* ── Meta row — ENHANCED: shadow + bottom margin ── */
.meta-row {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px;
  /* ENHANCED: proper bottom margin before list */
  margin-bottom: 18px;
}
.meta-item {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 15px;
  box-shadow: var(--shadow-xs);
}
.meta-label { font-size: 9.5px; text-transform: uppercase; letter-spacing: 1px; color: var(--text3); font-weight: 600; margin-bottom: 5px; }
.meta-val { font-family: 'DM Serif Display', serif; font-size: 24px; color: var(--accent); line-height: 1; }

/* ── Verdict banner — ENHANCED ── */
.verdict {
  border-radius: var(--radius-lg);
  padding: 18px 22px;
  border: 1px solid var(--border);
  background: var(--surface);
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
}

/* ── Event chip — ENHANCED ── */
.echip {
  display: inline-flex;
  align-items: center;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  margin-left: 6px;
}
.echip.accent { background: var(--accent-lt); border-color: #c3d9fd; color: var(--accent); }
.echip.red    { background: var(--danger-lt); border-color: #fcd6d6; color: var(--danger); }
.echip.amber  { background: var(--warn-lt);   border-color: #fde8c3; color: var(--warn); }

/* ── Event bar — ENHANCED ── */
.event-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 15px 18px;
  font-size: 13px;
  line-height: 1.75;
  color: var(--text2);
  margin-bottom: 20px;
  box-shadow: var(--shadow-xs);
  /* ENHANCED: left accent stripe */
  border-left: 3px solid var(--accent);
}

/* ── Upload zone — ENHANCED ── */
.upload-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  margin-bottom: 22px;
  box-shadow: var(--shadow-sm);
}

/* ── Streamlit tab overrides — ENHANCED ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--navy) !important;
  padding: 0 40px !important;
  gap: 4px !important;
  /* ENHANCED: tab bar shadow */
  box-shadow: 0 2px 10px rgba(0,0,0,.15) !important;
}
.stTabs [data-baseweb="tab"] {
  border: none !important;
  /* ENHANCED: thicker active indicator */
  border-bottom: 3px solid transparent !important;
  border-radius: 0 !important;
  background: transparent !important;
  color: #6d7f9e !important;
  /* ENHANCED: more vertical padding */
  padding: 15px 20px 12px !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
  letter-spacing: .2px !important;
  font-family: 'DM Sans', sans-serif !important;
  /* ENHANCED: smooth color transition */
  transition: color .18s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: #b0c0de !important;
}
.stTabs [aria-selected="true"] {
  color: #ffffff !important;
  border-bottom-color: #5b9cf6 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Column gap — ENHANCED: more breathing room ── */
div[data-testid="column"] {
  /* ENHANCED: wider gap between chart columns */
  padding: 8px !important;
}

/* ── Selectbox — ENHANCED ── */
.stSelectbox > div > div {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border2) !important;
  background: var(--surface) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  color: var(--text) !important;
  box-shadow: var(--shadow-xs) !important;
  transition: box-shadow .18s, border-color .18s !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(26,86,219,.12) !important;
}
.stSelectbox label {
  font-size: 12px !important;
  color: var(--text2) !important;
  font-weight: 500 !important;
  /* ENHANCED: small bottom margin */
  margin-bottom: 4px !important;
}
[data-testid="stFileUploader"] { background: var(--surface); border-radius: var(--radius-md); }
.stMarkdown p { margin: 0; }

/* ── Section spacer utility — ENHANCED ── */
.section-spacer {
  height: 32px;
}

/* ── Chart container — ENHANCED: ensures charts have min-height ── */
.js-plotly-plot, .plot-container {
  min-height: 200px;
}

/* ── Smooth page-level transitions ── */
* {
  box-sizing: border-box;
}

/* ── Scrollbar styling for webkit ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #a0aec0; }

</style>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def chart_layout(h=360):
    return dict(
        height=h,
        margin=dict(l=6, r=6, t=6, b=36),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", size=11, color="#6b7280"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(200,210,225,.45)", zeroline=False,
                   showline=False, tickfont=dict(size=10, color="#9ca3af")),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,210,225,.45)", zeroline=False,
                   showline=False, tickfont=dict(size=10, color="#9ca3af")),
    )

def fb(v): return f"${v:.2f}B"
def fp(v, d=1): return f"{v:.{d}f}%"

RISK_COLOR = {"Critical":"#c81e1e","High":"#c05621","Moderate":"#1a56db","Low":"#057a55"}

# ─── Navbar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-inner">
    <div class="nav-brand">
      <div class="nav-icon">⬡</div>
      <div>
        <div class="nav-title">SemiTrack India</div>
        <div class="nav-sub">Semiconductor Import Substitution Tracker</div>
      </div>
    </div>
    <div class="nav-pills">
      <span class="nav-pill">HS 8542 + HS 3818</span>
      <span class="nav-pill">CEPII BACI HS92</span>
      <span class="nav-pill">1995–2024 · ARIMAX 2025–27</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_import, tab_year, tab_subst, tab_risk = st.tabs([
    "  Overview  ", "  Import Analysis  ", "  Year Analysis  ",
    "  Substitution Tracker  ", "  Supplier Risk  "
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<div class="outer-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-head">
      <div class="page-head-row">
        <div>
          <div class="page-eyebrow">Executive Command Center</div>
          <h1 class="page-h1">India's Semiconductor Import Dashboard</h1>
          <p class="page-sub">1995–2024 trade record with ARIMAX 2025–27 baseline. No substitution signal visible yet — imports continue setting new highs.</p>
        </div>
        <span class="data-badge">CEPII BACI HS92 V202601 · WB WDI deflators</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI strip
    st.markdown("""
    <div class="kpi-strip">
      <div class="kpi blue"><div class="kpi-label">Import Bill 2024</div><div class="kpi-val">$23.05B</div><div class="kpi-sub">Nominal USD · ~100× the 1995 level</div></div>
      <div class="kpi green"><div class="kpi-label">Real Value 2024</div><div class="kpi-val">$14.60B</div><div class="kpi-sub">Constant 2015 USD · +14.6% vs 2023</div></div>
      <div class="kpi red"><div class="kpi-label">China Share</div><div class="kpi-val">45.8%</div><div class="kpi-sub">Largest single supplier node in 2024</div></div>
      <div class="kpi amber"><div class="kpi-label">Supplier HHI</div><div class="kpi-val">0.291</div><div class="kpi-sub">Above 0.25 high-concentration threshold</div></div>
      <div class="kpi red"><div class="kpi-label">Top-3 Control</div><div class="kpi-val">86.5%</div><div class="kpi-sub">China · Taiwan · South Korea</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Hero grid
    st.markdown("""
    <div class="hero-grid">
      <div class="hero-card">
        <div class="page-eyebrow" style="margin-bottom:8px;">Historical verdict</div>
        <h2 class="hero-h">The import bill is scaling faster than any visible substitution signal.</h2>
        <p class="hero-p">The 1995–2024 trade record reveals a sharper post-2018 import regime, overwhelming HS 8542 dominance, and deeper dependence on a narrow East Asian supplier corridor. This dashboard is structured as a decision surface: macro trend → supply-chain structure → risk concentration → year-wise diagnostics.</p>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;">
          <span class="echip accent">Full 30-year history</span>
          <span class="echip accent">ARIMAX forecast</span>
          <span class="echip accent">Year drilldown</span>
        </div>
      </div>
      <div class="hero-card">
        <div class="stat-quad" style="margin-bottom:14px;">
          <div class="stat-q"><div class="sq-label">2024 import bill</div><div class="sq-val">$23.05B</div><div class="sq-copy">Nominal; still rising after 2020 disruption</div></div>
          <div class="stat-q"><div class="sq-label">Structural break</div><div class="sq-val" style="color:#c81e1e;">2018</div><div class="sq-copy">Electronics-led import regime shift</div></div>
          <div class="stat-q"><div class="sq-label">China share</div><div class="sq-val" style="color:#c81e1e;">45.8%</div><div class="sq-copy">Largest supplier, 2024</div></div>
          <div class="stat-q"><div class="sq-label">Substitution?</div><div class="sq-val" style="color:#c05621;">None</div><div class="sq-copy">Finished-chip imports still at new highs</div></div>
        </div>
        <div class="card" style="padding:16px 18px;box-shadow:none;border-color:var(--border);">
          <div class="card-title" style="font-size:14px;margin-bottom:10px;">Shock Map</div>
          <div class="tl">
            <div class="tl-row"><div class="tl-yr">2008</div><div class="tl-txt">Global financial crisis cuts electronics demand, producing a visible import dip.</div></div>
            <div class="tl-row"><div class="tl-yr">2018+</div><div class="tl-txt">Electronics boom pushes series into a new, faster-growth import regime.</div></div>
            <div class="tl-row"><div class="tl-yr">2020</div><div class="tl-txt">COVID disrupts logistics but the reset is temporary, not structural.</div></div>
            <div class="tl-row"><div class="tl-yr">2022</div><div class="tl-txt">Chip shortage and recovery demand intensify urgency from a higher base.</div></div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Key insights
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head"><div class="sec-tag">Key Insights</div><h2 class="sec-h2">Top-line takeaways from the 1995–2024 trade record</h2></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sum-grid">
      <div class="sum-item"><div class="sum-kicker">Import dependence</div><div class="sum-strong">Imports still climbing</div><div class="sum-copy">Nominal imports rise from <strong>$0.24B</strong> in 1995 to <strong>$23.05B</strong> in 2024, no flattening post-2018.</div></div>
      <div class="sum-item"><div class="sum-kicker">Concentration</div><div class="sum-strong">Supplier HHI rising</div><div class="sum-copy">Index moves from <strong>0.051</strong> to <strong>0.291</strong>, firmly above the high-concentration threshold.</div></div>
      <div class="sum-item"><div class="sum-kicker">China exposure</div><div class="sum-strong">CN + TW = 71.5%</div><div class="sum-copy">China supplies <strong>45.8%</strong> of 2024 imports; combined with Taiwan it reaches <strong>71.5%</strong>.</div></div>
      <div class="sum-item"><div class="sum-kicker">Product mix</div><div class="sum-strong">HS 8542 dominates</div><div class="sum-copy">Integrated circuits make up <strong>99.2%</strong> of 2024 tracked imports — ecosystem depth is thin.</div></div>
      <div class="sum-item"><div class="sum-kicker">Strategic risk</div><div class="sum-strong">East Asia = binding constraint</div><div class="sum-copy">China, Taiwan, South Korea control roughly <strong>86.5%</strong> of 2024 imports.</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head"><div class="sec-tag">Macro Trends</div><h2 class="sec-h2">Import scale has shifted into a steeper post-2018 regime</h2><p class="sec-p">Historical real and nominal imports alongside the ARIMAX baseline for 2025–2027.</p></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Import trajectory, 1995–2027</div><div class="card-sub">Real 2015 USD, nominal USD, and ARIMAX forecast with confidence band</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=YEARS, y=REAL, name="Real (2015 USD)",
            line=dict(color="#1a56db", width=2.2), fill="tozeroy",
            fillcolor="rgba(26,86,219,.07)", mode="lines+markers",
            marker=dict(size=2.8, color="#1a56db")))
        fig.add_trace(go.Scatter(x=YEARS, y=NOM, name="Nominal USD",
            line=dict(color="#0694a2", width=1.8), mode="lines"))
        fig.add_trace(go.Scatter(x=FC_YEARS, y=FC_HI, showlegend=False,
            line=dict(color="rgba(192,86,33,.3)", width=1), mode="lines"))
        fig.add_trace(go.Scatter(x=FC_YEARS, y=FC_LO, name="Forecast band",
            fill="tonexty", fillcolor="rgba(192,86,33,.10)",
            line=dict(color="rgba(192,86,33,.3)", width=1), mode="lines"))
        fig.add_trace(go.Scatter(x=FC_YEARS, y=FC_VALS, name="ARIMAX forecast",
            line=dict(color="#c05621", width=2, dash="dash"),
            mode="lines+markers", marker=dict(symbol="diamond", size=8, color="#c05621")))
        layout = chart_layout(380)
        fig.update_layout(**layout)
        fig.update_xaxes(tickvals=list(range(1995,2028,5)))
        fig.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout"><span class="callout-label">Insight</span>Imports trend upward across the full sample. The slope steepens after <strong>2018</strong>, consistent with India\'s electronics boom. The 2020 dip is temporary.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Post-2017 acceleration index</div><div class="card-sub">Real and nominal indexed to 2017 = 100 to isolate the structural break</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=YEARS, y=REAL_IDX, name="Real index",
            line=dict(color="#1a56db", width=2.2), fill="tozeroy",
            fillcolor="rgba(26,86,219,.08)", mode="lines+markers",
            marker=dict(size=2.8)))
        fig2.add_trace(go.Scatter(x=YEARS, y=NOM_IDX, name="Nominal index",
            line=dict(color="#0694a2", width=1.8), fill="tozeroy",
            fillcolor="rgba(6,148,162,.06)", mode="lines"))
        fig2.update_layout(**chart_layout(380))
        fig2.update_xaxes(tickvals=list(range(1995,2025,5)))
        st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout"><span class="callout-label">Insight</span>Using <strong>2017</strong> as the base makes the regime break clear. Both indices re-rate sharply after <strong>2018</strong>. The 2020 dip is temporary — 2021–22 keeps the series on a higher trajectory.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Supply chain
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head"><div class="sec-tag">Supply Chain Structure</div><h2 class="sec-h2">Supplier exposure concentrated in a narrow East Asian corridor</h2><p class="sec-p">2024 supplier breakdown and how China\'s share evolved over 30 years.</p></div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">2024 supplier share by country</div><div class="card-sub">Coloured by risk level: red = critical, amber = high, blue = moderate, green = low</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(
            x=[c["share"] for c in COUNTRIES],
            y=[c["name"] for c in COUNTRIES],
            orientation="h",
            marker_color=[RISK_COLOR[c["level"]] for c in COUNTRIES],
            marker_line_width=0, marker_cornerradius=5))
        l3 = chart_layout(330)
        fig3.update_layout(**l3)
        fig3.update_xaxes(ticksuffix="%")
        fig3.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color="#374151"))
        st.plotly_chart(fig3, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout"><span class="callout-label">Insight</span>China, Taiwan, and South Korea dominate sourcing. Risk reduction requires dual-sourcing and trusted-partner diversification — not just country-count expansion.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">China share vs rest of world, 1995–2024</div><div class="card-sub">China\'s dominance rose from sub-1% to 45.8% over three decades</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=YEARS, y=CHINA, name="China share",
            line=dict(color="#c81e1e", width=2.2), fill="tozeroy",
            fillcolor="rgba(200,30,30,.10)", mode="lines+markers", marker=dict(size=2.8)))
        fig4.add_trace(go.Scatter(x=YEARS, y=NON_CHINA, name="Other suppliers",
            line=dict(color="#1a56db", width=1.8), fill="tozeroy",
            fillcolor="rgba(26,86,219,.05)", mode="lines"))
        l4 = chart_layout(330)
        fig4.update_layout(**l4)
        fig4.update_xaxes(tickvals=list(range(1995,2025,5)))
        fig4.update_yaxes(ticksuffix="%", range=[0,100])
        st.plotly_chart(fig4, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout red"><span class="callout-label">Insight</span>China\'s share grows from below <strong>1%</strong> in 1995 to nearly <strong>46%</strong> in 2024. The 2023 spike and 2024 partial easing do not change the broader concentration story.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Risk
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head"><div class="sec-tag">Risk Analysis</div><h2 class="sec-h2">Higher China share and higher concentration now move together</h2><p class="sec-p">Bubble scatter links China share with HHI directly; policy panel translates the pattern into thresholds.</p></div>', unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">China share vs HHI — risk migration</div><div class="card-sub">Bubble size scales with nominal import value; red = post-2018 regime</div><div class="card-divider"></div>', unsafe_allow_html=True)
        pre  = [(CHINA[i], round(HHI[i]*100,1), max(5,min(16,NOM[i]*1.1)), YEARS[i], NOM[i]) for i,y in enumerate(YEARS) if y <= 2017]
        post = [(CHINA[i], round(HHI[i]*100,1), max(5,min(20,NOM[i]*.9)),  YEARS[i], NOM[i]) for i,y in enumerate(YEARS) if y >= 2018]
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=[p[0] for p in pre], y=[p[1] for p in pre],
            mode="markers", name="1995–2017",
            marker=dict(size=[p[2] for p in pre], color="rgba(26,86,219,.25)",
                       line=dict(color="#1a56db", width=1.2)),
            customdata=[[p[3],p[4]] for p in pre],
            hovertemplate="Year %{customdata[0]}<br>China: %{x:.1f}%<br>HHI×100: %{y:.1f}<br>$%{customdata[1]:.2f}B<extra></extra>"))
        fig5.add_trace(go.Scatter(x=[p[0] for p in post], y=[p[1] for p in post],
            mode="markers", name="2018–2024",
            marker=dict(size=[p[2] for p in post], color="rgba(200,30,30,.28)",
                       line=dict(color="#c81e1e", width=1.2)),
            customdata=[[p[3],p[4]] for p in post],
            hovertemplate="Year %{customdata[0]}<br>China: %{x:.1f}%<br>HHI×100: %{y:.1f}<br>$%{customdata[1]:.2f}B<extra></extra>"))
        l5 = chart_layout(330)
        fig5.update_layout(**l5)
        fig5.update_xaxes(ticksuffix="%", title=dict(text="China share (%)", font=dict(size=10)))
        fig5.update_yaxes(title=dict(text="HHI × 100", font=dict(size=10)))
        st.plotly_chart(fig5, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout amber"><span class="callout-label">Insight</span>After <strong>2018</strong> the series migrates toward the upper-right risk zone — larger China share alongside a more concentrated supplier base.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Policy implications</div><div class="card-sub">Thresholds already breached in the historical data through 2024</div><div class="card-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="meta-row">
          <div class="meta-item"><div class="meta-label">CN + TW share</div><div class="meta-val">71.5%</div></div>
          <div class="meta-item"><div class="meta-label">Top-3 share</div><div class="meta-val">86.5%</div></div>
          <div class="meta-item"><div class="meta-label">Geo-risk score</div><div class="meta-val">7.41</div></div>
        </div>
        <ul class="plist">
          <li><strong>HHI is above 0.25.</strong> This is the high-concentration range associated with limited sourcing flexibility.</li>
          <li><strong>China and Taiwan together control 71.5%.</strong> A Taiwan Strait disruption would immediately threaten the majority of India's tracked import bill.</li>
          <li><strong>HS 8542 is still overwhelming.</strong> Finished-chip dependence remains the dominant story — materials-scale localisation is not yet visible.</li>
          <li><strong>Substitution is prospective, not historical.</strong> The domestic ecosystem may be building, but through 2024 the data still show dependence rather than replacement.</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # outer-wrap

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — IMPORT ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab_import:
    st.markdown('<div class="outer-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-head">
      <div class="page-head-row">
        <div>
          <div class="page-eyebrow">Supply Chain Structure</div>
          <h1 class="page-h1">Import Basket Analysis</h1>
          <p class="page-sub">The basket is almost entirely finished-chip value. HS 8542 dominance makes the lack of historical substitution explicit.</p>
        </div>
        <span class="data-badge">CEPII BACI HS92 V202601</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Product mix full width
    st.markdown('<div class="card" style="margin-bottom:24px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Product mix — HS 8542 vs HS 3818, 1995–2024</div><div class="card-sub">Nominal import value by code with HS 8542 share overlaid</div><div class="card-divider"></div>', unsafe_allow_html=True)
    fig_pm = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pm.add_trace(go.Bar(x=YEARS, y=HS8, name="HS 8542", marker_color="rgba(26,86,219,.8)", marker_cornerradius=4), secondary_y=False)
    fig_pm.add_trace(go.Bar(x=YEARS, y=HS3, name="HS 3818", marker_color="rgba(192,86,33,.85)", marker_cornerradius=4), secondary_y=False)
    fig_pm.add_trace(go.Scatter(x=YEARS, y=HS8_SHARE, name="HS 8542 share",
        line=dict(color="#057a55", width=2), mode="lines+markers", marker=dict(size=3)), secondary_y=True)
    lpm = chart_layout(380)
    lpm["barmode"] = "stack"
    fig_pm.update_layout(**lpm)
    fig_pm.update_xaxes(tickvals=list(range(1995,2025,5)), gridcolor="rgba(200,210,225,.45)", showline=False)
    fig_pm.update_yaxes(tickprefix="$", ticksuffix="B", gridcolor="rgba(200,210,225,.45)", secondary_y=False)
    fig_pm.update_yaxes(ticksuffix="%", range=[0,100], gridcolor="rgba(0,0,0,0)", secondary_y=True,
                        tickfont=dict(color="#057a55"))
    st.plotly_chart(fig_pm, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown('<div class="callout"><span class="callout-label">Insight</span>HS 8542 accounts for <strong>99.2%</strong> of the tracked 2024 bill. The 2023 HS 3818 bump never coincides with falling finished-chip imports — so it is not a substitution signal.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Regime comparison: pre- vs post-2018</div><div class="card-sub">Key metrics before and after the structural break</div><div class="card-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <table class="reg-tbl">
          <thead><tr><th>Metric</th><th style="text-align:right;color:#9ca3af;">1995–2017</th><th style="text-align:right;color:#1a56db;">2018–2024</th></tr></thead>
          <tbody>
            <tr><td>Avg real CAGR</td><td style="text-align:right;">6.5%</td><td class="hl" style="text-align:right;">22.4%</td></tr>
            <tr><td>Peak nominal import</td><td style="text-align:right;">$2.9B</td><td class="hl" style="text-align:right;">$23.05B</td></tr>
            <tr><td>China share (avg)</td><td style="text-align:right;">12.3%</td><td class="hl" style="text-align:right;">37.9%</td></tr>
            <tr><td>Supplier HHI (avg)</td><td style="text-align:right;">0.063</td><td class="hl" style="text-align:right;">0.213</td></tr>
            <tr><td>HS 8542 share (avg)</td><td style="text-align:right;">93.4%</td><td class="hl" style="text-align:right;">98.4%</td></tr>
            <tr><td>Observed pattern</td><td style="text-align:right;">Low base</td><td class="hl" style="text-align:right;">Accelerated dependence</td></tr>
          </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head"><div class="sec-tag">Growth Dynamics</div><h2 class="sec-h2">Demand volatile even as the underlying base keeps scaling</h2><p class="sec-p">Year-on-year real growth and rolling volatility isolate crisis periods and post-2018 instability.</p></div>', unsafe_allow_html=True)

    c_ia3, c_ia4 = st.columns(2)
    with c_ia3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Year-on-year real growth</div><div class="card-sub">Growth in 2015 USD; red bars mark contraction years</div><div class="card-divider"></div>', unsafe_allow_html=True)
        yoy_years = YEARS[1:]
        yoy_vals  = YOY[1:]
        bar_cols  = ["rgba(5,122,85,.8)" if (v is not None and v >= 0) else "rgba(200,30,30,.8)" for v in yoy_vals]
        fig_yoy = go.Figure(go.Bar(x=yoy_years, y=yoy_vals, marker_color=bar_cols, marker_cornerradius=4))
        fig_yoy.update_layout(**chart_layout(330))
        fig_yoy.update_xaxes(tickvals=list(range(1996,2025,4)))
        fig_yoy.update_yaxes(ticksuffix="%", zeroline=True, zerolinecolor="#e4e8f0", zerolinewidth=1)
        st.plotly_chart(fig_yoy, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout amber"><span class="callout-label">Insight</span>Growth turns sharply negative around <strong>2008</strong>, <strong>2013–15</strong>, and <strong>2020</strong>, then rebounds hard in 2021–22. Volatility rides on top of the long-run climb — it does not cancel it.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_ia4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">3-year rolling growth volatility</div><div class="card-sub">Rolling standard deviation of real growth rate, highlighting shock windows</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_vol = go.Figure(go.Scatter(x=YEARS, y=VOLATILITY, mode="lines", fill="tozeroy",
            fillcolor="rgba(192,86,33,.12)", line=dict(color="#c05621", width=2.2)))
        fig_vol.update_layout(**chart_layout(330))
        fig_vol.update_xaxes(tickvals=list(range(1995,2025,5)))
        st.plotly_chart(fig_vol, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout"><span class="callout-label">Insight</span>Volatility spikes around the <strong>2008 crisis</strong>, <strong>2018 structural break</strong>, and <strong>2020–22</strong> COVID plus chip-shortage period. Cools by 2024 — but from a far larger import base.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — YEAR ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab_year:
    st.markdown('<div class="outer-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-head">
      <div class="page-head-row">
        <div>
          <div class="page-eyebrow">Year Drilldown</div>
          <h1 class="page-h1">Year Analysis</h1>
          <p class="page-sub">Select any historical year from 1995 to 2024 to refresh all diagnostics.</p>
        </div>
        <span class="data-badge">CEPII BACI HS92 · 30 years</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Year selector
    st.markdown('<div class="card" style="margin-bottom:20px;padding:18px 22px;">', unsafe_allow_html=True)
    ya_year = st.selectbox("Select year", options=list(range(1995,2025)), index=29, key="ya_year")
    st.markdown('</div>', unsafe_allow_html=True)

    idx      = YEARS.index(ya_year)
    prev_idx = idx-1 if idx > 0 else None
    nominal  = NOM[idx]; real_v = REAL[idx]; china_v = CHINA[idx]
    hhi_v    = HHI[idx]; hs8_v = HS8[idx]; hs3_v = HS3[idx]
    hs8share = HS8_SHARE[idx]; hs3share = HS3_SHARE[idx]; yoy_v = YOY[idx]
    prev_nom   = NOM[prev_idx]   if prev_idx is not None else None
    prev_china = CHINA[prev_idx] if prev_idx is not None else None
    prev_hhi   = HHI[prev_idx]   if prev_idx is not None else None

    regime_label = "Post-2018" if ya_year >= 2018 else "Pre-2018"
    shock_labels = {2008:"GFC reset",2020:"COVID disruption",2021:"Chip shortage",2022:"Chip shortage"}
    shock = shock_labels.get(ya_year, "Electronics boom" if ya_year >= 2018 else "Pre-break base")

    def year_narrative(yr):
        if yr == 2008: return "The 2008 drop aligns with the global financial crisis, when electronics demand and trade finance both tightened."
        if yr == 2020: return "The 2020 pullback aligns with COVID disruption across demand, logistics, and industrial production."
        if yr in [2021,2022]: return "This sits inside the global chip-shortage period, when recovery demand and supply constraints lifted import urgency."
        if yr >= 2018: return "This year is inside the post-2018 higher-growth regime that the structural-break analysis flags as a new import phase."
        return "This year still belongs to the pre-2018 lower-base regime before the sharp acceleration in electronics-linked import demand."

    def pct_chg(cur, prev): return f"+{((cur-prev)/prev*100):.1f}% vs prior year" if prev else "Series baseline"
    def pp_chg(cur, prev):  return f"+{(cur-prev):.1f}pp vs prior year"           if prev else "Series baseline"

    # Event bar
    regime_chip = f'<span class="echip accent">{regime_label}</span>'
    shock_chip  = f'<span class="echip amber">{shock}</span>'
    st.markdown(f"""
    <div class="event-bar">
      <strong>{ya_year}</strong> — {year_narrative(ya_year)}
      &nbsp;{regime_chip}{shock_chip}
      &nbsp;<span style="color:#6b7280;">Imports: <strong>{fb(nominal)}</strong> nominal · <strong>{fb(real_v)}</strong> real (2015 USD)</span>
    </div>
    """, unsafe_allow_html=True)

    # KPI strip
    yoy_txt = "Series baseline" if yoy_v is None else (f"+{yoy_v:.1f}% real growth" if yoy_v >= 0 else f"{yoy_v:.1f}% real growth")
    risk_lv = "high-concentration" if hhi_v >= 0.25 else ("moderate" if hhi_v >= 0.15 else "low-concentration")
    st.markdown(f"""
    <div class="kpi-strip">
      <div class="kpi blue"><div class="kpi-label">Nominal Imports</div><div class="kpi-val">{fb(nominal)}</div><div class="kpi-sub">{pct_chg(nominal, prev_nom)}</div></div>
      <div class="kpi green"><div class="kpi-label">Real Imports</div><div class="kpi-val">{fb(real_v)}</div><div class="kpi-sub">{yoy_txt}</div></div>
      <div class="kpi red"><div class="kpi-label">China Share</div><div class="kpi-val">{fp(china_v)}</div><div class="kpi-sub">{pp_chg(china_v, prev_china)}</div></div>
      <div class="kpi amber"><div class="kpi-label">Supplier HHI</div><div class="kpi-val">{hhi_v:.3f}</div><div class="kpi-sub">{risk_lv} zone</div></div>
      <div class="kpi slate"><div class="kpi-label">HS 8542 Share</div><div class="kpi-val">{fp(hs8share)}</div><div class="kpi-sub">HS 3818: {fp(hs3share)}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Row 1
    ya_r1c1, ya_r1c2 = st.columns(2)
    with ya_r1c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Selected year in historical context</div><div class="card-sub">Real and nominal trajectories with chosen year highlighted</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_yc = go.Figure()
        fig_yc.add_trace(go.Scatter(x=YEARS, y=REAL, name="Real imports",
            line=dict(color="#1a56db", width=2), fill="tozeroy",
            fillcolor="rgba(26,86,219,.07)", mode="lines+markers", marker=dict(size=2.5)))
        fig_yc.add_trace(go.Scatter(x=YEARS, y=NOM, name="Nominal imports",
            line=dict(color="#0694a2", width=1.6), mode="lines"))
        fig_yc.add_trace(go.Scatter(x=[ya_year], y=[REAL[idx]], name="Selected (real)",
            mode="markers", marker=dict(size=11, symbol="circle", color="#057a55", line=dict(color="white", width=2))))
        fig_yc.add_trace(go.Scatter(x=[ya_year], y=[NOM[idx]], name="Selected (nominal)",
            mode="markers", marker=dict(size=11, symbol="triangle-up", color="#c81e1e", line=dict(color="white", width=2))))
        fig_yc.update_layout(**chart_layout(360))
        fig_yc.update_xaxes(tickvals=list(range(1995,2025,5)))
        fig_yc.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig_yc, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown(f'<div class="callout"><span class="callout-label">Context</span>{ya_year} is <strong>{(nominal/max(NOM)*100):.1f}%</strong> of the 2024 series peak. {year_narrative(ya_year)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ya_r1c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Five-year neighbourhood</div><div class="card-sub">Selected year compared within its local import cycle</div><div class="card-divider"></div>', unsafe_allow_html=True)
        lo = max(0, idx-2); hi = min(len(YEARS)-1, idx+2)
        win_years = YEARS[lo:hi+1]; win_noms = NOM[lo:hi+1]
        bar_colors_w = ["#1a56db" if y==ya_year else "rgba(203,213,225,.9)" for y in win_years]
        fig_yw = go.Figure(go.Bar(x=[str(y) for y in win_years], y=win_noms,
            marker_color=bar_colors_w, marker_cornerradius=8,
            text=[f"${v:.2f}B" for v in win_noms], textposition="outside",
            textfont=dict(size=11, color="#6b7280")))
        fig_yw.update_layout(**chart_layout(260))
        fig_yw.update_xaxes(showgrid=False)
        fig_yw.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig_yw, use_container_width=True, config=dict(displayModeBar=False))
        local_pos = "local peak" if nominal == max(win_noms) else ("local trough" if nominal == min(win_noms) else "inside the local range")
        st.markdown(f'<div class="callout"><span class="callout-label">Local cycle</span>Across {win_years[0]}–{win_years[-1]}, <strong>{ya_year}</strong> is the {local_pos}. {"Visible shock year." if ya_year in [2008,2020] else "Separates short-run swing from longer trajectory."}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2
    ya_r2c1, ya_r2c2, ya_r2c3 = st.columns(3)
    with ya_r2c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Nominal vs Real</div><div class="card-sub">Current-dollar vs constant-2015-dollar values</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_yi = go.Figure(go.Bar(
            x=["Nominal","Real (2015 USD)"], y=[nominal, real_v],
            marker_color=["rgba(6,148,162,.85)","rgba(26,86,219,.85)"],
            marker_cornerradius=8,
            text=[fb(nominal), fb(real_v)], textposition="outside",
            textfont=dict(size=12)))
        fig_yi.update_layout(**chart_layout(240))
        fig_yi.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig_yi, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown(f'<div class="callout"><span class="callout-label">Imports</span>Gap between nominal and real: <strong>${nominal-real_v:.2f}B</strong>. The real burden persists after stripping inflation.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ya_r2c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Product mix</div><div class="card-sub">HS 8542 and HS 3818 composition</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_ymix = go.Figure(go.Pie(
            labels=["HS 8542","HS 3818"], values=[hs8_v, hs3_v],
            marker_colors=["rgba(26,86,219,.9)","rgba(192,86,33,.88)"],
            hole=0.64,
            texttemplate="%{label}<br>%{percent}",
            textfont=dict(size=11)))
        fig_ymix.update_layout(**chart_layout(240))
        st.plotly_chart(fig_ymix, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown(f'<div class="callout"><span class="callout-label">Product mix</span>HS 8542 = <strong>{fp(hs8share)}</strong>; HS 3818 = <strong>{fp(hs3share)}</strong>. {"2023 materials bump arrived alongside rising finished-chip imports." if ya_year==2023 else "Mix still heavily weighted toward imported finished semiconductor value."}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ya_r2c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Concentration profile</div><div class="card-sub">China share, non-China share, HHI × 100</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_yr = go.Figure(go.Bar(
            x=["China share","Non-China","HHI × 100"],
            y=[china_v, round(100-china_v,1), round(hhi_v*100,1)],
            marker_color=["rgba(200,30,30,.85)","rgba(5,122,85,.82)","rgba(192,86,33,.85)"],
            marker_cornerradius=8,
            text=[fp(china_v), fp(round(100-china_v,1)), f"{hhi_v*100:.1f}"],
            textposition="outside", textfont=dict(size=11)))
        fig_yr.update_layout(**chart_layout(240))
        fig_yr.update_yaxes(range=[0,110])
        st.plotly_chart(fig_yr, use_container_width=True, config=dict(displayModeBar=False))
        risk_level = "high-concentration" if hhi_v >= 0.25 else ("moderate-concentration" if hhi_v >= 0.15 else "dispersed")
        st.markdown(f'<div class="callout amber"><span class="callout-label">Concentration</span>HHI = <strong>{hhi_v:.3f}</strong> → {risk_level} zone. {"Part of the post-2018 concentration phase." if ya_year >= 2018 else "More dispersed than the latest years."}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — SUBSTITUTION TRACKER
# ════════════════════════════════════════════════════════════════════════════
with tab_subst:
    st.markdown('<div class="outer-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-head">
      <div class="page-head-row">
        <div>
          <div class="page-eyebrow">Substitution Monitoring</div>
          <h1 class="page-h1">Substitution Tracker</h1>
          <p class="page-sub">Historical data through 2024 do not show substitution yet. Upload 2025–2026 trade data to compare against the BAU path.</p>
        </div>
        <span class="data-badge">ARIMAX(1,1,0) BAU baseline</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:22px;">
      <div class="card-title">Monitoring framework</div>
      <div class="card-sub">Detection logic: finished-chip imports (HS 8542) must fall <em>below</em> BAU while semiconductor materials (HS 3818) rise <em>above</em> BAU simultaneously. One alone is not sufficient.</div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="card-title" style="margin-bottom:4px;">Upload actual import data</div><div class="card-sub" style="margin-bottom:12px;">Required columns: <code>year</code>, <code>hs_code</code>, <code>actual_value_real_2015usd_bn</code></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["csv"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    actual_8542 = None; actual_3818 = None
    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded)
            df_up.columns = [c.lower().strip() for c in df_up.columns]
            act_col = [c for c in df_up.columns if "actual" in c]
            if act_col:
                row8 = df_up[(df_up.get("year",pd.Series()).astype(str).str.strip()=="2025") &
                             (df_up.get("hs_code",pd.Series()).astype(str).str.strip()=="8542")]
                row3 = df_up[(df_up.get("year",pd.Series()).astype(str).str.strip()=="2025") &
                             (df_up.get("hs_code",pd.Series()).astype(str).str.strip()=="3818")]
                if len(row8)>0: actual_8542 = float(row8.iloc[0][act_col[0]])
                if len(row3)>0: actual_3818 = float(row3.iloc[0][act_col[0]])
                st.success(f"✓ Loaded {len(df_up)} rows — {uploaded.name}")
        except Exception as e:
            st.error(f"Parse error: {e}")

    bau8 = 16.79; bau3 = 0.138
    if actual_8542 is None and actual_3818 is None:
        v_title="Awaiting actual data"; v_body="Upload a CSV to compare against the BAU counterfactual. The historical record through 2024 shows no substitution."; v_color="#6b7280"; v_bg="#f7f8fc"
    elif (actual_8542 is not None and actual_8542 < bau8) and (actual_3818 is not None and actual_3818 > bau3):
        d8=bau8-actual_8542; d3=actual_3818-bau3
        v_title="Substitution confirmed — 2025 data"; v_body=f"HS 8542 fell ${d8:.2f}B below BAU while HS 3818 rose ${d3:.3f}B above BAU simultaneously — consistent with domestic packaging activity."; v_color="#057a55"; v_bg="#f0fdf9"
    elif actual_8542 is not None and actual_8542 < bau8:
        v_title="Partial signal — finished chips below BAU"; v_body="HS 8542 is below the BAU path but HS 3818 has not yet moved decisively above BAU. Early ramp-up possible but not confirmed."; v_color="#c05621"; v_bg="#fffbf0"
    else:
        v_title="No substitution signal detected"; v_body="Both codes are tracking at or above BAU. Consistent with the broader historical dependence story through 2024."; v_color="#c81e1e"; v_bg="#fdf2f2"

    st.markdown(f"""
    <div class="verdict" style="background:{v_bg};border-left:4px solid {v_color};margin-bottom:22px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:9px;height:9px;border-radius:50%;background:{v_color};flex-shrink:0;"></div>
        <div style="font-family:'DM Serif Display',serif;font-size:21px;color:{v_color};">{v_title}</div>
      </div>
      <div style="font-size:13px;line-height:1.78;color:#4b5563;">{v_body}</div>
    </div>
    """, unsafe_allow_html=True)

    act8_disp = fb(actual_8542) if actual_8542 is not None else "Pending"
    act3_disp = fb(actual_3818) if actual_3818 is not None else "Pending"
    st.markdown(f"""
    <div class="kpi-strip cols4" style="margin-bottom:24px;">
      <div class="kpi slate"><div class="kpi-label">BAU HS 8542 forecast</div><div class="kpi-val">$16.79B</div><div class="kpi-sub">Without domestic production</div></div>
      <div class="kpi green"><div class="kpi-label">Actual HS 8542 (2025)</div><div class="kpi-val">{act8_disp}</div><div class="kpi-sub">{'−$'+f'{bau8-actual_8542:.2f}B vs forecast' if actual_8542 is not None else 'Upload CSV to populate'}</div></div>
      <div class="kpi slate"><div class="kpi-label">BAU HS 3818 forecast</div><div class="kpi-val">$0.138B</div><div class="kpi-sub">Without Micron Gujarat</div></div>
      <div class="kpi blue"><div class="kpi-label">Actual HS 3818 (2025)</div><div class="kpi-val">{act3_disp}</div><div class="kpi-sub">{'Upload CSV to populate' if actual_3818 is None else ('+' if actual_3818>bau3 else '')+f'${actual_3818-bau3:.3f}B vs BAU'}</div></div>
    </div>
    """, unsafe_allow_html=True)

    recent_years = YEARS[-8:]
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">HS 8542 — Finished ICs</div><div class="card-sub">Must fall below BAU for substitution signal to register</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_s8 = go.Figure()
        fig_s8.add_trace(go.Scatter(x=recent_years, y=HS8[-8:], name="Historical",
            line=dict(color="#1a56db", width=2), fill="tozeroy",
            fillcolor="rgba(26,86,219,.07)", mode="lines+markers", marker=dict(size=3)))
        fig_s8.add_trace(go.Scatter(x=[2025], y=[bau8], name="BAU forecast",
            line=dict(color="#c05621", dash="dash", width=2),
            mode="lines+markers", marker=dict(symbol="diamond", size=8, color="#c05621")))
        if actual_8542 is not None:
            fig_s8.add_trace(go.Scatter(x=[2025], y=[actual_8542], name="Actual 2025",
                mode="markers", marker=dict(symbol="star", size=14, color="#057a55")))
        fig_s8.update_layout(**chart_layout(330))
        fig_s8.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig_s8, use_container_width=True, config=dict(displayModeBar=False))
        if actual_8542 is not None:
            st.markdown(f'<div class="callout green"><span class="callout-label">Signal</span>Finished-chip imports are <strong>${bau8-actual_8542:.2f}B</strong> below BAU. If sustained alongside HS 3818 rising, points to domestic packaging absorbing value.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="callout"><span class="callout-label">Waiting for data</span>The test looks for HS 8542 to fall below BAU — a slowdown alone is not enough; it must pair with a rise in upstream materials.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_s2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">HS 3818 — Semiconductor materials</div><div class="card-sub">Must rise above BAU if domestic activity starts absorbing imported inputs</div><div class="card-divider"></div>', unsafe_allow_html=True)
        fig_s3 = go.Figure()
        fig_s3.add_trace(go.Scatter(x=recent_years, y=HS3[-8:], name="Historical",
            line=dict(color="#0694a2", width=2), fill="tozeroy",
            fillcolor="rgba(6,148,162,.08)", mode="lines+markers", marker=dict(size=3)))
        fig_s3.add_trace(go.Scatter(x=[2025], y=[bau3], name="BAU forecast",
            line=dict(color="#c05621", dash="dash", width=2),
            mode="lines+markers", marker=dict(symbol="diamond", size=8, color="#c05621")))
        if actual_3818 is not None:
            fig_s3.add_trace(go.Scatter(x=[2025], y=[actual_3818], name="Actual 2025",
                mode="markers", marker=dict(symbol="star", size=14, color="#c81e1e")))
        fig_s3.update_layout(**chart_layout(330))
        fig_s3.update_yaxes(tickprefix="$", ticksuffix="B")
        st.plotly_chart(fig_s3, use_container_width=True, config=dict(displayModeBar=False))
        if actual_3818 is not None:
            direction = "above" if actual_3818 >= bau3 else "below"
            st.markdown(f'<div class="callout red"><span class="callout-label">Signal</span>Upstream materials are {direction} BAU by <strong>${abs(actual_3818-bau3):.3f}B</strong>. A sustained rise above BAU = consistent with new domestic semiconductor activity.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="callout"><span class="callout-label">Waiting for data</span>The test expects HS 3818 to spike above BAU if domestic packaging or assembly starts consuming more imported inputs.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — SUPPLIER RISK
# ════════════════════════════════════════════════════════════════════════════
with tab_risk:
    weighted_risk = sum(c["share"]/100 * c["risk"] for c in COUNTRIES)
    riskYears_15  = YEARS[-15:]
    riskScores_15 = [min(9.5, CHINA[YEARS.index(y)]/100*9 + HHI[YEARS.index(y)]*15) for y in riskYears_15]
    hhi_15        = [HHI[YEARS.index(y)] for y in riskYears_15]

    st.markdown('<div class="outer-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-head">
      <div class="page-head-row">
        <div>
          <div class="page-eyebrow">Supply Chain Risk</div>
          <h1 class="page-h1">Supplier Risk Assessment</h1>
          <p class="page-sub">Concentration in a narrow East Asian corridor is the binding constraint. HHI has breached the 0.25 high-concentration threshold.</p>
        </div>
        <span class="data-badge">2024 import basket · CEPII BACI</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-strip cols4" style="margin-bottom:28px;">
      <div class="kpi red"><div class="kpi-label">Composite Geo-Risk</div><div class="kpi-val">{weighted_risk:.2f}/10</div><div class="kpi-sub">Weighted by market share</div></div>
      <div class="kpi amber"><div class="kpi-label">Supplier HHI 2024</div><div class="kpi-val">0.291</div><div class="kpi-sub">Above 0.25 high-concentration threshold</div></div>
      <div class="kpi red"><div class="kpi-label">China + Taiwan</div><div class="kpi-val">71.5%</div><div class="kpi-sub">Combined critical exposure</div></div>
      <div class="kpi green"><div class="kpi-label">Low-risk suppliers</div><div class="kpi-val">5.4%</div><div class="kpi-sub">Japan + Singapore + Philippines</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Full-width corridor chart
    st.markdown('<div class="card" style="margin-bottom:24px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">China share vs HHI — full timeline, 1995–2024</div><div class="card-sub">Both metrics rise together post-2018, confirming the supplier base is larger and more concentrated</div><div class="card-divider"></div>', unsafe_allow_html=True)
    fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
    fig_corr.add_trace(go.Scatter(x=YEARS, y=CHINA, name="China share (%)",
        line=dict(color="#c81e1e", width=2.2), fill="tozeroy",
        fillcolor="rgba(200,30,30,.08)", mode="lines+markers", marker=dict(size=2.8)),
        secondary_y=False)
    hhi_x100 = [round(h*100,1) for h in HHI]
    fig_corr.add_trace(go.Scatter(x=YEARS, y=hhi_x100, name="HHI × 100",
        line=dict(color="#c05621", width=2), fill="tozeroy",
        fillcolor="rgba(192,86,33,.10)", mode="lines+markers", marker=dict(size=2.8)),
        secondary_y=True)
    lc = chart_layout(380)
    fig_corr.update_layout(**lc)
    fig_corr.update_xaxes(tickvals=list(range(1995,2025,5)), gridcolor="rgba(200,210,225,.45)")
    fig_corr.update_yaxes(ticksuffix="%", range=[0,60], gridcolor="rgba(200,210,225,.45)", secondary_y=False)
    fig_corr.update_yaxes(range=[0,35], gridcolor="rgba(0,0,0,0)", secondary_y=True,
                          tickfont=dict(color="#c05621"))
    st.plotly_chart(fig_corr, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown('<div class="callout red"><span class="callout-label">Insight</span>China share and HHI rise together after <strong>2018</strong> — the import system is not only larger but also more concentrated. The 2020 interruption is temporary; 2021–22 chip shortage keeps the corridor elevated.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Composite supply-chain risk score</div><div class="card-sub">Weighted geo-risk index for the last 15 years</div><div class="card-divider"></div>', unsafe_allow_html=True)
        bar_colors_r = ["#c81e1e" if v >= 7 else ("#c05621" if v >= 5 else "#057a55") for v in riskScores_15]
        fig_risk = go.Figure(go.Bar(x=riskYears_15, y=riskScores_15,
            marker_color=bar_colors_r, marker_cornerradius=4))
        fig_risk.update_layout(**chart_layout(310))
        fig_risk.update_yaxes(range=[0,10])
        st.plotly_chart(fig_risk, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout red"><span class="callout-label">Insight</span>Risk score trends upward as China share and concentration rise together. 2021–22 chip shortages push the system into a high-risk pattern that persists through 2024.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_r2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Supplier concentration index (HHI)</div><div class="card-sub">HHI above 0.25 = highly concentrated supplier base</div><div class="card-divider"></div>', unsafe_allow_html=True)
        bar_colors_h = ["#c81e1e" if h >= 0.25 else ("#c05621" if h >= 0.15 else "#057a55") for h in hhi_15]
        fig_hhi = go.Figure(go.Bar(x=riskYears_15, y=hhi_15,
            marker_color=bar_colors_h, marker_cornerradius=4))
        fig_hhi.update_layout(**chart_layout(310))
        st.plotly_chart(fig_hhi, use_container_width=True, config=dict(displayModeBar=False))
        st.markdown('<div class="callout amber"><span class="callout-label">Insight</span>HHI rises sharply after <strong>2018</strong> and remains elevated through 2024 even after China\'s 2023 spike cools. Diversification should be judged by value dispersion, not supplier count.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Risk table
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="margin-bottom:24px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Supplier risk assessment matrix</div><div class="card-sub">2024 snapshot — market share, geo-risk score, and weighted exposure by country</div><div class="card-divider"></div>', unsafe_allow_html=True)

    rows_html = ""
    for c in COUNTRIES:
        w = c["share"]/100 * c["risk"]
        bar = c["share"]/50*100
        col = RISK_COLOR[c["level"]]
        sh_col = "#c81e1e" if c["share"]>20 else ("#c05621" if c["share"]>10 else "#4b5563")
        lv_cls = {"Critical":"b-crit","High":"b-high","Moderate":"b-mod","Low":"b-low"}[c["level"]]
        rows_html += f"""<tr>
          <td style="font-weight:600">{c['name']}</td>
          <td><div style="display:flex;align-items:center;gap:10px;">
            <div style="width:60px;height:5px;border-radius:999px;background:#e4e8f0;overflow:hidden;">
              <div style="width:{bar:.0f}%;height:100%;border-radius:999px;background:{col};"></div>
            </div>
            <span style="color:{sh_col};font-weight:600">{c['share']:.1f}%</span></div></td>
          <td style="font-family:'JetBrains Mono',monospace">${c['val']:.2f}B</td>
          <td style="color:{col};font-weight:600;font-family:'JetBrains Mono',monospace">{c['risk']:.1f}/10</td>
          <td style="font-family:'JetBrains Mono',monospace;font-weight:600">{w:.2f}</td>
          <td><span class="badge {lv_cls}">{c['level']}</span></td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow:auto;">
    <table class="rtable">
      <thead><tr><th>Country</th><th>Market Share</th><th>Import Value</th><th>Geo-Risk</th><th>Weighted Risk</th><th>Level</th></tr></thead>
      <tbody>{rows_html}</tbody>
      <tfoot><tr><td>Total / 2024</td><td>Full basket</td><td style="font-family:'JetBrains Mono',monospace">$23.05B</td><td>—</td><td style="font-family:'JetBrains Mono',monospace">{weighted_risk:.2f}</td><td><span class="badge b-crit">Critical</span></td></tr></tfoot>
    </table>
    </div>
    <div class="callout amber" style="margin-top:16px;">
    Japan, Germany, the US, and Vietnam remain minor in the current basket while China and Taiwan dominate the bill.
    The key policy gap is not supplier count — it is <strong>value concentration in the East Asian production corridor.</strong>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
# ENHANCED: footer with top border shadow and improved spacing
st.markdown("""
<div style="background:#ffffff;border-top:1px solid #e4e8f0;box-shadow:0 -2px 12px rgba(15,31,61,.05);padding:16px 40px;display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#9ca3af;font-family:'DM Sans',sans-serif;margin-top:8px;">
  <span>SemiTrack India · CEPII BACI HS92 V202601 · World Bank WDI deflators</span>
  <span>ARIMAX(1,1,0) with 2018 break, COVID, chip shortage, and semiconductor-policy dummies</span>
</div>
""", unsafe_allow_html=True)

