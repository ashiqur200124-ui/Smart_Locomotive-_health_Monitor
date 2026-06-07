"""
Database models for Smart Locomotive Health Monitor
Uses SQLAlchemy ORM for PostgreSQL support
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Locomotive(db.Model):
    """Locomotive database model"""
    __tablename__ = 'locomotives'
    
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    depot_name = db.Column(db.String(100))
    acquired_year = db.Column(db.Integer)
    total_mileage = db.Column(db.Float)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, MAINTENANCE
    health_score = db.Column(db.Float, default=100.0)
    current_risk = db.Column(db.Float, default=0.0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='locomotive', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='locomotive', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'depot_name': self.depot_name,
            'acquired_year': self.acquired_year,
            'total_mileage': self.total_mileage,
            'status': self.status,
            'health_score': self.health_score,
            'current_risk': self.current_risk,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class HealthRecord(db.Model):
    """Health analysis records for locomotives"""
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    locomotive_id = db.Column(db.String(20), db.ForeignKey('locomotives.id'), nullable=False)
    
    # Sensor data
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float)
    pressure = db.Column(db.Float)
    oil_quality = db.Column(db.Float)
    mileage = db.Column(db.Float)
    
    # Analysis results
    risk_score = db.Column(db.Float)
    health_score = db.Column(db.Float)
    risk_category = db.Column(db.String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Component-specific risks (stored as JSON)
    component_risks = db.Column(db.JSON, default={})
    recommendations = db.Column(db.JSON, default=[])
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'locomotive_id': self.locomotive_id,
            'temperature': self.temperature,
            'vibration': self.vibration,
            'pressure': self.pressure,
            'oil_quality': self.oil_quality,
            'mileage': self.mileage,
            'risk_score': self.risk_score,
            'health_score': self.health_score,
            'risk_category': self.risk_category,
            'component_risks': self.component_risks,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat()
        }


class Alert(db.Model):
    """Alert system for locomotives"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    locomotive_id = db.Column(db.String(20), db.ForeignKey('locomotives.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    severity = db.Column(db.String(20), nullable=False)  # INFO, WARNING, CRITICAL, EMERGENCY
    category = db.Column(db.String(50))  # ENGINE, BRAKING, COUPLING, WHEELS, BOILER
    
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.String(100))
    acknowledged_at = db.Column(db.DateTime)
    
    resolution = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'locomotive_id': self.locomotive_id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'category': self.category,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolution': self.resolution,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class User(db.Model):
    """User authentication model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    
    role = db.Column(db.String(20), default='USER')  # ADMIN, MANAGER, TECHNICIAN, USER
    department = db.Column(db.String(100))
    
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }
        if include_email:
            data['email'] = self.email
        return data


class FailurePrediction(db.Model):
    """Failure predictions for locomotive components"""
    __tablename__ = 'failure_predictions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    locomotive_id = db.Column(db.String(20), db.ForeignKey('locomotives.id'), nullable=False)
    
    component = db.Column(db.String(50), nullable=False)  # ENGINE, BRAKING, COUPLING, WHEELS, BOILER
    failure_probability = db.Column(db.Float)  # 0-1
    hours_to_failure = db.Column(db.Float)  # Estimated hours
    confidence_score = db.Column(db.Float)  # 0-1 confidence
    
    status = db.Column(db.String(20), default='PENDING')  # PENDING, MONITORED, RESOLVED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'locomotive_id': self.locomotive_id,
            'component': self.component,
            'failure_probability': self.failure_probability,
            'hours_to_failure': self.hours_to_failure,
            'confidence_score': self.confidence_score,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class MaintenanceSchedule(db.Model):
    """Maintenance schedule tracking"""
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    locomotive_id = db.Column(db.String(20), db.ForeignKey('locomotives.id'), nullable=False)
    
    maintenance_type = db.Column(db.String(100), nullable=False)  # Preventive, Corrective, Predictive
    component = db.Column(db.String(50))
    
    scheduled_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime)
    
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    
    priority = db.Column(db.String(20))  # LOW, MEDIUM, HIGH, URGENT
    status = db.Column(db.String(20), default='SCHEDULED')  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    
    notes = db.Column(db.Text)
    performed_by = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'locomotive_id': self.locomotive_id,
            'maintenance_type': self.maintenance_type,
            'component': self.component,
            'scheduled_date': self.scheduled_date.isoformat(),
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'priority': self.priority,
            'status': self.status,
            'notes': self.notes,
            'performed_by': self.performed_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
