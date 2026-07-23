import streamlit as st
import sqlite3
import pandas as pd

st.title("Prescription Renewal Oversight Dashboard")

conn = sqlite3.connect("audit.db")

df = pd.read_sql_query(
    "SELECT * FROM decisions",
    conn,
)

df["timestamp"] = pd.to_datetime(df["timestamp"])

###################################################
# Status filter
###################################################

status_filter = st.multiselect(
    "Filter by status",
    df["status"].unique(),
    default=df["status"].unique(),
)

###################################################
# Date filter
###################################################

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.date_input(
    "Date range",
    value=(min_date, max_date),
)

filtered = df[df["status"].isin(status_filter)]

if len(date_range) == 2:
    start, end = date_range

    filtered = filtered[
        filtered["timestamp"].dt.date.between(
            start,
            end,
        )
    ]

###################################################
# Metrics
###################################################

st.metric(
    "Total requests",
    len(filtered),
)

flagged = filtered[filtered["status"] != "processed"]

st.metric(
    "Flagged requests",
    len(flagged),
)

###################################################
# Visible alert
###################################################

THRESHOLD = 5

if len(flagged) > THRESHOLD:
    st.warning(
        f"{len(flagged)} flagged requests this period - review recommended."
    )

###################################################
# Charts
###################################################

st.bar_chart(
    filtered["status"].value_counts()
)

###################################################
# Stretch goal
###################################################

st.subheader("Flagged Requests")

st.dataframe(
    flagged[
        [
            "patient_id",
            "status",
            "reason",
            "timestamp",
        ]
    ].sort_values(
        "timestamp",
        ascending=False,
    )
)