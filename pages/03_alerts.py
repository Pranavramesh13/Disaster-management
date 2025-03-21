import streamlit as st
import plotly.express as px
from utils.data_generator import generate_alert_data
from utils.sms_handler import SMSHandler
from datetime import datetime
import uuid

st.set_page_config(page_title="Alert System", page_icon="🚨")

st.title("🚨 Alert System")

# Initialize SMS Handler
sms_handler = SMSHandler()

# Initialize session state for tracking
if 'evacuation_data' not in st.session_state:
    st.session_state.evacuation_data = {}
if 'alerts_sent' not in st.session_state:
    st.session_state.alerts_sent = []

# Demo mode toggle
demo_mode = st.sidebar.checkbox("Enable Demo Mode", True)

# Alert data
alerts = st.session_state.get('alert_data', generate_alert_data())

# Create new alert with SMS notification
st.subheader("📱 Create Emergency Alert")
with st.form("create_alert"):
    message = st.text_input("Alert Message")
    location = st.selectbox("Location", ["Mumbai", "Chennai", "Kolkata", "Delhi"])
    severity = st.select_slider("Severity", options=["Low", "Medium", "High"])

    # Only show phone number input for high severity alerts
    if severity == "High":
        st.warning("⚠️ This is a HIGH SEVERITY alert - SMS notifications will be sent")
        phone_numbers = st.text_area(
            "Enter phone numbers (one per line)",
            help="Enter phone numbers in international format (e.g., +1234567890)",
            value="+1234567890\n+1987654321" if demo_mode else ""
        )

    if st.form_submit_button("Create Alert"):
        alert_id = str(uuid.uuid4())

        if severity == "High" and phone_numbers:
            numbers_list = [num.strip() for num in phone_numbers.split('\n') if num.strip()]
            total_recipients = len(numbers_list)

            # Initialize evacuation tracking
            st.session_state.evacuation_data[alert_id] = {
                'total': total_recipients,
                'confirmed': 0,
                'location': location,
                'timestamp': datetime.now(),
                'message': message,
                'severity': severity
            }

            # Send SMS alerts
            for number in numbers_list:
                try:
                    if demo_mode:
                        st.success(f"DEMO: SMS would be sent to {number}")
                    else:
                        sms_handler.send_alert(
                            to_number=number,
                            message=f"EMERGENCY ALERT: {message} in {location}. Immediate evacuation required.",
                            alert_id=alert_id
                        )
                    st.session_state.alerts_sent.append({
                        'number': number,
                        'timestamp': datetime.now(),
                        'status': 'sent'
                    })
                except Exception as e:
                    st.error(f"Failed to send SMS to {number}: {str(e)}")

            st.success(f"Alert created and notifications sent to {total_recipients} recipients")
        else:
            st.success("Alert created successfully!")

# Evacuation Response Tracking Dashboard
st.subheader("📊 Evacuation Response Dashboard")
if st.session_state.evacuation_data:
    for alert_id, data in st.session_state.evacuation_data.items():
        with st.expander(f"Alert: {data['message']} - {data['location']}"):
            response_rate = (data['confirmed'] / data['total'] * 100) if data['total'] > 0 else 0

            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Recipients", data['total'])
            with col2:
                st.metric("Confirmed Evacuations", data['confirmed'])
            with col3:
                st.metric("Response Rate", f"{response_rate:.1f}%")

            # Progress bar for visual representation
            st.progress(response_rate/100)

            # Resource allocation recommendations
            if response_rate < 50:
                st.warning(f"""
                ⚠️ Low response rate detected in {data['location']}

                Recommended actions:
                1. Deploy additional emergency vehicles: {max(2, (data['total'] - data['confirmed']) // 50)}
                2. Set up emergency relief camps: {max(1, (data['total'] - data['confirmed']) // 100)}
                3. Mobilize emergency personnel: {max(5, (data['total'] - data['confirmed']) // 20)}
                4. Establish emergency communication centers
                """)

            # Demo: Simulate evacuation responses
            if demo_mode:
                if st.button(f"Simulate Evacuation Response (Alert {alert_id})", key=f"sim_{alert_id}"):
                    data['confirmed'] += min(
                        1,
                        data['total'] - data['confirmed']
                    )
                    st.rerun()  # Using st.rerun() instead of st.experimental_rerun()

# Alert Statistics
st.subheader("📈 Alert Statistics")
col1, col2 = st.columns(2)

with col1:
    # Severity distribution
    severity_counts = alerts['severity'].value_counts()
    fig = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title="Alerts by Severity",
        color_discrete_map={
            'High': '#D32F2F',
            'Medium': '#FFC107',
            'Low': '#388E3C'
        }
    )
    st.plotly_chart(fig)

with col2:
    st.markdown("### Alert Summary")
    st.metric("Total Active Alerts", len(alerts))
    st.metric("High Priority Alerts", len(alerts[alerts['severity'] == 'High']))
    st.metric("Medium Priority Alerts", len(alerts[alerts['severity'] == 'Medium']))

# Recent Alerts List
st.subheader("🔔 Recent Alerts")
for _, alert in alerts.iterrows():
    severity_class = f"alert-{alert['severity'].lower()}"
    st.markdown(
        f"""<div class="disaster-alert {severity_class}">
            <strong>{alert['severity']}</strong>: {alert['message']}
            <br>Location: {alert['location']}
            <br><small>{alert['timestamp']}</small>
        </div>""",
        unsafe_allow_html=True
    )

# Add CSS for better visualization
st.markdown("""
<style>
.evacuation-stats {
    padding: 1rem;
    background-color: #f0f2f6;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)