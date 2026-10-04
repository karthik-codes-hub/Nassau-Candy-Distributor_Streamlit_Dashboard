"""
Plotly chart generation module for Nassau Candy Distributor Profitability Dashboard.
Matches the Power BI dashboard aesthetics, exact color palette, sorting, and hover interactions.
Preserves visualization colors across light and dark themes.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Exact Power BI Color Palette
POWERBI_COLORS = {
    "primary_orange": "#F97316",
    "gradient_min": "#F5C4AF",       # Peach / Light coral
    "gradient_max": "#EB895F",       # Coral Orange
    "division_chocolate": "#F97316", # Orange
    "division_other": "#118DFF",     # Blue
    "division_sugar": "#E044A7",     # Pink / Magenta
    "risk_high": "#E53935",          # Red
    "risk_medium": "#FBC02D",        # Yellow
    "risk_low": "#43A047",           # Green
}

THEME_CONFIG = {
    "dark": {
        "bg_color": "#242E3D",
        "paper_color": "#242E3D",
        "text_color": "#F3F4F6",
        "muted_text": "#9CA3AF",
        "grid_color": "rgba(255, 255, 255, 0.08)",
        "tooltip_bg": "#1F2937",
        "tooltip_text": "#F9FAFB",
    },
    "light": {
        "bg_color": "#FFFFFF",
        "paper_color": "#FFFFFF",
        "text_color": "#1F2937",
        "muted_text": "#6B7280",
        "grid_color": "rgba(0, 0, 0, 0.06)",
        "tooltip_bg": "#FFFFFF",
        "tooltip_text": "#1F2937",
    },
}


def get_base_layout(title: str, theme: str = "dark") -> dict:
    """
    Returns standard Plotly layout configuration respecting the active theme
    without changing the Power BI data colors.
    """
    tc = THEME_CONFIG.get(theme, THEME_CONFIG["dark"])
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=15, color=tc["text_color"]),
            x=0.01,
            y=0.96,
        ),
        paper_bgcolor=tc["paper_color"],
        plot_bgcolor=tc["bg_color"],
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", color=tc["text_color"], size=12),
        margin=dict(l=10, r=20, t=45, b=25),
        showlegend=False,
        hoverlabel=dict(
            bgcolor=tc["tooltip_bg"],
            font_size=12,
            font_family="Segoe UI, Inter, Arial, sans-serif",
            font_color=tc["tooltip_text"],
            bordercolor=POWERBI_COLORS["primary_orange"],
        ),
    )


def create_highest_gross_margin_chart(df_products: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Visual 1: Clustered Horizontal Bar Chart
    Title: 'Which product deliver the highest gross margin?'
    Sorted numerically descending by Gross Margin % (Phase 11).
    Colors: Gradient #F5C4AF to #EB895F.
    """
    if len(df_products) == 0:
        fig = go.Figure()
        fig.update_layout(**get_base_layout("Which product deliver the highest gross margin?", theme))
        fig.add_annotation(
            text="No data for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=THEME_CONFIG[theme]["muted_text"])
        )
        return fig

    # Plotly horizontal bar draws bottom-up, so reverse to have top margin at top
    plot_df = df_products.iloc[::-1].copy()
    tc = THEME_CONFIG.get(theme, THEME_CONFIG["dark"])

    text_labels = [f"{v:.2f}%" for v in plot_df["Gross_Margin_%"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=plot_df["Product Name"],
            x=plot_df["Gross_Margin_%"],
            orientation="h",
            text=text_labels,
            textposition="outside",
            textfont=dict(size=11, color=tc["text_color"], family="Segoe UI"),
            marker=dict(
                color=plot_df["Gross_Margin_%"],
                colorscale=[[0, POWERBI_COLORS["gradient_min"]], [1, POWERBI_COLORS["gradient_max"]]],
                line=dict(color="rgba(0,0,0,0.05)", width=1),
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                + "Gross Margin: <b>%{x:.2f}%</b><br>"
                + "Total Sales: $%{customdata[0]:,.2f}<br>"
                + "Gross Profit: $%{customdata[1]:,.2f}<br>"
                + "Total Units: %{customdata[2]:,}<br>"
                + "<extra></extra>"
            ),
            customdata=plot_df[["Total_Sales", "Total_Gross_Profit", "Total_Units"]].values,
        )
    )

    max_margin = plot_df["Gross_Margin_%"].max() if len(plot_df) > 0 else 100
    x_range_max = max(max_margin * 1.18, 100)

    layout = get_base_layout("Which product deliver the highest gross margin?", theme)
    layout.update(
        xaxis=dict(
            title="",
            range=[0, x_range_max],
            showgrid=True,
            gridcolor=tc["grid_color"],
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(size=11, color=tc["text_color"], family="Segoe UI"),
        ),
        height=340,
        margin=dict(l=10, r=40, t=45, b=15),
    )
    fig.update_layout(**layout)
    return fig


