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
            elif any(key in col_str for key in [
                "PD Program Objectives", 
                "LR Materials", 
                "Content Relevance", 
                "RP/Subject Matter Expert Knowledge"
            ]):
                categories["SESSION"].append(col)

        # --- Category Averages ---
        category_averages = {}
        for cat, cols in categories.items():
            if cols:
                category_averages[cat] = df[cols].mean().mean()

        summary_df = pd.DataFrame.from_dict(
            category_averages, 
            orient='index', 
            columns=['Average Score']
        )
        summary_df['File'] = uploaded_file.name
        combined_summary.append(summary_df)

        # --- Session Averages ---
        session_cols = categories["SESSION"]
        session_groups = {}
        for col in session_cols:
    match = re.search(r"DAY\s*\d+\s*[-–]?\s*LM\s*\d+", str(col), re.IGNORECASE)
    if match:
        session_key = match.group(0).upper()
        session_groups.setdefault(session_key, []).append(col)
    else:
        st.write("⚠️ Skipped column (no session match):", col)

        session_averages = {}
        for session, cols in session_groups.items():
            session_averages[session] = df[cols].mean().mean()

        if session_averages:
            session_df = pd.DataFrame.from_dict(
                session_averages, 
                orient='index', 
                columns=['Average Score']
            )
            session_df['File'] = uploaded_file.name
            combined_sessions.append(session_df)

    # --- Combine all summaries ---
    if combined_summary:
        final_summary = pd.concat(combined_summary)
        final_summary_reset = final_summary.reset_index().rename(columns={'index':'Category'})

        st.subheader("Summary Table of Category Averages Across Files")
        st.dataframe(final_summary_reset)

        fig1 = px.bar(
            final_summary_reset, 
            x='Category', 
            y='Average Score', 
            color='File', 
            title='Average Scores by Category Across Files',
            barmode='group'
        )
        st.plotly_chart(fig1)

    if combined_sessions:
        final_sessions = pd.concat(combined_sessions)
        final_sessions_reset = final_sessions.reset_index().rename(columns={'index':'Session'})

        st.subheader("Session-wise Averages Across Files")
        st.dataframe(final_sessions_reset)

        fig2 = px.bar(
            final_sessions_reset, 
            x='Session', 
            y='Average Score', 
            color='File', 
            title='Average Scores by Session Across Files',
            barmode='group'
        )
        st.plotly_chart(fig2)
