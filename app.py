import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from datetime import datetime

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Waffarha Marketing Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
@st.cache_resource
def get_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        database=st.secrets["DB_NAME"]
    )
    return create_engine(url)

engine = get_engine()

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
@st.cache_data
def load_campaigns():
    query = "SELECT * FROM marketing_gold.gold_campaign_agg"
    return pd.read_sql(query, engine)

@st.cache_data
def load_channels():
    query = "SELECT * FROM marketing_gold.gold_channel_agg"
    return pd.read_sql(query, engine)

@st.cache_data
def load_segments():
    query = "SELECT * FROM marketing_gold.gold_segment_agg"
    return pd.read_sql(query, engine)

campaign_df = load_campaigns()
channel_df = load_channels()
segment_df = load_segments()

# --------------------------------------------------
# BUSINESS METRICS
# --------------------------------------------------
def overall_metrics(df):
    return {
        "avg_conversion": df["conversion_rate"].mean(),
        "avg_cac": df["cac"].mean(),
        "avg_roi": df["roi_percent"].mean(),
        "total_clicks": df["clicks"].sum()
    }

metrics = overall_metrics(campaign_df)

# --------------------------------------------------
# RECOMMENDATION ENGINE
# --------------------------------------------------
def campaign_alerts(df):
    alerts = []

    low_conv = df[df["conversion_rate"] < df["conversion_rate"].quantile(0.25)]
    low_roi = df[df["roi_percent"] < 0]

    for _, row in low_conv.iterrows():
        severity = "High" if row["roi_percent"] < 0 else "Medium"
        alerts.append({
            "campaign_id": row["campaign_id"],
            "issue": "Low Conversion Rate",
            "severity": severity,
            "recommendation": "Reallocate budget or test new creative/channel mix"
        })

    for _, row in low_roi.iterrows():
        alerts.append({
            "campaign_id": row["campaign_id"],
            "issue": "Negative ROI",
            "severity": "Critical",
            "recommendation": "Pause campaign immediately and investigate CAC drivers"
        })

    return pd.DataFrame(alerts)

alerts_df = campaign_alerts(campaign_df)

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Executive Summary",
        "Campaign Deep Dive",
        "Segment Analysis",
        "Channel Performance",
        "Trends & Recommendations"
    ]
)

# --------------------------------------------------
# PAGE 1: EXECUTIVE SUMMARY
# --------------------------------------------------
if page == "Executive Summary":
    st.title("Executive Summary – Marketing Performance")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Conversion Rate", f"{metrics['avg_conversion']:.2%}")
    col2.metric("Avg CAC", f"${metrics['avg_cac']:.2f}")
    col3.metric("Avg ROI", f"{metrics['avg_roi']:.1f}%")
    col4.metric("Total Clicks", f"{metrics['total_clicks']:,}")

    st.subheader("Which Campaigns Are Driving Results?")
    fig = px.bar(
        campaign_df.sort_values("conversion_rate"),
        x="conversion_rate",
        y="campaign_type",
        orientation="h",
        color="roi_percent",
        title="Conversion Rate by Campaign Type"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚨 Executive Alerts")
    st.dataframe(alerts_df, use_container_width=True)

# --------------------------------------------------
# PAGE 2: CAMPAIGN DEEP DIVE
# --------------------------------------------------
elif page == "Campaign Deep Dive":
    st.title("Campaign Deep Dive")

    selected_campaign = st.selectbox(
        "Select Campaign",
        campaign_df["campaign_id"].unique()
    )

    df = campaign_df[campaign_df["campaign_id"] == selected_campaign]

    st.metric("Conversion Rate", f"{df['conversion_rate'].iloc[0]:.2%}")
    st.metric("ROI", f"{df['roi_percent'].iloc[0]:.1f}%")
    st.metric("CAC", f"${df['cac'].iloc[0]:.2f}")

    st.dataframe(df)

# --------------------------------------------------
# PAGE 3: SEGMENT ANALYSIS
# --------------------------------------------------
elif page == "Segment Analysis":
    st.title("Customer Segment Performance")

    fig = px.scatter(
        segment_df,
        x="avg_cac",
        y="avg_conversion_rate",
        size="campaigns",
        color="avg_roi",
        hover_name="customer_segment",
        title="Segment Value Map (Efficiency vs Performance)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(segment_df)

# --------------------------------------------------
# PAGE 4: CHANNEL PERFORMANCE
# --------------------------------------------------
elif page == "Channel Performance":
    st.title("Channel Efficiency & ROI")

    fig = px.bar(
        channel_df,
        x="channel_used_clean",
        y="avg_roi",
        title="Average ROI by Channel"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        channel_df,
        x="channel_used_clean",
        y="avg_cac",
        title="Average CAC by Channel"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# PAGE 5: TRENDS & RECOMMENDATIONS
# --------------------------------------------------
elif page == "Trends & Recommendations":
    st.title("Strategic Insights & Recommendations")

    st.subheader("📌 Key Recommendations")
    st.markdown("""
    **1. Pause underperforming campaigns with negative ROI immediately**  
    **2. Shift budget toward high-ROI, low-CAC channels**  
    **3. Double down on high-conversion customer segments**  
    **4. Run creative and targeting experiments on medium-severity campaigns**
    """)

    st.subheader("🚦 Campaign Risk Matrix")
    st.dataframe(alerts_df)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
