import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Workora Business Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Load datasets
# -----------------------------
traffic = pd.read_csv("web_traffic.csv")
churn = pd.read_csv("customer_churn.csv")
regional = pd.read_csv("regional_market.csv")
ab_test = pd.read_csv("checkout_ab_test.csv")

traffic["Date"] = pd.to_datetime(traffic["Date"])
ab_test["Timestamp"] = pd.to_datetime(ab_test["Timestamp"])

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Dashboard Filters")

# Date range
min_date = min(
    traffic["Date"].min().date(),
    ab_test["Timestamp"].min().date()
)

max_date = max(
    traffic["Date"].max().date(),
    ab_test["Timestamp"].max().date()
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date)
)

# Region filter
regions = sorted(
    set(traffic["Region"].dropna().unique())
    | set(regional["State"].dropna().unique())
)

selected_region = st.sidebar.selectbox(
    "Region",
    ["All"] + regions
)

# Category filter
categories = sorted(
    regional["PopulationSegment"].dropna().unique()
)

selected_category = st.sidebar.selectbox(
    "Category",
    ["All"] + categories
)

# -----------------------------
# Apply filters
# -----------------------------
if len(date_range) == 2:
    start_date, end_date = date_range

    traffic_filtered = traffic[
        (traffic["Date"].dt.date >= start_date)
        & (traffic["Date"].dt.date <= end_date)
    ]

    ab_filtered = ab_test[
        (ab_test["Timestamp"].dt.date >= start_date)
        & (ab_test["Timestamp"].dt.date <= end_date)
    ]
else:
    traffic_filtered = traffic.copy()
    ab_filtered = ab_test.copy()

if selected_region != "All":
    traffic_filtered = traffic_filtered[
        traffic_filtered["Region"] == selected_region
    ]

    regional_filtered = regional[
        regional["State"] == selected_region
    ]
else:
    regional_filtered = regional.copy()

if selected_category != "All":
    regional_filtered = regional_filtered[
        regional_filtered["PopulationSegment"] == selected_category
    ]

# -----------------------------
# KPI calculations
# -----------------------------

# Revenue comes from checkout orders
total_revenue = ab_filtered["OrderValueINR"].sum()

# Active users = unique visitors
active_users = ab_filtered["VisitorID"].nunique()

# Churn percentage
churn_percentage = (
    (churn["Churn"] == "Yes").mean() * 100
)

# Average ticket size
converted_orders = ab_filtered[
    ab_filtered["Converted"] == "Yes"
]

if len(converted_orders) > 0:
    avg_ticket = converted_orders["OrderValueINR"].mean()
else:
    avg_ticket = 0

# -----------------------------
# Header
# -----------------------------
st.title("📊 Business Analytics Dashboard")
st.caption("Workora Labs Data Analytics Internship")

# -----------------------------
# KPI Cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

c2.metric(
    "Active Users",
    f"{active_users:,}"
)

c3.metric(
    "Churn %",
    f"{churn_percentage:.1f}%"
)

c4.metric(
    "Avg Ticket Size",
    f"₹{avg_ticket:,.2f}"
)

st.divider()

# -----------------------------
# Revenue by A/B Test Variant
# -----------------------------
st.subheader("Revenue by A/B Test Variant")

if len(ab_filtered) > 0:

    revenue_by_variant = (
        ab_filtered.groupby("Variant")["OrderValueINR"]
        .sum()
        .reset_index()
    )

    fig1 = px.bar(
        revenue_by_variant,
        x="Variant",
        y="OrderValueINR",
        title="Revenue by A/B Test Variant"
    )

    fig1.update_yaxes(title="Revenue (₹)")
    fig1.update_xaxes(title="Variant")

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# -----------------------------
# Regional Market Demand
# -----------------------------
st.subheader("Regional Market Demand")

market_summary = (
    regional_filtered.groupby("State")
    .agg(
        Search_Demand=("MonthlySearchDemand", "sum"),
        Competitors=("ExistingCompetitors", "sum")
    )
    .reset_index()
)

fig2 = px.bar(
    market_summary,
    x="State",
    y="Search_Demand",
    title="Monthly Search Demand by Region"
)

fig2.update_yaxes(title="Monthly Search Demand")
fig2.update_xaxes(title="Region")

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------
# Traffic Sources
# -----------------------------
st.subheader("Traffic Source Analysis")

source_summary = (
    traffic_filtered.groupby("Source")
    .size()
    .reset_index(name="Sessions")
)

fig3 = px.bar(
    source_summary,
    x="Source",
    y="Sessions",
    title="Sessions by Traffic Source"
)

fig3.update_yaxes(title="Sessions")
fig3.update_xaxes(title="Traffic Source")

st.plotly_chart(
    fig3,
    use_container_width=True
)

# -----------------------------
# Customer Churn
# -----------------------------
st.subheader("Customer Churn Analysis")

churn_summary = (
    churn["Churn"]
    .value_counts()
    .reset_index()
)

churn_summary.columns = ["Churn", "Customers"]

fig4 = px.bar(
    churn_summary,
    x="Churn",
    y="Customers",
    title="Customer Churn Distribution"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# -----------------------------
# Churn by Subscription
# -----------------------------
subscription_churn = (
    churn.groupby("SubscriptionType")["Churn"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="ChurnRate")
)

fig5 = px.bar(
    subscription_churn,
    x="SubscriptionType",
    y="ChurnRate",
    title="Churn Rate by Subscription Type"
)

fig5.update_yaxes(
    title="Churn Rate (%)"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# -----------------------------
# A/B Test
# -----------------------------
st.subheader("Checkout A/B Test")

ab_summary = (
    ab_filtered.groupby("Variant")["Converted"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="ConversionRate")
)

fig6 = px.bar(
    ab_summary,
    x="Variant",
    y="ConversionRate",
    title="Conversion Rate by A/B Test Variant"
)

fig6.update_yaxes(
    title="Conversion Rate (%)"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.success("Interactive dashboard loaded successfully.")