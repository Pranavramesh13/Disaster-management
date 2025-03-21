import streamlit as st
import plotly.express as px
from utils.data_generator import generate_resource_data
from utils.resource_optimizer import ResourceOptimizer
import numpy as np
import pandas as pd

st.set_page_config(page_title="Resource Management", page_icon="📦")

st.title("📦 Resource Management")

# Initialize resource optimizer
optimizer = ResourceOptimizer()

# Resource data
resources = st.session_state.get('resource_data', generate_resource_data())

# Get evacuation and alert data
evacuation_data = st.session_state.get('evacuation_data', {})
alerts = st.session_state.get('alert_data', {})

# Resource allocation
st.subheader("Resource Allocation")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Current Inventory")
    for resource, quantity in resources.items():
        st.metric(resource, quantity)

with col2:
    st.markdown("### Resource Distribution")
    fig = px.pie(
        values=list(resources.values()),
        names=list(resources.keys()),
        title="Resource Distribution"
    )
    st.plotly_chart(fig)

# Optimized Resource Allocation
if evacuation_data and alerts:
    st.subheader("🎯 Optimized Resource Allocation")

    # Get optimized allocations
    optimized_allocations = optimizer.optimize_allocation(
        available_resources=resources,
        alerts=alerts,
        evacuation_data=evacuation_data
    )

    # Calculate efficiency metrics
    efficiency_metrics = optimizer.calculate_efficiency_metrics(
        optimized_allocations,
        resources
    )

    # Display efficiency metrics
    st.markdown("### Resource Allocation Efficiency")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Resource Utilization",
            f"{efficiency_metrics['resource_utilization']:.1%}"
        )
    with col2:
        st.metric(
            "Allocation Balance",
            f"{efficiency_metrics['allocation_balance']:.1%}"
        )
    with col3:
        st.metric(
            "Coverage Ratio",
            f"{efficiency_metrics['coverage_ratio']:.1%}"
        )

    # Display allocations by location
    st.markdown("### Allocation by Location")
    for alert_id, allocation in optimized_allocations.items():
        location = alerts[alert_id]['location']
        response_rate = (
            evacuation_data[alert_id]['confirmed'] /
            evacuation_data[alert_id]['total']
        ) if evacuation_data[alert_id]['total'] > 0 else 0

        with st.expander(f"📍 {location} (Response Rate: {response_rate:.1%})"):
            # Create allocation visualization
            allocation_df = pd.DataFrame({
                'Resource': list(allocation.keys()),
                'Allocated': list(allocation.values()),
                'Available': [resources[r] for r in allocation.keys()]
            })

            fig = px.bar(
                allocation_df,
                x='Resource',
                y=['Allocated', 'Available'],
                title=f"Resource Allocation for {location}",
                barmode='group'
            )
            st.plotly_chart(fig)

            # Display allocation details
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Allocated Resources")
                for resource, amount in allocation.items():
                    st.metric(resource, amount)

            with col2:
                st.markdown("#### Optimization Factors")
                st.markdown(f"""
                - Population: {evacuation_data[alert_id]['total']}
                - Confirmed Evacuations: {evacuation_data[alert_id]['confirmed']}
                - Response Rate: {response_rate:.1%}
                - Severity: {alerts[alert_id]['severity']}
                """)

# Resource request form
st.subheader("Request Resources")
with st.form("resource_request"):
    resource_type = st.selectbox("Resource Type", list(resources.keys()))
    quantity = st.number_input("Quantity", min_value=1)
    location = st.text_input("Delivery Location")
    priority = st.select_slider("Priority", options=["Low", "Medium", "High"])

    # Show evacuation data if available for the location
    matching_evac_data = [
        data for data in evacuation_data.values() 
        if data['location'].lower() == location.lower()
    ]

    if matching_evac_data:
        data = matching_evac_data[0]
        st.info(f"""
        📊 Evacuation Status for {location}:
        - Confirmed Evacuees: {data['confirmed']}
        - Unconfirmed Residents: {data['total'] - data['confirmed']}
        - Response Rate: {(data['confirmed'] / data['total'] * 100):.1f}%
        """)

    if st.form_submit_button("Submit Request"):
        # Update resource inventory
        if resources[resource_type] >= quantity:
            resources[resource_type] -= quantity
            st.session_state.resource_data = resources
            st.success(f"Request submitted for {quantity} {resource_type}(s) to {location}")
        else:
            st.error(f"Insufficient {resource_type} in inventory")

# Inventory alerts
for resource, quantity in resources.items():
    if quantity < 100:  # Threshold for low inventory
        st.warning(f"⚠️ Low inventory alert: {resource} ({quantity} remaining)")

# Add CSS for better visualization
st.markdown("""
<style>
.allocation-metrics {
    padding: 1rem;
    background-color: #f0f2f6;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)