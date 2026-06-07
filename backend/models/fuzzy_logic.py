"""
Fuzzy Logic Risk Analysis System for Locomotive Health
Analyzes multiple sensor parameters and generates risk scores
"""

import numpy as np
from typing import Dict, List, Tuple

class FuzzyLogicRiskAnalyzer:
    """Evaluates locomotive health using fuzzy logic principles"""
    
    def __init__(self):
        self.membership_functions = self._initialize_membership_functions()
    
    def _initialize_membership_functions(self) -> Dict:
        """Initialize fuzzy membership functions"""
        return {
            'temperature': {'low': (0, 30, 50), 'medium': (40, 70, 90), 'high': (80, 120, 150)},
            'vibration': {'low': (0, 2, 4), 'medium': (3, 6, 9), 'high': (8, 15, 20)},
            'pressure': {'low': (0, 50, 100), 'normal': (80, 150, 200), 'high': (150, 250, 300)},
            'oil_quality': {'good': (0, 20, 40), 'fair': (30, 50, 70), 'poor': (60, 90, 100)},
            'mileage': {'new': (0, 25000, 50000), 'mid': (40000, 150000, 250000), 'old': (200000, 500000, 1000000)}
        }
    
    def triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        """Calculate triangular membership function value"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        else:
            return (c - x) / (c - b)
    
    def evaluate_parameter(self, value: float, param_type: str) -> Dict[str, float]:
        """Evaluate a single parameter's membership degrees"""
        memberships = {}
        for category, (a, b, c) in self.membership_functions[param_type].items():
            memberships[category] = self.triangular_membership(value, a, b, c)
        return memberships
    
    def calculate_risk_score(self, sensor_data: Dict) -> Tuple[float, Dict]:
        """
        Calculate overall risk score from multiple sensor inputs
        
        Args:
            sensor_data: Dict with keys like 'temperature', 'vibration', 'pressure', etc.
        
        Returns:
            Tuple of (risk_score: 0-100, component_risks: dict)
        """
        component_risks = {}
        weights = {'temperature': 0.25, 'vibration': 0.25, 'pressure': 0.2, 'oil_quality': 0.2, 'mileage': 0.1}
        
        weighted_risk = 0
        for param, value in sensor_data.items():
            if param not in self.membership_functions:
                continue
            
            # Get membership degrees
            memberships = self.evaluate_parameter(value, param)
            
            # Calculate risk from membership degrees
            risk_from_param = self._fuzzify_to_risk(param, memberships)
            component_risks[param] = risk_from_param
            
            # Add to weighted total
            weight = weights.get(param, 0.1)
            weighted_risk += risk_from_param * weight
        
        # Normalize to 0-100 scale
        risk_score = min(100, max(0, weighted_risk))
        
        return risk_score, component_risks
    
    def _fuzzify_to_risk(self, param_type: str, memberships: Dict[str, float]) -> float:
        """Convert membership degrees to risk level (0-100)"""
        # Risk increases with 'high', 'poor', 'old' categories
        risk_mappings = {
            'temperature': {'high': 90, 'medium': 40, 'low': 10},
            'vibration': {'high': 95, 'medium': 50, 'low': 5},
            'pressure': {'high': 85, 'normal': 20, 'low': 60},
            'oil_quality': {'poor': 90, 'fair': 50, 'good': 10},
            'mileage': {'old': 80, 'mid': 40, 'new': 5}
        }
        
        mapping = risk_mappings.get(param_type, {})
        risk = sum(memberships.get(cat, 0) * mapping.get(cat, 0) for cat in mapping)
        return min(100, max(0, risk))
    
    def get_risk_category(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score < 25:
            return "LOW"
        elif risk_score < 50:
            return "MEDIUM"
        elif risk_score < 75:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def get_recommendations(self, risk_score: float, component_risks: Dict) -> List[str]:
        """Generate maintenance recommendations based on risk analysis"""
        recommendations = []
        
        if risk_score > 75:
            recommendations.append("URGENT: Schedule immediate maintenance inspection")
        elif risk_score > 50:
            recommendations.append("Schedule preventive maintenance within 48 hours")
        
        if component_risks.get('temperature', 0) > 70:
            recommendations.append("Check cooling system - temperature anomaly detected")
        
        if component_risks.get('vibration', 0) > 75:
            recommendations.append("Inspect wheel alignment and bearing conditions")
        
        if component_risks.get('pressure', 0) > 70:
            recommendations.append("Service hydraulic/pneumatic systems")
        
        if component_risks.get('oil_quality', 0) > 70:
            recommendations.append("Replace engine oil and filter immediately")
        
        if component_risks.get('mileage', 0) > 60:
            recommendations.append("Schedule comprehensive overhaul - high mileage detected")
        
        return recommendations if recommendations else ["Continue regular monitoring"]
