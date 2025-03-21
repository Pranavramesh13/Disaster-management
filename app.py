import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
from utils.data_generator import generate_resource_data, generate_alert_data
from utils.ml_predictor import DisasterPredictor
from utils.sms_handler import SMSHandler
import pandas as pd
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
for directory in ['data', 'models', 'templates/errors']:
    os.makedirs(directory, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize predictor
try:
    logger.info("Initializing DisasterPredictor...")
    predictor = DisasterPredictor()
    if predictor.model is None:
        logger.info("No existing model found. Generating and training with sample data...")
        X, y = predictor.generate_sample_data()
        predictor.train(X, y)
    logger.info("DisasterPredictor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DisasterPredictor: {str(e)}", exc_info=True)
    predictor = None

# Initialize SMS handler
try:
    logger.info("Initializing SMSHandler...")
    sms_handler = SMSHandler()
    logger.info("SMSHandler initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SMSHandler: {str(e)}", exc_info=True)
    sms_handler = None

class SessionData:
    def __init__(self):
        self.alerts = []
        self.resources = generate_resource_data()
        self.evacuation_data = {}

session_data = SessionData()

@app.route('/')
def index():
    try:
        logger.info("Rendering index page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@app.route('/predictions')
def predictions():
    try:
        logger.info("Rendering predictions page")
        if predictor is None or predictor.model is None:
            return render_template('predictions.html', error="ML Predictor not available")
        return render_template('predictions.html')
    except Exception as e:
        logger.error(f"Error in predictions route: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if predictor is None or predictor.model is None:
            raise ValueError("ML Predictor not initialized")

        data = request.json
        logger.info(f"Prediction request data: {data}")

        input_data = pd.DataFrame({
            'rainfall': [float(data['rainfall'])],
            'temperature': [float(data['temperature'])],
            'seismic_activity': [float(data['seismic_activity'])],
            'wind_speed': [float(data['wind_speed'])]
        })

        result = predictor.predict(input_data)
        logger.info(f"Prediction result: {result}")

        # Check for high-risk predictions (probability > 0.7)
        high_risk_disasters = {k: v for k, v in result.items() if v > 0.7}
        alerts_info = []
        message_ids = []  # Track message IDs for display

        if high_risk_disasters:
            alert_id = str(uuid.uuid4())
            location = data['location']

            # Phone numbers for testing
            phone_numbers = {
                'Mumbai': ['+919742342120', '+916362171135'],
                'Delhi': ['+919742342120', '+916362171135'],
                'Chennai': ['+919742342120', '+916362171135'],
                'Kolkata': ['+919742342120', '+916362171135']
            }

            if location in phone_numbers:
                for disaster, probability in high_risk_disasters.items():
                    alert_message = (
                        f"🚨 EMERGENCY ALERT: {probability:.1%} risk of {disaster.upper()} "
                        f"predicted in {location}!\n"
                        f"• Take immediate precautions\n"
                        f"• Follow evacuation guidelines if issued\n"
                        f"• Reply YES to confirm you are safe\n"
                        f"• Alert ID: {alert_id}\n"
                        f"• Stay tuned for updates"
                    )

                    # Create alert record
                    alert = {
                        'id': alert_id,
                        'message': alert_message,
                        'location': location,
                        'severity': 'High',
                        'timestamp': str(datetime.now()),
                        'disaster_type': disaster,
                        'probability': probability,
                        'recipients': len(phone_numbers[location]),
                        'confirmed_safe': 0
                    }
                    session_data.alerts.append(alert)
                    alerts_info.append(alert)

                    # Send SMS to all numbers in the location
                    if sms_handler:
                        for phone_number in phone_numbers[location]:
                            try:
                                message_id = sms_handler.send_alert(
                                    to_number=phone_number,
                                    message=alert_message,
                                    alert_id=alert_id
                                )
                                message_ids.append(message_id)  # Store message ID
                                logger.info(f"Alert SMS sent to {phone_number}, Message ID: {message_id}")
                            except Exception as e:
                                logger.error(f"Error sending alert to {phone_number}: {str(e)}")
                                message_ids.append(None)  # Add None for failed messages

        return jsonify({
            'success': True,
            'predictions': result,
            'alerts_sent': bool(high_risk_disasters),
            'alerts_info': alerts_info,
            'message_ids': message_ids  # Include message IDs in response
        })
    except Exception as e:
        logger.error(f"Error in predict route: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/alerts')
def alerts():
    try:
        logger.info("Rendering alerts page")
        # Calculate confirmation statistics
        for alert in session_data.alerts:
            if 'confirmation_stats' not in alert:
                alert['confirmation_stats'] = {
                    'total_sent': alert.get('recipients', 0),
                    'confirmed': alert.get('confirmed_safe', 0),
                    'pending': alert.get('recipients', 0) - alert.get('confirmed_safe', 0)
                }

        return render_template('alerts.html', 
                             alerts=session_data.alerts,
                             evacuation_data=session_data.evacuation_data)
    except Exception as e:
        logger.error(f"Error in alerts route: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@app.route('/api/confirm-safe', methods=['POST'])
def confirm_safe():
    try:
        data = request.json
        alert_id = data.get('alert_id')
        phone_number = data.get('phone_number')

        logger.info(f"Received safety confirmation for alert {alert_id} from {phone_number}")

        # Find and update the alert
        for alert in session_data.alerts:
            if alert['id'] == alert_id:
                alert['confirmed_safe'] = alert.get('confirmed_safe', 0) + 1
                alert['confirmation_stats'] = {
                    'total_sent': alert.get('recipients', 0),
                    'confirmed': alert['confirmed_safe'],
                    'pending': alert.get('recipients', 0) - alert['confirmed_safe']
                }
                logger.info(f"Updated confirmation count for alert {alert_id}: {alert['confirmed_safe']}")

                # Simulate random confirmations for demo purposes
                if alert['confirmed_safe'] == 1:  # First real confirmation triggers simulation
                    for sim_phone in ['+919742342120', '+916362171135']:
                        if sim_phone != phone_number:  # Don't simulate for the actual confirming number
                            alert['confirmed_safe'] += 1
                            logger.info(f"Simulated confirmation from {sim_phone}")

                return jsonify({
                    'success': True,
                    'message': 'Safety confirmation recorded',
                    'alert': alert
                })

        raise ValueError(f"Alert {alert_id} not found")

    except Exception as e:
        logger.error(f"Error in confirm-safe route: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/resources')
def resources():
    try:
        logger.info("Rendering resources page")
        return render_template('resources.html', resources=session_data.resources)
    except Exception as e:
        logger.error(f"Error in resources route: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@app.route('/maps')
def maps():
    try:
        logger.info("Rendering maps page")
        return render_template('maps.html')
    except Exception as e:
        logger.error(f"Error in maps route: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}", exc_info=True)
        raise