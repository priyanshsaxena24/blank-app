import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="3-KPI Loss Analysis", layout="wide")

# Light theme CSS
st.markdown("""
<style>
.metric-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.kpi-main { font-size: 2.5rem; font-weight: 700; color: #059669; }
.status-good { background: #d1fae5; color: #065f46; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
.status-warning { background: #fef3c7; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# Generate data for 3 KPIs only
@st.cache_data
def generate_data():
    dates = pd.date_range('2026-01-01', periods=90, freq='D')
    np.random.seed(42)
    
    data = []
    for date in dates:
        design_loss = 25.0  # Fixed
        env_loss = np.random.uniform(15, 35)
        tech_loss = 100 - design_loss - env_loss
        
        data.append({
            'Date': date,
            'Design_Loss_%': design_loss,
            'Environmental_Loss_%': env_loss,
            'Technical_Loss_%': tech_loss
        })
    return pd.DataFrame(data)

df = generate_data()

# Header
st.title("🔍 **3-KPI Loss Analysis**")
st.markdown("*Design + Environmental + Technical = 100%*")

# Main KPI Cards
col1, col2, col3 = st.columns(3)
recent = df.tail(7).mean()  # Weekly average

with col1:
    st.markdown(f"""
    <div class="metric-card">
    <div style="font-size: 1.1rem; color: #374151;">Design Loss</div>
    <div class="kpi-main">{recent['Design_Loss_%']:.1f}%</div>
    <div style="font-size: 0.9rem; color: #6b7280;">Fixed (25%)</div>
    <span class="status-good">✅ Good</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    <div style="font-size: 1.1rem; color: #374151;">Environmental Loss</div>
    <div class="kpi-main" style="color: #10b981;">{recent['Environmental_Loss_%']:.1f}%</div>
    <div style="font-size: 0.9rem; color: #6b7280;">Weather-driven</div>
    <span class="status-good">✅ Normal</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
    <div style="font-size: 1.1rem; color: #374151;">Technical Loss</div>
    <div class="kpi-main" style="color: #f59e0b;">{recent['Technical_Loss_%']:.1f}%</div>
    <div style="font-size: 0.9rem; color: #6b7280;">Actionable</div>
    <span class="status-warning">⚠️ Monitor</span>
    </div>
    """, unsafe_allow_html=True)

# Loss Breakdown Pie (perfect for 3 KPIs)
st.markdown("### **📊 Loss Distribution**")
fig_pie = px.pie(
    values=[recent['Design_Loss_%'], recent['Environmental_Loss_%'], recent['Technical_Loss_%']],
    names=['Design Loss', 'Environmental Loss', 'Technical Loss'],
    color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b']
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(height=500)
st.plotly_chart(fig_pie, use_container_width=True)

# PERFECT Loss Analysis Table (matches screenshot exactly)
st.markdown("### **📋 Detailed Loss Analysis**")
loss_table = pd.DataFrame({
    'Loss Category': ['Design Loss', 'Environmental Loss', 'Technical Loss'],
    'Current Value (%)': [f"{recent['Design_Loss_%']:.1f}%", f"{recent['Environmental_Loss_%']:.1f}%", f"{recent['Technical_Loss_%']:.1f}%"],
    'Typical Range': ['25%', '15-35%', '<30%'],
    'Site ID': ['All', 'All', 'All'],
    'Status': ['✅ Good', '✅ Normal', '⚠️ Monitor']
})
st.dataframe(loss_table, use_container_width=True, hide_index=True)

# Formula Breakdown
st.markdown("### **⚙️ Formula Breakdown**")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    **Design Loss %** = 25% (fixed)<br><br>
    **Environmental Loss %** = (Deemed Gen - Actual Gen) / Theoretical Max × 100<br><br>
    **Technical Loss %** = 100 - Design Loss % - Environmental Loss %
    """)

with col2:
    st.latex(r"""
    \text{Where:}
    \\[1em]
    \text{Theoretical Max} = \text{Irradiance} \times \text{DC Capacity} \times 1.0
    \\[0.5em]
    \text{Deemed Gen} = \text{Irradiance} \times \text{DC Capacity} \times 0.75
    """)

# Trend Chart
st.markdown("### **📈 30-Day Trends**")
fig_line = px.line(df.tail(30), x='Date', y=['Design_Loss_%', 'Environmental_Loss_%', 'Technical_Loss_%'],
                   color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b'],
                   title="Loss Trends Over Time")
st.plotly_chart(fig_line, use_container_width=True)

# Tooltips / Explanations
with st.expander("ℹ️ **KPI Definitions**"):
    st.markdown("""
    - **Design Loss (25%)**: Unavoidable losses from plant design and technology limits  
    - **Environmental Loss (15-35%)**: Weather-driven losses (clouds, temperature, dust)  
    - **Technical Loss (<30%)**: Equipment/operational issues - **target for improvement**
    """)

st.caption("Deployed on Streamlit Cloud • Updated Feb 23, 2026")
