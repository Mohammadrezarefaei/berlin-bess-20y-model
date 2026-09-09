import numpy as np
import pulp
from sklearn.cluster import KMeans


def optimize_bess(cluster_centers, cluster_weights, p_max=200, fcr_rev=55000):
  model = pulp.LpProblem("Berlin_BESS_Optimization", pulp.LpMaximize)
  p_power = pulp.LpVariable(
      "BESS_Power_MW", lowBound=5, upBound=p_max, cat="Continuous"
  )
  e_energy = pulp.LpVariable(
      "BESS_Energy_MWh", lowBound=10, upBound=p_max * 2, cat="Continuous"
  )

  hours = range(24)
  eta = 0.92
  total_weighted_revenue = 0
  total_capex_expr = 75000 * p_power + 150000 * e_energy
  annualized_capex = total_capex_expr / 20
  annual_fixed_om = 0.01 * total_capex_expr

  for c in range(len(cluster_weights)):
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

  return (
      p_power.varValue,
      e_energy.varValue,
      pulp.value(total_weighted_revenue),
      pulp.value(total_capex_expr),
  )
