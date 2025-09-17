import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("Daily Evaluation Summary App")

uploaded_files = st.file_uploader(
    "Upload one or more CSV/XLSX files", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    combined_summary = []
    combined_sessions = []

    for uploaded_file in uploaded_files:
        # --- Handle both CSV and Excel ---
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # --- Remove unnamed columns safely ---
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]

        # --- Categories ---
        categories = {
            "PROGRAM MANAGEMENT": [],
            "TRAINING VENUE": [],
            "FOOD/MEALS": [],
            "ACCOMMODATION": [],
            "SESSION": []
        }

        for col in df.columns:
            col_str = str(col)  # ensure it's a string
            if "PROGRAM MANAGEMENT" in col_str:
                categories["PROGRAM MANAGEMENT"].append(col)
            elif "TRAINING VENUE" in col_str:
                categories["TRAINING VENUE"].append(col)
            elif "FOOD/MEALS" in col_str:
                categories["FOOD/MEALS"].append(col)
            elif "ACCOMMODATION" in col_str:
                categories["ACCOMMODATION"].append(col)
            elif any(key in col_st_
