"""
Dynamic Insights Engine for Nassau Candy Distributor Profitability Dashboard.
Intelligently generates contextual business intelligence tailored to active filters.
Uses clean HTML formatting to ensure crisp display across all browsers and themes.
"""

import pandas as pd
from utils.calculations import RISK_THRESHOLDS

CORPORATE_BENCHMARK_MARGIN = 65.91


def _add_insight(insights_list: list, category: str, icon: str, text: str):
    """Appends an insight dict with both text and html_text keys for compatibility."""
    insights_list.append({
        "category": category,
        "icon": icon,
        "text": text,
        "html_text": text
    })


def generate_insights(df: pd.DataFrame, active_filters: dict = None) -> list:
    """
    Analyzes the filtered dataset and generates dynamic business insights.
    Adapts the narrative based on active filters (Region, Division, Product, Year, Month).
    Returns a list of structured insight dicts: {category, icon, html_text, text}.
    """
    if len(df) == 0:
        return []

    insights = []
    active_filters = active_filters or {}

    sel_month = active_filters.get("month", "All")
    sel_year = str(active_filters.get("year", "All"))
    sel_region = active_filters.get("region", "All")
    sel_product = active_filters.get("product", "All")
    sel_division = active_filters.get("division", "All")

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Gross Profit"].sum())
    total_cost = float(df["Cost"].sum())
    total_units = int(df["Units"].sum())
    overall_margin = (total_profit / total_sales * 100.0) if total_sales > 0 else 0.0

    # Build context description string
    context_tokens = []
    if sel_month != "All":
        context_tokens.append(f"Month: {sel_month}")
    if sel_year != "All":
        context_tokens.append(f"Year: {sel_year}")
    if sel_region != "All":
        context_tokens.append(f"Region: {sel_region}")
    if sel_division != "All":
        context_tokens.append(f"Division: {sel_division}")
    if sel_product != "All":
        context_tokens.append(f"Product: {sel_product}")

    filter_desc = " (" + ", ".join(context_tokens) + ")" if context_tokens else " (All Records)"

    # -------------------------------------------------------------
    # CASE 1: Single Product Filtered
    # -------------------------------------------------------------
    if sel_product != "All":
        prod_div = df["Division"].iloc[0]
        profit_per_unit = (total_profit / total_units) if total_units > 0 else 0.0
        margin_diff = overall_margin - CORPORATE_BENCHMARK_MARGIN
        perf_label = "above" if margin_diff >= 0 else "below"

        _add_insight(
            insights,
            f"Product Performance{filter_desc}",
            "🍬",
            (
                f"<b>{sel_product}</b> ({prod_div}) achieved a gross margin of <b>{overall_margin:.2f}%</b>, "
                f"generating <b>${total_profit:,.2f}</b> profit from <b>${total_sales:,.2f}</b> revenue. "
                f"This is <b>{abs(margin_diff):.2f}% {perf_label}</b> the corporate benchmark (65.91%)."
            )
        )

        # Regional distribution for this product
        if "Region" in df.columns and sel_region == "All":
            reg_grp = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
            if len(reg_grp) > 0:
                top_reg = reg_grp.index[0]
                top_reg_sales = reg_grp.iloc[0]
                top_reg_pct = (top_reg_sales / total_sales * 100.0) if total_sales > 0 else 0.0
                _add_insight(
                    insights,
                    "Key Geographic Demand",
                    "📍",
                    (
                        f"The primary market for this product is <b>{top_reg}</b>, capturing "
                        f"<b>${top_reg_sales:,.2f}</b> ({top_reg_pct:.1f}% of volume) across "
                        f"<b>{df[df['Region'] == top_reg]['Units'].sum():,}</b> units."
                    )
                )

        # Unit economics
        _add_insight(
            insights,
            "Unit Economics & Pricing",
            "💵",
            (
                f"Each unit generates an average gross profit of <b>${profit_per_unit:.2f}</b> "
                f"(Unit cost: <b>${(total_cost/total_units):.2f}</b> vs Price realization: <b>${(total_sales/total_units):.2f}</b>) "
                f"across <b>{len(df):,}</b> transactions."
            )
        )

        # Risk classification
        if overall_margin < (RISK_THRESHOLDS["high_risk_max"] * 100.0):
            risk_msg = "Critical margin risk: pricing is inadequate relative to supplier product cost."
            risk_icon = "🔴"
        elif overall_margin < (RISK_THRESHOLDS["medium_risk_max"] * 100.0):
            risk_msg = "Moderate margin risk: margin is below the corporate 50% target threshold."
            risk_icon = "🟡"
        else:
            risk_msg = "Healthy profitability: margin exceeds the 50% executive target."
            risk_icon = "🟢"

        _add_insight(
            insights,
            "Risk & Pricing Evaluation",
            risk_icon,
            f"Status: <b>{risk_msg}</b> Total unit sales recorded: <b>{total_units:,}</b>."
        )

        return insights

    # -------------------------------------------------------------
    # CASE 2: Single Region Filtered
    # -------------------------------------------------------------
    if sel_region != "All":
        _add_insight(
            insights,
            f"Regional Performance{filter_desc}",
            "📍",
            (
                f"The <b>{sel_region}</b> region yielded <b>${total_profit:,.2f}</b> in gross profit on "
                f"<b>${total_sales:,.2f}</b> sales, delivering a strong gross margin of <b>{overall_margin:.2f}%</b> "
                f"across <b>{total_units:,}</b> units sold."
            )
        )

        # Top product in this region
        prod_sales = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
        if len(prod_sales) > 0:
            top_p = prod_sales.index[0]
            top_p_sales = prod_sales.iloc[0]
            top_p_pct = (top_p_sales / total_sales * 100.0) if total_sales > 0 else 0.0
            _add_insight(
                insights,
                f"Top Candy in {sel_region}",
                "🏆",
                (
                    f"<b>{top_p}</b> is the leading product in {sel_region}, generating "
                    f"<b>${top_p_sales:,.2f}</b> ({top_p_pct:.1f}% of regional sales)."
                )
            )

        # Division contribution in this region
        div_p = df.groupby("Division")["Gross Profit"].sum().sort_values(ascending=False)
        if len(div_p) > 0:
            top_div = div_p.index[0]
            top_div_val = div_p.iloc[0]
            top_div_pct = (top_div_val / total_profit * 100.0) if total_profit > 0 else 0.0
            _add_insight(
                insights,
                f"Division Mix in {sel_region}",
                "🍫",
                (
                    f"<b>{top_div}</b> accounts for <b>${top_div_val:,.2f}</b> ({top_div_pct:.1f}%) "
                    f"of total gross profit earned in {sel_region}."
                )
            )

        # Top State in this region
        if "State/Province" in df.columns:
            state_p = df.groupby("State/Province")["Gross Profit"].sum().sort_values(ascending=False)
            if len(state_p) > 0:
                top_state = state_p.index[0]
                top_state_val = state_p.iloc[0]
                _add_insight(
                    insights,
                    "Key State Driver",
                    "🗺️",
                    (
                        f"<b>{top_state}</b> is the top performing state in {sel_region}, delivering "
                        f"<b>${top_state_val:,.2f}</b> gross profit across {df[df['State/Province'] == top_state]['Units'].sum():,} units."
                    )
                )

        # Margin risk check in this region
        p_margins = df.groupby("Product Name").agg(Sales=("Sales", "sum"), Profit=("Gross Profit", "sum")).reset_index()
        p_margins["Margin_%"] = (p_margins["Profit"] / p_margins["Sales"] * 100.0).fillna(0)
        low_p = p_margins[p_margins["Margin_%"] < (RISK_THRESHOLDS["high_risk_max"] * 100.0)]
        if len(low_p) > 0:
            p_name = low_p.iloc[0]["Product Name"]
            p_margin = low_p.iloc[0]["Margin_%"]
            _add_insight(
                insights,
                "Regional Margin Alert",
                "⚠️",
                (
                    f"<b>{p_name}</b> exhibits severe margin vulnerability in {sel_region} with only "
                    f"<b>{p_margin:.2f}%</b> gross margin."
                )
            )
        else:
            _add_insight(
                insights,
                "Regional Portfolio Health",
                "✅",
                f"All product lines in {sel_region} maintain healthy gross margins meeting profitability thresholds."
            )

        return insights

    # -------------------------------------------------------------
    # CASE 3: General / Multi-Filtered View
    # -------------------------------------------------------------
    # 1. Division Profitability Leader
    div_profit = df.groupby("Division")["Gross Profit"].sum().sort_values(ascending=False)
    if len(div_profit) > 0:
        top_div = div_profit.index[0]
        top_div_val = div_profit.iloc[0]
        top_div_share = (top_div_val / total_profit * 100.0) if total_profit > 0 else 0.0
        _add_insight(
            insights,
            f"Division Leadership{filter_desc}",
            "🏆",
            (
                f"<b>{top_div}</b> is the dominant division by gross profit, contributing "
                f"<b>${top_div_val:,.2f}</b> ({top_div_share:.1f}% of total profit across active filters)."
            )
        )

    # 2. Regional Stronghold
    region_profit = df.groupby("Region")["Gross Profit"].sum().sort_values(ascending=False)
    if len(region_profit) > 0:
        top_region = region_profit.index[0]
        top_region_val = region_profit.iloc[0]
        top_region_share = (top_region_val / total_profit * 100.0) if total_profit > 0 else 0.0
        _add_insight(
            insights,
            "Regional Stronghold",
            "📍",
            (
                f"<b>{top_region}</b> is currently the strongest territory, generating "
                f"<b>${top_region_val:,.2f}</b> in gross profit ({top_region_share:.1f}% regional contribution)."
            )
        )

    # 3. Top Revenue Generator
    prod_sales = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
    if len(prod_sales) > 0:
        top_prod_sales = prod_sales.index[0]
        top_prod_sales_val = prod_sales.iloc[0]
        top_prod_sales_share = (top_prod_sales_val / total_sales * 100.0) if total_sales > 0 else 0.0
        _add_insight(
            insights,
            "Top Revenue Generator",
            "💰",
            (
                f"<b>{top_prod_sales}</b> leads in sales volume, generating "
                f"<b>${top_prod_sales_val:,.2f}</b> ({top_prod_sales_share:.1f}% of filtered revenue)."
            )
        )

    # 4. Highest Gross Margin Product
    prod_stats = df.groupby("Product Name").agg(
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum")
    ).reset_index()
    prod_stats["Margin_%"] = (prod_stats["Profit"] / prod_stats["Sales"] * 100.0).fillna(0)
    prod_stats = prod_stats.sort_values(by="Margin_%", ascending=False)

    if len(prod_stats) > 0:
        top_margin_prod = prod_stats.iloc[0]
        _add_insight(
            insights,
            "Peak Profitability Product",
            "📈",
            (
                f"<b>{top_margin_prod['Product Name']}</b> delivers the highest gross margin at "
                f"<b>{top_margin_prod['Margin_%']:.2f}%</b> (${top_margin_prod['Profit']:,.2f} profit from ${top_margin_prod['Sales']:,.2f} sales)."
            )
        )

    # 5. Margin Risk Warning
    low_margin_prods = prod_stats[prod_stats["Margin_%"] < (RISK_THRESHOLDS["high_risk_max"] * 100.0)]
    if len(low_margin_prods) > 0:
        worst_prod = low_margin_prods.iloc[-1]
        prod_cost = df[df["Product Name"] == worst_prod["Product Name"]]["Cost"].sum()
        _add_insight(
            insights,
            "Margin Risk Alert",
            "⚠️",
            (
                f"<b>{worst_prod['Product Name']}</b> presents severe margin risk with a gross margin of only "
                f"<b>{worst_prod['Margin_%']:.2f}%</b> (Cost: ${prod_cost:,.2f} vs Sales: ${worst_prod['Sales']:,.2f}). Immediate review advised."
            )
        )
    else:
        med_risk_prods = prod_stats[prod_stats["Margin_%"] < (RISK_THRESHOLDS["medium_risk_max"] * 100.0)]
        if len(med_risk_prods) > 0:
            lowest_med = med_risk_prods.iloc[-1]
            _add_insight(
                insights,
                "Margin Watch",
                "🔍",
                (
                    f"<b>{lowest_med['Product Name']}</b> has a moderate gross margin of "
                    f"<b>{lowest_med['Margin_%']:.2f}%</b>, below the corporate 50% target threshold."
                )
            )

    # 6. Overall Portfolio Health
    _add_insight(
        insights,
        "Filtered Portfolio Summary",
        "🎯",
        (
            f"Overall gross margin is <b>{overall_margin:.2f}%</b> across <b>{len(df):,}</b> transactions. "
            f"Total gross profit achieved is <b>${total_profit:,.2f}</b> against costs of <b>${total_cost:,.2f}</b>."
        )
    )

    return insights
