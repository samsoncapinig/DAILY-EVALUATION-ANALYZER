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
    combined_categories = {
        "PROGRAM MANAGEMENT": [],
        "TRAINING VENUE": [],
        "FOOD/MEALS": [],
        "ACCOMMODATION": []
    }
    combined_sessions = []

    for uploaded_file in uploaded_files:
        # Handle CSV or Excel
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Define categories
        categories = {
            "PROGRAM MANAGEMENT": [],
            "TRAINING VENUE": [],
            "FOOD/MEALS": [],
            "ACCOMMODATION": [],
            "SESSION": []
        }

        for col in df.columns:
            col_str = str(col).upper()

            if "PROGRAM MANAGEMENT" in col_str:
                categories["PROGRAM MANAGEMENT"].append(col)
            elif "TRAINING VENUE" in col_str:
                categories["TRAINING VENUE"].append(col)
            elif "FOOD/MEALS" in col_str:
                categories["FOOD/MEALS"].append(col)
            elif "ACCOMMODATION" in col_str:
                categories["ACCOMMODATION"].append(col)
            elif any(key in col_str for key in [
                "PROGRAM OBJECTIVES", "LR MATERIALS",
                "CONTENT RELEVANCE", "RP/SUBJECT MATTER EXPERT KNOWLEDGE"
            ]):
                categories["SESSION"].append(col)

        # Process non-session categories
        for cat in ["PROGRAM MANAGEMENT", "TRAINING VENUE", "FOOD/MEALS", "ACCOMMODATION"]:
            cols = categories[cat]
            if cols:
                avg_score = df[cols].mean().mean()
                summary_df = pd.DataFrame({
                    "Category": [cat],
                    "Average Score": [avg_score],
                    "File": [uploaded_file.name]
                })
                combined_categories[cat].append(summary_df)

        # Process session columns
        session_cols = categories["SESSION"]
        session_groups = {}
        for col in session_cols:
            col_str = str(col)

            # Match Qxx + DAY + LM
            match = re.search(r"Q\d+[_-]?\s*DAY\s*\d+\s*[-–]?\s*LM\s*\d+", col_str, re.IGNORECASE)

            if match:
                session_key = match.group(0).upper().replace(" ", "")
                session_groups.setdefault(session_key, []).append(col)
            else:
                # fallback: only DAY + LM
                match_day_lm = re.search(r"DAY\s*\d+\s*[-–]?\s*LM\s*\d+", col_str, re.IGNORECASE)
                if match_day_lm:
                    session_key = match_day_lm.group(0).upper().replace(" ", "")
                    session_groups.setdefault(session_key, []).append(col)
                else:
                    st.write("⚠️ Skipped column (no session match):", col)

        session_averages = {}
        for session, cols in session_groups.items():
            session_averages[session] = df[cols].mean().mean()

        if session_averages:
            session_df = pd.DataFrame.from_dict(session_averages, orient='index', columns=['Average Score'])
            session_df['File'] = uploaded_file.name
            combined_sessions.append(session_df)

    # Display category tables separately
    for cat, dfs in combined_categories.items():
        if dfs:
            final_cat_df = pd.concat(dfs)
            st.subheader(f"{cat} - Averages Across Files")
            st.dataframe(final_cat_df)

            fig = px.bar(
                final_cat_df,
                x="Category",
                y="Average Score",
                color="File",
                title=f"Average Scores - {cat}"
            )
            st.plotly_chart(fig)

    # Display sessions
    if combined_sessions:
        final_sessions = pd.concat(combined_sessions)
        st.subheader("Session-wise Averages Across Files")
        st.dataframe(final_sessions)

        fig2 = px.bar(
            final_sessions,
            x=final_sessions.index,
            y="Average Score",
            color="File",
            title="Average Scores by Session Across Files"
        )
        st.plotly_chart(fig2)
