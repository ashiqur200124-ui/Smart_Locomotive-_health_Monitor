"""
Smart Locomotive Health Monitor - Flask Backend API (v2)
With PostgreSQL Database Integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import csv
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Import custom modules
from config import get_config
from models.database import db, Locomotive, HealthRecord, Alert, User, FailurePrediction, MaintenanceSchedule
from models.fuzzy_logic import FuzzyLogicRiskAnalyzer
from models.failure_predictor import FailurePredictor
from models.location_finder import LocationFinder
from utils.alerts import AlertManager as AlertSystemManager, AlertSeverity
from utils.auth import AuthManager, token_required, role_required
from utils.data_utils import DataLoader, DataValidator, ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize extensions
db.init_app(app)
CORS(app)

# Initialize analysis components
fuzzy_analyzer = FuzzyLogicRiskAnalyzer()
failure_predictor = FailurePredictor()
location_finder = LocationFinder()
alert_system = AlertSystemManager()
data_loader = DataLoader()

# ==================== Authentication Routes ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=AuthManager.hash_password(data['password']),
        full_name=data.get('full_name', ''),
        role='USER',
        department=data.get('department', '')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = AuthManager.generate_token(user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict(include_email=True)
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not AuthManager.verify_password(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'User account is inactive'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    token = AuthManager.generate_token(user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict(include_email=True)
    }), 200


@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile"""
    return jsonify({
        'status': 'success',
        'user': request.user.to_dict(include_email=True)
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (invalidate token)"""
    # In production, add token to blacklist or use token revocation
    return jsonify({
        'status': 'success',
        'message': 'Logout successful'
    }), 200


# ==================== Locomotive Routes ====================

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'service': 'Smart Locomotive Health Monitor',
        'version': '2.0.0',
        'database': 'PostgreSQL',
        'status': 'ACTIVE',
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'profile': 'GET /api/auth/profile'
            },
            'locomotives': {
                'list': 'GET /api/locomotives',
                'detail': 'GET /api/locomotives/<id>',
                'create': 'POST /api/locomotives',
                'update': 'PUT /api/locomotives/<id>'
            },
            'health': {
                'analyze': 'POST /api/health/<id>',
                'history': 'GET /api/health/<id>/history'
            },
            'alerts': {
                'list': 'GET /api/alerts/<id>',
                'acknowledge': 'PUT /api/alerts/<id>/acknowledge',
                'resolve': 'PUT /api/alerts/<id>/resolve'
            },
            'predictions': {
                'list': 'GET /api/predictions/<id>',
                'detail': 'GET /api/predictions/<id>/<component>'
            },
            'maintenance': {
                'schedule': 'GET /api/maintenance/<id>',
                'create': 'POST /api/maintenance/<id>'
            }
        }
    })


@app.route('/api/locomotives', methods=['GET'])
@token_required
def get_locomotives():
    """Get all locomotives"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)
    
    query = Locomotive.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'status': 'success',
        'count': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'locomotives': [loco.to_dict() for loco in pagination.items]
    }), 200


@app.route('/api/locomotives/<loco_id>', methods=['GET'])
@token_required
def get_locomotive(loco_id):
    """Get single locomotive"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    # Get latest health record
    latest_health = HealthRecord.query.filter_by(locomotive_id=loco_id).order_by(
        HealthRecord.created_at.desc()
    ).first()
    
    # Get active alerts
    active_alerts = Alert.query.filter_by(
        locomotive_id=loco_id,
        resolved_at=None
    ).all()
    
    data = locomotive.to_dict()
    data['latest_health'] = latest_health.to_dict() if latest_health else None
    data['active_alerts'] = len(active_alerts)
    
    return jsonify({
        'status': 'success',
        'locomotive': data
    }), 200


@app.route('/api/locomotives', methods=['POST'])
@token_required
@role_required('ADMIN', 'MANAGER')
def create_locomotive():
    """Create new locomotive"""
    data = request.get_json()
    
    if Locomotive.query.get(data.get('id')):
        return jsonify({'error': 'Locomotive ID already exists'}), 409
    
    locomotive = Locomotive(
        id=data['id'],
        name=data.get('name', ''),
        depot_name=data.get('depot_name', ''),
        acquired_year=data.get('acquired_year'),
        total_mileage=data.get('total_mileage', 0),
        status='ACTIVE',
        latitude=data.get('latitude', 23.7275),
        longitude=data.get('longitude', 90.4086)
    )
    
    db.session.add(locomotive)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Locomotive created',
        'locomotive': locomotive.to_dict()
    }), 201


@app.route('/api/locomotives/<loco_id>', methods=['PUT'])
@token_required
@role_required('ADMIN', 'MANAGER')
def update_locomotive(loco_id):
    """Update locomotive"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    data = request.get_json()
    
    for key in ['name', 'depot_name', 'status', 'latitude', 'longitude']:
        if key in data:
            setattr(locomotive, key, data[key])
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'locomotive': locomotive.to_dict()
    }), 200


