import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
import os
from datetime import datetime
from twilio.rest import Client
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DisasterPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = ['rainfall', 'temperature', 'seismic_activity', 'wind_speed']
        self.disaster_types = ['flood', 'earthquake', 'cyclone', 'landslide']
        self.contacts_data = pd.DataFrame()
        self.model_path = 'models/disaster_model.joblib'

        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)

        # Try to load training data and train model
        try:
            data = pd.read_csv('data/training_data.csv')
            logger.info("Loading training data from CSV")
            X = data[self.feature_columns]
            y = data['disaster_type']
            self.train(X, y)
        except Exception as e:
            logger.error(f"Could not load training data: {e}")
            logger.info("Generating sample data for training")
            X, y = self.generate_sample_data()
            self.train(X, y)

    def initialize_twilio(self):
        """Initialize Twilio client with proper error handling"""
        try:
            # Verify Twilio credentials
            if not all([
                os.environ.get('TWILIO_ACCOUNT_SID'),
                os.environ.get('TWILIO_AUTH_TOKEN'),
                os.environ.get('TWILIO_PHONE_NUMBER')
            ]):
                print("Missing Twilio credentials!")
                return False

            print("Initializing Twilio client with credentials:")
            print(f"Account SID exists: {bool(os.environ.get('TWILIO_ACCOUNT_SID'))}")
            print(f"Auth Token exists: {bool(os.environ.get('TWILIO_AUTH_TOKEN'))}")
            print(f"Phone Number exists: {bool(os.environ.get('TWILIO_PHONE_NUMBER'))}")

            self.twilio_client = Client(
                os.environ.get('TWILIO_ACCOUNT_SID'),
                os.environ.get('TWILIO_AUTH_TOKEN')
            )
            self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
            return True
        except Exception as e:
            print(f"Error initializing Twilio client: {str(e)}")
            return False

    def load_training_data(self):
        """Load training data from CSV file"""
        try:
            # Try to load from data/sample_training.csv first
            data_path = 'data/sample_training.csv'
            if not os.path.exists(data_path):
                data_path = 'data/training_data.csv'

            print(f"Loading training data from: {data_path}")
            data = pd.read_csv(data_path)

            # Store contact information
            if 'phone_number' in data.columns and 'location' in data.columns:
                self.contacts_data = data[['phone_number', 'location']].drop_duplicates()
                print(f"Loaded {len(self.contacts_data)} unique contacts:")
                print(self.contacts_data)
            else:
                print("Warning: No contact information found in training data")

            return data
        except Exception as e:
            print(f"Error loading training data: {str(e)}")
            return None

    def train(self, X, y):
        """Train the model with input data"""
        logger.info(f"Training model with data shape: {X.shape}")

        # Preprocess input data
        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # Initialize and train model
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            class_weight='balanced',
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # Calculate metrics
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Save the model
        self.save_model()

        logger.info(f"Model trained successfully. Train accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}")
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'feature_importance': dict(zip(self.feature_columns, 
                                    self.model.feature_importances_))
        }

    def predict(self, input_data):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained")

        # Preprocess input data
        X_scaled = self.scaler.transform(input_data[self.feature_columns])

        # Get prediction probabilities
        probabilities = self.model.predict_proba(X_scaled)[0]
        logger.info(f"Raw prediction probabilities: {probabilities}")

        # Create dictionary mapping disaster types to their probabilities
        predictions = {}
        for disaster_type, prob in zip(self.disaster_types, probabilities):
            predictions[disaster_type] = float(prob)
            logger.info(f"Prediction for {disaster_type}: {prob}")

        # Sort predictions by probability in descending order
        predictions = dict(sorted(predictions.items(), key=lambda x: x[1], reverse=True))
        return predictions

    def predict_and_alert(self, input_data, location):
        """Make predictions and send alerts if risk is high"""
        if self.model is None:
            print("Model not trained, loading training data...")
            data = self.load_training_data()
            if data is not None:
                self.train(data[self.feature_columns], data['disaster_type'])

        # Preprocess input data
        X = self.preprocess_data(input_data)

        # Get prediction probabilities
        probabilities = self.model.predict_proba(X)

        # Map predictions to disaster types
        disaster_types = ['flood', 'earthquake', 'cyclone', 'landslide']
        predictions = dict(zip(disaster_types, probabilities[0]))

        # Print predictions for debugging
        print(f"Predictions for {location}:", predictions)

        # Check for high-risk predictions and send alerts
        threshold = 0.7  # 70% probability threshold
        high_risk_disasters = [
            (disaster, prob) for disaster, prob in predictions.items() 
            if prob >= threshold
        ]

        print(f"High risk disasters: {high_risk_disasters}")
        print(f"Available contacts data:\n{self.contacts_data}")

        # Send alerts for high-risk predictions
        alerts_sent = []
        if high_risk_disasters and not self.contacts_data.empty:
            # Filter contacts by location
            location_contacts = self.contacts_data[
                self.contacts_data['location'] == location
            ]

            print(f"Found {len(location_contacts)} contacts in {location}")
            if len(location_contacts) == 0:
                print(f"No contacts found for location: {location}")
                print("Available locations:", self.contacts_data['location'].unique())

            for disaster, probability in high_risk_disasters:
                alert_id = str(uuid.uuid4())
                alert_message = (
                    f"🚨 EMERGENCY ALERT: {probability:.1%} risk of {disaster.upper()} "
                    f"predicted in {location}!\n"
                    f"• Take immediate precautions\n"
                    f"• Follow evacuation guidelines if issued\n"
                    f"• Reply YES to {alert_id} to confirm evacuation\n"
                    f"• Stay tuned for updates\n"
                    f"Emergency Contact: 112"
                )

                # Send alerts to all contacts in the location
                for _, contact in location_contacts.iterrows():
                    phone = contact['phone_number']
                    print(f"Attempting to send alert to {phone}")
                    try:
                        success = self.send_alert(phone, alert_message)
                        if success:
                            print(f"Successfully sent alert to {phone}")
                            alerts_sent.append({
                                'id': alert_id,
                                'phone': phone,
                                'message': alert_message,
                                'timestamp': datetime.now(),
                                'disaster_type': disaster,
                                'probability': probability,
                                'location': location,
                                'evacuation_status': 'pending'
                            })
                        else:
                            print(f"Failed to send alert to {phone}")
                    except Exception as e:
                        print(f"Error sending alert to {phone}: {str(e)}")

        return {
            'predictions': predictions,
            'alerts_sent': alerts_sent
        }

    def send_alert(self, phone_number, message):
        """Send SMS alert using Twilio"""
        try:
            print(f"Sending SMS via Twilio to {phone_number}")
            print(f"Using Twilio phone number: {self.twilio_phone}")

            # Ensure phone number is in E.164 format
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number

            # Remove any spaces or special characters
            phone_number = ''.join(filter(lambda x: x.isdigit() or x == '+', phone_number))

            print(f"Formatted phone number: {phone_number}")

            # Verify Twilio client initialization
            if not self.twilio_client:
                print("Reinitializing Twilio client...")
                if not self.initialize_twilio():
                    print("Failed to initialize Twilio client")
                    return False

            # Print Twilio credentials status (without revealing actual values)
            print("Twilio Configuration Status:")
            print(f"Account SID exists: {bool(os.environ.get('TWILIO_ACCOUNT_SID'))}")
            print(f"Auth Token exists: {bool(os.environ.get('TWILIO_AUTH_TOKEN'))}")
            print(f"Phone Number exists: {bool(self.twilio_phone)}")

            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )

            print(f"SMS sent successfully. Message SID: {message.sid}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            if hasattr(e, 'code'):
                print(f"Twilio Error Code: {e.code}")
            if hasattr(e, 'msg'):
                print(f"Twilio Error Message: {e.msg}")
            return False

    def save_model(self):
        """Save the trained model"""
        try:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'disaster_types': self.disaster_types
            }, self.model_path)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Load a trained model if it exists"""
        try:
            if os.path.exists(self.model_path):
                saved_model = joblib.load(self.model_path)
                self.model = saved_model['model']
                self.scaler = saved_model['scaler']
                self.feature_columns = saved_model['feature_columns']
                self.disaster_types = saved_model.get('disaster_types', 
                    ['flood', 'earthquake', 'cyclone', 'landslide'])
                logger.info("Model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
        return False

    def preprocess_data(self, data):
        """Preprocess input data"""
        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required feature: {col}")

        # Scale features
        return self.scaler.fit_transform(data[self.feature_columns])

    def generate_sample_data(self):
        """Generate synthetic data for training"""
        np.random.seed(42)
        n_samples = 1000

        # Initialize arrays for features
        rainfall = np.zeros(n_samples)
        temperature = np.zeros(n_samples)
        seismic_activity = np.zeros(n_samples)
        wind_speed = np.zeros(n_samples)
        labels = np.zeros(n_samples)

        # Generate data in chunks to ensure clear patterns
        chunk_size = n_samples // 4

        # Flood conditions (high rainfall)
        rainfall[:chunk_size] = np.random.uniform(300, 500, chunk_size)
        temperature[:chunk_size] = np.random.uniform(20, 30, chunk_size)
        seismic_activity[:chunk_size] = np.random.uniform(0, 3, chunk_size)
        wind_speed[:chunk_size] = np.random.uniform(0, 30, chunk_size)
        labels[:chunk_size] = 0  # Flood

        # Earthquake conditions (high seismic activity)
        rainfall[chunk_size:2*chunk_size] = np.random.uniform(0, 100, chunk_size)
        temperature[chunk_size:2*chunk_size] = np.random.uniform(15, 35, chunk_size)
        seismic_activity[chunk_size:2*chunk_size] = np.random.uniform(7, 10, chunk_size)
        wind_speed[chunk_size:2*chunk_size] = np.random.uniform(0, 30, chunk_size)
        labels[chunk_size:2*chunk_size] = 1  # Earthquake

        # Cyclone conditions (high wind speed)
        rainfall[2*chunk_size:3*chunk_size] = np.random.uniform(100, 200, chunk_size)
        temperature[2*chunk_size:3*chunk_size] = np.random.uniform(25, 35, chunk_size)
        seismic_activity[2*chunk_size:3*chunk_size] = np.random.uniform(0, 3, chunk_size)
        wind_speed[2*chunk_size:3*chunk_size] = np.random.uniform(80, 120, chunk_size)
        labels[2*chunk_size:3*chunk_size] = 2  # Cyclone

        # Landslide conditions (combination of rainfall and seismic)
        rainfall[3*chunk_size:] = np.random.uniform(200, 300, chunk_size)
        temperature[3*chunk_size:] = np.random.uniform(20, 30, chunk_size)
        seismic_activity[3*chunk_size:] = np.random.uniform(4, 6, chunk_size)
        wind_speed[3*chunk_size:] = np.random.uniform(0, 30, chunk_size)
        labels[3*chunk_size:] = 3  # Landslide

        X = pd.DataFrame({
            'rainfall': rainfall,
            'temperature': temperature,
            'seismic_activity': seismic_activity,
            'wind_speed': wind_speed
        })

        return X, labels