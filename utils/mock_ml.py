import numpy as np
from datetime import datetime, timedelta

class DisasterPredictor:
    def predict_disasters(self, location):
        """Mock ML prediction for disaster probability"""
        disasters = {
            'Flood': np.random.random(),
            'Earthquake': np.random.random(),
            'Cyclone': np.random.random(),
            'Landslide': np.random.random()
        }
        return disasters

    def get_risk_factors(self, location):
        """Generate mock risk factors"""
        return {
            'Rainfall': np.random.randint(0, 100),
            'Wind Speed': np.random.randint(0, 150),
            'Seismic Activity': np.random.randint(0, 10),
            'Temperature': np.random.randint(20, 45)
        }

    def get_historical_data(self, location):
        """Generate mock historical disaster data"""
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]
        values = np.random.random(30)
        return dates, values