# ==================== Health Analysis Routes ====================

@app.route('/api/health/<loco_id>', methods=['POST'])
@token_required
def analyze_health(loco_id):
    """Analyze locomotive health"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    sensor_data = request.get_json()
    
    # Validate sensor data
    is_valid, errors = data_loader.validate_sensor_data(sensor_data)
    if not is_valid:
        return jsonify({'status': 'error', 'errors': errors}), 400
    
    # Perform analysis
    risk_score, component_risks = fuzzy_analyzer.calculate_risk_score(sensor_data)
    risk_category = fuzzy_analyzer.get_risk_category(risk_score)
    health_score = 100 - risk_score
    
    # Get failure predictions
    component_failures = failure_predictor.predict_failures(
        sensor_data, component_risks
    )
    
    # Create health record
    health_record = HealthRecord(
        locomotive_id=loco_id,
        temperature=sensor_data['temperature'],
        vibration=sensor_data['vibration'],
        pressure=sensor_data['pressure'],
        oil_quality=sensor_data['oil_quality'],
        mileage=sensor_data['mileage'],
        risk_score=risk_score,
        health_score=health_score,
        risk_category=risk_category,
        component_risks=component_risks,
        recommendations=data_loader.get_maintenance_recommendations(
            component_risks, component_failures
        )
    )
    
    db.session.add(health_record)
    
    # Update locomotive
    locomotive.health_score = health_score
    locomotive.current_risk = risk_score
    locomotive.latitude = sensor_data.get('latitude', locomotive.latitude)
    locomotive.longitude = sensor_data.get('longitude', locomotive.longitude)
    
    # Generate alerts if needed
    for component, risk in component_risks.items():
        if risk > 0.7:
            severity = AlertSeverity.CRITICAL if risk > 0.85 else AlertSeverity.WARNING
            alert = Alert(
                locomotive_id=loco_id,
                title=f'{component} Risk Alert',
                message=f'{component} risk score: {risk:.2%}',
                severity=severity,
                category=component
            )
            db.session.add(alert)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'analysis': {
            'risk_score': risk_score,
            'health_score': health_score,
            'risk_category': risk_category,
            'component_risks': component_risks,
            'component_failures': component_failures,
            'recommendations': health_record.recommendations,
            'timestamp': health_record.created_at.isoformat()
        }
    }), 200


@app.route('/api/health/<loco_id>/history', methods=['GET'])
@token_required
def get_health_history(loco_id):
    """Get health analysis history"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = HealthRecord.query.filter_by(locomotive_id=loco_id).order_by(
        HealthRecord.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'status': 'success',
        'count': pagination.total,
        'records': [record.to_dict() for record in pagination.items]
    }), 200


# ==================== Alerts Routes ====================

@app.route('/api/alerts/<loco_id>', methods=['GET'])
@token_required
def get_alerts(loco_id):
    """Get locomotive alerts"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'
    severity = request.args.get('severity', None)
    
    query = Alert.query.filter_by(locomotive_id=loco_id)
    
    if not include_resolved:
        query = query.filter(Alert.resolved_at == None)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'count': len(alerts),
        'alerts': [alert.to_dict() for alert in alerts]
    }), 200


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['PUT'])
@token_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    alert = Alert.query.get(alert_id)
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.is_acknowledged = True
    alert.acknowledged_by = request.user.username
    alert.acknowledged_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'alert': alert.to_dict()
    }), 200


@app.route('/api/alerts/<alert_id>/resolve', methods=['PUT'])
@token_required
def resolve_alert(alert_id):
    """Resolve an alert"""
    data = request.get_json()
    alert = Alert.query.get(alert_id)
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.resolution = data.get('resolution', '')
    alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'alert': alert.to_dict()
    }), 200


# ==================== Predictions Routes ====================

@app.route('/api/predictions/<loco_id>', methods=['GET'])
@token_required
def get_predictions(loco_id):
    """Get failure predictions for locomotive"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    predictions = FailurePrediction.query.filter_by(locomotive_id=loco_id).all()
    
    return jsonify({
        'status': 'success',
        'count': len(predictions),
        'predictions': [pred.to_dict() for pred in predictions]
    }), 200


