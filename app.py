import streamlit as st
import pandas as pd
import re

st.title("Daily Evaluation Summary App")

uploaded_files = st.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    indicators = ["PROGRAM MANAGEMENT", "TRAINING VENUE", "FOOD/MEALS", "ACCOMODATION", "SESSION"]
    days = ["DAY 1", "DAY 2", "DAY 3", "DAY 4", "DAY 5"]

    indicator_day_scores = {indicator: {day: [] for day in days} for indicator in indicators}

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        for col in df.columns:
            for indicator in indicators:
                if indicator == "SESSION":
                    if any(key in col for key in ["PD Program Objectives", "LR Materials", "Content Relevance", "RP/Subject Matter Expert Knowledge"]):
                        match = re.search(r"(DAY \\d+)", col)
                        if match:
                            day = match.group(1)
                            if day in days:
                                indicator_day_scores[indicator][day].append(df[col])
                elif indicator in col:
                    match = re.search(r"(DAY \\d+)", col)
                    if match:
                        day = match.group(1)
                        if day in days:
                            indicator_day_scores[indicator][day].append(df[col])

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

    columns = ["CRITERIA"] + days + ["GENERAL AVERAGE"]
    summary_df = pd.DataFrame(summary_data, columns=columns)

    # Final row: average per day and overall average
    final_row = ["AVERAGE"]
    for day in days:
        day_scores = summary_df[day].dropna()
        final_row.append(day_scores.mean() if not day_scores.empty else None)
    overall_scores = summary_df["GENERAL AVERAGE"].dropna()
    final_row.append(overall_scores.mean() if not overall_scores.empty else None)

    summary_df.loc[len(summary_df.index)] = final_row

    st.subheader("Evaluation Summary Table")
    st.dataframe(summary_df)
