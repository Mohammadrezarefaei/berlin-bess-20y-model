# Berlin 20-Year Utility-Scale BESS Financial & Optimization Model

[![BESS Model CI](https://github.com/Mohammadrezarefaei/berlin-bess-20y-model/actions/workflows/ci.yml/badge.svg)](https://github.com/Mohammadrezarefaei/berlin-bess-20y-model/actions/workflows/ci.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://berlin-bess-20y-model-7kwugb4hngseemfvzxsf6s.streamlit.app/)

An advanced techno-economic and bankable modeling platform for utility-scale Battery Energy Storage Systems (BESS) in Berlin, Germany. The framework incorporates EPEX Spot price proxies driven by renewable and gas generation, KMeans clustering for representative days, PuLP-based linear optimization for revenue stacking (Day-Ahead Arbitrage + FCR/aFRR ancillary services), 20-year degradation tracking, mid-life SOH augmentation, and dynamic animated visualizations.

## Live Application
Access the live interactive web dashboard: [Berlin 20Y BESS Model](https://berlin-bess-20y-model-7kwugb4hngseemfvzxsf6s.streamlit.app/)

## Visualizations & Optimal Dispatch
The model optimizes 24-hour revenue streams by leveraging renewable duck-curves and price spreads in the German market.

![BESS Dispatch Animation](bess_dispatch_animated.gif)

## Key Features
- **Revenue Stacking**: Combines energy arbitrage and high-tier ancillary capacity markets (FCR/aFRR).
- **20-Year Horizon Analysis**: Evaluates long-term cash flows, Net Present Value (NPV), Internal Rate of Return (IRR), and break-even points.
- **Battery Health (SOH) Management**: Includes mid-life cell augmentation modeling at Year 10 to recover degraded capacity.
- **Automated CI/CD**: Integrated with GitHub Actions for continuous testing and validation via Pytest.
- **Bankable Reports**: Automatically exports financial metrics and 20-year cash flow waterfalls to Excel (`Berlin_BESS_Bankable_Model.xlsx`).
## Repository Structure
```text
berlin-bess-20y-model/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── __init__.py
│   ├── optimizer.py
│   └── financial.py
├── tests/
│   ├── __init__.py
│   ├── test_financial.py
│   └── test_optimizer.py
├── data/
│   └── smard_germany_data.csv
├── app.py
├── requirements.txt
└── README.md
