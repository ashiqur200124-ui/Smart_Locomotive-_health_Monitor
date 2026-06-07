"""
Real-time Features for Smart Locomotive Health Monitor
Includes WebSocket for live dashboard updates and MQTT for IoT sensor integration
"""

import json
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import os
from models.database import db, Locomotive, HealthRecord, Alert
from models.fuzzy_logic import FuzzyLogicRiskAnalyzer
from utils.data_utils import DataLoader

class RealtimeManager:
    """Manages WebSocket and MQTT connections for real-time updates"""
    
    def __init__(self, app=None):
        """
        Initialize real-time manager
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.socketio = None
        self.mqtt_client = None
        self.fuzzy_analyzer = FuzzyLogicRiskAnalyzer()
        self.data_loader = DataLoader()
        self.connected_clients = {}
        
    def init_socketio(self, app):
        """Initialize SocketIO for WebSocket"""
        self.socketio = SocketIO(
            app,
            cors_allowed_origins=['*'],
            async_mode='threading',
            ping_timeout=60,
            ping_interval=25
        )
        
        self.setup_socketio_events()
        return self.socketio
    
    def setup_socketio_events(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def on_connect():
            client_id = request.sid
            self.connected_clients[client_id] = {
                'connected_at': datetime.utcnow(),
                'subscribed_locomotives': set()
            }
            emit('connection_response', {
                'data': 'Connected to real-time server',
                'client_id': client_id
            })
        
        @self.socketio.on('disconnect')
        def on_disconnect():
            client_id = request.sid
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
        
        @self.socketio.on('subscribe_locomotive')
        def on_subscribe(data):
            """Subscribe to locomotive updates"""
            client_id = request.sid
            loco_id = data.get('loco_id')
            
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['subscribed_locomotives'].add(loco_id)
                join_room(f'locomotive_{loco_id}')
                emit('subscription_confirmed', {'loco_id': loco_id})
        
        @self.socketio.on('unsubscribe_locomotive')
        def on_unsubscribe(data):
            """Unsubscribe from locomotive updates"""
            client_id = request.sid
            loco_id = data.get('loco_id')
            
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['subscribed_locomotives'].discard(loco_id)
                leave_room(f'locomotive_{loco_id}')
                emit('unsubscription_confirmed', {'loco_id': loco_id})
    
    def init_mqtt(self, broker=None, port=1883, username=None, password=None):
        """
        Initialize MQTT client for sensor data
        
        Args:
            broker: MQTT broker address
            port: MQTT broker port
            username: MQTT username
            password: MQTT password
        """
        broker = broker or os.getenv('MQTT_BROKER', 'mqtt.example.com')
        username = username or os.getenv('MQTT_USERNAME', '')
        password = password or os.getenv('MQTT_PASSWORD', '')
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
        
        try:
            self.mqtt_client.connect(broker, port, keepalive=60)
            self.mqtt_client.loop_start()
            return True
        except Exception as e:
            print(f'MQTT connection failed: {str(e)}')
            return False
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            print('MQTT Connected successfully')
            topic = os.getenv('MQTT_TOPIC', 'locomotives/+/sensors')
            client.subscribe(topic)
        else:
            print(f'MQTT connection failed with code {rc}')
    
    def on_mqtt_message(self, client, userdata, msg):
        """
        Handle MQTT messages from sensors
        Expected topic format: locomotives/<loco_id>/sensors
        Expected payload: JSON with sensor data
        """
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split('/')
            
            if len(topic_parts) >= 2:
                loco_id = topic_parts[1]
                self.process_sensor_data(loco_id, payload)
        except Exception as e:
            print(f'MQTT message processing error: {str(e)}')
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            print(f'MQTT disconnected with code {rc}')
    
    def process_sensor_data(self, loco_id, sensor_data):
        """
        Process incoming sensor data and broadcast updates
        
        Args:
            loco_id: Locomotive ID
            sensor_data: Dict with sensor readings
        """
        try:
            with self.app.app_context():
                # Validate sensor data
                is_valid, errors = self.data_loader.validate_sensor_data(sensor_data)
                if not is_valid:
                    print(f'Invalid sensor data for {loco_id}: {errors}')
                    return
                
                # Get locomotive
                locomotive = Locomotive.query.get(loco_id)
                if not locomotive:
                    print(f'Locomotive {loco_id} not found')
                    return
                
                # Perform analysis
                risk_score, component_risks = self.fuzzy_analyzer.calculate_risk_score(sensor_data)
                health_score = 100 - risk_score
                
                # Create health record
                health_record = HealthRecord(
                    locomotive_id=loco_id,
                    temperature=sensor_data.get('temperature'),
                    vibration=sensor_data.get('vibration'),
                    pressure=sensor_data.get('pressure'),
                    oil_quality=sensor_data.get('oil_quality'),
                    mileage=sensor_data.get('mileage'),
                    risk_score=risk_score,
                    health_score=health_score,
                    risk_category=self.fuzzy_analyzer.get_risk_category(risk_score),
                    component_risks=component_risks
                )
                
                # Update locomotive
                locomotive.health_score = health_score
                locomotive.current_risk = risk_score
                locomotive.updated_at = datetime.utcnow()
                
                # Generate alerts if critical
                for component, risk in component_risks.items():
                    if risk > 0.85:
                        alert = Alert(
                            locomotive_id=loco_id,
                            title=f'{component} Critical Risk',
                            message=f'Component risk: {risk:.2%}',
                            severity='CRITICAL',
                            category=component
                        )
                        db.session.add(alert)
                
                db.session.add(health_record)
                db.session.commit()
                
                # Broadcast to WebSocket clients
                self.broadcast_locomotive_update(loco_id, {
                    'locomotive_id': loco_id,
                    'health_score': health_score,
                    'risk_score': risk_score,
                    'risk_category': self.fuzzy_analyzer.get_risk_category(risk_score),
                    'component_risks': component_risks,
                    'timestamp': datetime.utcnow().isoformat(),
                    'sensor_data': {
                        'temperature': sensor_data.get('temperature'),
                        'vibration': sensor_data.get('vibration'),
                        'pressure': sensor_data.get('pressure'),
                        'oil_quality': sensor_data.get('oil_quality'),
                        'mileage': sensor_data.get('mileage')
                    }
                })
                
        except Exception as e:
            print(f'Error processing sensor data: {str(e)}')
    
    def broadcast_locomotive_update(self, loco_id, data):
        """
        Broadcast locomotive update to all WebSocket clients
        
        Args:
            loco_id: Locomotive ID
            data: Update data
        """
        if self.socketio:
            self.socketio.emit(
                'locomotive_update',
                data,
                room=f'locomotive_{loco_id}'
            )
    
    def broadcast_alert(self, loco_id, alert_data):
        """Broadcast alert to WebSocket clients"""
        if self.socketio:
            self.socketio.emit(
                'alert_generated',
                alert_data,
                room=f'locomotive_{loco_id}'
            )
    
    def broadcast_dashboard_update(self, summary_data):
        """Broadcast dashboard summary update"""
        if self.socketio:
            self.socketio.emit('dashboard_update', summary_data, room='dashboard_subscribers')
    
    def get_connected_clients_count(self):
        """Get number of connected WebSocket clients"""
        return len(self.connected_clients)
    
    def stop(self):
        """Stop real-time services"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


