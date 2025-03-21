import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from utils.data_generator import generate_disaster_data, generate_resource_data

st.set_page_config(page_title="Interactive Map", page_icon="🗺️", layout="wide")

st.title("🗺️ Interactive Disaster Management Map")

# Initialize map centered on India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Get data from session state or generate new
disasters = st.session_state.get('disaster_data', generate_disaster_data())
resources = st.session_state.get('resource_data', generate_resource_data())
alerts = st.session_state.get('alert_data', {})
evacuation_data = st.session_state.get('evacuation_data', {})

# Sidebar controls
st.sidebar.header("Map Controls")
show_disasters = st.sidebar.checkbox("Show Disaster Zones", True)
show_resources = st.sidebar.checkbox("Show Resource Locations", True)
show_evacuation = st.sidebar.checkbox("Show Evacuation Routes", True)

# City coordinates (example data)
city_coords = {
    'Mumbai': [19.0760, 72.8777],
    'Delhi': [28.6139, 77.2090],
    'Chennai': [13.0827, 80.2707],
    'Kolkata': [22.5726, 88.3639]
}

# Add disaster zones
if show_disasters:
    for _, disaster in disasters.iterrows():
        if disaster['location'] in city_coords:
            color = {
                'High': 'red',
                'Medium': 'orange',
                'Low': 'green'
            }.get(disaster['severity'], 'gray')
            
            folium.Circle(
                location=city_coords[disaster['location']],
                radius=50000,  # 50km radius
                color=color,
                fill=True,
                popup=f"""
                <b>{disaster['disaster_type']}</b><br>
                Location: {disaster['location']}<br>
                Severity: {disaster['severity']}<br>
                Risk Score: {disaster['risk_score']:.2f}
                """
            ).add_to(m)

# Add resource markers
if show_resources:
    for location, coords in city_coords.items():
        # Add marker for each resource type
        resource_info = "<b>Available Resources</b><br>"
        for resource, quantity in resources.items():
            resource_info += f"{resource}: {quantity}<br>"
        
        folium.Marker(
            coords,
            popup=folium.Popup(resource_info, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

# Add evacuation routes
if show_evacuation and evacuation_data:
    for alert_id, data in evacuation_data.items():
        if data['location'] in city_coords:
            # Create evacuation route (example: straight line to nearest safe zone)
            start = city_coords[data['location']]
            # Example: Create a safe point 50km east
            end = [start[0], start[1] + 0.5]
            
            folium.PolyLine(
                locations=[start, end],
                color='green',
                weight=2,
                popup=f"""
                <b>Evacuation Route</b><br>
                Location: {data['location']}<br>
                Evacuees: {data['confirmed']}/{data['total']}<br>
                Response Rate: {(data['confirmed']/data['total']*100):.1f}%
                """
            ).add_to(m)

# Display map
st.markdown("### Real-time Disaster Management Map")
folium_static(m)

# Map Legend
st.markdown("""
### Map Legend
- 🔴 Red Circles: High-risk disaster zones
- 🟡 Orange Circles: Medium-risk disaster zones
- 🟢 Green Circles: Low-risk disaster zones
- 📍 Blue Markers: Resource locations
- 📍 Green Lines: Evacuation routes
""")

# Statistics and Information
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Active Disaster Zones")
    for _, disaster in disasters.iterrows():
        severity_color = {
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(disaster['severity'], '⚪')
        st.markdown(f"{severity_color} {disaster['location']}: {disaster['disaster_type']}")

with col2:
    st.markdown("### Resource Distribution")
    for resource, quantity in resources.items():
        st.metric(resource, quantity)
