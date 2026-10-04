"""
Nassau Candy Distributor — Profitability Analysis Dashboard
A production-quality Streamlit BI application recreating the original Power BI report.
"""

import os
import base64
import pandas as pd
import numpy as np
import streamlit as st

# Local modules
from utils.data_loader import load_data, MONTH_ORDER
from utils.calculations import (
    apply_filters,
    calculate_kpis,
    get_product_margins,
    get_division_profitability,
    get_scatter_data,
    get_product_details,
    RISK_THRESHOLDS
)
from utils.insights import generate_insights
from charts import (
    create_highest_gross_margin_chart,
    create_profitability_scatter_chart,
    create_division_profitability_chart,
    POWERBI_COLORS
)

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy Distributor — Profitability Analysis",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# THEME & SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

if "sb_year" not in st.session_state:
    st.session_state["sb_year"] = "All"

if "sb_region" not in st.session_state:
    st.session_state["sb_region"] = "All"

if "sb_product" not in st.session_state:
    st.session_state["sb_product"] = "All"

if "sb_division" not in st.session_state:
    st.session_state["sb_division"] = "All"

if "radio_month" not in st.session_state:
    st.session_state["radio_month"] = "All"

if "modal_product" not in st.session_state:
    st.session_state["modal_product"] = None


def reset_all_filters():
    """Resets all filter selections back to default 'All' state."""
    st.session_state["sb_year"] = "All"
    st.session_state["sb_region"] = "All"
    st.session_state["sb_product"] = "All"
    st.session_state["sb_division"] = "All"
    st.session_state["radio_month"] = "All"
    st.session_state["modal_product"] = None


def toggle_theme():
    """Toggles between dark and light themes."""
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"


