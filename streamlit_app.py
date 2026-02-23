import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.figure_factory as ff

# Page config - Light theme
st.set_page_config(
    page_title="Solar Performance Insights",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light theme
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stMetric > label {
        color: #1f2937;
        font-weight: 600;
    }
    .stMetric > div > div {
        color: #059669;
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data (30 days)
@st.cache_data
def generate_solar_data():
    dates = pd.date_range(start='2026-01-25', end='2026-02-23', freq='D')
    np.random.seed(42)
    
    data = []
    for date in dates:
        # Base values with realistic variation
        theoretical_max = np.random.uniform(2500, 3500)  # kWh
        deemed_gen = theoretical_max * 0.75
        actual_gen = deemed_gen * np.random.uniform(0.65, 0.95)
        
        # Design Loss: Fixed at 25%
        design_loss_pct = 25.0
        
        # Environmental Loss: Varies with "weather"
        env_factor = np.random.uniform(0.15, 0.35)  # Weather impact
        env_loss_pct = (deemed_gen - actual_gen) / theoretical_max * 100
        
        # Technical Loss: Residual
        tech_loss_pct = 100 - design_loss_pct - env_loss_pct
        
        data.append({
            'Date': date,
            'Theoretical_Max_kWh': theoretical_max,
            'Deemed_Gen_kWh': deemed_gen,
            'Actual_Gen_kWh': actual_gen,
            'Design_Loss_pct': design_loss_pct,
            'Env_Loss_pct': env_loss_pct,
            'Tech_Loss_pct': tech_loss_pct,
            'Plant_ID': np.random.choice(['Plant_A', 'Plant_B', 'Plant_C'])
        })
    
    return pd.DataFrame(data)

# Load data
df = generate_solar_data()

# Title
st.title("☀️ Solar Performance Insights")
st.markdown("***Executive Dashboard for Utility Administrators***")

# Sidebar filters
st.sidebar.header("📊 Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)
plants = st.sidebar.multiselect(
    "Select Plants",
    options=df['Plant_ID'].unique(),
    default=df['Plant_ID'].unique()
)

# Filter data
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) & 
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Plant_ID'].isin(plants))
].copy()

# KPI Cards - Current Month Summary
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_design = filtered_df['Design_Loss_pct'].mean()
    st.metric("Design Loss", f"{avg_design:.1f}%", "0%", delta_color="normal")
with col2:
    avg_env = filtered_df['Env_Loss_pct'].mean()
    st.metric("Environmental Loss", f"{avg_env:.1f}%", "+1.2%", delta_color="normal")
with col3:
    avg_tech = filtered_df['Tech_Loss_pct'].mean()
    st.metric("Technical Loss", f"{avg_tech:.1f}%", "+0.8%", delta_color="inverse")
with col4:
    performance_score = 100 - avg_tech - (avg_design + avg_env - 25)
    st.metric("Performance Score", f"{performance_score:.0f}%", "+2%", delta_color="normal")

# Loss Breakdown Chart
st.subheader("📈 Loss Breakdown (Average)")
loss_data = filtered_df[['Design_Loss_pct', 'Env_Loss_pct', 'Tech_Loss_pct']].mean()
fig_pie = px.pie(
    values=loss_data.values,
    names=loss_data.index,
    color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b'],
    title="Loss Category Distribution"
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(showlegend=True)
st.plotly_chart(fig_pie, use_container_width=True)

# Trend Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Loss Trends Over Time")
    trend_df = filtered_df.groupby('Date')[['Design_Loss_pct', 'Env_Loss_pct', 'Tech_Loss_pct']].mean().reset_index()
    fig_line = px.line(
        trend_df, x='Date', y=['Design_Loss_pct', 'Env_Loss_pct', 'Tech_Loss_pct'],
        color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b'],
        title="Daily Loss Trends"
    )
    fig_line.update_layout(yaxis_title="Loss %", xaxis_title="Date")
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("🏭 Performance by Plant")
    plant_summary = filtered_df.groupby('Plant_ID')['Tech_Loss_pct'].mean().reset_index()
    fig_bar = px.bar(
        plant_summary, x='Plant_ID', y='Tech_Loss_pct',
        color='Tech_Loss_pct',
        color_continuous_scale='YlOrRd',
        title="Technical Loss by Plant"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# KPI Definitions (tooltips for manager)
with st.expander("ℹ️ KPI Definitions", expanded=False):
    st.markdown("""
    **Design Loss (25%)**: Unavoidable losses from plant design (temperature coefficient, wiring, inverter sizing). Expected even for healthy plants.
    
    **Environmental Loss (15-35%)**: Weather-driven losses (clouds, haze, high temperatures, dust). Varies by season/location.
    
    **Technical Loss (residual)**: Equipment/operational issues (inverter efficiency drop, unplanned outages, suboptimal controls). **Target <20%**.
    """)

# Alerts Section
st.subheader("🚨 Current Alerts")
alerts_df = filtered_df[filtered_df['Tech_Loss_pct'] > 25]
if not alerts_df.empty:
    for _, row in alerts_df.tail(3).iterrows():
        st.error(f"**{row['Plant_ID']}** - Technical Loss: {row['Tech_Loss_pct']:.1f}% on {row['Date'].strftime('%Y-%m-%d')}")
else:
    st.success("✅ All plants within normal Technical Loss thresholds")

# Footer
st.markdown("---")
st.markdown("*Dashboard auto-updates with new data. Last updated: Feb 23, 2026*")
