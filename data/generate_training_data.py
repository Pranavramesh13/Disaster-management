import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_training_dataset(n_samples=1000):
    """
    Generate a training dataset with clear patterns for disaster prediction
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Initialize arrays
    data = []
    
    # Define conditions for each disaster type
    disaster_conditions = {
        'flood': {
            'rainfall': (300, 500),  # Heavy rainfall
            'temperature': (20, 30),
            'seismic_activity': (0, 3),
            'wind_speed': (0, 30)
        },
        'earthquake': {
            'rainfall': (0, 100),
            'temperature': (15, 35),
            'seismic_activity': (7, 10),  # High seismic activity
            'wind_speed': (0, 30)
        },
        'cyclone': {
            'rainfall': (100, 200),
            'temperature': (25, 35),
            'seismic_activity': (0, 3),
            'wind_speed': (80, 120)  # High wind speed
        },
        'landslide': {
            'rainfall': (200, 300),
            'temperature': (20, 30),
            'seismic_activity': (4, 6),
            'wind_speed': (0, 30)
        }
    }
    
    # Generate samples for each disaster type
    for disaster_type, conditions in disaster_conditions.items():
        n_type_samples = n_samples // 4  # Equal distribution
        
        for _ in range(n_type_samples):
            sample = {
                'rainfall': np.random.uniform(*conditions['rainfall']),
                'temperature': np.random.uniform(*conditions['temperature']),
                'seismic_activity': np.random.uniform(*conditions['seismic_activity']),
                'wind_speed': np.random.uniform(*conditions['wind_speed']),
                'disaster_type': disaster_type
            }
            data.append(sample)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add some noise to make the data more realistic
    df['rainfall'] += np.random.normal(0, 5, len(df))
    df['temperature'] += np.random.normal(0, 2, len(df))
    df['seismic_activity'] += np.random.normal(0, 0.3, len(df))
    df['wind_speed'] += np.random.normal(0, 3, len(df))
    
    # Ensure values are within realistic ranges
    df['rainfall'] = df['rainfall'].clip(0, 500)
    df['temperature'] = df['temperature'].clip(-20, 50)
    df['seismic_activity'] = df['seismic_activity'].clip(0, 10)
    df['wind_speed'] = df['wind_speed'].clip(0, 120)
    
    # Convert disaster type to numeric
    disaster_map = {'flood': 0, 'earthquake': 1, 'cyclone': 2, 'landslide': 3}
    df['disaster_type'] = df['disaster_type'].map(disaster_map)
    
    # Save to CSV
    output_path = 'data/training_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Dataset generated and saved to {output_path}")
    print("\nSample data:")
    print(df.head())
    print("\nSummary statistics:")
    print(df.describe())
    print("\nDisaster type distribution:")
    print(df['disaster_type'].value_counts())
    
    return df

if __name__ == "__main__":
    generate_training_dataset()