# ---------------------------------------------------------
# ASSET HELPERS
# ---------------------------------------------------------
@st.cache_data
def get_image_base64(filepath: str) -> str:
    """Reads an image file and converts to base64 string for fast inline rendering."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


ASSET_PATHS = {
    "logo": os.path.join("assets", "logo.png"),
    "sales": os.path.join("assets", "icon_sales.png"),
    "units": os.path.join("assets", "icon_units.png"),
    "margin": os.path.join("assets", "icon_margin.png"),
    "profit": os.path.join("assets", "icon_profit.png"),
    "cost": os.path.join("assets", "icon_cost.png"),
}

B64_ICONS = {k: get_image_base64(v) for k, v in ASSET_PATHS.items()}


# ---------------------------------------------------------
# LOAD STYLES
# ---------------------------------------------------------
def inject_custom_css(theme: str):
    """Injects custom CSS styling with theme responsiveness."""
    css_content = ""
    for path in ["style.css", os.path.join("assets", "style.css")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                css_content = f.read()
            break

    bg_color = "#1F2937" if theme == "dark" else "#F3F4F6"
    sidebar_bg = "#111827" if theme == "dark" else "#FFFFFF"
    text_color = "#F9FAFB" if theme == "dark" else "#1F2937"
    btn_bg = "#242E3D" if theme == "dark" else "#FFFFFF"
    btn_color = "#F9FAFB" if theme == "dark" else "#1F2937"
    btn_border = "rgba(249, 115, 22, 0.4)" if theme == "dark" else "#D1D5DB"

    theme_overrides = f"""
    <style>
    {css_content}
    
    /* Hide Streamlit Header Bar, Deploy Button, and MainMenu (Image 2) */
    header[data-testid="stHeader"], 
    [data-testid="stHeader"], 
    #MainMenu, 
    .stDeployButton, 
    footer {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    .stAppViewBlockContainer, .block-container {{
        padding-top: 1.25rem !important;
        padding-bottom: 2rem !important;
    }}

    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    .header-title-text {{
        color: #FFFFFF !important;
    }}
    
    .header-subtitle {{
        color: #F97316 !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid rgba(249, 115, 22, 0.2);
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] span {{
        color: {text_color} !important;
    }}
    
    /* Top horizontal slicers styling */
    div[data-testid="stSelectbox"] > label {{
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: {text_color} !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    
    button, .stButton > button, div[data-testid="stDownloadButton"] > button {{
        background-color: {btn_bg} !important;
        color: {btn_color} !important;
        border: 1px solid {btn_border} !important;
    }}
    </style>
    """
    st.markdown(theme_overrides, unsafe_allow_html=True)


# Inject CSS
inject_custom_css(st.session_state["theme"])

# ---------------------------------------------------------
# LOAD & VALIDATE DATA
# ---------------------------------------------------------
try:
    df_raw, source_path = load_data()
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}")
    st.stop()


# ---------------------------------------------------------
# SIDEBAR FILTERS (Month Slicer matching Power BI)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📅 Select Month")
    st.caption("Filter records by calendar month")

    raw_months = [m for m in MONTH_ORDER if m in df_raw["Order Month Name"].unique()]
    month_options = ["All"] + raw_months

    selected_month = st.radio(
        label="Select Month",
        options=month_options,
        key="radio_month",
        label_visibility="collapsed"
    )


# ---------------------------------------------------------
# APPLY CUMULATIVE FILTERS (Phase 8)
# ---------------------------------------------------------
filtered_df = apply_filters(
    df=df_raw,
    selected_months=st.session_state["radio_month"],
    selected_years=st.session_state["sb_year"],
    selected_regions=st.session_state["sb_region"],
    selected_products=st.session_state["sb_product"],
    selected_divisions=st.session_state["sb_division"]
)

# ---------------------------------------------------------
# TOP HEADER BAR
# ---------------------------------------------------------
theme_icon = "☀ Light" if st.session_state["theme"] == "dark" else "🌙 Dark"
current_theme = st.session_state["theme"]

logo_html = ""
if B64_ICONS["logo"]:
    logo_html = f'<img src="data:image/png;base64,{B64_ICONS["logo"]}" style="height: 52px; object-fit: contain; margin-right: 16px;">'

header_html = f"""
<div class="dashboard-header">
    <div class="header-title-box">
        {logo_html}
        <div>
            <h1 class="header-title-text">NASSAU CANDY DISTRIBUTOR – PROFITABILITY ANALYSIS</h1>
            <p class="header-subtitle">Executive Business Intelligence & Profitability Performance Dashboard</p>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Header Controls Row
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([4, 1.5, 1.5, 1.5])
with ctrl_col1:
    st.empty()
with ctrl_col2:
    st.button(f"Theme: {theme_icon}", width="stretch", on_click=toggle_theme, key="header_theme_btn")
with ctrl_col3:
    st.button("↻ Reset All", width="stretch", on_click=reset_all_filters, key="header_reset_btn")
with ctrl_col4:
    csv_export_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Export Filtered Data",
        data=csv_export_data,
        file_name="Nassau_Candy_Filtered_Data.csv",
        mime="text/csv",
        width="stretch",
        key="header_export_btn"
    )


# ---------------------------------------------------------
# CALCULATE KPIS (Phase 10 - Exact Power BI Match)
# ---------------------------------------------------------
kpis = calculate_kpis(filtered_df)


def format_kpi_sales(val: float) -> str:
    """Matches Power BI $142K format."""
    if val >= 1_000_000:
        return f"${val/1_000_000:,.1f}M"
    elif val >= 1000:
        return f"${round(val/1000):,.0f}K"
    else:
        return f"${val:,.0f}"


def format_kpi_profit_cost(val: float) -> str:
    """Matches Power BI $93.4K and $48.3K format."""
    if val >= 1_000_000:
        return f"${val/1_000_000:,.1f}M"
    elif val >= 1000:
        return f"${val/1000:,.1f}K"
    else:
        return f"${val:,.0f}"


def format_kpi_units(val: int) -> str:
    """Matches Power BI 39K format."""
    if val >= 1_000_000:
        return f"{val/1_000_000:,.1f}M"
    elif val >= 1000:
        return f"{round(val/1000):,.0f}K"
    else:
        return f"{val:,}"


theme_str = st.session_state["theme"]
kpi_card_class = f"kpi-card kpi-card-{theme_str}"
kpi_label_class = f"kpi-label-{theme_str}"
kpi_val_class = f"kpi-value-{theme_str}"

sales_str = format_kpi_sales(kpis["total_sales"]) if not kpis["is_empty"] else "$0"
units_str = format_kpi_units(kpis["total_units"]) if not kpis["is_empty"] else "0"
margin_str = f"{kpis['gross_margin_pct']:.2f}%" if not kpis["is_empty"] else "0.00%"
profit_str = format_kpi_profit_cost(kpis["total_gross_profit"]) if not kpis["is_empty"] else "$0"
cost_str = format_kpi_profit_cost(kpis["total_cost"]) if not kpis["is_empty"] else "$0"

# Render 5 KPI Cards in top row (directly beneath header, exactly like Power BI)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    icon_img = f'<img class="kpi-icon-img" src="data:image/png;base64,{B64_ICONS["sales"]}"/>' if B64_ICONS["sales"] else "💰"
    st.markdown(f"""
    <div class="{kpi_card_class}">
        <div class="kpi-content">
            <span class="{kpi_label_class}">Total Sales</span>
            <span class="{kpi_val_class}">{sales_str}</span>
            <span class="kpi-subtext">${kpis['total_sales']:,.2f}</span>
        </div>
        <div class="kpi-icon-container">{icon_img}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    icon_img = f'<img class="kpi-icon-img" src="data:image/png;base64,{B64_ICONS["units"]}"/>' if B64_ICONS["units"] else "📦"
    st.markdown(f"""
    <div class="{kpi_card_class}">
        <div class="kpi-content">
            <span class="{kpi_label_class}">Total Units</span>
            <span class="{kpi_val_class}">{units_str}</span>
            <span class="kpi-subtext">{kpis['total_units']:,} Units</span>
        </div>
        <div class="kpi-icon-container">{icon_img}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    icon_img = f'<img class="kpi-icon-img" src="data:image/png;base64,{B64_ICONS["margin"]}"/>' if B64_ICONS["margin"] else "📈"
    st.markdown(f"""
    <div class="{kpi_card_class}">
        <div class="kpi-content">
            <span class="{kpi_label_class}">Gross Margin %</span>
            <span class="{kpi_val_class}">{margin_str}</span>
            <span class="kpi-subtext">{kpis['margin_risk']}</span>
        </div>
        <div class="kpi-icon-container">{icon_img}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    icon_img = f'<img class="kpi-icon-img" src="data:image/png;base64,{B64_ICONS["profit"]}"/>' if B64_ICONS["profit"] else "💵"
    st.markdown(f"""
    <div class="{kpi_card_class}">
        <div class="kpi-content">
            <span class="{kpi_label_class}">Total Gross Profit</span>
            <span class="{kpi_val_class}">{profit_str}</span>
            <span class="kpi-subtext">${kpis['total_gross_profit']:,.2f}</span>
        </div>
        <div class="kpi-icon-container">{icon_img}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    icon_img = f'<img class="kpi-icon-img" src="data:image/png;base64,{B64_ICONS["cost"]}"/>' if B64_ICONS["cost"] else "🧾"
    st.markdown(f"""
    <div class="{kpi_card_class}">
        <div class="kpi-content">
            <span class="{kpi_label_class}">Total Cost</span>
            <span class="{kpi_val_class}">{cost_str}</span>
            <span class="kpi-subtext">${kpis['total_cost']:,.2f}</span>
        </div>
        <div class="kpi-icon-container">{icon_img}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# HORIZONTAL SLICERS ROW (Positioned under KPIs like Power BI)
# ---------------------------------------------------------
year_options = ["All"] + sorted([str(y) for y in df_raw["Order Year"].unique().tolist()])
region_options = ["All"] + sorted(df_raw["Region"].astype(str).str.strip().unique().tolist())
product_options = ["All"] + sorted(df_raw["Product Name"].unique().tolist())
division_options = ["All"] + sorted(df_raw["Division"].unique().tolist())

slicer_col1, slicer_col2, slicer_col3, slicer_col4 = st.columns(4)

with slicer_col1:
    st.selectbox("Select Order Year", options=year_options, key="sb_year")

with slicer_col2:
    st.selectbox("Select Region", options=region_options, key="sb_region")

with slicer_col3:
    st.selectbox("Select Product Name", options=product_options, key="sb_product")

with slicer_col4:
    st.selectbox("Select Division", options=division_options, key="sb_division")


# Active filter feedback badges
active_filter_list = []
if st.session_state["radio_month"] != "All":
    active_filter_list.append(f"Month: {st.session_state['radio_month']}")
if str(st.session_state["sb_year"]) != "All":
    active_filter_list.append(f"Year: {st.session_state['sb_year']}")
if st.session_state["sb_region"] != "All":
    active_filter_list.append(f"Region: {st.session_state['sb_region']}")
if st.session_state["sb_product"] != "All":
    active_filter_list.append(f"Product: {st.session_state['sb_product']}")
if st.session_state["sb_division"] != "All":
    active_filter_list.append(f"Division: {st.session_state['sb_division']}")

if active_filter_list:
    st.markdown(
        f"<div style='font-size: 0.82rem; color: #F97316; margin-bottom: 8px;'><b>Active Filters ({len(filtered_df):,} records):</b> " +
        " &nbsp;|&nbsp; ".join([f"<code>{af}</code>" for af in active_filter_list]) + "</div>",
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# EMPTY DATA HANDLING (Phase 23)
# ---------------------------------------------------------
if len(filtered_df) == 0:
    st.warning("⚠️ No data available for the selected filters. Please adjust your filter selection.")


# ---------------------------------------------------------
# PREPARE AGGREGATED DATA FOR CHARTS (Phase 11 & 13)
# ---------------------------------------------------------
df_product_margins = get_product_margins(filtered_df)
df_scatter = get_scatter_data(filtered_df)
df_divisions = get_division_profitability(filtered_df)


# ---------------------------------------------------------
# VISUALIZATIONS ROW 1 (Horizontal Bar & Scatter Chart)
# ---------------------------------------------------------
chart_row1_col1, chart_row1_col2 = st.columns([1, 1])

with chart_row1_col1:
    fig_bar = create_highest_gross_margin_chart(df_product_margins, theme=st.session_state["theme"])
    st.plotly_chart(fig_bar, width="stretch", config={"displayModeBar": False})

with chart_row1_col2:
    fig_scatter = create_profitability_scatter_chart(df_scatter, theme=st.session_state["theme"])
    st.plotly_chart(fig_scatter, width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------
# VISUALIZATIONS ROW 2 (Division Column Chart & Risk Table)
# ---------------------------------------------------------
chart_row2_col1, chart_row2_col2 = st.columns([1, 1.25])

with chart_row2_col1:
    fig_div = create_division_profitability_chart(df_divisions, theme=st.session_state["theme"])
    st.plotly_chart(fig_div, width="stretch", config={"displayModeBar": False})

with chart_row2_col2:
    st.markdown(
        f"<div class='visual-title-{theme_str}'>Which products represent margin risk?</div>",
        unsafe_allow_html=True
    )

    if len(df_product_margins) == 0:
        st.info("No product margin records available for the active filters.")
    else:
        table_rows = []
        for _, row in df_product_margins.iterrows():
            prod_name = row["Product Name"]
            sales_val = f"${row['Total_Sales']:,.1f}"
            cost_val = f"${row['Total_Cost']:,.1f}"
            profit_val = f"${row['Total_Gross_Profit']:,.1f}"
            margin_pct = f"{row['Gross_Margin_%']:.2f}%"
            units_val = f"{row['Total_Units']:,}"

            if row["Margin Risk"] == "High Risk":
                badge_html = "<span class='badge-high'>🔴 High Risk</span>"
            elif row["Margin Risk"] == "Medium Risk":
                badge_html = "<span class='badge-med'>🟡 Medium</span>"
            else:
                badge_html = "<span class='badge-low'>🟢 Low Risk</span>"

            row_str = (
                f"<tr>"
                f"<td>{prod_name}</td>"
                f"<td>{sales_val}</td>"
                f"<td>{cost_val}</td>"
                f"<td>{profit_val}</td>"
                f"<td>{margin_pct}</td>"
                f"<td>{units_val}</td>"
                f"<td>{badge_html}</td>"
                f"</tr>"
            )
            table_rows.append(row_str)

        tot_sales = f"${kpis['total_sales']:,.1f}"
        tot_cost = f"${kpis['total_cost']:,.1f}"
        tot_profit = f"${kpis['total_gross_profit']:,.1f}"
        tot_margin = f"{kpis['gross_margin_pct']:.2f}%"
        tot_units = f"{kpis['total_units']:,}"
        tot_risk = "🟢 Low Risk" if kpis['gross_margin_pct'] >= 50 else ("🟡 Medium" if kpis['gross_margin_pct'] >= 20 else "🔴 High Risk")

        total_row_str = (
            f"<tr class='total-row'>"
            f"<td>Total</td>"
            f"<td>{tot_sales}</td>"
            f"<td>{tot_cost}</td>"
            f"<td>{tot_profit}</td>"
            f"<td>{tot_margin}</td>"
            f"<td>{tot_units}</td>"
            f"<td>{tot_risk}</td>"
            f"</tr>"
        )

        table_html = (
            f"<div style='overflow-x: auto; max-height: 330px; overflow-y: auto;'>"
            f"<table class='risk-table risk-table-{theme_str}'>"
            f"<thead><tr>"
            f"<th>Product Name</th><th>Total Sales</th><th>Total Cost</th><th>Total Gross Profit</th><th>Gross Margin %</th><th>Total Units</th><th>Risk Indicator</th>"
            f"</tr></thead>"
            f"<tbody>{''.join(table_rows)}{total_row_str}</tbody>"
            f"</table></div>"
        )
        st.html(table_html)


# ---------------------------------------------------------
# DYNAMIC BUSINESS INSIGHTS (Phase 17 & Phase 18)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## 💡 Key Business Insights")
st.caption("Dynamically generated executive intelligence based on current filter context")

active_filters_dict = {
    "month": st.session_state["radio_month"],
    "year": st.session_state["sb_year"],
    "region": st.session_state["sb_region"],
    "product": st.session_state["sb_product"],
    "division": st.session_state["sb_division"],
}

insights = generate_insights(filtered_df, active_filters=active_filters_dict)

if not insights:
    st.info("No business insights available for the current filter selection.")
else:
    ins_cols = st.columns(2)
    for idx, ins in enumerate(insights):
        col_target = ins_cols[idx % 2]
        with col_target:
            st.html(
                f"<div class='insight-card insight-{theme_str}'>"
                f"<span style='font-size: 1.4rem;'>{ins['icon']}</span>"
                f"<div>"
                f"<div style='font-size: 0.78rem; text-transform: uppercase; color: #F97316; font-weight: 700; letter-spacing: 0.04em;'>{ins['category']}</div>"
                f"<div style='font-size: 0.92rem; line-height: 1.35; margin-top: 2px;'>{ins['html_text']}</div>"
                f"</div>"
                f"</div>"
            )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align: center; font-size: 0.78rem; color: {'#9CA3AF' if theme_str == 'dark' else '#6B7280'};'>"
    "Nassau Candy Distributor — Profitability Analysis Dashboard | Recreated from Power BI &bull; Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
