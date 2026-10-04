# Nassau Candy Distributor — Profitability Analysis Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vp99qlucxbvhnofwqsqunn.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/karthik-codes-hub/Nassau-Candy-Distributor_Streamlit_Dashboard)

> 🚀 **Live Dashboard:** [https://vp99qlucxbvhnofwqsqunn.streamlit.app/](https://vp99qlucxbvhnofwqsqunn.streamlit.app/)

A production-quality interactive Streamlit business intelligence dashboard recreating the original Power BI report for **Nassau Candy Distributor**.

![Dashboard Preview](assets/logo.png)

---

## 🔗 Live Application

The dashboard is deployed and publicly accessible on Streamlit Community Cloud:
- **Direct Web Link:** [https://vp99qlucxbvhnofwqsqunn.streamlit.app/](https://vp99qlucxbvhnofwqsqunn.streamlit.app/)

---

## Overview

This dashboard translates an executive Power BI dashboard into a responsive, high-performance Streamlit application backed by the cleaned dataset. It preserves the exact visual identity, layout hierarchy, color palette, DAX calculations, and interactive behavior.

---

## Key Features

- **Pixel-Accurate Visual Hierarchy**: Matches the original Power BI report structure with top KPI cards, left month slicer, top horizontal slicers, and a 2x2 visualization grid.
- **Color Preservation**: Exact Power BI hex color palette preserved (`#F97316`, `#F5C4AF`, `#EB895F`, `#118DFF`, `#E044A7`, `#E53935`, `#FBC02D`, `#43A047`).
- **Dark and Light Themes**: Seamless toggle between Power BI Slate Dark (`#1F2937`) and Modern Clean Light (`#F3F4F6`), while keeping all chart visualization series colors constant.
- **Cumulative Multi-Dimension Filtering**:
  - Month (Calendar ordered vertical slicer with All + Jan–Dec)
  - Order Year (2024, 2025)
  - Region (strictly validated actual dataset values: `Atlantic`, `Gulf`, `Interior`, `Pacific`)
  - Product Name (15 candy products)
  - Division (`Chocolate`, `Other`, `Sugar`)
- **Executive KPI Cards**:
  - Total Sales ($142K / $141,783.63)
  - Total Units Sold (39K / 38,654)
  - Gross Margin % (65.91%)
  - Total Gross Profit ($93.4K / $93,442.80)
  - Total Cost ($48.3K / $48,340.83)
  - Custom 8px orange accent bar and original Power BI metric icons.
- **Numerical Gross Profit & Margin Sorting**: Visualizations sort by numerical value descending, never alphabetically.
- **Interactive Visualizations (Plotly)**:
  1. *Product Gross Margin Bar Chart*: Horizontal bar chart sorted by margin % with coral gradient.
  2. *Sales vs. Gross Profit Scatter Plot*: Profitability correlation chart with bubble sizes by Units and color by Division.
  3. *Division Profitability Column Chart*: Gross profit distribution across product divisions.
  4. *Margin Risk Matrix*: Detailed product breakdown with conditional status indicators (🟢 Low Risk, 🟡 Medium Risk, 🔴 High Risk) and a summary totals row.
- **Interactive Product Modal & Drilldown**:
  - Modal dialog and expandable panel displaying product-specific sales, cost, profit, margin %, units, transactions, and profit per unit.
  - Calculated strictly within the current active filter context.
- **Export Filtered Data**:
  - One-click CSV export generating `Nassau_Candy_Filtered_Data.csv` containing only records matching active filters.
- **Dynamic Business Insights Engine**:
  - Narrative intelligence automatically calculated from the active dataset (e.g. margin risk alerts, division leadership, regional strength, top revenue generators).
- **Graceful Empty State Handling**: Safe fallback warning banner and N/A cards when filters match 0 rows.

---

## Project Structure

```text
streamlit/
│
├── app.py                     # Main Streamlit dashboard application
├── charts.py                  # Plotly chart generators matching Power BI design
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation with live demo links
├── style.css                  # Custom styling and theme variables
│
├── data/
│   ├── Nassau_Candy_Distributor.csv
│   └── Nassau_Candy_Distributor_Properly_Cleaned(2)(2)(1).csv
│
├── assets/
│   ├── style.css
│   ├── logo.png
│   ├── icon_sales.png
│   ├── icon_units.png
│   ├── icon_margin.png
│   ├── icon_profit.png
│   └── icon_cost.png
│
└── utils/
    ├── __init__.py
    ├── data_loader.py         # Cached dataset loading and type validation
    ├── calculations.py        # DAX logic, risk thresholds, and filters
    └── insights.py            # Dynamic narrative insight generation engine
```

---

## Installation & Setup

1. **Clone or navigate to the directory**:
   ```bash
   git clone https://github.com/karthik-codes-hub/Nassau-Candy-Distributor_Streamlit_Dashboard.git
   cd Nassau-Candy-Distributor_Streamlit_Dashboard
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard locally**:
   ```bash
   streamlit run app.py
   ```

4. The dashboard will automatically launch in your default web browser at `http://localhost:8501`.

---

## Business Logic & DAX Calculations

- **Total Sales**: `SUM(Sales)`
- **Total Cost**: `SUM(Cost)`
- **Total Gross Profit**: `SUM(Gross Profit)`
- **Gross Margin %**: `DIVIDE(Total Gross Profit, Total Sales, 0) * 100`
- **Total Units**: `SUM(Units)`
- **Profit per Unit**: `DIVIDE(Total Gross Profit, Total Units, 0)`
- **Margin Risk Classification**:
  - **High Risk (🔴)**: Gross Margin < 20%
  - **Medium Risk (🟡)**: 20% ≤ Gross Margin < 50%
  - **Low Risk (🟢)**: Gross Margin ≥ 50%