import streamlit as st
# from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

st.set_page_config(page_title="Trash Tracker", layout="wide", page_icon="♻️")

# Load data from JSON
@st.cache_data(ttl=2)
def load_data():
    with open('data.json') as f:
        raw_data = json.load(f)
    return pd.DataFrame(raw_data)

df = load_data()
df['timestamp'] = pd.to_datetime(df['timestamp'])

with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("HALO.png", width=80)
    with col2:
        st.markdown("## HALO")

# # Auto-refresh every 2 seconds
# st_autorefresh(interval= 2 * 1000, key="auto_refresh")

# Layout
st.markdown("## ♻️ Trash Tracker")
st.caption("Real-time waste classification insights")

# Helper functions
def get_latest_trash(limit=5):
    return df.sort_values("timestamp", ascending=False).head(limit)

def get_daily_trash_summary():
    today = datetime.now().strftime('%Y-%m-%d')
    daily = df[df['timestamp'].dt.strftime('%Y-%m-%d') == today]
    return daily['class'].value_counts().reset_index().rename(columns={"index": "_id", "class": "count"})

def get_trash_classification():
    df_count = df['class'].value_counts().reset_index()
    df_count.columns = ["_id", "total_count"]
    return df_count


# Row 1: Latest Trash + Daily Summary
col1, col2 = st.columns(2)

with col1:
    st.subheader("Latest Trash")
    latest = get_latest_trash(limit=5)
    if not latest.empty:
        for _, item in latest.iterrows():
            time_str = item['timestamp'].strftime('%I:%M %p')
            st.markdown(f"""
            <div style="padding: 10px; border-bottom: 1px solid #3C4C3C;">
                <strong style="color: #FFF;">{item['class']}</strong><br>
                <small style="color: #FFF;">{time_str}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trash data available.")

with col2:
    st.subheader("Daily Trash Summary")
    today = datetime.now().strftime('%Y-%m-%d')
    daily_df = df[df['timestamp'].dt.strftime('%Y-%m-%d') == today]['class'].value_counts().reset_index()
    daily_df.columns = ["_id", "count"]
    if not daily_df.empty:
        fig = px.bar(
            daily_df, 
            x="_id", 
            y="count", 
            labels={"_id": "Trash Type", "count": "Item Count"},
            color_discrete_sequence=["#81C784"] 
        )
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="",
            yaxis_title="Count",
            showlegend=False,
            plot_bgcolor="#1B1F1B",
            paper_bgcolor="#1B1F1B",
            font_color="#E8F5E9"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for today.")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Trash Classification")
    class_df = get_trash_classification()
    if not class_df.empty:
        fig = px.pie(
            class_df, 
            names="_id", 
            values="total_count", 
            hole=0.5, 
            color_discrete_sequence=px.colors.sequential.Greens
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1B1F1B",
            font_color="#E8F5E9"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No classification data.")


with col4:
    st.subheader("Trash Trends")
    time_range = st.radio("Select Time Range:", ["Daily", "Weekly", "Monthly"], horizontal=True)

    def get_time_based_trash_summary(time_range):
        if time_range == "Daily":
            df['group_date'] = df['timestamp'].dt.strftime("%Y-%m-%d")
        elif time_range == "Weekly":
            df['group_date'] = df['timestamp'].dt.strftime("%Y-%U")
        elif time_range == "Monthly":
            df['group_date'] = df['timestamp'].dt.strftime("%Y-%m")
        summary = df.groupby('group_date').size().reset_index(name='count')
        return summary

    time_based_df = get_time_based_trash_summary(time_range)

    if not time_based_df.empty:
        # Try parsing group_date to datetime for line chart
        time_based_df['group_date'] = pd.to_datetime(time_based_df['group_date'], errors='coerce')
        time_based_df = time_based_df.dropna().sort_values('group_date')

        fig = px.line(time_based_df, x="group_date", y="count", labels={"group_date": "Date", "count": "Item Count"})
        fig.update_traces(line=dict(color="#81C784"))
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Count",
            showlegend=False,
            plot_bgcolor="#1B1F1B",
            paper_bgcolor="#1B1F1B",
            font_color="#E8F5E9"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for the selected {time_range.lower()} range.")
