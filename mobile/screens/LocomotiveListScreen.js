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
  RefreshControl,
} from 'react-native';
import { getLocomotives } from '../services/api';

export default function LocomotiveListScreen({ navigation }) {
  const [allLocomotives, setAllLocomotives] = useState([]);
  const [filteredLocomotives, setFilteredLocomotives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');

  const fetchLocomotives = async () => {
    try {
      setLoading(true);
      const data = await getLocomotives();
      setAllLocomotives(data);
      filterLocomotieves(data, searchQuery, filterStatus);
    } catch (error) {
      Alert.alert('Error', 'Failed to load locomotives');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const filterLocomotieves = (locos, query, status) => {
    let filtered = locos;

    // Filter by search query
    if (query) {
      filtered = filtered.filter((loco) =>
        loco.name.toLowerCase().includes(query.toLowerCase()) ||
        loco.id.toLowerCase().includes(query.toLowerCase())
      );
    }

    // Filter by status
    if (status !== 'ALL') {
      filtered = filtered.filter((loco) => loco.status === status);
    }

    setFilteredLocomotives(filtered);
  };

  const handleSearch = (text) => {
    setSearchQuery(text);
    filterLocomotieves(allLocomotives, text, filterStatus);
  };

  const handleStatusFilter = (status) => {
    setFilterStatus(status);
    filterLocomotieves(allLocomotives, searchQuery, status);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchLocomotives();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchLocomotives();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'CRITICAL':
        return '#ff4444';
      case 'WARNING':
        return '#ffaa00';
      case 'HEALTHY':
        return '#44aa44';
      default:
        return '#999';
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
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Locomotives</Text>
        <Text style={styles.subtitle}>Total: {allLocomotives.length}</Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchSection}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by name or ID..."
          placeholderTextColor="#999"
          value={searchQuery}
          onChangeText={handleSearch}
        />
      </View>

      {/* Filter Buttons */}
      <View style={styles.filterSection}>
        {['ALL', 'CRITICAL', 'WARNING', 'HEALTHY'].map((status) => (
          <TouchableOpacity
            key={status}
            style={[
              styles.filterButton,
              filterStatus === status && styles.filterButtonActive,
            ]}
            onPress={() => handleStatusFilter(status)}
          >
            <Text
              style={[
                styles.filterButtonText,
                filterStatus === status && styles.filterButtonTextActive,
              ]}
            >
              {status}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Locomotive List */}
      <View style={styles.listSection}>
        {filteredLocomotives.length > 0 ? (
          filteredLocomotives.map((loco) => (
            <TouchableOpacity
              key={loco.id}
              style={styles.locoCard}
              onPress={() =>
                navigation.navigate('Analysis', { locomotiveId: loco.id })
              }
            >
              <View style={styles.cardLeft}>
                <View
                  style={[
                    styles.statusIndicator,
                    { backgroundColor: getStatusColor(loco.status) },
                  ]}
                />
                <View style={styles.cardInfo}>
                  <Text style={styles.locoName}>{loco.name}</Text>
                  <Text style={styles.locoId}>{loco.id}</Text>
                  <Text style={styles.locoType}>{loco.type || 'Locomotive'}</Text>
                </View>
              </View>

              <View style={styles.cardRight}>
                <View
                  style={[
                    styles.statusBadge,
                    { borderColor: getStatusColor(loco.status) },
                  ]}
                >
                  <Text
                    style={[
                      styles.statusBadgeText,
                      { color: getStatusColor(loco.status) },
                    ]}
                  >
                    {loco.status}
                  </Text>
                </View>
                <Text style={styles.health}>Health: {loco.health_score || 'N/A'}%</Text>
              </View>
            </TouchableOpacity>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No locomotives found</Text>
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
  searchSection: {
    padding: 15,
    backgroundColor: '#fff',
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#333',
  },
  filterSection: {
    flexDirection: 'row',
    paddingHorizontal: 15,
    paddingVertical: 10,
    justifyContent: 'space-between',
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  filterButtonActive: {
    backgroundColor: '#0066cc',
    borderColor: '#0066cc',
  },
  filterButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  listSection: {
    padding: 15,
  },
  locoCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  cardLeft: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  cardInfo: {
    flex: 1,
  },
  locoName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  locoId: {
    fontSize: 12,
    color: '#0066cc',
    marginTop: 3,
    fontWeight: '500',
  },
  locoType: {
    fontSize: 11,
    color: '#999',
    marginTop: 2,
  },
  cardRight: {
    alignItems: 'flex-end',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 15,
    borderWidth: 1.5,
    marginBottom: 5,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  health: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#999',
  },
});
