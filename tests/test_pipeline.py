from src.financial import calculate_cash_flows, evaluate_financials
import numpy as np


def test_calculate_cash_flows_length():
  cfs = calculate_cash_flows(
      init_capex=30000000.0,
      opt_arb=5000000.0,
      p_power=200.0,
      fcr_rev=55000.0,
      years=20,
  )
  assert len(cfs) == 21  # Year 0 (negative capex) + 20 operating years


def test_evaluate_financials_metrics():
  cfs = [-30000000.0] + [6000000.0] * 20
  npv, irr = evaluate_financials(cfs, discount_rate=0.07)
  assert isinstance(npv, float)
  assert not np.isnan(irr)
  assert irr > 0.07
