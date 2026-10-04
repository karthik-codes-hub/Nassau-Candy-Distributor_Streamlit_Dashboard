import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import pandas as pd
from utils.data_loader import load_data
from utils.calculations import (
    apply_filters,
    calculate_kpis,
    get_product_margins,
    get_division_profitability,
    get_scatter_data,
    get_product_details
)
from utils.insights import generate_insights
from charts import (
    create_highest_gross_margin_chart,
    create_profitability_scatter_chart,
    create_division_profitability_chart
)


def run_tests():
    print("=" * 60)
    print("RUNNING AUTOMATED TEST SUITE FOR NASSAU CANDY STREAMLIT DASHBOARD")
    print("=" * 60)

    # TEST 1: Load Data
    print("\n[TEST 1] Loading and cleaning dataset...")
    df, source = load_data()
    print(f"  Loaded {len(df)} rows from {source}")
    assert len(df) == 10194, f"Expected 10194 rows, got {len(df)}"
    assert "Region" in df.columns
    assert "Sales" in df.columns
    assert "Gross Profit" in df.columns
    print("  [PASS] Test 1 Passed!")

    # TEST 2: Overall KPIs match Power BI
    print("\n[TEST 2] Verifying KPI calculations against Power BI reference...")
    kpis = calculate_kpis(df)
    print(f"  Total Sales: ${kpis['total_sales']:,.2f} (Expected ~$141,783.63)")
    print(f"  Total Units: {kpis['total_units']:,} (Expected 38,654)")
    print(f"  Total Cost: ${kpis['total_cost']:,.2f} (Expected ~$48,340.83)")
    print(f"  Total Gross Profit: ${kpis['total_gross_profit']:,.2f} (Expected ~$93,442.80)")
    print(f"  Gross Margin %: {kpis['gross_margin_pct']:.2f}% (Expected 65.91%)")

    assert abs(kpis["total_sales"] - 141783.63) < 1.0, "Sales mismatch"
    assert kpis["total_units"] == 38654, "Units mismatch"
    assert abs(kpis["total_cost"] - 48340.83) < 1.0, "Cost mismatch"
    assert abs(kpis["total_gross_profit"] - 93442.80) < 1.0, "Profit mismatch"
    assert abs(kpis["gross_margin_pct"] - 65.91) < 0.1, "Margin mismatch"
    print("  [PASS] Test 2 Passed: Exact match to Power BI!")

    # TEST 3: Region Validation
    print("\n[TEST 3] Validating Region values strictly against dataset...")
    regions = sorted(df["Region"].unique().tolist())
    print(f"  Unique Regions: {regions}")
    assert regions == ["Atlantic", "Gulf", "Interior", "Pacific"], f"Unexpected regions: {regions}"
    print("  [PASS] Test 3 Passed: Regions verified!")

    # TEST 4: Numerical Sorting for Margins and Profits
    print("\n[TEST 4] Testing Numerical Sorting (Phase 11)...")
    prod_margins = get_product_margins(df)
    margins_list = prod_margins["Gross_Margin_%"].tolist()
    assert margins_list == sorted(margins_list, reverse=True), "Product margins are not sorted numerically descending!"
    print(f"  Top 3 products by margin: {prod_margins['Product Name'].iloc[:3].tolist()} -> {margins_list[:3]}")

    div_profit = get_division_profitability(df)
    profits_list = div_profit["Total_Gross_Profit"].tolist()
    assert profits_list == sorted(profits_list, reverse=True), "Division profits are not sorted numerically descending!"
    print(f"  Divisions sorted by profit: {div_profit['Division'].tolist()} -> {profits_list}")
    print("  [PASS] Test 4 Passed: Strict numerical sorting confirmed!")

    # TEST 5: Cumulative Filtering
    print("\n[TEST 5] Testing Cumulative Filters (Phase 8)...")
    filtered = apply_filters(df, selected_regions=["Atlantic"], selected_divisions=["Chocolate"])
    print(f"  Atlantic + Chocolate rows: {len(filtered)}")
    assert len(filtered) > 0, "No records for Atlantic + Chocolate"
    assert set(filtered["Region"].unique()) == {"Atlantic"}
    assert set(filtered["Division"].unique()) == {"Chocolate"}

    filtered_month_year = apply_filters(df, selected_months=["March"], selected_years=[2024])
    print(f"  March 2024 rows: {len(filtered_month_year)}")
    assert len(filtered_month_year) > 0
    assert set(filtered_month_year["Order Month Name"].unique()) == {"March"}
    assert set(filtered_month_year["Order Year"].unique()) == {2024}
    print("  [PASS] Test 5 Passed: Cumulative filtering works seamlessly!")

    # TEST 6: Product Details with Current Filter Context (Phase 15)
    print("\n[TEST 6] Testing Product Details within current filter context...")
    # Unfiltered
    det_all = get_product_details(df, "Wonka Bar - Milk Chocolate")
    # Filtered to Atlantic
    df_atlantic = apply_filters(df, selected_regions=["Atlantic"])
    det_atlantic = get_product_details(df_atlantic, "Wonka Bar - Milk Chocolate")
    print(f"  Wonka Bar Milk Chocolate Unfiltered Sales: ${det_all['sales']:,.2f}")
    print(f"  Wonka Bar Milk Chocolate Atlantic Sales: ${det_atlantic['sales']:,.2f}")
    assert det_atlantic["sales"] < det_all["sales"], "Filtered sales should be less than unfiltered sales"
    assert det_atlantic["regions"] == ["Atlantic"]
    print("  [PASS] Test 6 Passed: Filtered context isolation verified!")

    # TEST 7: Dynamic Business Insights
    print("\n[TEST 7] Testing Dynamic Insights Engine...")
    insights_full = generate_insights(df)
    assert len(insights_full) >= 4, f"Expected at least 4 insights, got {len(insights_full)}"
    for ins in insights_full:
        print(f"  [{ins['icon']} {ins['category']}] {ins['text']}")
    print("  [PASS] Test 7 Passed: Narrative insights generated dynamically!")

    # TEST 8: Empty Filter Handling
    print("\n[TEST 8] Testing Empty Filter Selection (Phase 23)...")
    empty_df = apply_filters(df, selected_regions=["NonExistentRegion"])
    assert len(empty_df) == 0
    empty_kpis = calculate_kpis(empty_df)
    assert empty_kpis["is_empty"] is True
    assert empty_kpis["total_sales"] == 0.0
    empty_insights = generate_insights(empty_df)
    assert empty_insights == []
    print("  [PASS] Test 8 Passed: Empty state handled cleanly without errors!")

    # TEST 9: Chart Generation (Light & Dark Theme)
    print("\n[TEST 9] Testing Plotly Chart Generators in Dark & Light Themes...")
    for theme in ["dark", "light"]:
        fig1 = create_highest_gross_margin_chart(prod_margins, theme=theme)
        fig2 = create_profitability_scatter_chart(get_scatter_data(df), theme=theme)
        fig3 = create_division_profitability_chart(div_profit, theme=theme)
        assert fig1 is not None and fig2 is not None and fig3 is not None
        # Test empty charts
        empty_fig = create_highest_gross_margin_chart(pd.DataFrame(), theme=theme)
        assert empty_fig is not None
    print("  [PASS] Test 9 Passed: Charts render in both themes!")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% SUITE PASS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
