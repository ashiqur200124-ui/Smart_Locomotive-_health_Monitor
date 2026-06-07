"""
AI-Based Locomotive Failure Prediction Model
Uses machine learning for predictive maintenance
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

class FailurePredictor:
    """Predicts locomotive failure probability using historical patterns"""
    
    def __init__(self):
        self.failure_thresholds = {
            'engine': 0.75,
            'braking': 0.70,
            'coupling': 0.65,
            'boiler': 0.80,
            'wheels': 0.72
        }
        
        # Historical failure patterns (component-specific)
        self.failure_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Initialize known failure patterns"""
        return {
            'engine': {
                'temperature_surge': 0.85,
                'vibration_increase': 0.75,
                'pressure_drop': 0.70,
                'oil_contamination': 0.80
            },
            'braking': {
                'pressure_variance': 0.80,
                'slack_increase': 0.75,
                'wear_rate_high': 0.85,
                'pad_thickness_low': 0.90
            },
            'coupling': {
                'misalignment': 0.70,
                'rust_detected': 0.65,
                'bolt_looseness': 0.75,
                'stress_marks': 0.70
            },
            'wheels': {
                'flat_spots': 0.85,
                'rim_crack': 0.95,
                'bearing_temp_high': 0.80,
                'wear_excessive': 0.75
            },
            'boiler': {
                'pressure_instability': 0.80,
                'leak_detected': 0.90,
                'scale_buildup': 0.70,
                'corrosion_advanced': 0.85
            }
        }
    
    def predict_failure_probability(self, loco_data: Dict) -> Dict:
        """
        Predict failure probability for each component
        
        Args:
            loco_data: Dictionary with locomotive sensor data and history
        
        Returns:
            Dict with failure predictions for each component
        """
        predictions = {}
        
        # Analyze each component
        predictions['engine'] = self._predict_engine_failure(loco_data)
        predictions['braking'] = self._predict_braking_failure(loco_data)
        predictions['coupling'] = self._predict_coupling_failure(loco_data)
        predictions['wheels'] = self._predict_wheel_failure(loco_data)
        predictions['boiler'] = self._predict_boiler_failure(loco_data)
        
        return predictions
    
    def _predict_engine_failure(self, loco_data: Dict) -> Dict:
        """Predict engine system failure"""
        risk_factors = []
        
        temp = loco_data.get('temperature', 0)
        if temp > 100:
            risk_factors.append(0.3 * min(1.0, (temp - 100) / 50))  # Temp over 100°C
        
        vibration = loco_data.get('vibration', 0)
        if vibration > 10:
            risk_factors.append(0.4 * min(1.0, (vibration - 10) / 10))  # Vibration high
        
        oil_quality = loco_data.get('oil_quality', 0)
        if oil_quality > 60:
            risk_factors.append(0.3 * (oil_quality / 100))  # Oil degraded
        
        prob = np.mean(risk_factors) if risk_factors else 0.1
        
        return {
            'probability': float(min(1.0, prob)),
            'threshold': self.failure_thresholds['engine'],
            'status': 'RISKY' if float(prob) > self.failure_thresholds['engine'] else 'NORMAL',
            'hours_to_failure': self._estimate_hours_to_failure(prob, 'engine')
        }
    
    def _predict_braking_failure(self, loco_data: Dict) -> Dict:
        """Predict braking system failure"""
        risk_factors = []
        
        brake_pressure = loco_data.get('brake_pressure', 0)
        if brake_pressure < 80 or brake_pressure > 200:
            risk_factors.append(0.4)  # Pressure out of normal range
        
        brake_pad_wear = loco_data.get('brake_pad_wear', 0)
        if brake_pad_wear > 70:
            risk_factors.append(0.5)  # Pad wear critical
        
        brake_temp = loco_data.get('brake_temp', 0)
        if brake_temp > 120:
            risk_factors.append(0.35)  # Excessive heat
        
        prob = np.mean(risk_factors) if risk_factors else 0.05
        
        return {
            'probability': min(1.0, prob),
            'threshold': self.failure_thresholds['braking'],
            'status': 'RISKY' if float(prob) > self.failure_thresholds['braking'] else 'NORMAL',
            'hours_to_failure': self._estimate_hours_to_failure(prob, 'braking')
        }
    
    def _predict_coupling_failure(self, loco_data: Dict) -> Dict:
        """Predict coupling system failure"""
        risk_factors = []
        
        coupling_wear = loco_data.get('coupling_wear', 0)
        if coupling_wear > 50:
            risk_factors.append(coupling_wear / 100)
        
        misalignment = loco_data.get('coupling_misalignment', 0)
        if misalignment > 5:
            risk_factors.append(0.3)
        
        prob = np.mean(risk_factors) if risk_factors else 0.02
        
        return {
            'probability': min(1.0, prob),
            'threshold': self.failure_thresholds['coupling'],
            'status': 'RISKY' if float(prob) > self.failure_thresholds['coupling'] else 'NORMAL',
            'hours_to_failure': self._estimate_hours_to_failure(prob, 'coupling')
        }
    
    def _predict_wheel_failure(self, loco_data: Dict) -> Dict:
        """Predict wheel system failure"""
        risk_factors = []
        
        wheel_wear = loco_data.get('wheel_wear', 0)
        if wheel_wear > 60:
            risk_factors.append(wheel_wear / 100)
        
        wheel_temp = loco_data.get('wheel_bearing_temp', 0)
        if wheel_temp > 95:
            risk_factors.append(0.4)
        
        prob = np.mean(risk_factors) if risk_factors else 0.08
        
        return {
            'probability': min(1.0, prob),
            'threshold': self.failure_thresholds['wheels'],
            'status': 'RISKY' if float(prob) > self.failure_thresholds['wheels'] else 'NORMAL',
            'hours_to_failure': self._estimate_hours_to_failure(prob, 'wheels')
        }
    
    def _predict_boiler_failure(self, loco_data: Dict) -> Dict:
        """Predict boiler system failure"""
        risk_factors = []
        
        boiler_pressure = loco_data.get('boiler_pressure', 0)
        if boiler_pressure < 100 or boiler_pressure > 280:
            risk_factors.append(0.35)
        
        boiler_temp = loco_data.get('boiler_temp', 0)
        if boiler_temp > 250:
            risk_factors.append(0.4)
        
        scale_buildup = loco_data.get('scale_buildup', 0)
        if scale_buildup > 40:
            risk_factors.append(scale_buildup / 100)
        
        prob = np.mean(risk_factors) if risk_factors else 0.06
        
        return {
            'probability': min(1.0, prob),
            'threshold': self.failure_thresholds['boiler'],
            'status': 'RISKY' if float(prob) > self.failure_thresholds['boiler'] else 'NORMAL',
            'hours_to_failure': self._estimate_hours_to_failure(prob, 'boiler')
        }
    
    def _estimate_hours_to_failure(self, probability: float, component: str) -> int:
        """Estimate hours until potential failure"""
        if probability < 0.3:
            return 500  # Low risk: many hours left
        elif probability < 0.6:
            return 200  # Medium risk
        elif probability < 0.8:
            return 50   # High risk
        else:
            return 12   # Critical risk: failure imminent
    
    def get_overall_health_score(self, predictions: Dict) -> Dict:
        """Calculate overall locomotive health"""
        probs = [p['probability'] for p in predictions.values()]
        
        # Weighted average (critical components weighted more)
        weights = {'engine': 0.3, 'braking': 0.25, 'wheels': 0.25, 'boiler': 0.15, 'coupling': 0.05}
        weighted_sum = sum(predictions[comp]['probability'] * weights[comp] for comp in weights)
        
        health_score = 100 * (1 - weighted_sum)
        
        return {
            'health_score': float(max(0, health_score)),
            'predicted_reliability': float((100 - max(p['probability'] for p in predictions.values()) * 100)),
            'components_at_risk': [comp for comp, pred in predictions.items() if pred['status'] == 'RISKY'],
            'immediate_action_needed': bool(max(pred['probability'] for pred in predictions.values()) > 0.8)
        }