class SensorDataSimulator:
    """Simulates sensor data for testing without real IoT devices"""
    
    @staticmethod
    def generate_sensor_data(loco_id, degradation=0):
        """
        Generate realistic sensor data with optional degradation
        
        Args:
            loco_id: Locomotive ID
            degradation: Degradation factor (0-1) for failure simulation
        
        Returns:
            Dict with sensor data
        """
        import random
        
        base_values = {
            'temperature': 75 + random.randint(-5, 10),
            'vibration': 4.5 + random.randint(-2, 3),
            'pressure': 150 + random.randint(-10, 10),
            'oil_quality': 30 + random.randint(-5, 5),
            'mileage': 100000 + random.randint(-50000, 50000)
        }
        
        # Apply degradation if specified
        if degradation > 0:
            base_values['temperature'] += int(30 * degradation)
            base_values['vibration'] += int(8 * degradation)
            base_values['pressure'] -= int(30 * degradation)
            base_values['oil_quality'] -= int(20 * degradation)
        
        base_values['latitude'] = 23.7275 + random.uniform(-0.5, 0.5)
        base_values['longitude'] = 90.4086 + random.uniform(-0.5, 0.5)
        
        return base_values
    
    @staticmethod
    def start_simulation(realtime_manager, loco_ids, interval=10, duration=None):
        """
        Start sensor data simulation
        
        Args:
            realtime_manager: RealtimeManager instance
            loco_ids: List of locomotive IDs to simulate
            interval: Interval between messages in seconds
            duration: Total duration in seconds (None = infinite)
        """
        import time
        
        elapsed = 0
        while duration is None or elapsed < duration:
            for loco_id in loco_ids:
                sensor_data = SensorDataSimulator.generate_sensor_data(loco_id)
                realtime_manager.process_sensor_data(loco_id, sensor_data)
            
            time.sleep(interval)
            elapsed += interval


class RealtimeHealthMonitor:
    """Unified real-time health monitoring dashboard"""
    
    def __init__(self, realtime_manager):
        """Initialize health monitor"""
        self.realtime_manager = realtime_manager
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def start_monitoring(self, update_interval=5):
        """
        Start continuous health monitoring
        
        Args:
            update_interval: Update interval in seconds
        """
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(update_interval,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self, update_interval):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                with self.realtime_manager.app.app_context():
                    # Get fleet statistics
                    total_locomotives = Locomotive.query.count()
                    active_locomotives = Locomotive.query.filter_by(status='ACTIVE').count()
                    
                    critical_alerts = Alert.query.filter(
                        Alert.resolved_at == None,
                        Alert.severity.in_(['CRITICAL', 'EMERGENCY'])
                    ).count()
                    
                    avg_health = db.session.query(
                        db.func.avg(Locomotive.health_score)
                    ).scalar() or 0
                    
                    # Broadcast dashboard update
                    self.realtime_manager.broadcast_dashboard_update({
                        'total_locomotives': total_locomotives,
                        'active_locomotives': active_locomotives,
                        'critical_alerts': critical_alerts,
                        'average_health': round(avg_health, 2),
                        'connected_clients': self.realtime_manager.get_connected_clients_count(),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    import time
                    time.sleep(update_interval)
                    
            except Exception as e:
                print(f'Monitoring error: {str(e)}')
