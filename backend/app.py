"""
Smart Locomotive Health Monitor - Flask Backend API
Provides RESTful API for predictive maintenance and health monitoring
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import csv
import os

# Import our custom modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.fuzzy_logic import FuzzyLogicRiskAnalyzer
from models.failure_predictor import FailurePredictor
from models.location_finder import LocationFinder
from utils.alerts import AlertManager, AlertType, AlertSeverity
from utils.data_utils import DataLoader, DataValidator, ReportGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
fuzzy_analyzer = FuzzyLogicRiskAnalyzer()
failure_predictor = FailurePredictor()
location_finder = LocationFinder()
alert_manager = AlertManager()
data_loader = DataLoader()

# In-memory storage for sim (use database in production)
locomotive_database = {}
monitoring_history = {}

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'service': 'Smart Locomotive Health Monitor',
        'version': '1.0.0',
        'status': 'ACTIVE',
        'endpoints': {
            'locomotives': '/api/locomotives',
            'health_check': '/api/health/<loco_id>',
            'analysis': '/api/analysis/<loco_id>',
            'alerts': '/api/alerts/<loco_id>',
            'locations': '/api/locations/<loco_id>',
            'predictions': '/api/predictions/<loco_id>'
        }
    })

@app.route('/api/locomotives', methods=['GET'])
def get_locomotives():
    """Get all locomotives in the system"""
    # Load data from CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bangladesh_railways.csv')
    locos = data_loader.load_locomotive_data(csv_path)
    
    # Add health status for each
    for loco in locos:
        loco_id = loco['loco_id']
        if loco_id in locomotive_database:
            loco['current_risk'] = locomotive_database[loco_id].get('risk_score', 0)
            loco['health_score'] = locomotive_database[loco_id].get('health_score', 100)
        else:
            loco['current_risk'] = 0
            loco['health_score'] = 100
    
    return jsonify({
        'status': 'success',
        'count': len(locos),
        'locomotives': locos
    })

@app.route('/api/health/<loco_id>', methods=['POST'])
def check_locomotive_health(loco_id):
    """
    Analyze locomotive health from sensor data
    Expected JSON: {
        'temperature': float, 'vibration': float, 'pressure': float,
        'oil_quality': float, 'mileage': float, 'latitude': float, 'longitude': float
    }
    """
    try:
        sensor_data = request.get_json()
        
        if not sensor_data:
            return jsonify({'error': 'No sensor data provided'}), 400
        
        # Validate sensor data
        is_valid, errors = data_loader.validate_sensor_data(sensor_data)
        if not is_valid:
            return jsonify({'status': 'error', 'message': 'Invalid sensor input', 'errors': errors}), 400
        
        # Perform fuzzy logic analysis
        risk_score, component_risks = fuzzy_analyzer.calculate_risk_score(sensor_data)
        risk_category = fuzzy_analyzer.get_risk_category(risk_score)
        recommendations = fuzzy_analyzer.get_recommendations(risk_score, component_risks)
        
        # Perform failure predictions
        predictions = failure_predictor.predict_failure_probability(sensor_data)
        health_info = failure_predictor.get_overall_health_score(predictions)
        
        # Store in database
        locomotive_database[loco_id] = {
            'risk_score': risk_score,
            'health_score': health_info['health_score'],
            'timestamp': datetime.now(),
            'sensor_data': sensor_data,
            'predictions': predictions
        }
        
        # Generate alerts
        risk_alerts = alert_manager.generate_alerts_from_risk_analysis(
            loco_id, risk_score, component_risks, recommendations
        )
        prediction_alerts = alert_manager.generate_alerts_from_predictions(
            loco_id, predictions, health_info
        )
        
        # Add to history
        if loco_id not in monitoring_history:
            monitoring_history[loco_id] = []
        
        monitoring_history[loco_id].append({
            'timestamp': datetime.now(),
            'risk_score': risk_score,
            'health_score': health_info['health_score']
        })
        
        return jsonify({
            'status': 'success',
            'loco_id': loco_id,
            'risk_analysis': {
                'risk_score': round(risk_score, 2),
                'risk_category': risk_category,
                'component_risks': {k: round(v, 2) for k, v in component_risks.items()},
                'recommendations': recommendations
            },
            'health_status': {
                'health_score': round(health_info['health_score'], 2),
                'predicted_reliability': round(health_info['predicted_reliability'], 2),
                'components_at_risk': health_info['components_at_risk'],
                'immediate_action_needed': health_info['immediate_action_needed']
            },
            'failure_predictions': {
                comp: {
                    'probability': round(pred['probability'], 3),
                    'status': pred['status'],
                    'hours_to_failure': pred['hours_to_failure']
                }
                for comp, pred in predictions.items()
            },
            'alerts_generated': len(risk_alerts) + len(prediction_alerts),
            'active_alerts': alert_manager.get_active_alerts(loco_id)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analysis/<loco_id>', methods=['GET'])
def get_analysis(loco_id):
    """Get stored analysis for a locomotive"""
    
    if loco_id not in locomotive_database:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    data = locomotive_database[loco_id]
    
    return jsonify({
        'status': 'success',
        'loco_id': loco_id,
        'timestamp': data['timestamp'].isoformat(),
        'current_risk_score': data['risk_score'],
        'current_health_score': data['health_score'],
        'history_available': len(monitoring_history.get(loco_id, []))
    })

@app.route('/api/alerts/<loco_id>', methods=['GET'])
def get_alerts(loco_id):
    """Get all active alerts for a locomotive"""
    severity_filter = request.args.get('severity', None)
    
    alerts = alert_manager.get_active_alerts(loco_id)
    summary = alert_manager.get_alert_summary(loco_id)
    
    return jsonify({
        'status': 'success',
        'loco_id': loco_id,
        'alert_summary': summary,
        'active_alerts': alerts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/<loco_id>/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(loco_id, alert_id):
    """Acknowledge an alert"""
    success = alert_manager.acknowledge_alert(alert_id)
    
    return jsonify({
        'status': 'success' if success else 'failed',
        'alert_id': alert_id,
        'message': 'Alert acknowledged' if success else 'Alert not found'
    })

@app.route('/api/locations/<loco_id>', methods=['POST'])
def get_support_locations(loco_id):
    """Get nearest junctions and sheds for a locomotive"""
    try:
        location_data = request.get_json()
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        support_network = location_finder.get_support_network(latitude, longitude)
        
        return jsonify({
            'status': 'success',
            'loco_id': loco_id,
            'current_location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'support_network': support_network,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/predictions/<loco_id>', methods=['GET'])
def get_predictions(loco_id):
    """Get failure predictions for a locomotive"""
    
    if loco_id not in locomotive_database:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    predictions = locomotive_database[loco_id].get('predictions', {})
    
    # Calculate maintenance schedule
    schedule = ReportGenerator.generate_maintenance_schedule(predictions)
    
    return jsonify({
        'status': 'success',
        'loco_id': loco_id,
        'failure_predictions': predictions,
        'recommended_maintenance_schedule': schedule,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/report/<loco_id>', methods=['GET'])
def generate_report(loco_id):
    """Generate comprehensive health report for a locomotive"""
    
    if loco_id not in locomotive_database:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    data = locomotive_database[loco_id]
    predictions = data.get('predictions', {})
    alerts = alert_manager.get_active_alerts(loco_id)
    
    # Get location if available
    sensor_data = data.get('sensor_data', {})
    location_info = {}
    if 'latitude' in sensor_data and 'longitude' in sensor_data:
        location_info = location_finder.get_support_network(
            sensor_data['latitude'],
            sensor_data['longitude']
        )
    
    report = ReportGenerator.generate_health_report(
        loco_id,
        data['risk_score'],
        predictions,
        location_info,
        alerts
    )
    
    return jsonify(report)

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'OPERATIONAL',
        'timestamp': datetime.now().isoformat(),
        'locomotives_monitored': len(locomotive_database),
        'total_alerts': sum(len(alerts) for alerts in alert_manager.active_alerts.values()),
        'analysis_history_entries': sum(len(history) for history in monitoring_history.values()),
        'components': {
            'fuzzy_logic': 'ACTIVE',
            'failure_predictor': 'ACTIVE',
            'location_finder': 'ACTIVE',
            'alert_system': 'ACTIVE'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Smart Locomotive Health Monitor API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
