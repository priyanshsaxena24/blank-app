import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Solar Loss Analysis", layout="wide")

# Custom CSS (same as before)
st.markdown("""
<style>
.metric-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem; }
.kpi-header { font-size: 1.1rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2.2rem; font-weight: 700; color: #059669; }
.kpi-subtext { font-size: 0.9rem; color: #6b7280; }
.status-good { background: #d1fae5; color: #065f46; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
.status-warning { background: #fef3c7; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
.status-critical { background: #fee2e2; color: #991b1b; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# Generate FIXED sample data
@st.cache_data
def generate_data():
    dates = pd.date_range('2025-11-01', periods=90, freq='D')
    np.random.seed(42)
    
    data = []
    for date in dates:
        plant_avail_pct = np.random.uniform(97.2, 99.5)
        potential_gen = np.random.uniform(500, 550)
        avail_loss_pct = (100 - plant_avail_pct)
        avail_loss_mwh = (100 - plant_avail_pct) / 100 * potential_gen
        
        data.append({
            'Date': date,
            'Plant_Availability_%': plant_avail_pct,
            'Potential_Gen_MWh': potential_gen,
            'Availability_Loss_MWh': avail_loss_mwh,
            'Availability_Loss_%': avail_loss_pct,
            'Design_Loss_%': 25.0,
            'Env_Loss_%': np.random.uniform(15, 35),
            'Tech_Loss_%': 100 - 25 - np.random.uniform(15, 35)
        })
    return pd.DataFrame(data)

df = generate_data()

# Header
st.markdown("# **Availability Loss**")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Availability Loss</div>
    <div class="kpi-value">2.8%</div>
    <div class="kpi-subtext">14.56 MWh</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Source</div>
    <div class="kpi-subtext">Calculated</div>
    <div class="kpi-subtext">2026-02-16 10:05</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Status</div>
    <div><span class="status-warning">⚠️ Warning</span></div>
    </div>
    """, unsafe_allow_html=True)

# Historical Trend + Recommendations
col1, col2 = st.columns(2)
with col1:
    st.markdown("### **📈 Historical Trend (Last 3 Months)**")
    monthly = df.resample('M', on='Date')['Availability_Loss_%'].mean().tail(3)
    fig = go.Figure(data=[go.Bar(
        x=['2025-11', '2025-12', '2026-01'], 
        y=monthly.values,
        marker_color=['#3b82f6', '#3b82f6', '#f59e0b']
    )])
    fig.update_layout(height=300, showlegend=False, yaxis_title="Loss %")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### **💡 Recommendations**")
    st.markdown("""
    <ul style="color: #374151; line-height: 1.6; padding-left: 1.5rem;">
        <li><span style="color: #059669;">✅</span> Any unscheduled plant downtime is impacting generation</li>
        <li><span style="color: #059669;">✅</span> An easy KPI summarizing how much energy lost due to outages across portfolio</li>
        <li><span style="color: #059669;">✅</span> Investigate causes of reduced availability and improve maintenance practices</li>
    </ul>
    """, unsafe_allow_html=True)

