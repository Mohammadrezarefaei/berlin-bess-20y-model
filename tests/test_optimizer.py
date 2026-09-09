from src.optimizer import optimize_bess
import numpy as np


def test_optimize_bess_convergence():
  np.random.seed(42)
  cluster_centers = np.random.uniform(20, 100, size=(3, 24))
  cluster_weights = np.array([100, 150, 115])

  power, energy, revenue, capex = optimize_bess(
      cluster_centers, cluster_weights, p_max=100, fcr_rev=55000
  )

  assert power is not None
  assert energy is not None
  assert power > 0
  assert energy == 2 * power
  assert capex > 0
