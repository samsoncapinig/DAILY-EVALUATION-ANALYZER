import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("Daily Evaluation Summary App")

uploaded_files = st.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    indicators = ["PROGRAM MANAGEMENT", "TRAINING VENUE", "FOOD/MEALS", "ACCOMMODATION", "SESSION"]
    days = ["DAY 1", "DAY 2", "DAY 3", "DAY 4", "DAY 5"]

    indicator_day_scores = {indicator: {day: [] for day in days} for indicator in indicators}
    combined_summary = []
    combined_sessions = []

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Categorize columns for category and session averages
        categories = {indicator: [] for indicator in indicators}
        for col in df.columns:
            for indicator in indicators:
                if indicator == "SESSION":
                    if any(key in col for key in ["PD Program Objectives", "LR Materials", "Content Relevance", "RP/Subject Matter Expert Knowledge"]):
                        categories[indicator].append(col)
                        match = re.search(r"(DAY \d+)", col)
                        if match:
                            day = match.group(1)
                            if day in days:
                                indicator_day_scores[indicator][day].append(df[col])
                elif indicator in col:
                    categories[indicator].append(col)
                    match = re.search(r"(DAY \d+)", col)
                    if match:
                        day = match.group(1)
                        if day in days:
                            indicator_day_scores[indicator][day].append(df[col])

        # Category averages per file
        category_averages = {}
        for cat, cols in categories.items():
            if cols:
                category_averages[cat] = df[cols].mean().mean()

        # Overall average of all indicators
        all_indicator_cols = sum(categories.values(), [])
        overall_average = df[all_indicator_cols].mean().mean()

        summary_df = pd.DataFrame.from_dict(category_averages, orient='index', columns=['Average Score'])
        summary_df['File'] = uploaded_file.name

        overall_df = pd.DataFrame({
            'Average Score': [overall_average],
            'File': [uploaded_file.name]
        }, index=['OVERALL AVERAGE'])

        summary_df = pd.concat([summary_df, overall_df])
        combined_summary.append(summary_df)

        # Session-wise averages
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

    # Final summary tables
    final_summary = pd.concat(combined_summary)
    final_sessions = pd.concat(combined_sessions)

    # Display category averages
    st.subheader("Summary Table of Category Averages Across Files")
    st.dataframe(final_summary)

    fig1 = px.bar(final_summary, x=final_summary.index, y='Average Score', color='File', title='Average Scores by Category Across Files')
    st.plotly_chart(fig1)

    # Display session averages
    st.subheader("Session-wise Averages Across Files")
    st.dataframe(final_sessions)

    fig2 = px.bar(final_sessions, x=final_sessions.index, y='Average Score', color='File', title='Average Scores by Session Across Files')
    st.plotly_chart(fig2)

    # Daily indicator-wise summary table
    summary_data = []
    for indicator in indicators:
        row = [indicator]
        day_averages = []
        for day in days:
            if indicator_day_scores[indicator][day]:
                day_df = pd.concat(indicator_day_scores[indicator][day], axis=1)
                avg_score = day_df.mean().mean()
            else:
                avg_score = None
            row.append(avg_score)
            day_averages.append(avg_score)
        valid_scores = [score for score in day_averages if score is not None]
        overall_avg = sum(valid_scores) / len(valid_scores) if valid_scores else None
        row.append(overall_avg)
        summary_data.append(row)

    columns = ["Indicator"] + days + ["Average"]
    indicator_summary_df = pd.DataFrame(summary_data, columns=columns)

    # Final row: average per day and overall average
    final_row = ["OVERALL AVERAGE"]
    for day in days:
        day_scores = indicator_summary_df[day].dropna()
        final_row.append(day_scores.mean() if not day_scores.empty else None)
    overall_scores = indicator_summary_df["Average"].dropna()
    final_row.append(overall_scores.mean() if not overall_scores.empty else None)

    indicator_summary_df.loc[len(indicator_summary_df.index)] = final_row

    st.subheader("Daily Indicator-wise Summary Table")
    st.dataframe(indicator_summary_df)
