"""
Advanced Machine Learning Models for Locomotive Health Prediction
Includes LSTM and CNN models for time-series and sequence analysis
"""

import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
import os

class LSTMFailurePredictor:
    """LSTM-based failure prediction model for time-series sensor data"""
    
    def __init__(self, sequence_length=10, n_features=5):
        """
        Initialize LSTM predictor
        
        Args:
            sequence_length: Number of time steps for LSTM input
            n_features: Number of sensor features (temperature, vibration, pressure, oil, mileage)
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.scaler = MinMaxScaler()
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build LSTM neural network"""
        model = models.Sequential([
            layers.LSTM(64, activation='relu', input_shape=(self.sequence_length, self.n_features)),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(5, activation='sigmoid')  # 5 components: engine, braking, coupling, wheels, boiler
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        self.model = model
        return model
    
    def prepare_sequences(self, data):
        """
        Prepare data as sequences for LSTM
        
        Args:
            data: Array of shape (n_samples, 5) containing sensor readings
        
        Returns:
            Sequences of shape (n_sequences, sequence_length, 5)
        """
        scaled_data = self.scaler.fit_transform(data)
        sequences = []
        
        for i in range(len(scaled_data) - self.sequence_length):
            sequences.append(scaled_data[i:(i + self.sequence_length)])
        
        return np.array(sequences)
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train LSTM model
        
        Args:
            X: Training sequences
            y: Target failure probabilities
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Validation split ratio
        """
        if self.model is None:
            self.build_model()
        
        self.history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=3,
                    min_lr=0.00001
                )
            ],
            verbose=0
        )
        
        return self.history
    
    def predict(self, sequence):
        """
        Predict failure probabilities for components
        
        Args:
            sequence: Single sequence of shape (sequence_length, n_features)
        
        Returns:
            Array of failure probabilities for each component
        """
        if self.model is None:
            raise ValueError('Model not trained. Call train() first.')
        
        # Add batch dimension
        sequence = np.expand_dims(sequence, axis=0)
        predictions = self.model.predict(sequence, verbose=0)
        
        return predictions[0]  # Return first (only) prediction
    
    def save(self, model_path):
        """Save model and scaler"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.model.save(f'{model_path}_lstm.h5')
        
        with open(f'{model_path}_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def load(self, model_path):
        """Load model and scaler"""
        self.model = keras.models.load_model(f'{model_path}_lstm.h5')
        
        with open(f'{model_path}_scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)


class CNNFailurePredictor:
    """CNN-based failure prediction model for spatial-temporal patterns"""
    
    def __init__(self, input_shape=(10, 5, 1)):
        """
        Initialize CNN predictor
        
        Args:
            input_shape: Input shape (sequence_length, n_features, 1)
        """
        self.input_shape = input_shape
        self.model = None
        self.scaler = MinMaxScaler()
        
    def build_model(self):
        """Build CNN neural network"""
        model = models.Sequential([
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same', 
                         input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 1)),
            layers.Dropout(0.2),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 1)),
            layers.Dropout(0.2),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(5, activation='sigmoid')  # 5 components
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        self.model = model
        return model
    
    def prepare_data(self, sensor_sequences):
        """
        Prepare data for CNN
        
        Args:
            sensor_sequences: Array of shape (n_sequences, seq_length, n_features)
        
        Returns:
            Array of shape (n_sequences, seq_length, n_features, 1)
        """
        return np.expand_dims(sensor_sequences, axis=-1)
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2):
        """Train CNN model"""
        if self.model is None:
            self.build_model()
        
        self.history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ],
            verbose=0
        )
        
        return self.history
    
    def predict(self, data):
        """Predict failure probabilities"""
        if self.model is None:
            raise ValueError('Model not trained.')
        
        data = np.expand_dims(data, axis=-1)
        data = np.expand_dims(data, axis=0)
        
        predictions = self.model.predict(data, verbose=0)
        return predictions[0]
    
    def save(self, model_path):
        """Save CNN model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.model.save(f'{model_path}_cnn.h5')
    
    def load(self, model_path):
        """Load CNN model"""
        self.model = keras.models.load_model(f'{model_path}_cnn.h5')


class EnsembleFailurePredictor:
    """Ensemble model combining LSTM and CNN for robust predictions"""
    
    def __init__(self):
        """Initialize ensemble predictor"""
        self.lstm_model = LSTMFailurePredictor()
        self.cnn_model = CNNFailurePredictor()
        self.weights = {'lstm': 0.6, 'cnn': 0.4}  # LSTM weighted more
        
    def train(self, X, y, epochs=50):
        """Train both models"""
        print("Training LSTM model...")
        self.lstm_model.build_model()
        self.lstm_model.train(X, y, epochs=epochs)
        
        print("Training CNN model...")
        X_cnn = self.cnn_model.prepare_data(X)
        self.cnn_model.build_model()
        self.cnn_model.train(X_cnn, y, epochs=epochs)
    
    def predict(self, sequence):
        """
        Get ensemble prediction
        
        Args:
            sequence: Input sequence
        
        Returns:
            Weighted average of LSTM and CNN predictions
        """
        lstm_pred = self.lstm_model.predict(sequence)
        cnn_pred = self.cnn_model.predict(sequence)
        
        ensemble_pred = (
            self.weights['lstm'] * lstm_pred +
            self.weights['cnn'] * cnn_pred
        )
        
        return ensemble_pred
    
    def get_component_predictions(self, sequence):
        """Get predictions with component names"""
        components = ['ENGINE', 'BRAKING', 'COUPLING', 'WHEELS', 'BOILER']
        predictions = self.predict(sequence)
        
        return {
            component: float(pred)
            for component, pred in zip(components, predictions)
        }


class RegressionPredictor:
    """Regression model for hours-to-failure estimation"""
    
    def __init__(self):
        """Initialize regression predictor"""
        self.model = None
        self.scaler = MinMaxScaler()
        
    def build_model(self):
        """Build regression model"""
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(5,)),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='relu')  # Non-negative hours output
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, X, y, epochs=50, batch_size=32):
        """Train regression model"""
        if self.model is None:
            self.build_model()
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(
            X_scaled, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ],
            verbose=0
        )
    
    def predict_hours_to_failure(self, sensor_data):
        """
        Predict hours until failure
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Estimated hours to failure
        """
        if self.model is None:
            raise ValueError('Model not trained.')
        
        sensor_array = np.array([
            sensor_data['temperature'],
            sensor_data['vibration'],
            sensor_data['pressure'],
            sensor_data['oil_quality'],
            sensor_data['mileage']
        ]).reshape(1, -1)
        
        sensor_scaled = self.scaler.transform(sensor_array)
        hours = self.model.predict(sensor_scaled, verbose=0)[0][0]
        
        return max(1, hours)  # At least 1 hour

