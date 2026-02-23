import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Solar Loss Analysis", layout="wide")

# Custom CSS to match your screenshots
st.markdown("""
<style>
    .metric-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .kpi-header { font-size: 1.1rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; color: #059669; }
    .kpi-subtext { font-size: 0.9rem; color: #6b7280; }
    .status-good { background: #d1fae5; color: #065f46; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
    .status-warning { background: #fef3c7; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
    .status-critical { background: #fee2e2; color: #991b1b; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# Generate sample data matching your structure
@st.cache_data
def generate_data():
    dates = pd.date_range('2025-11-01', periods=90, freq='D')  # 3 months
    np.random.seed(42)
    
    data = []
    for date in dates:
        # Plant availability (97-99.5%)
        plant_avail = np.random.uniform(0.972, 0.995)
        
        # Potential generation (design capacity based)
        potential_gen = np.random.uniform(500, 550)  # MWh
        
        # Availability loss
        avail_loss_mwh = (1 - plant_avail) * potential_gen
        avail_loss_pct = ((1 - plant_avail) * 100)
        
        data.append({
            'Date': date,
            'Plant_Availability_%': plant_avail * 100,
            'Potential_Gen_MWh': potential_gen,
            'Availability_Loss_MWh': avail_loss_mwh,
            'Availability_Loss_%': avail_loss_pct
        })
    
    # Add your 3 KPI model
    df = pd.DataFrame(data)
    df['Design_Loss_%'] = 25.0  # Fixed
    df['Env_Loss_%'] = np.random.uniform(15, 35, len(df))
    df['Tech_Loss_%'] = 100 - df['Design_Loss_%'] - df['Env_Loss_%']
    return df

df = generate_data()

# Header matching your screenshot
st.markdown("# **Availability Loss**")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<div class="metric-card"><div class="kpi-header">Availability Loss</div><div class="kpi-value">2.8%</div><div class="kpi-subtext">14.56 MWh</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-header">Source</div><div class="kpi-subtext">Calculated</div><div class="kpi-subtext">2026-02-16 10:05</div>')
with col3:
    st.markdown('<div class="kpi-header">Status</div><div><span class="status-warning">⚠️ Warning</span></div>')

# Historical Trend (exactly like screenshot)
col1, col2 = st.columns(2)
with col1:
    st.markdown("### **📈 Historical Trend (Last 3 Months)**")
    trend_data = df.tail(90).resample('M', on='Date')['Availability_Loss_%'].mean()
    fig_trend = go.Figure(data=[
        go.Bar(x=['2025-11', '2025-12', '2026-01'], y=[2.1, 2.5, 2.8], 
               marker_color=['#3b82f6', '#3b82f6', '#f59e0b'])
    ])
    fig_trend.update_layout(height=300, showlegend=False, yaxis_title="Loss %")
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown("### **💡 Recommendations**")
    st.markdown("""
    <div class="metric-card">
    <ul style="color: #374151; line-height: 1.6;">
        <li><span style="color: #059669;">✅</span> Any unscheduled plant downtime is impacting generation</li>
        <li><span style="color: #059669;">✅</span> An easy KPI summarizing how much energy lost due to outages across portfolio</li>
        <li><span style="color: #059669;">✅</span> Investigate causes of reduced availability and improve maintenance practices</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Formula Breakdown (exact replica)
st.markdown("### **📊 Total Availability Loss - Formula Breakdown**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Calculation Formula</div>
    <div class="kpi-subtext" style="font-family: monospace; font-size: 0.95rem;">
    Loss = (1 - Plant Availability) × Potential Gen
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Data Components & Sources</div>
    <div class="kpi-subtext" style="font-size: 0.85rem;">
    **Plant Availability**<br>
    <span style="color: #059669;">97.2%</span><br>
    <span style="color: #6b7280;">Source: SCADA</span><br>
    <span style="color: #6b7280;">2026-02-16 10:00</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Potential Generation</div>
    <div class="kpi-value">520 MWh</div>
    <div class="kpi-subtext">Source: Design Capacity<br>2026-02-16 10:00</div>
    </div>
    
    <div class="metric-card" style="margin-top: 1rem;">
    <div class="kpi-header">Availability Loss</div>
    <div class="kpi-value">14.56 MWh</div>
    <div class="kpi-subtext">Source: Calculated<br>2026-02-16 10:05</div>
    </div>
    """, unsafe_allow_html=True)

# Loss Analysis Table (exact replica)
st.markdown("### **🔍 Detailed Loss Analysis**")
loss_table = pd.DataFrame({
    'Loss Category': ['Total Availability Loss', 'Design/Configuration', 'Environmental', 'Soiling Loss', 'Environmental', 'Incidence/Cloud Loss', 'Clipping Loss'],
    'Specific Loss Type': ['Total Availability Loss', 'Total Design Loss', 'Soiling Loss', 'Incidence/Cloud Loss', 'Clipping Loss'],
    'Current Value (%)': ['2.8%', '25%', '6%', '18%', '2%'],
    'Typical Range': ['1-5%', '25%', '2-8%', '10-30%', '1-5%'],
    'Site ID': ['All', 'All', 'Site B', 'All', 'Site C'],
    'Status': ['⚠️ Warning', '✅ Good', '🔴 Critical', '✅ Good', '✅ Good']
})

st.dataframe(loss_table, use_container_width=True, hide_index=True)

# EPF Cards (exact replica of screenshot)
st.markdown("### **🌿 Environmental Performance Factor (EPF)**")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Site A</div>
    <div class="kpi-value" style="color: #dc2626;">82.0%</div>
    <div class="kpi-subtext">
    <span class="status-critical">CRITICAL</span><br>
    Performance Ratio: 87.2%<br>
    Deemed Generation: 450 MWh<br>
    Actual Loss: 30 MWh
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Site B</div>
    <div class="kpi-value" style="color: #ea580c;">88.0%</div>
    <div class="kpi-subtext">
    <span class="status-warning">WARNING</span><br>
    Performance Ratio: 86.5%<br>
    Deemed Generation: 520 MWh<br>
    Actual Loss: 46.5 MWh
    </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Site C</div>
    <div class="kpi-value" style="color: #059669;">93.0%</div>
    <div class="kpi-subtext">
    <span class="status-good">GOOD</span><br>
    Performance Ratio: 88.9%<br>
    Deemed Generation: 380 MWh<br>
    Actual Loss: 35 MWh
    </div>
    </div>
    """, unsafe_allow_html=True)

# Your Modified 3-KPI Model (highlighted)
st.markdown("### **🎯 Modified 3-KPI Model (New)**")
col1, col2, col3 = st.columns(3)
recent_avg = df.tail(30).mean()

with col1:
    st.metric("Design Loss %", f"{recent_avg['Design_Loss_%']:.1f}%", "Fixed")
with col2:
    st.metric("Environmental Loss %", f"{recent_avg['Env_Loss_%']:.1f}%", "+1.2%")
with col3:
    st.metric("Technical Loss %", f"{recent_avg['Tech_Loss_%']:.1f}%", "+0.8%", delta_color="inverse")

st.caption("Technical Loss = 100 - Design Loss - Environmental Loss")
