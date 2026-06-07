import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import MapView, { Marker, Callout } from 'react-native-maps';
import { Ionicons } from '@expo/vector-icons';
import { getLocomotives } from '../services/api';

const { width, height } = Dimensions.get('window');
const ASPECT_RATIO = width / height;
const LATITUDE_DELTA = 8;
const LONGITUDE_DELTA = LATITUDE_DELTA * ASPECT_RATIO;

export default function MapScreen() {
  const [locomotives, setLocomotives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLoco, setSelectedLoco] = useState(null);
  const [mapRef, setMapRef] = useState(null);

  const fetchLocomotives = async () => {
    try {
      setLoading(true);
      const data = await getLocomotives();
      setLocomotives(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load locomotive data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocomotives();
    const interval = setInterval(fetchLocomotives, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (healthScore) => {
    if (healthScore >= 80) return '#44aa44'; // Green
    if (healthScore >= 60) return '#ffaa00'; // Orange
    if (healthScore >= 40) return '#ff8844'; // Red-Orange
    return '#ff4444'; // Red
  };

  const handleMarkerPress = (locomotive) => {
    setSelectedLoco(locomotive);
  };

  const handleZoomToLoco = (loco) => {
    if (mapRef) {
      mapRef.animateToRegion({
        latitude: loco.latitude || 23.7275,
        longitude: loco.longitude || 90.4086,
        latitudeDelta: LATITUDE_DELTA / 2,
        longitudeDelta: LONGITUDE_DELTA / 2,
      });
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0066cc" />
      </View>
    );
  }

  const filteredLocomotives = locomotives.filter(
    (loco) => loco.latitude && loco.longitude
  );

  return (
    <View style={styles.container}>
      {/* Map */}
      <MapView
        ref={setMapRef}
        style={styles.map}
        initialRegion={{
          latitude: 23.7275,
          longitude: 90.4086,
          latitudeDelta: LATITUDE_DELTA,
          longitudeDelta: LONGITUDE_DELTA,
        }}
      >
        {filteredLocomotives.map((locomotive, index) => (
          <Marker
            key={index}
            coordinate={{
              latitude: locomotive.latitude,
              longitude: locomotive.longitude,
            }}
            onPress={() => handleMarkerPress(locomotive)}
          >
            <View
              style={[
                styles.markerContainer,
                {
                  borderColor: getStatusColor(locomotive.health_score || 100),
                },
              ]}
            >
              <Ionicons name="train" size={24} color="#fff" />
            </View>

            <Callout>
              <View style={styles.calloutContainer}>
                <Text style={styles.calloutTitle}>{locomotive.name}</Text>
                <Text style={styles.calloutText}>ID: {locomotive.id}</Text>
                <Text style={styles.calloutText}>
                  Health: {(locomotive.health_score || 100).toFixed(1)}%
                </Text>
                <Text style={styles.calloutText}>
                  Risk: {(locomotive.current_risk || 0).toFixed(1)}%
                </Text>
              </View>
            </Callout>
          </Marker>
        ))}
      </MapView>

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#44aa44' }]} />
          <Text style={styles.legendText}>Healthy (>80%)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#ffaa00' }]} />
          <Text style={styles.legendText}>Warning (60-80%)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#ff4444' }]} />
          <Text style={styles.legendText}>Critical (<40%)</Text>
        </View>
      </View>

      {/* Selected Locomotive Info */}
      {selectedLoco && (
        <View style={styles.infoPanel}>
          <View style={styles.infoPanelHeader}>
            <Text style={styles.infoPanelTitle}>{selectedLoco.name}</Text>
            <TouchableOpacity onPress={() => setSelectedLoco(null)}>
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>

          <View style={styles.infoPanelContent}>
            <View style={styles.infoPanelRow}>
              <Text style={styles.infoPanelLabel}>ID:</Text>
              <Text style={styles.infoPanelValue}>{selectedLoco.id}</Text>
            </View>
            <View style={styles.infoPanelRow}>
              <Text style={styles.infoPanelLabel}>Status:</Text>
              <Text
                style={[
                  styles.infoPanelValue,
                  {
                    color:
                      selectedLoco.status === 'ACTIVE'
                        ? '#44aa44'
                        : '#ff4444',
                  },
                ]}
              >
                {selectedLoco.status}
              </Text>
            </View>
            <View style={styles.infoPanelRow}>
              <Text style={styles.infoPanelLabel}>Health:</Text>
              <Text style={styles.infoPanelValue}>
                {(selectedLoco.health_score || 100).toFixed(1)}%
              </Text>
            </View>
            <View style={styles.infoPanelRow}>
              <Text style={styles.infoPanelLabel}>Risk:</Text>
              <Text style={styles.infoPanelValue}>
                {(selectedLoco.current_risk || 0).toFixed(1)}%
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.detailsButton}
            onPress={() => handleZoomToLoco(selectedLoco)}
          >
            <Ionicons name="zoom-in" size={20} color="#fff" />
            <Text style={styles.detailsButtonText}>Zoom In</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  map: {
    flex: 1,
  },
  markerContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0066cc',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
  },
  calloutContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    minWidth: 150,
  },
  calloutTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  calloutText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  legend: {
    position: 'absolute',
    bottom: 80,
    left: 15,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendText: {
    fontSize: 12,
    color: '#666',
  },
  infoPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    paddingTop: 15,
    paddingHorizontal: 15,
    paddingBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoPanelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  infoPanelTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  infoPanelContent: {
    marginBottom: 15,
  },
  infoPanelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoPanelLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  infoPanelValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  detailsButton: {
    flexDirection: 'row',
    backgroundColor: '#0066cc',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  detailsButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
});
