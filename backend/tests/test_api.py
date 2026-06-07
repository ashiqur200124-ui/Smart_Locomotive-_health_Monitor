"""
Unit and Integration Tests for Smart Locomotive Health Monitor Backend
Using pytest framework
"""

import pytest
import json
from datetime import datetime, timedelta
import sys
import os

# Force testing configuration before importing the app
os.environ.setdefault('FLASK_ENV', 'testing')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app_v2 import app, db, alert_system, fuzzy_analyzer, failure_predictor
from models.database import Locomotive, HealthRecord, Alert, User, FailurePrediction
from utils.auth import AuthManager
from utils.data_utils import DataLoader


@pytest.fixture
def client():
    """Create Flask test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.session.remove()
        try:
            db.engine.dispose()
        except Exception:
            pass
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_token(client):
    """Create test user and get auth token"""
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=AuthManager.hash_password('testpass'),
            full_name='Test User',
            role='USER'
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthManager.generate_token(user.id)
        return f'Bearer {token}'


@pytest.fixture
def admin_token(client):
    """Create admin user and get auth token"""
    with app.app_context():
        # Create admin user
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=AuthManager.hash_password('adminpass'),
            full_name='Admin User',
            role='ADMIN'
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthManager.generate_token(user.id)
        return f'Bearer {token}'


@pytest.fixture
def test_locomotive():
    """Create test locomotive"""
    with app.app_context():
        loco = Locomotive(
            id='BR1001',
            name='Rajdhani Express',
            depot_name='Dhaka Depot',
            acquired_year=2015,
            total_mileage=150000,
            status='ACTIVE',
            health_score=80.0,
            current_risk=20.0,
            latitude=23.7275,
            longitude=90.4086
        )
        db.session.add(loco)
        db.session.commit()
        return loco


# ==================== Authentication Tests ====================

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'full_name': 'New User'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'token' in data
        assert data['user']['username'] == 'newuser'
    
    def test_register_duplicate_username(self, client, auth_token):
        """Test registering with duplicate username"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_login_success(self, client, auth_token):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'token' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401
    
    def test_get_profile(self, client, auth_token):
        """Test getting user profile"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['user']['username'] == 'testuser'
    
    def test_profile_without_token(self, client):
        """Test accessing profile without token"""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401


# ==================== Locomotive Tests ====================

class TestLocomotives:
    """Test locomotive endpoints"""
    
    def test_get_locomotives(self, client, auth_token, test_locomotive):
        """Test getting list of locomotives"""
        response = client.get(
            '/api/locomotives',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['locomotives']) > 0
    
    def test_get_locomotive_detail(self, client, auth_token, test_locomotive):
        """Test getting locomotive details"""
        response = client.get(
            '/api/locomotives/BR1001',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['locomotive']['id'] == 'BR1001'
        assert data['locomotive']['name'] == 'Rajdhani Express'
    
    def test_get_nonexistent_locomotive(self, client, auth_token):
        """Test getting nonexistent locomotive"""
        response = client.get(
            '/api/locomotives/NONEXISTENT',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 404
    
    def test_create_locomotive(self, client, admin_token):
        """Test creating new locomotive"""
        response = client.post(
            '/api/locomotives',
            json={
                'id': 'BR2001',
                'name': 'Express Train',
                'depot_name': 'Chittagong Depot',
                'acquired_year': 2018,
                'total_mileage': 120000
            },
            headers={'Authorization': admin_token}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['locomotive']['id'] == 'BR2001'
    
    def test_create_locomotive_duplicate(self, client, admin_token, test_locomotive):
        """Test creating locomotive with duplicate ID"""
        response = client.post(
            '/api/locomotives',
            json={
                'id': 'BR1001',
                'name': 'Duplicate Train'
            },
            headers={'Authorization': admin_token}
        )
        
        assert response.status_code == 409


# ==================== Health Analysis Tests ====================

class TestHealthAnalysis:
    """Test health analysis endpoints"""
    
    def test_analyze_health_success(self, client, auth_token, test_locomotive):
        """Test successful health analysis"""
        response = client.post(
            '/api/health/BR1001',
            json={
                'temperature': 85.5,
                'vibration': 5.2,
                'pressure': 150,
                'oil_quality': 25,
                'mileage': 150000,
                'latitude': 23.7275,
                'longitude': 90.4086
            },
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'analysis' in data
        assert 'risk_score' in data['analysis']
        assert 'health_score' in data['analysis']
    
    def test_analyze_health_invalid_data(self, client, auth_token, test_locomotive):
        """Test health analysis with invalid sensor data"""
        response = client.post(
            '/api/health/BR1001',
            json={
                'temperature': -100,  # Invalid
                'vibration': 5.2,
                'pressure': 150,
                'oil_quality': 25,
                'mileage': 150000
            },
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 400
    
    def test_analyze_nonexistent_locomotive(self, client, auth_token):
        """Test analyzing nonexistent locomotive"""
        response = client.post(
            '/api/health/NONEXISTENT',
            json={
                'temperature': 85.5,
                'vibration': 5.2,
                'pressure': 150,
                'oil_quality': 25,
                'mileage': 150000
            },
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 404
    
    def test_get_health_history(self, client, auth_token, test_locomotive):
        """Test getting health analysis history"""
        # First add a health record
        with app.app_context():
            record = HealthRecord(
                locomotive_id='BR1001',
                temperature=85.5,
                vibration=5.2,
                pressure=150,
                oil_quality=25,
                mileage=150000,
                risk_score=35.0,
                health_score=65.0,
                risk_category='MEDIUM',
                component_risks={'engine': 0.3, 'braking': 0.2}
            )
            db.session.add(record)
            db.session.commit()
        
        response = client.get(
            '/api/health/BR1001/history',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['records']) > 0


# ==================== Alert Tests ====================

class TestAlerts:
    """Test alert endpoints"""
    
    def test_get_alerts(self, client, auth_token, test_locomotive):
        """Test getting alerts"""
        # Create test alert
        with app.app_context():
            alert = Alert(
                locomotive_id='BR1001',
                title='Engine Temperature High',
                message='Temperature exceeds threshold',
                severity='WARNING',
                category='ENGINE'
            )
            db.session.add(alert)
            db.session.commit()
        
        response = client.get(
            '/api/alerts/BR1001',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['alerts']) > 0
    
    def test_acknowledge_alert(self, client, auth_token, test_locomotive):
        """Test acknowledging alert"""
        # Create test alert
        alert_id = None
        with app.app_context():
            alert = Alert(
                locomotive_id='BR1001',
                title='Test Alert',
                message='Test message',
                severity='INFO',
                category='ENGINE'
            )
            db.session.add(alert)
            db.session.commit()
            alert_id = alert.id
        
        response = client.put(
            f'/api/alerts/{alert_id}/acknowledge',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['alert']['is_acknowledged'] == True
    
    def test_resolve_alert(self, client, auth_token, test_locomotive):
        """Test resolving alert"""
        # Create test alert
        alert_id = None
        with app.app_context():
            alert = Alert(
                locomotive_id='BR1001',
                title='Test Alert',
                message='Test message',
                severity='WARNING',
                category='ENGINE'
            )
            db.session.add(alert)
            db.session.commit()
            alert_id = alert.id
        
        response = client.put(
            f'/api/alerts/{alert_id}/resolve',
            json={'resolution': 'Issue fixed'},
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['alert']['resolution'] == 'Issue fixed'


# ==================== Dashboard Tests ====================

class TestDashboard:
    """Test dashboard endpoints"""
    
    def test_get_dashboard_summary(self, client, auth_token, test_locomotive):
        """Test getting dashboard summary"""
        response = client.get(
            '/api/summary',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'summary' in data
        assert 'total_locomotives' in data['summary']
        assert 'average_health' in data['summary']


# ==================== Data Validation Tests ====================

class TestDataValidation:
    """Test data validation utilities"""
    
    def test_validate_sensor_data_valid(self):
        """Test validating valid sensor data"""
        data_loader = DataLoader()
        sensor_data = {
            'temperature': 85.5,
            'vibration': 5.2,
            'pressure': 150,
            'oil_quality': 25,
            'mileage': 150000
        }
        
        is_valid, errors = data_loader.validate_sensor_data(sensor_data)
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_sensor_data_invalid_temperature(self):
        """Test validating sensor data with invalid temperature"""
        data_loader = DataLoader()
        sensor_data = {
            'temperature': -50,  # Invalid
            'vibration': 5.2,
            'pressure': 150,
            'oil_quality': 25,
            'mileage': 150000
        }
        
        is_valid, errors = data_loader.validate_sensor_data(sensor_data)
        assert is_valid == False


# ==================== Fuzzy Logic Tests ====================

class TestFuzzyLogic:
    """Test fuzzy logic analyzer"""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        fuzzy = fuzzy_analyzer
        sensor_data = {
            'temperature': 85.5,
            'vibration': 5.2,
            'pressure': 150,
            'oil_quality': 25,
            'mileage': 150000
        }
        
        risk_score, component_risks = fuzzy.calculate_risk_score(sensor_data)
        
        assert isinstance(risk_score, (int, float))
        assert 0 <= risk_score <= 100
        assert isinstance(component_risks, dict)
        assert len(component_risks) > 0
    
    def test_get_risk_category(self):
        """Test risk category determination"""
        fuzzy = fuzzy_analyzer
        
        assert fuzzy.get_risk_category(15) == 'LOW'
        assert fuzzy.get_risk_category(45) == 'MEDIUM'
        assert fuzzy.get_risk_category(75) == 'HIGH'
        assert fuzzy.get_risk_category(95) == 'CRITICAL'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
