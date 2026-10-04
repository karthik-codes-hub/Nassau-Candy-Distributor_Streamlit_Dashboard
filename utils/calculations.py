"""
Calculations module for Nassau Candy Distributor Profitability Dashboard.
Implements DAX measures, business logic, margin risk rules, and cumulative filters.
"""

import pandas as pd
import numpy as np

# Risk classification thresholds matching Power BI DAX
RISK_THRESHOLDS = {
    "high_risk_max": 0.20,     # < 20% Gross Margin is High Risk
    "medium_risk_max": 0.50,   # 20% - 50% Gross Margin is Medium Risk
    # >= 50% Gross Margin is Low Risk
}


def apply_filters(
    df: pd.DataFrame,
    selected_months=None,
    selected_years=None,
    selected_regions=None,
    selected_products=None,
    selected_divisions=None,
) -> pd.DataFrame:
    """
    Applies cumulative filters across Month, Year, Region, Product Name, and Division.
    Treats None, empty iterable, or containing 'All' as unconstrained.
    """
    filtered = df.copy()

    # Month filter
    if selected_months:
        if isinstance(selected_months, str):
            selected_months = [selected_months]
        active_months = [m for m in selected_months if m != "All"]
        if active_months:
            filtered = filtered[filtered["Order Month Name"].isin(active_months)]

    # Year filter
    if selected_years:
        if not isinstance(selected_years, (list, tuple, set)):
            selected_years = [selected_years]
        active_years = [y for y in selected_years if y != "All"]
        if active_years:
            # Cast to int for comparison
            active_years_int = [int(y) for y in active_years]
            filtered = filtered[filtered["Order Year"].isin(active_years_int)]

    # Region filter
    if selected_regions:
        if isinstance(selected_regions, str):
            selected_regions = [selected_regions]
        active_regions = [r for r in selected_regions if r != "All"]
        if active_regions:
            filtered = filtered[filtered["Region"].isin(active_regions)]

    # Product Name filter
    if selected_products:
        if isinstance(selected_products, str):
            selected_products = [selected_products]
        active_products = [p for p in selected_products if p != "All"]
        if active_products:
            filtered = filtered[filtered["Product Name"].isin(active_products)]

    # Division filter
    if selected_divisions:
        if isinstance(selected_divisions, str):
            selected_divisions = [selected_divisions]
        active_divisions = [d for d in selected_divisions if d != "All"]
        if active_divisions:
            filtered = filtered[filtered["Division"].isin(active_divisions)]

    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates primary KPI metrics matching Power BI DAX measures:
    - Total Sales = SUM(Sales)
    - Total Units = SUM(Units)
    - Total Cost = SUM(Cost)
    - Total Gross Profit = SUM(Gross Profit)
    - Gross Margin % = DIVIDE(Total Gross Profit, Total Sales, 0) * 100
    - Profit per Unit = DIVIDE(Total Gross Profit, Total Units, 0)
    """
    if len(df) == 0:
        return {
            "total_sales": 0.0,
            "total_units": 0,
            "total_cost": 0.0,
            "total_gross_profit": 0.0,
            "gross_margin_pct": 0.0,
            "profit_per_unit": 0.0,
            "margin_risk": "N/A",
            "is_empty": True
        }

    total_sales = float(df["Sales"].sum())
    total_units = int(df["Units"].sum())
    total_cost = float(df["Cost"].sum())
    total_gross_profit = float(df["Gross Profit"].sum())

    gross_margin_pct = (total_gross_profit / total_sales * 100.0) if total_sales != 0 else 0.0
    profit_per_unit = (total_gross_profit / total_units) if total_units != 0 else 0.0

    margin_ratio = gross_margin_pct / 100.0
    if margin_ratio < RISK_THRESHOLDS["high_risk_max"]:
        margin_risk = "High Risk"
    elif margin_ratio < RISK_THRESHOLDS["medium_risk_max"]:
        margin_risk = "Medium Risk"
    else:
        margin_risk = "Low Risk"

    return {
        "total_sales": total_sales,
        "total_units": total_units,
        "total_cost": total_cost,
        "total_gross_profit": total_gross_profit,
        "gross_margin_pct": gross_margin_pct,
        "profit_per_unit": profit_per_unit,
        "margin_risk": margin_risk,
        "is_empty": False
    }


def get_product_margins(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates metrics by Product Name for:
    - Horizontal Bar Chart ('Which product deliver the highest gross margin?')
    - Margin Risk Pivot Table ('Which products represent margin risk?')

    Sorted numerically descending by Gross Margin % (Phase 11 requirement).
    """
    if len(df) == 0:
        return pd.DataFrame(columns=[
            "Product Name", "Total Sales", "Total Cost", "Total Gross Profit",
            "Gross Margin %", "Total Units", "Margin Risk", "Risk Status"
        ])

    agg = df.groupby("Product Name").agg(
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Division=("Division", "first")
    ).reset_index()

    agg["Margin_Ratio"] = np.where(
        agg["Total_Sales"] != 0,
        agg["Total_Gross_Profit"] / agg["Total_Sales"],
        0.0
    )
    agg["Gross_Margin_%"] = agg["Margin_Ratio"] * 100.0

    # Risk logic
    conditions = [
        agg["Margin_Ratio"] < RISK_THRESHOLDS["high_risk_max"],
        (agg["Margin_Ratio"] >= RISK_THRESHOLDS["high_risk_max"]) & (agg["Margin_Ratio"] < RISK_THRESHOLDS["medium_risk_max"]),
        agg["Margin_Ratio"] >= RISK_THRESHOLDS["medium_risk_max"]
    ]
    risk_labels = ["High Risk", "Medium Risk", "Low Risk"]
    risk_icons = ["🔴 High Risk", "🟡 Medium Risk", "🟢 Low Risk"]
    agg["Margin Risk"] = np.select(conditions, risk_labels, default="Low Risk")
    agg["Risk Status"] = np.select(conditions, risk_icons, default="🟢 Low Risk")

    # Strictly sort numerically descending by Gross Margin %
    agg = agg.sort_values(by="Gross_Margin_%", ascending=False).reset_index(drop=True)
    return agg


