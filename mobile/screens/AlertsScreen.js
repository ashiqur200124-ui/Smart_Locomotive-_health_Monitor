import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { getLocomotives, getAlerts } from '../services/api';

export default function AlertsScreen() {
  const [allAlerts, setAllAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterLevel, setFilterLevel] = useState('ALL');

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const locomotives = await getLocomotives();

      // Fetch alerts for all locomotives
      const allAlertsData = [];
      for (const loco of locomotives) {
        try {
          const alerts = await getAlerts(loco.id);
          if (alerts && alerts.length > 0) {
            allAlertsData.push(
              ...alerts.map((alert) => ({
                ...alert,
                locomotive_id: loco.id,
                locomotive_name: loco.name,
              }))
            );
          }
        } catch (error) {
          console.warn(`Failed to fetch alerts for ${loco.id}`);
        }
      }

      // Sort by timestamp (newest first)
      allAlertsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setAllAlerts(allAlertsData);
    } catch (error) {
      Alert.alert('Error', 'Failed to load alerts');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchAlerts();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return '#ff4444';
      case 'EMERGENCY':
        return '#cc0000';
      case 'WARNING':
        return '#ffaa00';
      case 'INFO':
        return '#0066cc';
      default:
        return '#999';
    }
  };

  const filteredAlerts =
    filterLevel === 'ALL'
      ? allAlerts
      : allAlerts.filter((alert) => alert.severity === filterLevel);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0066cc" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>System Alerts</Text>
        <Text style={styles.subtitle}>Total: {allAlerts.length} alerts</Text>
      </View>

      {/* Filter Buttons */}
      <View style={styles.filterSection}>
        {['ALL', 'CRITICAL', 'EMERGENCY', 'WARNING', 'INFO'].map((level) => (
          <TouchableOpacity
            key={level}
            style={[
              styles.filterButton,
              filterLevel === level && styles.filterButtonActive,
            ]}
            onPress={() => setFilterLevel(level)}
          >
            <Text
              style={[
                styles.filterButtonText,
                filterLevel === level && styles.filterButtonTextActive,
              ]}
            >
              {level}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Alerts List */}
      <View style={styles.alertsSection}>
        {filteredAlerts.length > 0 ? (
          filteredAlerts.map((alert, index) => (
            <View key={index} style={styles.alertCard}>
              <View style={styles.alertHeader}>
                <View
                  style={[
                    styles.severityIndicator,
                    { backgroundColor: getSeverityColor(alert.severity) },
                  ]}
                />
                <View style={styles.alertTitleSection}>
                  <Text style={styles.alertTitle}>{alert.message}</Text>
                  <Text style={styles.locomotiveName}>{alert.locomotive_name}</Text>
                </View>
                <View
                  style={[
                    styles.severityBadge,
                    { borderColor: getSeverityColor(alert.severity) },
                  ]}
                >
                  <Text
                    style={[
                      styles.severityText,
                      { color: getSeverityColor(alert.severity) },
                    ]}
                  >
                    {alert.severity}
                  </Text>
                </View>
              </View>

              <View style={styles.alertDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Time:</Text>
                  <Text style={styles.detailValue}>
                    {new Date(alert.timestamp).toLocaleString()}
                  </Text>
                </View>
                {alert.details && (
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Details:</Text>
                    <Text style={styles.detailValue}>{alert.details}</Text>
                  </View>
                )}
                {alert.recommended_action && (
                  <View style={styles.actionBox}>
                    <Text style={styles.actionLabel}>Recommended Action:</Text>
                    <Text style={styles.actionText}>{alert.recommended_action}</Text>
                  </View>
                )}
              </View>
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateTitle}>No Alerts</Text>
            <Text style={styles.emptyStateText}>All systems operating normally</Text>
          </View>
        )}
      </View>
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
  filterSection: {
    flexDirection: 'row',
    paddingHorizontal: 15,
    paddingVertical: 10,
    justifyContent: 'space-between',
    backgroundColor: '#fff',
  },
  filterButton: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  filterButtonActive: {
    backgroundColor: '#0066cc',
    borderColor: '#0066cc',
  },
  filterButtonText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#666',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  alertsSection: {
    padding: 15,
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
    borderLeftWidth: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  severityIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 10,
    marginTop: 4,
  },
  alertTitleSection: {
    flex: 1,
    marginRight: 10,
  },
  alertTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  locomotiveName: {
    fontSize: 12,
    color: '#0066cc',
    marginTop: 3,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1.5,
  },
  severityText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  alertDetails: {
    padding: 12,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    width: 50,
  },
  detailValue: {
    flex: 1,
    fontSize: 12,
    color: '#333',
  },
  actionBox: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#f9f9f9',
    borderLeftWidth: 3,
    borderLeftColor: '#ff6b6b',
    borderRadius: 5,
  },
  actionLabel: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 5,
  },
  actionText: {
    fontSize: 12,
    color: '#333',
    lineHeight: 18,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#999',
  },
  emptyStateText: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 8,
  },
});