# Formula Breakdown
st.markdown("### **📊 Total Availability Loss - Formula Breakdown**")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="metric-card">
    <div class="kpi-header">Calculation Formula</div>
    <div style="font-family: monospace; font-size: 0.95rem; color: #1f2937;">
    Loss = (1 - Plant Availability) × Potential Gen
    </div>
    </div>
    """, unsafe_allow_html=True)

    recent = df.iloc[-1]
    st.markdown(f"""
    <div class="metric-card">
    <div class="kpi-header">Data Components & Sources</div>
    <div style="font-size: 0.85rem;">
    **Plant Availability**<br>
    <span style="color: #059669;">{recent['Plant_Availability_%']:.1f}%</span><br>
    <span style="color: #6b7280;">Source: SCADA</span><br>
    <span style="color: #6b7280;">{recent['Date'].strftime('%Y-%m-%d %H:%M')}</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    <div class="kpi-header">Potential Generation</div>
    <div class="kpi-value">{recent['Potential_Gen_MWh']:.0f} MWh</div>
    <div class="kpi-subtext">Source: Design Capacity<br>{recent['Date'].strftime('%Y-%m-%d %H:%M')}</div>
    </div>
    
    <div class="metric-card" style="margin-top: 1rem;">
    <div class="kpi-header">Availability Loss</div>
    <div class="kpi-value">{recent['Availability_Loss_MWh']:.1f} MWh</div>
    <div class="kpi-subtext">Source: Calculated<br>{recent['Date'].strftime('%Y-%m-%d %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

# FIXED Loss Analysis Table
st.markdown("### **🔍 Detailed Loss Analysis**")
loss_data = {
    'Loss Category': ['Total Availability Loss', 'Design/Configuration', 'Environmental', 'Soiling Loss', 'Environmental', 'Incidence/Cloud Loss', 'Clipping Loss'],
    'Specific Loss Type': ['Total Availability Loss', 'Total Design Loss', 'Soiling Loss', 'Incidence/Cloud Loss', 'Clipping Loss', '', ''],
    'Current Value (%)': ['2.8%', '25%', '6%', '18%', '2%', '', ''],
    'Typical Range': ['1-5%', '25%', '2-8%', '10-30%', '1-5%', '', ''],
    'Site ID': ['All', 'All', 'Site B', 'All', 'Site C', '', ''],
    'Status': ['⚠️ Warning', '✅ Good', '🔴 Critical', '✅ Good', '✅ Good', '', '']
}
loss_df = pd.DataFrame(loss_data)
st.dataframe(loss_df, use_container_width=True, hide_index=True, column_config={
    "Status": st.column_config.Column("Status", width="medium")
})

# EPF Cards (3-plant layout)
st.markdown("### **🌿 Environmental Performance Factor (EPF)**")
col1, col2, col3 = st.columns(3)

plants_data = [
    {'name': 'Site A', 'epf': 82.0, 'status': 'CRITICAL', 'pr': '87.2%', 'deemed': '450', 'loss': '30'},
    {'name': 'Site B', 'epf': 88.0, 'status': 'WARNING', 'pr': '86.5%', 'deemed': '520', 'loss': '46.5'},
    {'name': 'Site C', 'epf': 93.0, 'status': 'GOOD', 'pr': '88.9%', 'deemed': '380', 'loss': '35'}
]

for i, plant in enumerate(plants_data):
    color = "#dc2626" if plant['status'] == 'CRITICAL' else "#ea580c" if plant['status'] == 'WARNING' else "#059669"
    status_class = f"status-{plant['status'].lower()}"
    
    st.markdown(f"""
    <div class="metric-card">
    <div class="kpi-header">{plant['name']}</div>
    <div class="kpi-value" style="color: {color};">{plant['epf']}%</div>
    <div class="kpi-subtext">
    <span class="{status_class}">{plant['status']}</span><br>
    Performance Ratio: {plant['pr']}<br>
    Deemed Generation: {plant['deemed']} MWh<br>
    Actual Loss: {plant['loss']} MWh
    </div>
    </div>
    """, unsafe_allow_html=True)

# Modified 3-KPI Model
st.markdown("### **🎯 Modified 3-KPI Model**")
col1, col2, col3 = st.columns(3)
recent_avg = df.tail(30)[['Design_Loss_%', 'Env_Loss_%', 'Tech_Loss_%']].mean()

st.metric("Design Loss %", f"{recent_avg['Design_Loss_%']:.1f}%")
st.metric("Environmental Loss %", f"{recent_avg['Env_Loss_%']:.1f}%")
st.metric("Technical Loss %", f"{recent_avg['Tech_Loss_%']:.1f}%")

st.caption("**Technical Loss = 100 - Design Loss - Environmental Loss**")
