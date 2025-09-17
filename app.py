import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("Daily Evaluation Summary App")

uploaded_files = st.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    combined_summary = []
    combined_sessions = []

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        categories = {
            "PROGRAM MANAGEMENT": [],
            "TRAINING VENUE": [],
            "FOOD/MEALS": [],
            "ACCOMODATION": [],
            "SESSION": []
        }

        for col in df.columns:
            if "PROGRAM MANAGEMENT" in col:
                categories["PROGRAM MANAGEMENT"].append(col)
            elif "TRAINING VENUE" in col:
                categories["TRAINING VENUE"].append(col)
            elif "FOOD/MEALS" in col:
                categories["FOOD/MEALS"].append(col)
            elif "ACCOMODATION" in col:
                categories["ACCOMODATION"].append(col)
            elif "-&gt;(PD Program Objectives)" in col or "-&gt;(LR Materials)" in col or "-&gt;(Content Relevance)" in col or "-&gt;(RP/Subject Matter Expert Knowledge)" in col:
                categories["SESSION"].append(col)

        category_averages = {}
        for cat, cols in categories.items():
            if cols:
                category_averages[cat] = df[cols].mean().mean()

        # Compute overall average of all indicators in the file
        all_indicator_cols = sum(categories.values(), [])  # Flatten all category columns
        overall_average = df[all_indicator_cols].mean().mean()

        summary_df = pd.DataFrame.from_dict(category_averages, orient='index', columns=['Average Score'])
        summary_df['File'] = uploaded_file.name

        # Add overall average to summary_df
        overall_df = pd.DataFrame({
            'Average Score': [overall_average],
            'File': [uploaded_file.name]
        }, index=['OVERALL AVERAGE'])

        summary_df = pd.concat([summary_df, overall_df])
        combined_summary.append(summary_df)

        session_cols = categories["SESSION"]
        session_groups = {}
        for col in session_cols:
            match = re.search(r"(DAY \d+-LM\d+)", col)
            if match:
                session_key = match.group(1)
                session_groups.setdefault(session_key, []).append(col)

        session_averages = {}
        for session, cols in session_groups.items():
            session_averages[session] = df[cols].mean().mean()

        session_df = pd.DataFrame.from_dict(session_averages, orient='index', columns=['Average Score'])
        session_df['File'] = uploaded_file.name
        combined_sessions.append(session_df)

    final_summary = pd.concat(combined_summary)
    final_sessions = pd.concat(combined_sessions)

    st.subheader("Summary Table of Category Averages Across Files")
    st.dataframe(final_summary)

    fig1 = px.bar(final_summary, x=final_summary.index, y='Average Score', color='File', title='Average Scores by Category Across Files')
    st.plotly_chart(fig1)

    st.subheader("Session-wise Averages Across Files")
    st.dataframe(final_sessions)

    fig2 = px.bar(final_sessions, x=final_sessions.index, y='Average Score', color='File', title='Average Scores by Session Across Files')
    st.plotly_chart(fig2)
