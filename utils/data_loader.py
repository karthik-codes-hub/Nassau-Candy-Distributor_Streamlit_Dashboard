"""
Data loader module for Nassau Candy Distributor Profitability Dashboard.
Handles cached dataset loading, cleaning, validation, and type conversions.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st

CANDIDATE_DATA_PATHS = [
    os.path.join("data", "Nassau_Candy_Distributor.csv"),
    "Nassau_Candy_Distributor.csv",
    "Nassau_Candy_Distributor_Properly_Cleaned(2)(2)(1).csv",
    os.path.join("data", "Nassau_Candy_Distributor_Properly_Cleaned(2)(2)(1).csv"),
    os.path.join("data", "Nassau_Candy_Distributor_Properly_Cleaned(2).xlsx"),
    "Nassau_Candy_Distributor_Properly_Cleaned(2).xlsx",
]

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


@st.cache_data(show_spinner=False)
def load_data():
    """
    Finds and loads the Nassau Candy Distributor dataset from CSV or Excel.
    Performs comprehensive data cleaning and type validation.
    """
    df = None
    loaded_source = None

    for path in CANDIDATE_DATA_PATHS:
        if os.path.exists(path):
            try:
                if path.endswith(".csv"):
                    df = pd.read_csv(path)
                elif path.endswith(".xlsx"):
                    df = pd.read_excel(path)
                loaded_source = path
                break
            except Exception as e:
                continue

    if df is None:
        raise FileNotFoundError(
            f"Could not locate Nassau Candy Distributor data file. Looked in: {CANDIDATE_DATA_PATHS}"
        )

    # Clean and validate DataFrame
    df = clean_data(df)
    return df, loaded_source


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and cleans columns, ensuring proper data types,
    stripping whitespace from string columns, and standardizing dates.
    """
    df = df.copy()

    # Strip column names
    df.columns = [col.strip() for col in df.columns]

    # Validate and clean Region strictly from dataset
    if "Region" in df.columns:
        df["Region"] = df["Region"].astype(str).str.strip()

    # Validate categorical columns
    text_cols = ["Division", "Product Name", "City", "State/Province", "Country/Region", "Ship Mode", "Customer ID"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Ensure numeric columns have correct types
    numeric_cols = ["Sales", "Units", "Cost", "Gross Profit", "Gross Margin %", "Profit per Unit", "Shipping Days", "Order Year", "Order Month"]
    for col in numeric_cols:
        if col in df.columns:
            # Handle potential string currency/percent artifacts if present
            if df[col].dtype == object:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.replace("%", "", regex=False)
                    .str.strip()
                )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Ensure Order Year is integer
    if "Order Year" in df.columns:
        df["Order Year"] = df["Order Year"].astype(int)

    # Ensure Units is integer
    if "Units" in df.columns:
        df["Units"] = df["Units"].astype(int)

    # Standardize Order Month Name
    if "Order Month Name" in df.columns:
        df["Order Month Name"] = df["Order Month Name"].astype(str).str.strip().str.capitalize()
    elif "Order Month" in df.columns:
        month_map = {i + 1: m for i, m in enumerate(MONTH_ORDER)}
        df["Order Month Name"] = df["Order Month"].map(month_map)

    # Date conversion
    date_cols = ["Order Date", "Ship Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Ensure Gross Profit matches Sales - Cost if missing
    if "Gross Profit" not in df.columns and "Sales" in df.columns and "Cost" in df.columns:
        df["Gross Profit"] = df["Sales"] - df["Cost"]

    # Ensure Gross Margin % matches (Gross Profit / Sales) * 100
    if "Gross Margin %" not in df.columns and "Sales" in df.columns and "Gross Profit" in df.columns:
        df["Gross Margin %"] = np.where(df["Sales"] != 0, (df["Gross Profit"] / df["Sales"]) * 100.0, 0.0)

    return df
