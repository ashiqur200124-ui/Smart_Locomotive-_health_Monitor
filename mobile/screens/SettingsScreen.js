import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRoute } from '@react-navigation/native';

export default function SettingsScreen({ navigation }) {
  const [settings, setSettings] = useState({
    notifications: true,
    realtime_updates: true,
    dark_mode: false,
    auto_refresh: true,
    refresh_interval: 30,
    unit_system: 'metric',
    language: 'en',
  });
  const [loading, setLoading] = useState(false);

  const toggleSetting = (key) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', onPress: () => {} },
      {
        text: 'Logout',
        onPress: () => {
          // Clear auth token and navigate to login
          navigation.reset({
            index: 0,
            routes: [{ name: 'Login' }],
          });
        },
      },
    ]);
  };

  const handleClearCache = () => {
    Alert.alert('Clear Cache', 'Clear application cache?', [
      { text: 'Cancel', onPress: () => {} },
      {
        text: 'Clear',
        onPress: () => {
          Alert.alert('Success', 'Application cache cleared');
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
      </View>

      {/* Preferences Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>

        <View style={styles.settingItem}>
          <View style={styles.settingLabel}>
            <Ionicons name="notifications" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Notifications</Text>
          </View>
          <Switch
            value={settings.notifications}
            onValueChange={() => toggleSetting('notifications')}
            trackColor={{ false: '#ddd', true: '#81c784' }}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLabel}>
            <Ionicons name="sync" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Real-time Updates</Text>
          </View>
          <Switch
            value={settings.realtime_updates}
            onValueChange={() => toggleSetting('realtime_updates')}
            trackColor={{ false: '#ddd', true: '#81c784' }}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLabel}>
            <Ionicons name="moon" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Dark Mode</Text>
          </View>
          <Switch
            value={settings.dark_mode}
            onValueChange={() => toggleSetting('dark_mode')}
            trackColor={{ false: '#ddd', true: '#81c784' }}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLabel}>
            <Ionicons name="refresh" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Auto-refresh</Text>
          </View>
          <Switch
            value={settings.auto_refresh}
            onValueChange={() => toggleSetting('auto_refresh')}
            trackColor={{ false: '#ddd', true: '#81c784' }}
          />
        </View>
      </View>

      {/* System Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System</Text>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => Alert.alert('Language', 'Select your language')}
        >
          <View style={styles.settingLabel}>
            <Ionicons name="language" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Language</Text>
          </View>
          <Text style={styles.settingValue}>{settings.language.toUpperCase()}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => Alert.alert('Units', 'Select unit system')}
        >
          <View style={styles.settingLabel}>
            <Ionicons name="settings" size={20} color="#0066cc" />
            <Text style={styles.settingName}>Unit System</Text>
          </View>
          <Text style={styles.settingValue}>{settings.unit_system}</Text>
        </TouchableOpacity>
      </View>

      {/* Data Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data</Text>

        <TouchableOpacity style={styles.settingButton} onPress={handleClearCache}>
          <Ionicons name="trash" size={20} color="#ff4444" />
          <Text style={[styles.buttonText, { color: '#ff4444' }]}>Clear Cache</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingButton}
          onPress={() => Alert.alert('Download Reports', 'Export data as CSV?')}
        >
          <Ionicons name="download" size={20} color="#0066cc" />
          <Text style={styles.buttonText}>Download Reports</Text>
        </TouchableOpacity>
      </View>

      {/* Account Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>

        <TouchableOpacity
          style={styles.settingButton}
          onPress={() => Alert.alert('Change Password', 'Update your password')}
        >
          <Ionicons name="lock" size={20} color="#0066cc" />
          <Text style={styles.buttonText}>Change Password</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingButton} onPress={handleLogout}>
          <Ionicons name="log-out" size={20} color="#ff4444" />
          <Text style={[styles.buttonText, { color: '#ff4444' }]}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Version Info */}
      <View style={styles.footer}>
        <Text style={styles.versionText}>Locomotive Monitor v1.0.0</Text>
        <Text style={styles.copyrightText}>© 2025 Bangladesh Railways</Text>
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
    backgroundColor: '#0066cc',
    padding: 20,
    paddingTop: 40,
    paddingBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 15,
    marginBottom: 10,
    paddingVertical: 10,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    paddingHorizontal: 15,
    paddingVertical: 10,
    textTransform: 'uppercase',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingName: {
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
  },
  settingValue: {
    fontSize: 14,
    color: '#999',
    marginRight: 10,
  },
  settingButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  buttonText: {
    fontSize: 16,
    color: '#0066cc',
    marginLeft: 15,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 30,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    marginTop: 30,
  },
  versionText: {
    fontSize: 14,
    color: '#999',
  },
  copyrightText: {
    fontSize: 12,
    color: '#ccc',
    marginTop: 5,
  },
});
