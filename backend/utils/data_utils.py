"""
Data Utilities for Locomotive Health Monitoring
Handles data loading, preprocessing, and validation
"""

import csv
import json
from datetime import datetime
from typing import Dict, List, Tuple
import os

class DataLoader:
    """Loads and manages locomotive health data"""
    
    @staticmethod
    def load_locomotive_data(csv_path: str) -> List[Dict]:
        """Load locomotive data from CSV"""
        locomotives = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    locomotives.append(row)
        except FileNotFoundError:
            print(f"Warning: Data file not found at {csv_path}")
            locomotives = DataLoader.get_sample_data()
        
        return locomotives
    
    @staticmethod
    def get_sample_data() -> List[Dict]:
        """Return sample locomotive data for testing"""
        return [
            {
                'loco_id': 'BR1001',
                'name': 'Rajdhani Express',
                'type': 'Electric',
                'route': 'Dhaka-Chittagong',
                'mileage': 145000,
                'last_maintenance': '2025-01-15',
                'status': 'ACTIVE',
                'owner': 'Bangladesh Railway'
            },
            {
                'loco_id': 'BR1002',
                'name': 'Sundarbans Express',
                'type': 'Diesel',
                'route': 'Dhaka-Khulna',
                'mileage': 234000,
                'last_maintenance': '2024-12-20',
                'status': 'ACTIVE',
                'owner': 'Bangladesh Railway'
            },
            {
                'loco_id': 'BR1003',
                'name': 'Chittagong Mail',
                'type': 'Diesel',
                'route': 'Dhaka-Cox\'s Bazar',
                'mileage': 89000,
                'last_maintenance': '2025-02-10',
                'status': 'ACTIVE',
                'owner': 'Bangladesh Railway'
            }
        ]
    
    @staticmethod
    def validate_sensor_data(sensor_data: Dict) -> Tuple[bool, List[str]]:
        """Validate sensor data for completeness and reasonable values"""
        errors = []
        
        # Required fields
        required_fields = ['temperature', 'vibration', 'pressure', 'oil_quality']
        for field in required_fields:
            if field not in sensor_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate ranges
        if 'temperature' in sensor_data:
            temp = sensor_data['temperature']
            if not isinstance(temp, (int, float)) or temp < -10 or temp > 200:
                errors.append(f"Temperature {temp} out of valid range (-10 to 200°C)")
        
        if 'vibration' in sensor_data:
            vib = sensor_data['vibration']
            if not isinstance(vib, (int, float)) or vib < 0 or vib > 50:
                errors.append(f"Vibration {vib} out of valid range (0 to 50)")
        
        if 'pressure' in sensor_data:
            pres = sensor_data['pressure']
            if not isinstance(pres, (int, float)) or pres < 0 or pres > 500:
                errors.append(f"Pressure {pres} out of valid range (0 to 500)")
        
        if 'oil_quality' in sensor_data:
            oil = sensor_data['oil_quality']
            if not isinstance(oil, (int, float)) or oil < 0 or oil > 100:
                errors.append(f"Oil quality {oil} out of valid range (0 to 100)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def normalize_sensor_data(sensor_data: Dict) -> Dict:
        """Normalize sensor data to standard ranges"""
        normalized = {}
        
        # Normalize all numeric values to 0-100 scale
        normalizations = {
            'temperature': (0, 150),  # 0-150°C -> 0-100
            'vibration': (0, 20),     # 0-20 mm/s -> 0-100
            'pressure': (0, 300),      # 0-300 kPa -> 0-100
            'oil_quality': (0, 100),   # Already 0-100
            'mileage': (0, 1000000)    # 0-1M km -> 0-100
        }
        
        for key, value in sensor_data.items():
            if key not in normalizations:
                normalized[key] = value
                continue
            
            min_val, max_val = normalizations[key]
            normalized[key] = max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
        
        return normalized
    
    @staticmethod
    def save_monitoring_report(loco_id: str, report: Dict, output_dir: str = './reports'):
        """Save monitoring report as JSON"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = f"{output_dir}/loco_{loco_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filename
    
    @staticmethod
    def generate_csv_export(locomotives_data: List[Dict], output_path: str):
        """Export locomotive data to CSV"""
        if not locomotives_data:
            return
        
        keys = locomotives_data[0].keys()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(locomotives_data)

class DataValidator:
    """Validates data consistency and quality"""
    
    @staticmethod
    def check_data_quality(locomotive: Dict) -> Dict:
        """Check overall quality of locomotive data"""
        quality_score = 100
        issues = []
        
        # Check mileage
        try:
            mileage = float(locomotive.get('mileage', 0))
            if mileage < 0:
                issues.append("Invalid mileage value")
                quality_score -= 10
        except:
            issues.append("Mileage not a valid number")
            quality_score -= 15
        
        # Check maintenance date
        try:
            last_maint = locomotive.get('last_maintenance')
            if last_maint:
                maint_date = datetime.strptime(last_maint, '%Y-%m-%d')
                days_since = (datetime.now() - maint_date).days
                if days_since > 180:
                    issues.append("Maintenance overdue")
                    quality_score -= 5
        except:
            issues.append("Invalid maintenance date format")
            quality_score -= 10
        
        # Check required fields
        required = ['loco_id', 'name', 'type', 'status']
        for field in required:
            if not locomotive.get(field):
                issues.append(f"Missing field: {field}")
                quality_score -= 5
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'status': 'GOOD' if quality_score >= 80 else 'FAIR' if quality_score >= 60 else 'POOR'
        }

class ReportGenerator:
    """Generates comprehensive health reports"""
    
    @staticmethod
    def generate_health_report(loco_id: str, risk_score: float, predictions: Dict,
                              location_info: Dict, alerts: List[Dict]) -> Dict:
        """Generate comprehensive health report"""
        
        return {
            'report_id': f"REPORT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'locomotive_id': loco_id,
            'timestamp': datetime.now().isoformat(),
            'risk_analysis': {
                'overall_risk_score': round(risk_score, 2),
                'risk_category': 'CRITICAL' if risk_score > 75 else 'HIGH' if risk_score > 50 else 'MEDIUM' if risk_score > 25 else 'LOW'
            },
            'failure_predictions': {
                'engine': predictions.get('engine', {}),
                'braking': predictions.get('braking', {}),
                'coupling': predictions.get('coupling', {}),
                'wheels': predictions.get('wheels', {}),
                'boiler': predictions.get('boiler', {})
            },
            'support_network': location_info,
            'active_alerts': alerts,
            'report_status': 'GENERATED',
            'next_check_due': (datetime.now() + timedelta(hours=4)).isoformat()
        }
    
    @staticmethod
    def generate_maintenance_schedule(predictions: Dict) -> List[Dict]:
        """Generate recommended maintenance schedule"""
        schedule = []
        
        for component, pred in predictions.items():
            if pred['probability'] > 0.5:
                hours_left = pred['hours_to_failure']
                
                if hours_left < 48:
                    priority = 'URGENT'
                elif hours_left < 168:
                    priority = 'HIGH'
                else:
                    priority = 'NORMAL'
                
                schedule.append({
                    'component': component,
                    'priority': priority,
                    'action': f"Service/Replace {component}",
                    'estimated_hours': hours_left,
                    'estimated_cost_tk': 50000 + pred['probability'] * 100000,  # Placeholder
                    'parts_needed': []
                })
        
        # Sort by priority and time urgency
        severity_order = {'URGENT': 0, 'HIGH': 1, 'NORMAL': 2}
        schedule.sort(key=lambda x: (severity_order[x['priority']], x['estimated_hours']))
        
        return schedule

# Import timedelta if not already imported
from datetime import timedelta
