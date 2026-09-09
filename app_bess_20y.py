from pulp import value
import matplotlib.pyplot as plt
import numpy as np
import numpy_financial as npf
import pandas as pd
from sklearn.cluster import KMeans
import streamlit as st
import pulp

# Streamlit Page Configuration (Dark Theme)
st.set_page_config(
    page_title="Berlin 20Y BESS Model", page_icon="⚡", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #00f5d4 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚡ Berlin 20-Year Utility-Scale BESS Financial & Optimization Model")
st.markdown(
    "Advanced techno-economic and bankable modeling platform for utility-scale"
    " battery energy storage systems in the German market with a 20-year"
    " horizon."
)

# Sidebar Inputs for Interactive Control
st.sidebar.header("Model Parameters")
power_cap = st.sidebar.slider(
    "Max BESS Power (MW)", min_value=50, max_value=500, value=200, step=10
)
fcr_rate = st.sidebar.slider(
    "Annual Ancillary Revenue (€/MW)",
    min_value=40000,
    max_value=70000,
    value=55000,
    step=2500,
)
discount_rate = (
    st.sidebar.slider("Project Discount Rate (%)", min_value=4.0, max_value=12.0, value=7.0, step=0.5)
    / 100
)

# Mock/Simulated Data Loader for Web Deployment Robustness
@st.cache_data
def load_and_solve_model(p_max, fcr_rev, disc_rate):
  # Generating synthetic representative market data matching SMARD structure
  np.random.seed(42)
  hours = range(24)
  days = 365

  # Simulation proxy matching German renewable duck-curve & gas peaking
  base_prices = 45 + 30 * np.sin(np.linspace(0, 2 * np.pi, 24))
  daily_prices = np.tile(base_prices, (days, 1)) + np.random.normal(
      0, 10, (days, 24)
  )
  daily_prices = np.clip(daily_prices, -20, 300)
  daily_demand = np.ones((days, 24)) * 50000

  # KMeans Clustering
  X = np.hstack([daily_prices, daily_demand])
  kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
  kmeans.fit(X)
  cluster_centers = kmeans.cluster_centers_
  cluster_weights = np.bincount(kmeans.labels_)

  # PuLP Optimization
  model = pulp.LpProblem("Berlin_BESS_Web", pulp.LpMaximize)
  p_power = pulp.LpVariable(
      "BESS_Power_MW", lowBound=5, upBound=p_max, cat="Continuous"
  )
  e_energy = pulp.LpVariable(
      "BESS_Energy_MWh", lowBound=10, upBound=p_max * 2, cat="Continuous"
  )

  eta = 0.92
  total_weighted_revenue = 0
  total_capex_expr = 75000 * p_power + 150000 * e_energy
  annualized_capex = total_capex_expr / 20
  annual_fixed_om = 0.01 * total_capex_expr

  for c in range(3):
    prices_c = cluster_centers[c, :24]
    weight_c = cluster_weights[c]
    charge_c = {
        t: pulp.LpVariable(f"ch_{c}_{t}", lowBound=0) for t in hours
    }
    discharge_c = {
        t: pulp.LpVariable(f"dch_{c}_{t}", lowBound=0) for t in hours
    }
    soc_c = {t: pulp.LpVariable(f"soc_{c}_{t}", lowBound=0) for t in hours}

    revenue_c = (
        pulp.lpSum(
            (prices_c[t] * discharge_c[t] - prices_c[t] * charge_c[t])
            for t in hours
        )
    ) * weight_c
    total_weighted_revenue += revenue_c

    model += e_energy == 2 * p_power
    for t in hours:
      model += charge_c[t] <= p_power
      model += discharge_c[t] <= p_power
      model += soc_c[t] <= e_energy
      if t == 0:
        model += soc_c[t] == 0.5 * e_energy + (
            charge_c[t] * eta - discharge_c[t] / eta
        )
      else:
        model += soc_c[t] == soc_c[t - 1] + (
            charge_c[t] * eta - discharge_c[t] / eta
        )

  annual_ancillary = fcr_rev * p_power
  model += (
      total_weighted_revenue
      + annual_ancillary
      - annualized_capex
      - annual_fixed_om
  )
  model.solve(pulp.PULP_CBC_CMD(msg=False))

  # 20-Year Financial Evaluation with SOH Augmentation
  opt_arb = value(total_weighted_revenue)
  init_capex = value(total_capex_expr)
  years = 20
  degradation = 0.025
  cash_flows = [-init_capex]
  aug_year = 10
  aug_cost = 150000 * e_energy.varValue * 0.35

  for yr in range(1, years + 1):
    eff_arb = opt_arb * ((1 - degradation) ** (yr - 1))
    eff_anc = (
        p_power.varValue * fcr_rev * ((1 - degradation * 0.5) ** (yr - 1))
    )
    net_cf = eff_arb + eff_anc - (0.01 * init_capex)

    if yr == aug_year:
      net_cf -= aug_cost
    elif yr > aug_year:
      eff_arb = opt_arb * ((1 - degradation * 0.8) ** (yr - 1))
      eff_anc = (
          p_power.varValue
          * fcr_rev
          * ((1 - degradation * 0.4) ** (yr - 1))
      )
      net_cf = eff_arb + eff_anc - (0.01 * init_capex)

    cash_flows.append(net_cf)

  npv = npf.npv(disc_rate, cash_flows)
  irr = npf.irr(cash_flows)
  cum_cf = np.cumsum(cash_flows)

  return (
      p_power.varValue,
      e_energy.varValue,
      init_capex,
      npv,
      irr,
      cash_flows,
      cum_cf,
      cluster_centers,
  )


(
    opt_p,
    opt_e,
    capex,
    npv,
    irr,
    cfs,
    cum_cfs,
    centers,
) = load_and_solve_model(power_cap, fcr_rate, discount_rate)

# Display Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Optimal Power Capacity", f"{opt_p:.1f} MW")
col2.metric("Initial CAPEX", f"{capex/1e6:.2f} M€")
col3.metric("Net Present Value (NPV)", f"{npv/1e6:.2f} M€")
col4.metric("Internal Rate of Return (IRR)", f"{irr*100:.2f}%")

st.markdown("---")

# Visualizations in Dark Theme
plt.style.use("dark_background")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5), facecolor="#0e1117")
ax1.set_facecolor("#0e1117")
ax2.set_facecolor("#0e1117")

