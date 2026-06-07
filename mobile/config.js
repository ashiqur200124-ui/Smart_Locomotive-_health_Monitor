/**
 * Configuration for Smart Locomotive Health Monitor Mobile App
 * Update these values for your deployment environment
 */

// Backend API Configuration
export const API_CONFIG = {
  // Change this to your backend server address
  // For local development: 'http://localhost:5000'
  // For production: 'https://your-domain.com'
  BASE_URL: 'http://localhost:5000',

  // API endpoints (append to BASE_URL)
  ENDPOINTS: {
    HEALTH_CHECK: '/',
    LOCOMOTIVES: '/api/locomotives',
    LOCOMOTIVE_DETAIL: '/api/locomotives/:id',
    HEALTH_ANALYSIS: '/api/health/:id',
    ALERTS: '/api/alerts/:id',
    NEARBY_LOCATIONS: '/api/locations/:id',
    DASHBOARD_SUMMARY: '/api/summary',
  },

  // Request timeout in milliseconds
  TIMEOUT: 10000,

  // Default coordinates (Dhaka, Bangladesh)
  DEFAULT_LATITUDE: 23.7275,
  DEFAULT_LONGITUDE: 90.4086,
};

// App Configuration
export const APP_CONFIG = {
  APP_NAME: 'Locomotive Monitor',
  VERSION: '1.0.0',
  ENVIRONMENT: 'development', // 'development' or 'production'
};

// UI Configuration
export const UI_CONFIG = {
  PRIMARY_COLOR: '#0066cc',
  DANGER_COLOR: '#ff4444',
  WARNING_COLOR: '#ffaa00',
  SUCCESS_COLOR: '#44aa44',
  INFO_COLOR: '#0066cc',

  // Risk thresholds
  RISK_THRESHOLDS: {
    LOW: 0,
    MEDIUM: 30,
    HIGH: 60,
    CRITICAL: 75,
  },

  // Severity levels
  SEVERITY_LEVELS: {
    INFO: 'INFO',
    WARNING: 'WARNING',
    CAUTION: 'CAUTION',
    CRITICAL: 'CRITICAL',
    EMERGENCY: 'EMERGENCY',
  },
};

// Log Configuration
export const LOG_CONFIG = {
  ENABLED: true,
  DEBUG_MODE: true,
};

export default {
  API_CONFIG,
  APP_CONFIG,
  UI_CONFIG,
  LOG_CONFIG,
};
