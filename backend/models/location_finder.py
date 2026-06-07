"""
Location Finder - Identifies nearest junction and locomotive shed
Uses geographical data and haversine distance calculations
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class Location:
    """Represents a geographical location"""
    name: str
    latitude: float
    longitude: float
    type: str  # 'junction', 'shed', 'station'
    capacity: int = 0
    services: List[str] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = []

class LocationFinder:
    """Finds nearest junctions and locomotive sheds"""
    
    def __init__(self):
        self.junctions = self._load_bangladesh_junctions()
        self.sheds = self._load_locomotive_sheds()
        self.stations = self._load_major_stations()
    
    def _load_bangladesh_junctions(self) -> List[Location]:
        """Load major railway junctions in Bangladesh"""
        return [
            Location("Dhaka Junction (Kamalapur)", 23.7346, 90.4107, "junction", 
                    services=["maintenance", "refueling", "crew_change", "passenger"]),
            Location("Narayanganj Junction", 23.6500, 90.5000, "junction",
                    services=["maintenance"]),
            Location("Tongi Junction", 23.8641, 90.3854, "junction",
                    services=["maintenance"]),
            Location("Joydebpur Junction", 24.0000, 90.4250, "junction",
                    services=["maintenance"]),
            Location("Mymensingh Junction", 24.7465, 90.4081, "junction",
                    services=["maintenance", "crew_change"]),
            Location("Santahar Junction", 24.3325, 88.4702, "junction",
                    services=["maintenance", "freight"]),
            Location("Kushtia Junction", 23.9020, 89.1194, "junction",
                    services=["maintenance"]),
            Location("Jessore Junction", 23.1672, 89.2143, "junction",
                    services=["maintenance"]),
            Location("Khulna Junction", 22.8043, 89.1680, "junction",
                    services=["maintenance"]),
            Location("Ishwardi Junction", 24.1823, 89.0805, "junction",
                    services=["maintenance"]),
            Location("Natore Junction", 24.4105, 88.9764, "junction",
                    services=["maintenance"]),
            Location("Rajshahi Junction", 24.3745, 88.6042, "junction",
                    services=["maintenance", "refueling"]),
            Location("Pabna Junction", 23.9884, 89.2494, "junction",
                    services=["maintenance"]),
            Location("Bogra Junction", 24.8465, 89.3669, "junction",
                    services=["maintenance"]),
            Location("Dinajpur Junction", 25.6217, 88.6353, "junction",
                    services=["maintenance"]),
            Location("Rangpur Junction", 25.7484, 89.2397, "junction",
                    services=["maintenance"]),
            Location("Nilphamari Junction", 26.0000, 88.7300, "junction",
                    services=["maintenance"]),
            Location("Lalmonirhat Junction", 25.9167, 89.4333, "junction",
                    services=["maintenance"]),
            Location("Sylhet Junction", 24.9154, 91.8746, "junction",
                    services=["maintenance"]),
            Location("Chittagong Junction", 22.3596, 91.7623, "junction",
                    services=["maintenance", "cargo_handling"]),
            Location("Akhaura Junction", 23.8495, 91.2718, "junction",
                    services=["maintenance", "freight"]),
            Location("Laksham Junction", 22.9882, 91.3304, "junction",
                    services=["maintenance", "passenger"]),
            Location("Kulaura Junction", 24.4947, 91.7744, "junction",
                    services=["maintenance", "passenger"]),
            Location("Cox's Bazar Junction", 21.4272, 91.9754, "junction",
                    services=["maintenance"])
        ]
    
    def _load_locomotive_sheds(self) -> List[Location]:
        """Load locomotive maintenance sheds"""
        return [
            Location("Dhaka Shed", 23.7400, 90.3950, "shed", capacity=50,
                    services=["major_repair", "overhaul", "wheel_lathe", "boiler_shop"]),
            Location("Chittagong Shed", 22.3700, 91.7700, "shed", capacity=40,
                    services=["major_repair", "boiler_shop", "welding"]),
            Location("Khulna Shed", 22.8100, 89.1700, "shed", capacity=30,
                    services=["major_repair", "wheel_lathe"]),
            Location("Rajshahi Shed", 24.3800, 88.6000, "shed", capacity=25,
                    services=["major_repair", "welding"]),
            Location("Sylhet Shed", 24.9200, 91.8800, "shed", capacity=20,
                    services=["major_repair"]),
            Location("Narayanganj Depot", 23.6600, 90.5100, "shed", capacity=28,
                    services=["maintenance", "welding"])
        ]
    
    def _load_major_stations(self) -> List[Location]:
        """Load all station types including junctions and sheds"""
        major_stations = [
            Location("Kamalapur", 23.7346, 90.4107, "station"),
            Location("Dhaka Cantonment", 23.7450, 90.4036, "station"),
            Location("Tongi", 23.8641, 90.3854, "station"),
            Location("Joydebpur", 24.0000, 90.4250, "station"),
            Location("Narayanganj", 23.6667, 90.5000, "station"),
            Location("Chittagong", 22.3569, 91.7832, "station"),
            Location("Cox's Bazar", 21.4272, 91.9754, "station"),
            Location("Khulna", 22.8250, 89.5600, "station"),
            Location("Jessore", 23.1672, 89.2143, "station"),
            Location("Rajshahi", 24.3681, 88.6040, "station"),
            Location("Natore", 24.4105, 88.9764, "station"),
            Location("Sylhet", 24.9045, 91.8611, "station"),
            Location("Rangpur", 25.7484, 89.2397, "station"),
            Location("Dinajpur", 25.6250, 88.6339, "station"),
            Location("Comilla", 23.4638, 91.1808, "station"),
            Location("Dhaka Bimanbandar", 23.8448, 90.3961, "station"),
            Location("Narsingdi", 24.1478, 90.7084, "station"),
            Location("Bhairab Bazar Junction", 24.0305, 90.9830, "junction"),
            Location("Brahmanbaria", 23.9607, 91.0851, "station"),
            Location("Qusba", 23.8289, 91.1560, "station"),
            Location("Feni", 23.0036, 91.3982, "station"),
            Location("Shayestaganj", 24.2275, 91.6019, "station"),
            Location("Sreemangal", 24.3091, 91.7196, "station"),
            Location("Vanugach", 24.3300, 91.6100, "station"),
            Location("Maijgaon", 23.8738, 90.4660, "station")
        ]

        # Include all junctions and sheds as station candidates
        all_station_types = []
        all_station_types.extend(self._load_bangladesh_junctions())
        all_station_types.extend(self._load_locomotive_sheds())
        all_station_types.extend(major_stations)
        return all_station_types
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def find_nearest_junction(self, loco_lat: float, loco_lon: float) -> Dict:
        """Find the nearest junction to locomotive"""
        nearest = None
        min_distance = float('inf')
        
        for junction in self.junctions:
            distance = self.haversine_distance(loco_lat, loco_lon, junction.latitude, junction.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest = junction
        
        return {
            'name': nearest.name,
            'latitude': nearest.latitude,
            'longitude': nearest.longitude,
            'distance_km': round(min_distance, 2),
            'services': nearest.services,
            'estimated_time_hours': round(min_distance / 60, 1)  # Assuming 60 km/h average speed
        }
    
    def find_nearest_shed(self, loco_lat: float, loco_lon: float) -> Dict:
        """Find the nearest locomotive shed"""
        nearest = None
        min_distance = float('inf')
        
        for shed in self.sheds:
            distance = self.haversine_distance(loco_lat, loco_lon, shed.latitude, shed.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest = shed
        
        return {
            'name': nearest.name,
            'latitude': nearest.latitude,
            'longitude': nearest.longitude,
            'distance_km': round(min_distance, 2),
            'capacity': nearest.capacity,
            'services': nearest.services,
            'estimated_time_hours': round(min_distance / 60, 1),
            'availability_score': 0.85  # Placeholder - would query real database
        }
    
    def find_nearest_station(self, loco_lat: float, loco_lon: float) -> Dict:
        """Find the nearest railway station"""
        nearest = None
        min_distance = float('inf')
        
        for station in self.stations:
            distance = self.haversine_distance(loco_lat, loco_lon, station.latitude, station.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest = station
        
        return {
            'name': nearest.name,
            'latitude': nearest.latitude,
            'longitude': nearest.longitude,
            'distance_km': round(min_distance, 2),
            'estimated_time_hours': round(min_distance / 60, 1)
        }
    
    def find_alternative_destinations(self, loco_lat: float, loco_lon: float, 
                                      location_type: str = 'shed', limit: int = 3) -> List[Dict]:
        """Find multiple alternative destinations"""
        locations = self.sheds if location_type == 'shed' else self.junctions
        
        distances = []
        for loc in locations:
            distance = self.haversine_distance(loco_lat, loco_lon, loc.latitude, loc.longitude)
            distances.append({
                'name': loc.name,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'distance_km': round(distance, 2),
                'services': loc.services,
                'capacity': getattr(loc, 'capacity', None),
                'estimated_time_hours': round(distance / 60, 1)
            })
        
        # Sort by distance and return top N
        distances.sort(key=lambda x: x['distance_km'])
        return distances[:limit]
    
    def get_support_network(self, loco_lat: float, loco_lon: float) -> Dict:
        """Get complete support network information for the locomotive"""
        return {
            'current_location': {'latitude': loco_lat, 'longitude': loco_lon},
            'nearest_junction': self.find_nearest_junction(loco_lat, loco_lon),
            'nearest_shed': self.find_nearest_shed(loco_lat, loco_lon),
            'nearest_station': self.find_nearest_station(loco_lat, loco_lon),
            'alternative_sheds': self.find_alternative_destinations(loco_lat, loco_lon, 'shed', 2),
            'alternative_junctions': self.find_alternative_destinations(loco_lat, loco_lon, 'junction', 2),
            'network_density': self._calculate_network_density(loco_lat, loco_lon)
        }
    
    def _calculate_network_density(self, loco_lat: float, loco_lon: float, radius_km: float = 100) -> float:
        """Calculate infrastructure density within radius"""
        count = 0
        for location in self.junctions + self.sheds + self.stations:
            distance = self.haversine_distance(loco_lat, loco_lon, location.latitude, location.longitude)
            if distance <= radius_km:
                count += 1
        return round(count / (math.pi * radius_km ** 2), 4)
