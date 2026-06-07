import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { getDashboardSummary, getLocomotives } from '../services/api';

export default function DashboardScreen() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [locomotives, setLocomotives] = useState([]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const [summary, locos] = await Promise.all([
        getDashboardSummary(),
        getLocomotives(),
      ]);
      setData(summary);
      setLocomotives(locos);
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboard();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0066cc" />
      </View>
    );
  }

  const criticalCount = locomotives.filter((l) => l.status === 'CRITICAL').length;
  const warningCount = locomotives.filter((l) => l.status === 'WARNING').length;
  const healthyCount = locomotives.filter((l) => l.status === 'HEALTHY').length;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.title}>Locomotive Health Monitor</Text>
        <Text style={styles.subtitle}>Real-time Status Dashboard</Text>
      </View>

      {/* Status Cards */}
      <View style={styles.cardsContainer}>
        <View style={[styles.card, styles.criticalCard]}>
          <Text style={styles.cardTitle}>Critical</Text>
          <Text style={styles.cardValue}>{criticalCount}</Text>
          <Text style={styles.cardSubtitle}>Needs Immediate Attention</Text>
        </View>

        <View style={[styles.card, styles.warningCard]}>
          <Text style={styles.cardTitle}>Warning</Text>
          <Text style={styles.cardValue}>{warningCount}</Text>
          <Text style={styles.cardSubtitle}>Monitor Closely</Text>
        </View>

        <View style={[styles.card, styles.healthyCard]}>
          <Text style={styles.cardTitle}>Healthy</Text>
          <Text style={styles.cardValue}>{healthyCount}</Text>
          <Text style={styles.cardSubtitle}>Operating Normal</Text>
        </View>
      </View>

      {/* Total Locomotives */}
      <View style={styles.summarySection}>
        <Text style={styles.sectionTitle}>Fleet Overview</Text>
        <View style={styles.summaryCard}>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Total Locomotives</Text>
            <Text style={styles.summaryValue}>{locomotives.length}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Average Health Score</Text>
            <Text style={styles.summaryValue}>
              {data?.average_health?.toFixed(1) || 'N/A'}%
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Active Alerts</Text>
            <Text style={styles.summaryValue}>{data?.total_alerts || 0}</Text>
          </View>
        </View>
      </View>

      {/* Recent Locomotives */}
      <View style={styles.summarySection}>
        <Text style={styles.sectionTitle}>Recent Locomotives</Text>
        {locomotives.slice(0, 3).map((loco) => (
          <View key={loco.id} style={styles.locoItem}>
            <View style={styles.locoInfo}>
              <Text style={styles.locoName}>{loco.name}</Text>
              <Text style={styles.locoId}>{loco.id}</Text>
            </View>
            <View
              style={[
                styles.statusBadge,
                loco.status === 'CRITICAL'
                  ? styles.statusCritical
                  : loco.status === 'WARNING'
                  ? styles.statusWarning
                  : styles.statusHealthy,
              ]}
            >
              <Text style={styles.statusText}>{loco.status}</Text>
            </View>
          </View>
        ))}
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
  cardsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 10,
    paddingVertical: 15,
  },
  card: {
    flex: 1,
    marginHorizontal: 5,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  criticalCard: {
    backgroundColor: '#ff4444',
  },
  warningCard: {
    backgroundColor: '#ffaa00',
  },
  healthyCard: {
    backgroundColor: '#44aa44',
  },
  cardTitle: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  cardValue: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
    marginVertical: 5,
  },
  cardSubtitle: {
    color: '#fff',
    fontSize: 10,
    textAlign: 'center',
  },
  summarySection: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  summaryLabel: {
    color: '#666',
    fontSize: 14,
  },
  summaryValue: {
    color: '#0066cc',
    fontSize: 16,
    fontWeight: 'bold',
  },
  locoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
  },
  locoInfo: {
    flex: 1,
  },
  locoName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  locoId: {
    fontSize: 12,
    color: '#999',
    marginTop: 3,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  statusCritical: {
    backgroundColor: '#ffcccc',
  },
  statusWarning: {
    backgroundColor: '#ffe6cc',
  },
  statusHealthy: {
    backgroundColor: '#ccffcc',
  },
  statusText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#333',
  },
});
