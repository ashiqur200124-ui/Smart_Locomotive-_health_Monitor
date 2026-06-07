"""
Automatic Alert System for Locomotive Health Monitoring
Generates and manages real-time alerts for critical conditions
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List
import json

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class AlertType(Enum):
    """Types of alerts"""
    SENSOR_ANOMALY = "SENSOR_ANOMALY"
    COMPONENT_FAILURE = "COMPONENT_FAILURE"
    MAINTENANCE_DUE = "MAINTENANCE_DUE"
    OPERATIONAL_DEVIATION = "OPERATIONAL_DEVIATION"
    LOCATION_ADVISORY = "LOCATION_ADVISORY"
    PREDICTIVE_WARNING = "PREDICTIVE_WARNING"

class Alert:
    """Individual alert object"""
    
    def __init__(self, loco_id: str, alert_type: AlertType, severity: AlertSeverity, 
                 message: str, component: str = None, action_required: str = None):
        self.alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.loco_id = loco_id
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.component = component
        self.action_required = action_required
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.resolved = False
        self.escalation_count = 0
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'loco_id': self.loco_id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'component': self.component,
            'action_required': self.action_required,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'escalation_count': self.escalation_count
        }

class AlertManager:
    """Manages alert generation, storage, and escalation"""
    
    def __init__(self):
        self.active_alerts: Dict[str, List[Alert]] = {}  # loco_id -> list of alerts
        self.alert_history: List[Alert] = []
        self.escalation_rules = self._initialize_escalation_rules()
        self.notification_channels = ['dashboard', 'email', 'sms']
    
    def _initialize_escalation_rules(self) -> Dict:
        """Define how alerts escalate over time"""
        return {
            AlertSeverity.INFO: {'escalate_after': 3600, 'escalate_to': AlertSeverity.WARNING},
            AlertSeverity.WARNING: {'escalate_after': 900, 'escalate_to': AlertSeverity.CRITICAL},
            AlertSeverity.CRITICAL: {'escalate_after': 300, 'escalate_to': AlertSeverity.EMERGENCY},
            AlertSeverity.EMERGENCY: {'escalate_after': 0, 'escalate_to': None}
        }
    
    def create_alert(self, loco_id: str, alert_type: AlertType, severity: AlertSeverity,
                    message: str, component: str = None, action_required: str = None) -> Alert:
        """Create and register a new alert"""
        alert = Alert(loco_id, alert_type, severity, message, component, action_required)
        
        if loco_id not in self.active_alerts:
            self.active_alerts[loco_id] = []
        
        self.active_alerts[loco_id].append(alert)
        self.alert_history.append(alert)
        
        return alert
    
    def generate_alerts_from_risk_analysis(self, loco_id: str, risk_score: float, 
                                          component_risks: Dict, recommendations: List[str]) -> List[Alert]:
        """Generate alerts based on fuzzy logic risk analysis"""
        alerts = []
        
        # Overall risk alert
        if risk_score > 75:
            alert = self.create_alert(
                loco_id,
                AlertType.PREDICTIVE_WARNING,
                AlertSeverity.CRITICAL if risk_score > 85 else AlertSeverity.WARNING,
                f"Risk score {risk_score:.1f}% - Locomotive health compromised",
                action_required="Schedule immediate maintenance"
            )
            alerts.append(alert)
        
        # Component-specific alerts
        for component, risk_value in component_risks.items():
            if risk_value > 70:
                severity = AlertSeverity.CRITICAL if risk_value > 85 else AlertSeverity.WARNING
                alert = self.create_alert(
                    loco_id,
                    AlertType.SENSOR_ANOMALY,
                    severity,
                    f"{component.upper()} risk level {risk_value:.1f}%",
                    component=component,
                    action_required=self._get_component_action(component, risk_value)
                )
                alerts.append(alert)
        
        return alerts
    
    def generate_alerts_from_predictions(self, loco_id: str, predictions: Dict, 
                                       health_score: Dict) -> List[Alert]:
        """Generate alerts based on failure predictions"""
        alerts = []
        
        # Check each component's failure probability
        for component, pred in predictions.items():
            if pred['status'] == 'RISKY':
                hours_left = pred['hours_to_failure']
                
                if hours_left < 12:
                    severity = AlertSeverity.EMERGENCY
                    message = f"{component.upper()} FAILURE IMMINENT - {hours_left} hours estimated"
                elif hours_left < 50:
                    severity = AlertSeverity.CRITICAL
                    message = f"{component.upper()} may fail in {hours_left} hours"
                else:
                    severity = AlertSeverity.WARNING
                    message = f"{component.upper()} showing failure indicators"
                
                alert = self.create_alert(
                    loco_id,
                    AlertType.COMPONENT_FAILURE,
                    severity,
                    message,
                    component=component,
                    action_required=f"Arrange {component} maintenance/replacement"
                )
                alerts.append(alert)
        
        # Overall health alert
        if health_score['immediate_action_needed']:
            alert = self.create_alert(
                loco_id,
                AlertType.MAINTENANCE_DUE,
                AlertSeverity.EMERGENCY,
                "CRITICAL: Multiple component failures predicted",
                action_required="Locomotive must be taken to maintenance shed immediately"
            )
            alerts.append(alert)
        
        return alerts
    
    def get_active_alerts(self, loco_id: str, severity_filter: AlertSeverity = None) -> List[Dict]:
        """Get all active alerts for a locomotive"""
        if loco_id not in self.active_alerts:
            return []
        
        active = [a for a in self.active_alerts[loco_id] if not a.resolved]
        
        if severity_filter:
            active = [a for a in active if a.severity == severity_filter]
        
        return [a.to_dict() for a in active]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alerts_list in self.active_alerts.values():
            for alert in alerts_list:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alerts_list in self.active_alerts.values():
            for alert in alerts_list:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    return True
        return False
    
    def check_escalation(self) -> List[Alert]:
        """Check and escalate alerts if necessary"""
        escalated_alerts = []
        current_time = datetime.now()
        
        for alerts_list in self.active_alerts.values():
            for alert in alerts_list:
                if alert.resolved or alert.acknowledged:
                    continue
                
                time_since_creation = (current_time - alert.timestamp).total_seconds()
                rules = self.escalation_rules.get(alert.severity)
                
                if rules and rules['escalate_after'] > 0 and time_since_creation > rules['escalate_after']:
                    if rules['escalate_to']:
                        alert.severity = rules['escalate_to']
                        alert.escalation_count += 1
                        escalated_alerts.append(alert)
        
        return escalated_alerts
    
    def _get_component_action(self, component: str, risk_value: float) -> str:
        """Get recommended action for component"""
        actions_map = {
            'temperature': "Check cooling system and radiator",
            'vibration': "Inspect bearings and wheel alignment",
            'pressure': "Service hydraulic/pneumatic systems",
            'oil_quality': "Replace engine oil and filter",
            'mileage': "Schedule comprehensive overhaul"
        }
        return actions_map.get(component, "Schedule maintenance inspection")
    
    def get_alert_summary(self, loco_id: str) -> Dict:
        """Get alert summary for a locomotive"""
        if loco_id not in self.active_alerts:
            return {
                'total_active': 0,
                'emergency': 0,
                'critical': 0,
                'warning': 0,
                'info': 0,
                'acknowledged': 0
            }
        
        alerts_list = [a for a in self.active_alerts[loco_id] if not a.resolved]
        
        summary = {
            'total_active': len(alerts_list),
            'emergency': len([a for a in alerts_list if a.severity == AlertSeverity.EMERGENCY]),
            'critical': len([a for a in alerts_list if a.severity == AlertSeverity.CRITICAL]),
            'warning': len([a for a in alerts_list if a.severity == AlertSeverity.WARNING]),
            'info': len([a for a in alerts_list if a.severity == AlertSeverity.INFO]),
            'acknowledged': len([a for a in alerts_list if a.acknowledged])
        }
        
        return summary
    
    def export_alerts_json(self, loco_id: str) -> str:
        """Export alerts as JSON"""
        alerts = self.get_active_alerts(loco_id)
        return json.dumps(alerts, indent=2)
