from src.financial import calculate_cash_flows, evaluate_financials
import numpy as np


def test_financial_pipeline():
  init_capex = 30000000.0
  opt_arb = 5000000.0
  p_power = 200.0
  fcr_rev = 55000.0

  cfs = calculate_cash_flows(init_capex, opt_arb, p_power, fcr_rev)
  npv, irr = evaluate_financials(cfs, 0.07)

  assert len(cfs) == 21
  assert isinstance(npv, float)
  assert not np.isnan(irr)
