/**
 * API Service for Smart Locomotive Health Monitor
 * Connects to Flask backend at http://localhost:5000
 */

// Change this to your backend server IP/domain in production
const API_BASE_URL = 'http://localhost:5000/api';

// Timeout for API requests (10 seconds)
const TIMEOUT = 10000;

/**
 * Wrapper for fetch with timeout
 */
const fetchWithTimeout = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

/**
 * Get all locomotives
 */
export const getLocomotives = async () => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/locomotives`);
    return response;
  } catch (error) {
    console.error('Error fetching locomotives:', error);
    throw error;
  }
};

/**
 * Get single locomotive by ID
 */
export const getLocomotiveById = async (id) => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/locomotives/${id}`);
    return response;
  } catch (error) {
    console.error(`Error fetching locomotive ${id}:`, error);
    throw error;
  }
};

/**
 * Perform health analysis on a locomotive
 */
export const performHealthAnalysis = async (id, sensorData) => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sensorData),
    });
    return response;
  } catch (error) {
    console.error(`Error analyzing health for ${id}:`, error);
    throw error;
  }
};

/**
 * Get alerts for a locomotive
 */
export const getAlerts = async (id) => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/alerts/${id}`);
    return response;
  } catch (error) {
    console.error(`Error fetching alerts for ${id}:`, error);
    throw error;
  }
};

/**
 * Get nearby junctions and sheds
 */
export const getNearbyLocations = async (id, latitude, longitude) => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/locations/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ latitude, longitude }),
    });
    return response;
  } catch (error) {
    console.error(`Error fetching nearby locations for ${id}:`, error);
    throw error;
  }
};

/**
 * Get dashboard summary
 */
export const getDashboardSummary = async () => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/summary`);
    return response;
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    throw error;
  }
};

/**
 * Health check - verify backend is running
 */
export const healthCheck = async () => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL.replace('/api', '')}`);
    return response;
  } catch (error) {
    console.error('Backend health check failed:', error);
    throw error;
  }
};

export default {
  getLocomotives,
  getLocomotiveById,
  performHealthAnalysis,
  getAlerts,
  getNearbyLocations,
  getDashboardSummary,
  healthCheck,
  API_BASE_URL,
};
