import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { ActivityIndicator, View } from 'react-native';

import DashboardScreen from './screens/DashboardScreen';
import LocomotiveListScreen from './screens/LocomotiveListScreen';
import HealthAnalysisScreen from './screens/HealthAnalysisScreen';
import AlertsScreen from './screens/AlertsScreen';
import SettingsScreen from './screens/SettingsScreen';
import MapScreen from './screens/MapScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

/**
 * Dashboard Stack Navigator
 */
function DashboardStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="DashboardHome" component={DashboardScreen} />
    </Stack.Navigator>
  );
}

/**
 * Locomotives Stack Navigator
 */
function LocomotivesStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="LocomotiveHome" component={LocomotiveListScreen} />
      <Stack.Screen
        name="Analysis"
        component={HealthAnalysisScreen}
        options={{
          headerShown: true,
          headerTitle: 'Health Analysis',
          headerBackTitle: 'Back',
          headerTintColor: '#0066cc',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      />
    </Stack.Navigator>
  );
}

/**
 * Alerts Stack Navigator
 */
function AlertsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="AlertsHome" component={AlertsScreen} />
    </Stack.Navigator>
  );
}

/**
 * Map Stack Navigator
 */
function MapStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="MapHome" component={MapScreen} />
    </Stack.Navigator>
  );
}

/**
 * Settings Stack Navigator
 */
function SettingsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="SettingsHome" component={SettingsScreen} />
    </Stack.Navigator>
  );
}

/**
 * Main App Component with Bottom Tab Navigation
 */
export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize app
    setIsReady(true);
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0066cc" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Dashboard') {
              iconName = focused ? 'speedometer' : 'speedometer-outline';
            } else if (route.name === 'Locomotives') {
              iconName = focused ? 'train' : 'train-outline';
            } else if (route.name === 'Alerts') {
              iconName = focused ? 'alert' : 'alert-outline';
            } else if (route.name === 'Map') {
              iconName = focused ? 'map' : 'map-outline';
            } else if (route.name === 'Settings') {
              iconName = focused ? 'settings' : 'settings-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#0066cc',
          tabBarInactiveTintColor: '#999',
          tabBarStyle: {
            backgroundColor: '#fff',
            borderTopColor: '#f0f0f0',
            borderTopWidth: 1,
            height: 60,
            paddingBottom: 8,
            paddingTop: 5,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            marginTop: 4,
          },
        })}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardStack}
          options={{
            tabBarLabel: 'Dashboard',
          }}
        />
        <Tab.Screen
          name="Locomotives"
          component={LocomotivesStack}
          options={{
            tabBarLabel: 'Locomotives',
          }}
        />
        <Tab.Screen
          name="Alerts"
          component={AlertsStack}
          options={{
            tabBarLabel: 'Alerts',
          }}
        />
        <Tab.Screen
          name="Map"
          component={MapStack}
          options={{
            tabBarLabel: 'Map',
          }}
        />
        <Tab.Screen
          name="Settings"
          component={SettingsStack}
          options={{
            tabBarLabel: 'Settings',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
