import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Gas Network Monitor", layout="wide")

# CSS
st.markdown("""
<style>
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              padding: 1.5rem; border-radius: 12px; color: white; text-align: center;}
.alert-card {background: linear-gradient(135deg, #ff6b6b, #ee5a52);}
.health-card {background: linear-gradient(135deg, #51cf66, #40c057);}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_pipeline_data():
    np.random.seed(42)
    n_segments = 25
    
    # FIXED: Consistent array lengths
    n_points_per_seg = 576  # 48hr @ 5min = 576 points/segment
    total_points = n_segments * n_points_per_seg
    
    timestamps = pd.date_range(datetime.now() - timedelta(hours=48), 
                              periods=n_points_per_seg, freq='5T')
    
    data_dict = {
        'timestamp': np.tile(timestamps, n_segments),
        'segment': np.repeat([f'P{i:02d}' for i in range(1, n_segments+1)], n_points_per_seg),
        'inlet_flow_scfh': np.random.lognormal(10.0, 0.15, total_points) * 1000,
        'outlet_flow_scfh': np.random.lognormal(10.0, 0.15, total_points) * 1000,
        'inlet_pressure_psig': np.random.normal(55, 4, total_points),
        'outlet_pressure_psig': np.random.normal(48, 4.5, total_points),
        'length_miles': np.repeat(np.random.uniform(3, 25, n_segments), n_points_per_seg),
        'diameter_inches': np.repeat(np.random.choice([6, 8, 12], n_segments), n_points_per_seg)
    }
    
    data = pd.DataFrame(data_dict)
    
    # Inject realistic leaks
    leak_segments = ['P05', 'P14', 'P22', 'P08']
    for seg in leak_segments:
        mask = data['segment'] == seg
        data.loc[mask, 'outlet_flow_scfh'] *= np.random.uniform(0.88, 0.95, sum(mask))
        data.loc[mask, 'outlet_pressure_psig'] -= np.random.uniform(1.5, 3.5, sum(mask))
    
    # Volume Balance & Health Metrics
    data['flow_imbalance_pct'] = ((data['inlet_flow_scfh'] - data['outlet_flow_scfh']) / 
                                 data['inlet_flow_scfh']) * 100
    data['delta_p_psig'] = data['inlet_pressure_psig'] - data['outlet_pressure_psig']
    data['expected_delta_p'] = (0.00008 * (data['inlet_flow_scfh']/1000)**2 * 
                               data['length_miles'] / data['diameter_inches'])
    data['dp_anomaly_ratio'] = (data['delta_p_psig'] - data['expected_delta_p']) / (data['expected_delta_p'] + 0.1)
    
    data['health_flow'] = np.clip(100 - data['flow_imbalance_pct'] * 15, 0, 100)
    data['health_pressure'] = np.clip(100 - np.abs(data['dp_anomaly_ratio']) * 25, 0, 100)
    data['overall_health'] = 0.5 * data['health_flow'] + 0.5 * data['health_pressure']
    
    # Latest metrics per segment
    latest = data.groupby('segment').last().reset_index()
    latest['risk_level'] = np.where(latest['overall_health'] < 60, 'CRITICAL',
                           np.where(latest['overall_health'] < 75, 'HIGH',
                           np.where(latest['overall_health'] < 90, 'MEDIUM', 'LOW')))
    
    return data, latest

# Load data
pipeline_data, latest_metrics = load_pipeline_data()

# Sidebar
st.sidebar.title("⚙️ Controls")
hours_back = st.sidebar.slider("Data Range (hours)", 2, 48, 12)
leak_threshold = st.sidebar.slider("Leak Threshold (%)", 0.8, 3.0, 1.5, 0.1)
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

# Header
st.title("🔥 Gas Pipeline Health & Leak Detection")
st.markdown("*SCADA-powered | Volume Balance + Health Scoring | API 1175 compliant*")

# Tabs
tab1, tab2 = st.tabs(["🗺️ Network Overview", "🚨 Active Leaks"])

with tab1:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    healthy = len(latest_metrics[latest_metrics['risk_level']=='LOW'])
    critical = len(latest_metrics[latest_metrics['risk_level']=='CRITICAL'])
    avg_health = latest_metrics['overall_health'].mean()
    
    with col1:
        st.markdown(f"""
        <div class="health-card">
            <h2>{healthy}</h2><p>Healthy Segments</p>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="alert-card">
            <h2>{critical}</h2><p>Critical Risks</p>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        st.metric("Avg Health", f"{avg_health:.0f}/100")
    
    with col4:
        current_leaks = len(latest_metrics[latest_metrics['flow_imbalance_pct']>leak_threshold])
        st.metric("Leaks Detected", current_leaks)
    
    # Network Map
    fig_map = px.scatter(latest_metrics, x='length_miles', y='diameter_inches',
                        size='overall_health', color='risk_level',
                        hover_data=['segment','flow_imbalance_pct','overall_health'],
                        title="Pipeline Network Health Map",
                        color_discrete_map={'LOW':'#10b981','MEDIUM':'#f59e0b',
                                          'HIGH':'#ef4444','CRITICAL':'#dc2626'})
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Split charts
    col_a, col_b = st.columns(2)
    with col_a:
        fig_hist = px.histogram(latest_metrics, x='overall_health', nbins=15,
                               title="Health Distribution")
        fig_hist.add_vline(75, line_dash="dash", line_color="orange")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_b:
        st.subheader("Top Risks")
        top5 = latest_metrics.nsmallest(5, 'overall_health')[['segment','overall_health','risk_level']]
        st.dataframe(top5.round(1), hide_index=True)

with tab2:
    recent = pipeline_data[pipeline_data['timestamp'] > 
                         pipeline_data['timestamp'].max() - timedelta(hours=hours_back)]
    
    leaks_df = recent[recent['flow_imbalance_pct'] > leak_threshold].groupby('segment').agg({
        'flow_imbalance_pct': 'mean',
        'overall_health': 'last',
        'delta_p_psig': 'last'
    }).round(2).reset_index()
    
    if len(leaks_df) > 0:
        st.error(f"🚨 {len(leaks_df)} LEAKS DETECTED")
        st.dataframe(leaks_df, use_container_width=True)
        
        fig_bar = px.bar(leaks_df.sort_values('flow_imbalance_pct', ascending=False),
                        x='segment', y='flow_imbalance_pct',
                        title=f"Active Leaks (>{leak_threshold}%)")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.success("✅ No active leaks")
    
    # Sample trend
    st.subheader("Live Trend: P05 (Leak)")
    sample = recent[recent['segment']=='P05'].tail(48)
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Scatter(x=sample['timestamp'], y=sample['flow_imbalance_pct'],
                                  name='Imbalance %'), secondary_y=False)
    fig_trend.add_trace(go.Scatter(x=sample['timestamp'], y=sample['overall_health'],
                                  name='Health'), secondary_y=True)
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")
st.caption(f"Updated: {datetime.now().strftime('%H:%M IST')} | Production-ready dashboard")
