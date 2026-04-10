import streamlit as st
import pandas as pd

# 1. Page Config & Professional Theme
st.set_page_config(page_title="Wealth Strategy", layout="wide")

# Custom CSS for a "Nicest" look: Deep Blue/Slate theme
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #0e1117; color: #ffffff; }
    /* Card-like styling for input areas */
    div[data-testid="stExpander"] { border: 1px solid #30363d; border-radius: 10px; background-color: #161b22; }
    /* Metric styling */
    [data-testid="stMetricValue"] { color: #00d4ff; font-weight: bold; }
    /* Table styling */
    .dataframe { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Wealth Projection Strategy")
st.caption("Multi-asset growth and inflation-adjusted valuation")

# --- GLOBAL SETTINGS ---
with st.expander("⚙️ Global Assumptions & Scenario", expanded=True):
    set1, set2, set3 = st.columns(3)
    with set1:
        start_age = st.number_input("Current Age", value=50)
        years_to_project = st.slider("Timeline (Years)", 1, 50, 30)
    with set2:
        inflation = st.number_input("Inflation Rate %", value=2.5, step=0.1) / 100
        tax = st.number_input("Effective Tax %", value=15.0, step=0.5) / 100
    with set3:
        asset_names_list = [st.session_state.get(f"n{i}", f"Asset {i+1}") for i in range(5)]
        target_options = ["Aggregate Portfolio"] + asset_names_list
        scenario_target = st.selectbox("Scenario Target", target_options)
        scenario_impact = st.number_input("ROR Adjustment % (e.g. -2.0)", value=0.0, step=0.5) / 100

# --- ASSET CONFIGURATION ---
st.subheader("🏦 Asset Portfolio")
assets = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        st.markdown(f"**Asset {i+1}**")
        name = st.text_input("Name", value=f"Asset {i+1}", key=f"n{i}")
        # 'Step' adds arrows and makes it easy to jump by $10k
        bal = st.number_input("Start Balance", value=100000, step=10000, key=f"b{i}", format="%d")
        ror = st.number_input("Est. ROR %", value=7.0, step=0.5, key=f"r{i}") / 100
        wd = st.number_input("Annual WD", value=0, step=1000, key=f"w{i}", format="%d")
        assets.append({"name": name, "bal": bal, "ror": ror, "wd": wd})

# --- CALCULATION ENGINE ---
data = []
current_balances = [a["bal"] for a in assets]

for yr in range(years_to_project + 1):
    age = start_age + yr
    row = {"Age": age, "Year": 2026 + yr}
    total_nominal = 0
    
    for i, asset in enumerate(assets):
        active_ror = asset["ror"]
        if scenario_target == asset["name"] or scenario_target == "Aggregate Portfolio":
            active_ror += scenario_impact
            
        if yr > 0:
            current_balances[i] = (current_balances[i] * (1 + active_ror)) - asset["wd"]
            current_balances[i] = max(0, current_balances[i])
            
        row[asset["name"]] = current_balances[i]
        total_nominal += current_balances[i]
    
    # Simple net value and inflation adjustment
    real_val = total_nominal / ((1 + inflation) ** yr)
    
    row["Portfolio Total"] = total_nominal
    row["Inflation Adj."] = real_val
    data.append(row)

df = pd.DataFrame(data)

# --- VISUALS ---
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Portfolio Composition Over Time")
    # Clean area chart
    chart_cols = [a["name"] for a in assets]
    st.area_chart(df.set_index("Age")[chart_cols])

with c2:
    st.subheader("Financial Milestones")
    final_nominal = df["Portfolio Total"].iloc[-1]
    final_real = df["Inflation Adj."].iloc[-1]
    
    # Metrics with comma separators (the : ,.0f part)
    st.metric("Future Value (Nominal)", f"${final_nominal:,.0f}")
    st.metric("Future Value (Real Today $)", f"${final_real:,.0f}")
    st.info(f"At age {start_age + years_to_project}, your portfolio is worth ${final_real:,.0f} in today's purchasing power.")

# --- FINAL TABLE ---
st.subheader("📈 Detailed Annual Breakdown")
# This formats every number in the table with commas and removes decimals
st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)