def get_division_profitability(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates metrics by Division for Clustered Column Chart:
    - 'How does profitability vary across product divisions?'
    - Value: Total Gross Profit
    - Tooltips: Total Sales, Total Cost, Gross Margin %

    Sorted numerically descending by Total Gross Profit.
    """
    if len(df) == 0:
        return pd.DataFrame(columns=[
            "Division", "Total_Gross_Profit", "Total_Sales", "Total_Cost", "Gross_Margin_%", "Total_Units"
        ])

    div_df = df.groupby("Division").agg(
        Total_Gross_Profit=("Gross Profit", "sum"),
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Units=("Units", "sum")
    ).reset_index()

    div_df["Gross_Margin_%"] = np.where(
        div_df["Total_Sales"] != 0,
        (div_df["Total_Gross_Profit"] / div_df["Total_Sales"]) * 100.0,
        0.0
    )

    # Strictly sort numerically descending by Gross Profit
    div_df = div_df.sort_values(by="Total_Gross_Profit", ascending=False).reset_index(drop=True)
    return div_df


def get_scatter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates data by Product Name and Division for Scatter Chart:
    - 'Are high-sales products actually profitable?'
    - X-Axis: Total Sales
    - Y-Axis: Total Gross Profit
    - Marker Size: Total Units
    - Color/Series: Division
    """
    if len(df) == 0:
        return pd.DataFrame(columns=[
            "Product Name", "Division", "Sales", "Gross Profit", "Units", "Gross_Margin_%"
        ])

    scat_df = df.groupby(["Product Name", "Division"]).agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    ).reset_index()

    scat_df["Gross_Margin_%"] = np.where(
        scat_df["Sales"] != 0,
        (scat_df["Gross_Profit"] / scat_df["Sales"]) * 100.0,
        0.0
    )

    return scat_df


def get_product_details(df: pd.DataFrame, product_name: str) -> dict:
    """
    Computes detailed product metrics within the CURRENT filtered context (Phase 15).
    """
    prod_df = df[df["Product Name"] == product_name]
    if len(prod_df) == 0:
        return None

    sales = float(prod_df["Sales"].sum())
    cost = float(prod_df["Cost"].sum())
    profit = float(prod_df["Gross Profit"].sum())
    units = int(prod_df["Units"].sum())
    margin_pct = (profit / sales * 100.0) if sales != 0 else 0.0
    profit_per_unit = (profit / units) if units != 0 else 0.0
    transactions = int(len(prod_df))
    division = prod_df["Division"].iloc[0]
    regions = sorted(prod_df["Region"].unique().tolist())

    margin_ratio = margin_pct / 100.0
    if margin_ratio < RISK_THRESHOLDS["high_risk_max"]:
        risk_status = "High Risk"
        risk_color = "#E53935"
        risk_badge = "🔴 High Risk"
    elif margin_ratio < RISK_THRESHOLDS["medium_risk_max"]:
        risk_status = "Medium Risk"
        risk_color = "#FBC02D"
        risk_badge = "🟡 Medium Risk"
    else:
        risk_status = "Low Risk"
        risk_color = "#43A047"
        risk_badge = "🟢 Low Risk"

    return {
        "product_name": product_name,
        "division": division,
        "regions": regions,
        "sales": sales,
        "cost": cost,
        "gross_profit": profit,
        "margin_pct": margin_pct,
        "units": units,
        "transactions": transactions,
        "profit_per_unit": profit_per_unit,
        "risk_status": risk_status,
        "risk_color": risk_color,
        "risk_badge": risk_badge
    }
