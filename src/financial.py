import numpy as np
import numpy_financial as npf


def calculate_cash_flows(
    init_capex, opt_arb, p_power, fcr_rev, degradation=0.025, years=20
):
  cash_flows = [-init_capex]
  aug_year = 10
  aug_cost = 150000 * (p_power * 2) * 0.35

  for yr in range(1, years + 1):
    eff_arb = opt_arb * ((1 - degradation) ** (yr - 1))
    eff_anc = p_power * fcr_rev * ((1 - degradation * 0.5) ** (yr - 1))
    net_cf = eff_arb + eff_anc - (0.01 * init_capex)

    if yr == aug_year:
      net_cf -= aug_cost
    elif yr > aug_year:
      eff_arb = opt_arb * ((1 - degradation * 0.8) ** (yr - 1))
      eff_anc = p_power * fcr_rev * ((1 - degradation * 0.4) ** (yr - 1))
      net_cf = eff_arb + eff_anc - (0.01 * init_capex)

    cash_flows.append(net_cf)
  return cash_flows


def evaluate_financials(cash_flows, discount_rate=0.07):
  npv = npf.npv(discount_rate, cash_flows)
  irr = npf.irr(cash_flows)
  return npv, irr
