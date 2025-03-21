import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.data_generator import generate_disaster_data, generate_resource_data, generate_alert_data
from utils.ml_predictor import DisasterPredictor  # Changed import to use proper ML predictor

# Page configuration
st.set_page_config(
    page_title="Disaster Management System",
    page_icon="🚨",
    layout="wide"
)

# Load custom CSS
with open('assets/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Header
st.title("🚨 Disaster Management & ML Analysis Dashboard")

# Initialize session state
if 'disaster_data' not in st.session_state:
    st.session_state.disaster_data = generate_disaster_data()
if 'resource_data' not in st.session_state:
    st.session_state.resource_data = generate_resource_data()
if 'alert_data' not in st.session_state:
    st.session_state.alert_data = generate_alert_data()

# Layout
col1, col2, col3 = st.columns(3)

# Key Metrics
with col1:
    st.metric("Active Alerts", len(st.session_state.alert_data))
with col2:
    st.metric("High Risk Areas", len(st.session_state.disaster_data[st.session_state.disaster_data['severity'] == 'High']))
with col3:
    st.metric("Available Resources", sum(st.session_state.resource_data.values()))

# Disaster Predictions
st.subheader("🔮 Disaster Predictions")
predictor = DisasterPredictor()

# Location selector
location = st.selectbox(
    "Select Location",
    ["Maharashtra", "Kerala", "Gujarat", "Tamil Nadu", "West Bengal"]
)

# Get and display predictions
predictions = predictor.predict_disasters(location)
risk_factors = predictor.get_risk_factors(location)

col1, col2 = st.columns(2)

with col1:
    # Prediction chart
    fig1 = px.bar(
        x=list(predictions.keys()),
        y=list(predictions.values()),
        title=f"Disaster Probability for {location}",
        color=list(predictions.values()),
        color_continuous_scale="RdYlGn_r"
    )
    fig1.update_layout(yaxis_title="Probability", xaxis_title="Disaster Type")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Risk factors
    st.subheader("Risk Factors")
    for factor, value in risk_factors.items():
        st.metric(factor, value)

# Recent Alerts
st.subheader("🚨 Recent Alerts")
for _, alert in st.session_state.alert_data.iloc[:3].iterrows():
    severity_class = f"alert-{alert['severity'].lower()}"
    st.markdown(
        f"""<div class="disaster-alert {severity_class}">
            <strong>{alert['severity']}</strong>: {alert['message']}
            <br>Location: {alert['location']}
            <br><small>{alert['timestamp']}</small>
        </div>""",
        unsafe_allow_html=True
    )

# Resource Overview
st.subheader("📦 Resource Overview")
fig2 = px.bar(
    x=list(st.session_state.resource_data.keys()),
    y=list(st.session_state.resource_data.values()),
    title="Available Resources",
    color=list(st.session_state.resource_data.values()),
    color_continuous_scale="Viridis"
)
fig2.update_layout(xaxis_title="Resource Type", yaxis_title="Quantity")
st.plotly_chart(fig2, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Emergency Contact: 📞 112")