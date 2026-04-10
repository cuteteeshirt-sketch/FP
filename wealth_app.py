import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Wealth Strategy", layout="wide")

# Custom CSS for the "Executive" Look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; background-color: #161b22; }
    [data-testid="stMetricValue"] { color: #00d4ff; }
    /* Make the table text slightly larger and easier to read */
    .dataframe { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Wealth Projection Strategy")

# --- GLOBAL SETTINGS ---
with st.expander("⚙️ Global Assumptions & Scenarios", expanded=True):
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
        scenario_impact = st.number_input("ROR Adjustment %", value=0.0, step=0.5) / 100

# --- ASSET CONFIGURATION ---
st.subheader("🏦 Asset Portfolio")
assets = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        st.markdown(f"**Asset {i+1}**")
        name = st.text_input("Name", value=f"Asset {i+1}", key=f"n{i}")
        bal = st.number_input("Start Balance", value=100000, step=10000, key=f"b{i}")
        # THIS IS THE FIX: Shows the formatted number right under the box
        st.caption(f"Current: ${bal:,.0f}")
        
        ror = st.number_input("Est. ROR %", value=7.0, step=0.5, key=f"r{i}") / 100
        wd = st.number_input("Annual WD", value=0, step=1000, key=f"w{i}")
        st.caption(f"WD: ${wd:,.0f}")
        
        assets.append({"name": name, "bal": bal, "ror": ror, "wd": wd})

# --- CALCULATION ENGINE ---
data = []
current_balances = [a["bal"] for a in assets]

for yr in range(years_to_project + 1):
    age = start_age + yr
    row = {"Age": age}
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
    
    real_val = total_nominal / ((1 + inflation) ** yr)
    row["Portfolio Total"] = total_nominal
    row["Inflation Adj."] = real_val
    data.append(row)

df = pd.DataFrame(data)

# --- VISUALS ---
st.divider()
final_real = df["Inflation Adj."].iloc[-1]
st.info(f"💡 At age {start_age + years_to_project}, your portfolio is worth **${final_real:,.0f}** in today's purchasing power.")

# CHART
st.subheader("Visual Growth")
chart_cols = [a["name"] for a in assets]
# We use a built-in streamlit command that handles large numbers better
st.area_chart(df.set_index("Age")[chart_cols])

# TABLE - This is the "Tidy" view with full commas
st.subheader("📋 Annual Breakdown (Full Comma Formatting)")
st.dataframe(df.set_index("Age").style.format("${:,.0f}"), use_container_width=True)