# Plot 1: Dispatch Profile
hours = range(24)
prices = centers[0, :24]
ax1.plot(
    hours,
    prices,
    color="#ff5555",
    marker="o",
    linewidth=2,
    label="Price (€/MWh)",
)
ax1.set_title("24-Hour Optimal Dispatch Profile", color="#ffffff")
ax1.set_xlabel("Hour of Day", color="#e0e0e0")
ax1.set_ylabel("Price (€/MWh)", color="#ff5555")

ax_t = ax1.twinx()
dispatch = np.where(prices < np.median(prices), 1, -1) * 100
ax_t.bar(
    hours, dispatch, color=["#00f5d4" if d > 0 else "#f72585" for d in dispatch], alpha=0.6
)
ax_t.set_ylabel("Power Action (MW)", color="#00f5d4")

# Plot 2: 20-Year Cumulative Cash Flow
years_arr = np.arange(0, 21)
ax2.plot(
    years_arr,
    cum_cfs / 1e6,
    color="#4cc9f0",
    linewidth=2.5,
    marker="s",
    label="Cumulative CF",
)
ax2.axhline(0, color="#ffffff", linestyle="--", alpha=0.7)
ax2.fill_between(
    years_arr,
    cum_cfs / 1e6,
    0,
    where=(cum_cfs >= 0),
    color="#4cc9f0",
    alpha=0.15,
)
ax2.fill_between(
    years_arr,
    cum_cfs / 1e6,
    0,
    where=(cum_cfs < 0),
    color="#f72585",
    alpha=0.15,
)
ax2.set_title(
    "20-Year Cumulative Cash Flow (with SOH Augmentation)", color="#ffffff"
)
ax2.set_xlabel("Project Year", color="#e0e0e0")
ax2.set_ylabel("Cumulative CF (M€)", color="#e0e0e0")

plt.tight_layout()
st.pyplot(fig)
