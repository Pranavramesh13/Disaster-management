# Disaster Management System

A machine learning-powered disaster management system built with Streamlit.

## Project Setup in VS Code

### 1. Prerequisites
- Python 3.11 installed
- Visual Studio Code with Python extension
- Git (optional, for version control)

### 2. Setup Steps

1. Create a new project directory:
```bash
mkdir disaster-management-system
cd disaster-management-system
```

2. Create project structure:
```
├── assets/
│   └── custom.css           # Custom styling
├── pages/
│   ├── 01_predictions.py    # ML predictions page
│   ├── 02_resources.py      # Resource management
│   └── 03_alerts.py         # Alert system
├── utils/
│   ├── data_generator.py    # Data generation utilities
│   ├── ml_predictor.py      # ML model implementation
│   └── mock_ml.py          # Mock ML functions
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── main.py                 # Main application file
```

3. Install required packages:
```bash
pip install streamlit pandas numpy plotly scikit-learn joblib
```

4. Configuration:
- Create `.streamlit/config.toml` with the following content:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#D32F2F"
backgroundColor = "#F5F5F5"
secondaryBackgroundColor = "#1976D2"
textColor = "#212121"
font = "sans serif"
```

### 3. Running the Application

1. Open the project folder in VS Code:
```bash
code .
```

2. Start the Streamlit server:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:5000`

## Features
- Real-time disaster prediction using machine learning
- Resource management and tracking
- Alert system with severity levels
- Interactive data visualization
- Custom data upload and model training
- Random Forest model for disaster prediction

## Current Implementation
- ML model using scikit-learn Random Forest Classifier
- Interactive data upload and training interface
- Real-time predictions based on environmental factors
- Feature importance visualization
- Model performance metrics

## Note
The ML model is configured to handle four types of disasters:
- Floods (0)
- Earthquakes (1)
- Cyclones (2)
- Landslides (3)

Required data format for training:
- rainfall (mm)
- temperature (Celsius)
- seismic_activity (Richter scale)
- wind_speed (m/s)
- disaster_type (0-3)