def create_profitability_scatter_chart(df_scatter: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Visual 2: Scatter Chart
    Title: 'Are high-sales products actually profitable?'
    X: Total Sales
    Y: Total Gross Profit
    Bubble Size: Total Units
    Series / Color: Division
    """
    if len(df_scatter) == 0:
        fig = go.Figure()
        fig.update_layout(**get_base_layout("Are high-sales products actually profitable?", theme))
        fig.add_annotation(
            text="No data for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=THEME_CONFIG[theme]["muted_text"])
        )
        return fig

    tc = THEME_CONFIG.get(theme, THEME_CONFIG["dark"])
    division_colors = {
        "Chocolate": POWERBI_COLORS["division_chocolate"],
        "Other": POWERBI_COLORS["division_other"],
        "Sugar": POWERBI_COLORS["division_sugar"],
    }

    fig = go.Figure()
    max_units = df_scatter["Units"].max() if len(df_scatter) > 0 and df_scatter["Units"].max() > 0 else 1

    for division in ["Chocolate", "Other", "Sugar"]:
        div_data = df_scatter[df_scatter["Division"] == division]
        if len(div_data) == 0:
            continue

        # Scale bubble sizes nicely between 14 and 38
        bubble_sizes = [
            max(14, min(38, int(np.sqrt(u / max_units) * 36) + 12))
            for u in div_data["Units"]
        ]

        fig.add_trace(
            go.Scatter(
                x=div_data["Sales"],
                y=div_data["Gross_Profit"],
                mode="markers",
                name=division,
                marker=dict(
                    size=bubble_sizes,
                    color=division_colors.get(division, POWERBI_COLORS["primary_orange"]),
                    opacity=0.82,
                    line=dict(color="#FFFFFF", width=1.5),
                ),
                text=div_data["Product Name"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    + "Division: " + division + "<br>"
                    + "Total Sales: $%{x:,.2f}<br>"
                    + "Gross Profit: $%{y:,.2f}<br>"
                    + "Gross Margin: %{customdata[0]:.2f}%<br>"
                    + "Total Units: %{customdata[1]:,}<br>"
                    + "<extra></extra>"
                ),
                customdata=div_data[["Gross_Margin_%", "Units"]].values,
            )
        )

    layout = get_base_layout("Are high-sales products actually profitable?", theme)
    layout.update(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=tc["text_color"]),
        ),
        xaxis=dict(
            title=dict(text="Total Sales", font=dict(size=11, color=tc["muted_text"])),
            tickprefix="$",
            tickformat=",.0s",
            showgrid=True,
            gridcolor=tc["grid_color"],
            zeroline=False,
            tickfont=dict(color=tc["text_color"]),
        ),
        yaxis=dict(
            title=dict(text="Total Gross Profit", font=dict(size=11, color=tc["muted_text"])),
            tickprefix="$",
            tickformat=",.0s",
            showgrid=True,
            gridcolor=tc["grid_color"],
            zeroline=False,
            tickfont=dict(color=tc["text_color"]),
        ),
        height=340,
        margin=dict(l=15, r=20, t=55, b=20),
    )
    fig.update_layout(**layout)
    return fig


def create_division_profitability_chart(df_divisions: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Visual 3: Clustered Column Chart
    Title: 'How does profitability vary across product divisions?'
    Category: Division
    Value: Total Gross Profit
    Sorted descending by Total Gross Profit.
    """
    if len(df_divisions) == 0:
        fig = go.Figure()
        fig.update_layout(**get_base_layout("How does profitability vary across product divisions?", theme))
        fig.add_annotation(
            text="No data for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=THEME_CONFIG[theme]["muted_text"])
        )
        return fig

    tc = THEME_CONFIG.get(theme, THEME_CONFIG["dark"])

    # Format data labels
    text_labels = [f"${v/1000:,.1f}K" if v >= 1000 else f"${v:,.0f}" for v in df_divisions["Total_Gross_Profit"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_divisions["Division"],
            y=df_divisions["Total_Gross_Profit"],
            text=text_labels,
            textposition="outside",
            textfont=dict(size=11, color=tc["text_color"], family="Segoe UI"),
            marker=dict(
                color=df_divisions["Total_Gross_Profit"],
                colorscale=[[0, POWERBI_COLORS["gradient_min"]], [1, POWERBI_COLORS["gradient_max"]]],
                line=dict(color="rgba(0,0,0,0.05)", width=1),
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                + "Gross Profit: $%{y:,.2f}<br>"
                + "Total Sales: $%{customdata[0]:,.2f}<br>"
                + "Total Cost: $%{customdata[1]:,.2f}<br>"
                + "Gross Margin: %{customdata[2]:.2f}%<br>"
                + "<extra></extra>"
            ),
            customdata=df_divisions[["Total_Sales", "Total_Cost", "Gross_Margin_%"]].values,
        )
    )

    max_profit = df_divisions["Total_Gross_Profit"].max() if len(df_divisions) > 0 else 100
    y_range_max = max_profit * 1.25

    layout = get_base_layout("How does profitability vary across product divisions?", theme)
    layout.update(
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(size=12, color=tc["text_color"], family="Segoe UI"),
        ),
        yaxis=dict(
            title="",
            range=[0, y_range_max],
            tickprefix="$",
            tickformat=",.0s",
            showgrid=True,
            gridcolor=tc["grid_color"],
            zeroline=False,
            tickfont=dict(color=tc["text_color"]),
        ),
        height=340,
        margin=dict(l=15, r=20, t=45, b=20),
    )
    fig.update_layout(**layout)
    return fig
