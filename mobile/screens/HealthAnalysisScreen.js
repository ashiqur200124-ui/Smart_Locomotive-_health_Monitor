import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  TextInput,
} from 'react-native';
import { performHealthAnalysis, getLocomotiveById } from '../services/api';

export default function HealthAnalysisScreen({ route }) {
  const { locomotiveId } = route.params || {};
  const [locomotive, setLocomotive] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  // Sensor input states
  const [temperature, setTemperature] = useState('80');
  const [vibration, setVibration] = useState('5.0');
  const [pressure, setPressure] = useState('150');
  const [oilQuality, setOilQuality] = useState('25');
  const [mileage, setMileage] = useState('150000');

  useEffect(() => {
    loadLocomotiveDetails();
  }, []);

  const loadLocomotiveDetails = async () => {
    if (!locomotiveId) {
      setLoading(false);
      return;
    }

    try {
      const data = await getLocomotiveById(locomotiveId);
      setLocomotive(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load locomotive details');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!locomotiveId) {
      Alert.alert('Error', 'No locomotive selected');
      return;
    }

    // Validate inputs
    const temp = parseFloat(temperature);
    const vib = parseFloat(vibration);
    const press = parseFloat(pressure);
    const oil = parseFloat(oilQuality);
    const miles = parseFloat(mileage);

    if (isNaN(temp) || isNaN(vib) || isNaN(press) || isNaN(oil) || isNaN(miles)) {
      Alert.alert('Validation Error', 'Please enter valid numbers for all fields');
      return;
    }

    try {
      setAnalyzing(true);
      const sensorData = {
        temperature: temp,
        vibration: vib,
        pressure: press,
        oil_quality: oil,
        mileage: miles,
        latitude: 23.7275,
        longitude: 90.4086, // Default Dhaka coordinates
      };

      const response = await performHealthAnalysis(locomotiveId, sensorData);
      setResult(response);
    } catch (error) {
      Alert.alert('Analysis Error', 'Failed to perform analysis');
      console.error(error);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0066cc" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Health Analysis</Text>
        {locomotive && <Text style={styles.subtitle}>{locomotive.name}</Text>}
      </View>

      {/* Input Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Sensor Readings</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Temperature (°C)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter temperature"
            keyboardType="decimal-pad"
            value={temperature}
            onChangeText={setTemperature}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Vibration Level (m/s²)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter vibration"
            keyboardType="decimal-pad"
            value={vibration}
            onChangeText={setVibration}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Pressure (PSI)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter pressure"
            keyboardType="decimal-pad"
            value={pressure}
            onChangeText={setPressure}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Oil Quality (%)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter oil quality"
            keyboardType="decimal-pad"
            value={oilQuality}
            onChangeText={setOilQuality}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Mileage (km)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter mileage"
            keyboardType="number-pad"
            value={mileage}
            onChangeText={setMileage}
          />
        </View>

        <TouchableOpacity
          style={[styles.analyzeButton, analyzing && styles.analyzeButtonDisabled]}
          onPress={handleAnalyze}
          disabled={analyzing}
        >
          {analyzing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.analyzeButtonText}>Perform Analysis</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Results Section */}
      {result && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Analysis Results</Text>

          {/* Risk Score */}
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>Overall Risk Score</Text>
            <View style={styles.riskContainer}>
              <Text style={styles.riskScore}>{result.risk_score?.toFixed(1)}%</Text>
              <View
                style={[
                  styles.riskLevelBadge,
                  result.risk_level === 'CRITICAL'
                    ? styles.riskCritical
                    : result.risk_level === 'WARNING'
                    ? styles.riskWarning
                    : result.risk_level === 'CAUTION'
                    ? styles.riskCaution
                    : styles.riskHealthy,
                ]}
              >
                <Text style={styles.riskLevelText}>{result.risk_level}</Text>
              </View>
            </View>
          </View>

          {/* Component Risks */}
          {result.component_risks && (
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>Component Risk Analysis</Text>
              {Object.entries(result.component_risks).map(([component, risk]) => (
                <View key={component} style={styles.componentRow}>
                  <Text style={styles.componentName}>
                    {component.charAt(0).toUpperCase() + component.slice(1)}
                  </Text>
                  <View style={styles.riskBar}>
                    <View
                      style={[
                        styles.riskFill,
                        {
                          width: `${risk}%`,
                          backgroundColor:
                            risk > 75 ? '#ff4444' : risk > 50 ? '#ffaa00' : '#44aa44',
                        },
                      ]}
                    />
                  </View>
                  <Text style={styles.componentRisk}>{risk.toFixed(1)}%</Text>
                </View>
              ))}
            </View>
          )}

          {/* Recommendations */}
          {result.recommendations && (
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>Recommendations</Text>
              {result.recommendations.map((rec, index) => (
                <View key={index} style={styles.recommendationItem}>
                  <Text style={styles.recommendationBullet}>•</Text>
                  <Text style={styles.recommendationText}>{rec}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Predicted Failures */}
          {result.predicted_failures && (
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>Predicted Failures (hours)</Text>
              {Object.entries(result.predicted_failures).map(([component, hours]) => (
                <View key={component} style={styles.failureRow}>
                  <Text style={styles.failureComponent}>
                    {component.charAt(0).toUpperCase() + component.slice(1)}
                  </Text>
                  <Text style={styles.failureHours}>{hours.toFixed(0)} hours</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#0066cc',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 5,
  },
  section: {
    padding: 15,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#333',
    backgroundColor: '#fff',
  },
  analyzeButton: {
    backgroundColor: '#0066cc',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 10,
  },
  analyzeButtonDisabled: {
    backgroundColor: '#999',
  },
  analyzeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  resultLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  riskContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  riskScore: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#0066cc',
  },
  riskLevelBadge: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },
  riskCritical: {
    backgroundColor: '#ffcccc',
  },
  riskWarning: {
    backgroundColor: '#ffe6cc',
  },
  riskCaution: {
    backgroundColor: '#fff3cd',
  },
  riskHealthy: {
    backgroundColor: '#ccffcc',
  },
  riskLevelText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#333',
  },
  componentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  componentName: {
    width: 80,
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  riskBar: {
    flex: 1,
    height: 20,
    backgroundColor: '#eee',
    borderRadius: 10,
    overflow: 'hidden',
    marginHorizontal: 10,
  },
  riskFill: {
    height: '100%',
  },
  componentRisk: {
    width: 40,
    textAlign: 'right',
    fontSize: 12,
    fontWeight: 'bold',
    color: '#333',
  },
  recommendationItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  recommendationBullet: {
    marginRight: 10,
    fontSize: 14,
    color: '#0066cc',
  },
  recommendationText: {
    flex: 1,
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  failureRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  failureComponent: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
  },
  failureHours: {
    fontSize: 13,
    color: '#ff6b6b',
    fontWeight: 'bold',
  },
});
