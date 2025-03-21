import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.ml_predictor import DisasterPredictor
from utils.sms_handler import SMSHandler
import io
import uuid
from datetime import datetime

st.set_page_config(page_title="ML Predictions", page_icon="📊")

st.title("📊 ML-Based Disaster Predictions")

# Initialize predictor and SMS handler
predictor = DisasterPredictor()
sms_handler = SMSHandler()

# Initialize session state for alerts
if 'alert_threshold' not in st.session_state:
    st.session_state.alert_threshold = 0.7  # 70% probability threshold for alerts
if 'alert_data' not in st.session_state:
    st.session_state.alert_data = []  # Initialize as empty list

# Sidebar configuration
st.sidebar.header("Alert Configuration")
alert_threshold = st.sidebar.slider(
    "Alert Threshold",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.alert_threshold,
    help="Probability threshold for generating alerts"
)
st.session_state.alert_threshold = alert_threshold

# Data input section
st.header("Data Input & Model Training")
data_source = st.radio(
    "Choose data source",
    ["Upload Custom Data", "Use Sample Data"]
)

if data_source == "Upload Custom Data":
    st.info("""
    Upload a CSV file with the following columns:
    - rainfall (mm)
    - temperature (Celsius)
    - seismic_activity (Richter scale)
    - wind_speed (m/s)
    - disaster_type (0: flood, 1: earthquake, 2: cyclone, 3: landslide)
    """)

    uploaded_file = st.file_uploader("Upload your disaster data (CSV)", type=['csv'])
    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            st.write("Data Preview:", data.head())

            if st.button("Train Model with Uploaded Data"):
                with st.spinner("Training model..."):
                    # Separate features and labels
                    X = data[predictor.feature_columns]
                    y = data['disaster_type']

                    # Train the model
                    metrics = predictor.train(X, y)

                    # Display metrics
                    st.success("Model trained successfully!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Training Accuracy", f"{metrics['train_accuracy']:.2%}")
                    with col2:
                        st.metric("Test Accuracy", f"{metrics['test_accuracy']:.2%}")

                    # Feature importance plot
                    fig = px.bar(
                        x=list(metrics['feature_importance'].keys()),
                        y=list(metrics['feature_importance'].values()),
                        title="Feature Importance"
                    )
                    st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error processing uploaded data: {str(e)}")

else:
    if st.button("Generate and Train with Sample Data"):
        with st.spinner("Generating sample data and training model..."):
            # Generate sample data
            X, y = predictor.generate_sample_data()

            # Train model
            metrics = predictor.train(X, y)

            # Display metrics
            st.success("Model trained successfully with sample data!")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Training Accuracy", f"{metrics['train_accuracy']:.2%}")
            with col2:
                st.metric("Test Accuracy", f"{metrics['test_accuracy']:.2%}")

            # Feature importance plot
            fig = px.bar(
                x=list(metrics['feature_importance'].keys()),
                y=list(metrics['feature_importance'].values()),
                title="Feature Importance"
            )
            st.plotly_chart(fig)

# Prediction Section with Automatic Alerts
st.header("Make Predictions & Generate Alerts")
st.write("Enter values to predict disaster probability:")

col1, col2 = st.columns(2)
with col1:
    rainfall = st.number_input("Rainfall (mm)", 0.0, 500.0, 100.0)
    temperature = st.number_input("Temperature (°C)", -20.0, 50.0, 25.0)
with col2:
    seismic = st.number_input("Seismic Activity (Richter)", 0.0, 10.0, 2.0)
    wind = st.number_input("Wind Speed (m/s)", 0.0, 100.0, 15.0)

location = st.selectbox("Location", ["Mumbai", "Chennai", "Kolkata", "Delhi"])

if st.button("Predict and Check for Alerts"):
    try:
        # Create input data
        input_data = pd.DataFrame({
            'rainfall': [rainfall],
            'temperature': [temperature],
            'seismic_activity': [seismic],
            'wind_speed': [wind]
        })

        # Get prediction
        prediction = predictor.predict(input_data)

        # Display results
        st.subheader("Prediction Results")
        fig = px.bar(
            x=list(prediction.keys()),
            y=list(prediction.values()),
            title="Disaster Probability",
            color=list(prediction.values()),
            color_continuous_scale="RdYlGn_r"
        )
        st.plotly_chart(fig)

        # Find highest risk disaster
        highest_risk = max(prediction.items(), key=lambda x: x[1])
        disaster_type = highest_risk[0]
        probability = highest_risk[1]

        st.warning(f"Highest risk: {disaster_type.title()} ({probability:.1%} probability)")

        # Generate alert if probability exceeds threshold
        if probability >= alert_threshold:
            alert_id = str(uuid.uuid4())
            alert_message = f"⚠️ HIGH RISK ALERT: {probability:.1%} probability of {disaster_type} in {location}"

            # Create new alert
            new_alert = {
                'id': alert_id,
                'message': alert_message,
                'location': location,
                'severity': 'High',
                'timestamp': str(datetime.now()),
                'disaster_type': disaster_type,
                'probability': probability
            }

            # Add to session state
            st.session_state.alert_data.append(new_alert)

            st.error(f"""
            🚨 Alert Generated!
            {alert_message}

            This alert has been added to the alert system. You can manage it in the Alerts page:
            - Send SMS notifications
            - Track evacuation responses
            - Allocate resources based on response rates
            """)

    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")

# Show recent alerts
if st.session_state.alert_data:  # Check if list is not empty
    st.subheader("Recent ML-Generated Alerts")
    # Get last 5 alerts (or fewer if less exist)
    recent_alerts = list(reversed(st.session_state.alert_data[-5:]))
    for alert in recent_alerts:
        st.markdown(f"""
        🚨 **{alert['disaster_type'].title()}** ({alert['probability']:.1%} probability)
        - Location: {alert['location']}
        - Time: {alert['timestamp']}
        - Message: {alert['message']}
        """)