@app.route('/api/predictions/<loco_id>/<component>', methods=['GET'])
@token_required
def get_component_prediction(loco_id, component):
    """Get prediction for specific component"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    prediction = FailurePrediction.query.filter_by(
        locomotive_id=loco_id,
        component=component
    ).first()
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    return jsonify({
        'status': 'success',
        'prediction': prediction.to_dict()
    }), 200


# ==================== Maintenance Routes ====================

@app.route('/api/maintenance/<loco_id>', methods=['GET'])
@token_required
def get_maintenance_schedule(loco_id):
    """Get maintenance schedule"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    status = request.args.get('status', None)
    
    query = MaintenanceSchedule.query.filter_by(locomotive_id=loco_id)
    
    if status:
        query = query.filter_by(status=status)
    
    schedules = query.order_by(MaintenanceSchedule.scheduled_date).all()
    
    return jsonify({
        'status': 'success',
        'count': len(schedules),
        'schedules': [schedule.to_dict() for schedule in schedules]
    }), 200


@app.route('/api/maintenance/<loco_id>', methods=['POST'])
@token_required
@role_required('ADMIN', 'MANAGER', 'TECHNICIAN')
def create_maintenance(loco_id):
    """Create maintenance schedule"""
    locomotive = Locomotive.query.get(loco_id)
    
    if not locomotive:
        return jsonify({'error': 'Locomotive not found'}), 404
    
    data = request.get_json()
    
    schedule = MaintenanceSchedule(
        locomotive_id=loco_id,
        maintenance_type=data['maintenance_type'],
        component=data.get('component'),
        scheduled_date=datetime.fromisoformat(data['scheduled_date']),
        estimated_cost=data.get('estimated_cost'),
        priority=data.get('priority', 'MEDIUM'),
        notes=data.get('notes', '')
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'schedule': schedule.to_dict()
    }), 201


# ==================== Dashboard Routes ====================

@app.route('/api/summary', methods=['GET'])
@token_required
def get_dashboard_summary():
    """Get dashboard summary"""
    total_locomotives = Locomotive.query.count()
    active_locomotives = Locomotive.query.filter_by(status='ACTIVE').count()
    critical_alerts = Alert.query.filter_by(
        severity='CRITICAL',
        resolved_at=None
    ).count()
    emergency_alerts = Alert.query.filter_by(
        severity='EMERGENCY',
        resolved_at=None
    ).count()
    
    avg_health = db.session.query(db.func.avg(Locomotive.health_score)).scalar() or 0
    maintenance_due = MaintenanceSchedule.query.filter(
        MaintenanceSchedule.scheduled_date <= datetime.utcnow() + timedelta(days=7),
        MaintenanceSchedule.status == 'SCHEDULED'
    ).count()
    
    return jsonify({
        'status': 'success',
        'summary': {
            'total_locomotives': total_locomotives,
            'active_locomotives': active_locomotives,
            'critical_alerts': critical_alerts,
            'emergency_alerts': emergency_alerts,
            'average_health': round(avg_health, 2),
            'maintenance_due': maintenance_due,
            'timestamp': datetime.utcnow().isoformat()
        }
    }), 200


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f'Internal error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Database Management ====================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized')


@app.cli.command()
def load_initial_data():
    """Load initial locomotive data from CSV"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bangladesh_railways.csv')
    
    if not os.path.exists(csv_path):
        print(f'CSV file not found: {csv_path}')
        return
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not Locomotive.query.get(row['loco_id']):
                loco = Locomotive(
                    id=row['loco_id'],
                    name=row.get('loco_name', ''),
                    depot_name=row.get('depot_name', ''),
                    acquired_year=int(row.get('acquired_year', 0)) if row.get('acquired_year') else None,
                    total_mileage=float(row.get('total_mileage', 0)) if row.get('total_mileage') else 0,
                    status='ACTIVE'
                )
                db.session.add(loco)
    
    db.session.commit()
    print('Initial data loaded')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
