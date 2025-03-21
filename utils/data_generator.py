import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_disaster_data():
    """Generate mock disaster prediction data"""
    disasters = ['Flood', 'Earthquake', 'Cyclone', 'Landslide']
    locations = ['Maharashtra', 'Kerala', 'Gujarat', 'Tamil Nadu', 'West Bengal']
    
    data = []
    current_date = datetime.now()
    
    for i in range(50):
        date = current_date + timedelta(days=i)
        for location in locations:
            risk = np.random.random()
            disaster = np.random.choice(disasters)
            data.append({
                'date': date,
                'location': location,
                'disaster_type': disaster,
                'risk_score': risk,
                'severity': 'High' if risk > 0.7 else 'Medium' if risk > 0.4 else 'Low'
            })
    
    return pd.DataFrame(data)

def generate_resource_data():
    """Generate mock resource inventory data"""
    resources = {
        'Emergency Vehicles': np.random.randint(50, 100),
        'Medical Supplies (units)': np.random.randint(1000, 5000),
        'Relief Camps': np.random.randint(10, 30),
        'Food Supplies (kg)': np.random.randint(5000, 10000),
        'Water (liters)': np.random.randint(10000, 20000),
        'Emergency Personnel': np.random.randint(200, 500)
    }
    return resources

def generate_alert_data():
    """Generate mock alert data"""
    alerts = []
    severities = ['High', 'Medium', 'Low']
    current_time = datetime.now()
    
    for i in range(10):
        time = current_time - timedelta(hours=i)
        alerts.append({
            'timestamp': time,
            'message': f'Alert #{i+1}: {np.random.choice(["Flood warning", "Evacuation notice", "Weather alert"])}',
            'severity': np.random.choice(severities),
            'location': np.random.choice(['Mumbai', 'Chennai', 'Kolkata', 'Delhi'])
        })
    
    return pd.DataFrame(alerts)
