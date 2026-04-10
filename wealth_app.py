import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Wealth Projections", layout="wide")

# Custom CSS to make the app look "tight"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_index=True)

st.title("💼 Multi-Asset Wealth Model")

# --- SETTINGS GRID ---
with st.expander("🛠️ Global Model Settings & Scenarios", expanded=True):
    set1, set2, set3 = st.columns(3)
    with set1:
        start_age = st.number_input("Current Age", value=50)
        years_to_project = st.slider("Project for (Years)", 1, 50, 30)
    with set2:
        inflation = st.number_input("Inflation %", value=2.5) / 100
        tax = st.number_input("Effective Tax %", value=15.0) / 100
    with set3:
        target_options = ["Aggregate Portfolio", "Asset 1", "Asset 2", "Asset 3", "Asset 4", "Asset 5"]
        scenario_target = st.selectbox("Scenario Target", target_options)
        scenario_impact = st.number_input("ROR Adjustment %", value=0.0) / 100

# --- ASSET CONFIGURATION (Tighter Grid) ---
st.subheader("1. Asset Inputs")
assets = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        st.markdown(f"**Asset {i+1}**")
        name = st.text_input("Name", value=f"Asset {i+1}", key=f"n{i}")
        bal = st.number_input("Balance", value=100000, step=10000, key=f"b{i}")
        ror = st.number_input("ROR %", value=7.0, step=0.5, key=f"r{i}") / 100
        wd = st.number_input("Annual WD", value=0, step=1000, key=f"w{i}")
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
        # Scenario Logic
        if scenario_target == asset["name"] or scenario_target == "Aggregate Portfolio":
            active_ror += scenario_impact
            
        if yr > 0:
            current_balances[i] = (current_balances[i] * (1 + active_ror)) - asset["wd"]
            current_balances[i] = max(0, current_balances[i])
            
        row[asset["name"]] = current_balances[i]
        total_nominal += current_balances[i]
    
    # Simple Tax & Inflation logic
    net_nominal = total_nominal * (1 - (tax * 0.2)) # Simplified tax on growth
    real_val = net_nominal / ((1 + inflation) ** yr)
    
    row["Portfolio Total"] = net_nominal
    row["Inflation Adj."] = real_val
    data.append(row)

df = pd.DataFrame(data)

# --- VISUALS ---
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Growth Projection")
    # Tighter chart with cleaner labels
    chart_data = df.set_index("Age")[[a["name"] for a in assets]]
    st.area_chart(chart_data)

with c2:
    st.subheader("Key Milestones")
    final_nominal = df["Portfolio Total"].iloc[-1]
    final_real = df["Inflation Adj."].iloc[-1]
    
    st.metric("Nominal at End", f"${final_nominal:,.0f}")
    st.metric("Real Value (Today's $)", f"${final_real:,.0f}")

st.subheader("Detailed Breakdown")
# Formats the table with commas and zero decimals
st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)
