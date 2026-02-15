from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins including file://

# Global variables to store trained models
rf_model = None
nn_model = None
training_data = None

def generate_training_data(n_samples=1000):
    """Generate synthetic financial data for training ML models"""
    np.random.seed(42)
    
    # Features: Returns, Volatility, Volume, Momentum, Beta, Market Cap (log), P/E Ratio, ROE
    n_features = 8
    X = np.random.randn(n_samples, n_features)
    
    # Add realistic scaling
    X[:, 0] = X[:, 0] * 0.02  # Returns (-0.06 to 0.06)
    X[:, 1] = np.abs(X[:, 1] * 0.15) + 0.1  # Volatility (0.1 to 0.4)
    X[:, 2] = np.abs(X[:, 2] * 1e6) + 5e5  # Volume
    X[:, 3] = X[:, 3] * 0.1  # Momentum
    X[:, 4] = np.abs(X[:, 4] * 0.5) + 0.8  # Beta (0.3 to 1.8)
    X[:, 5] = np.abs(X[:, 5] * 2) + 8  # Market Cap (log, 6 to 12)
    X[:, 6] = np.abs(X[:, 6] * 10) + 15  # P/E Ratio (5 to 35)
    X[:, 7] = np.abs(X[:, 7] * 0.1) + 0.05  # ROE (0 to 0.25)
    
    # Target: Portfolio Risk (complex non-linear function of features)
    # Volatility has highest impact, but interactions matter
    risk = (0.4 * X[:, 1] +  # Base volatility
            0.2 * np.abs(X[:, 0]) +  # Returns magnitude
            0.15 * X[:, 4] +  # Beta
            0.1 * np.log(X[:, 2] / 1e6) * X[:, 1] +  # Volume-volatility interaction
            0.05 * X[:, 3] * X[:, 1] +  # Momentum-volatility interaction
            0.05 * (X[:, 6] / 20) * X[:, 1] +  # P/E-volatility interaction
            0.05 * np.random.randn(n_samples) * 0.01)  # Noise
    
    # Ensure risk is positive
    risk = np.abs(risk)
    
    return X, risk

def train_models():
    """Train Random Forest and Neural Network models"""
    global rf_model, nn_model, training_data
    
    # Generate training data
    X, y = generate_training_data(1000)
    training_data = (X, y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42
    )
    rf_model.fit(X_train, y_train)
    
    # Train Neural Network
    nn_model = MLPRegressor(
        hidden_layer_sizes=(64, 32, 16),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True
    )
    nn_model.fit(X_train, y_train)
    
    # Store test data for evaluation
    return X_test, y_test

# Train models on startup
print("Training ML models...")
X_test, y_test = train_models()
print("Models trained successfully!")


# Simulated portfolio data
def generate_portfolio_performance(months=12, volatility=0.02):
    """Generate realistic portfolio performance data"""
    ml_portfolio = [100]
    traditional_portfolio = [100]
    
    for i in range(months - 1):
        # ML portfolio with better risk-adjusted returns
        ml_return = np.random.normal(0.012, volatility)
        ml_portfolio.append(ml_portfolio[-1] * (1 + ml_return))
        
        # Traditional portfolio with lower returns
        trad_return = np.random.normal(0.008, volatility * 1.2)
        traditional_portfolio.append(traditional_portfolio[-1] * (1 + trad_return))
    
    return ml_portfolio, traditional_portfolio

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get portfolio performance data"""
    months = int(request.args.get('months', 12))
    
    ml_data, trad_data = generate_portfolio_performance(months)
    
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:months]
    
    return jsonify({
        'labels': labels,
        'ml_portfolio': [round(x, 2) for x in ml_data],
        'traditional_portfolio': [round(x, 2) for x in trad_data]
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get portfolio performance metrics"""
    ml_data, trad_data = generate_portfolio_performance()
    
    # Calculate metrics
    ml_return = ((ml_data[-1] / ml_data[0]) - 1) * 100
    trad_return = ((trad_data[-1] / trad_data[0]) - 1) * 100
    
    ml_returns = np.diff(ml_data) / ml_data[:-1]
    trad_returns = np.diff(trad_data) / trad_data[:-1]
    
    ml_sharpe = (np.mean(ml_returns) * 12) / (np.std(ml_returns) * np.sqrt(12))
    trad_sharpe = (np.mean(trad_returns) * 12) / (np.std(trad_returns) * np.sqrt(12))
    
    sharpe_improvement = ((ml_sharpe / trad_sharpe) - 1) * 100
    
    return jsonify({
        'ml_return': round(ml_return, 1),
        'traditional_return': round(trad_return, 1),
        'sharpe_improvement': round(sharpe_improvement, 0)
    })

@app.route('/api/model-performance', methods=['GET'])
def get_model_performance():
    """Get ML model performance metrics from actual trained models"""
    global rf_model, nn_model, X_test, y_test
    
    # Get predictions
    rf_pred = rf_model.predict(X_test)
    nn_pred = nn_model.predict(X_test)
    
    # Calculate metrics
    rf_r2 = r2_score(y_test, rf_pred)
    rf_mse = mean_squared_error(y_test, rf_pred)
    
    nn_r2 = r2_score(y_test, nn_pred)
    nn_mse = mean_squared_error(y_test, nn_pred)
    
    return jsonify({
        'random_forest': {
            'r2_score': round(rf_r2, 3),
            'mse': round(rf_mse, 4),
            'n_estimators': 100,
            'max_depth': 10
        },
        'neural_network': {
            'r2_score': round(nn_r2, 3),
            'mse': round(nn_mse, 4),
            'architecture': '64-32-16',
            'activation': 'relu'
        }
    })

@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get feature importance from trained Random Forest model"""
    global rf_model
    
    features = [
        'Returns',
        'Volatility', 
        'Volume',
        'Momentum',
        'Beta',
        'Market Cap (log)',
        'P/E Ratio',
        'ROE'
    ]
    
    # Get actual feature importance from trained model
    importance = rf_model.feature_importances_
    
    # Sort by importance
    sorted_idx = np.argsort(importance)[::-1]
    sorted_features = [features[i] for i in sorted_idx]
    sorted_importance = [importance[i] for i in sorted_idx]
    
    return jsonify({
        'features': sorted_features,
        'importance': [round(x, 3) for x in sorted_importance]
    })

@app.route('/api/risk-metrics', methods=['GET'])
def get_risk_metrics():
    """Get portfolio risk metrics"""
    return jsonify({
        'ml_portfolio': {
            'volatility': round(np.random.uniform(0.12, 0.15), 3),
            'max_drawdown': round(np.random.uniform(-0.08, -0.05), 3),
            'var_95': round(np.random.uniform(-0.025, -0.015), 4),
            'cvar_95': round(np.random.uniform(-0.035, -0.025), 4)
        },
        'traditional_portfolio': {
            'volatility': round(np.random.uniform(0.15, 0.18), 3),
            'max_drawdown': round(np.random.uniform(-0.12, -0.09), 3),
            'var_95': round(np.random.uniform(-0.032, -0.022), 4),
            'cvar_95': round(np.random.uniform(-0.045, -0.035), 4)
        }
    })

@app.route('/api/allocation', methods=['GET'])
def get_allocation():
    """Get current portfolio allocation"""
    assets = ['Tech', 'Finance', 'Healthcare', 'Energy', 'Consumer', 'Industrials']
    
    # ML-based allocation
    ml_weights = np.random.dirichlet(np.ones(len(assets)) * 3)
    
    # Traditional (more balanced) allocation
    trad_weights = np.random.dirichlet(np.ones(len(assets)) * 5)
    
    return jsonify({
        'assets': assets,
        'ml_allocation': [round(x * 100, 1) for x in ml_weights],
        'traditional_allocation': [round(x * 100, 1) for x in trad_weights]
    })

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest with custom parameters"""
    data = request.get_json()
    
    months = data.get('months', 12)
    initial_capital = data.get('initial_capital', 100000)
    
    ml_data, trad_data = generate_portfolio_performance(months)
    
    return jsonify({
        'success': True,
        'final_ml_value': round(initial_capital * (ml_data[-1] / 100), 2),
        'final_traditional_value': round(initial_capital * (trad_data[-1] / 100), 2),
        'ml_returns': [round(x, 2) for x in ml_data],
        'traditional_returns': [round(x, 2) for x in trad_data]
    })

@app.route('/api/predict-risk', methods=['POST'])
def predict_risk():
    """Predict portfolio risk using trained ML models"""
    global rf_model, nn_model
    
    data = request.get_json()
    
    # Extract features from request
    # Expected: returns, volatility, volume, momentum, beta, market_cap, pe_ratio, roe
    features = np.array([[
        data.get('returns', 0.01),
        data.get('volatility', 0.15),
        data.get('volume', 1000000),
        data.get('momentum', 0.05),
        data.get('beta', 1.0),
        data.get('market_cap_log', 10),
        data.get('pe_ratio', 20),
        data.get('roe', 0.12)
    ]])
    
    # Get predictions from both models
    rf_prediction = rf_model.predict(features)[0]
    nn_prediction = nn_model.predict(features)[0]
    
    # Ensemble prediction (average)
    ensemble_prediction = (rf_prediction + nn_prediction) / 2
    
    return jsonify({
        'random_forest_prediction': round(float(rf_prediction), 4),
        'neural_network_prediction': round(float(nn_prediction), 4),
        'ensemble_prediction': round(float(ensemble_prediction), 4),
        'input_features': {
            'returns': data.get('returns', 0.01),
            'volatility': data.get('volatility', 0.15),
            'volume': data.get('volume', 1000000),
            'momentum': data.get('momentum', 0.05),
            'beta': data.get('beta', 1.0),
            'market_cap_log': data.get('market_cap_log', 10),
            'pe_ratio': data.get('pe_ratio', 20),
            'roe': data.get('roe', 0.12)
        }
    })

@app.route('/api/model-comparison', methods=['GET'])
def get_model_comparison():
    """Compare predictions from RF vs NN on test set"""
    global rf_model, nn_model, X_test, y_test
    
    # Get predictions
    rf_pred = rf_model.predict(X_test[:50])  # First 50 test samples
    nn_pred = nn_model.predict(X_test[:50])
    actual = y_test[:50]
    
    return jsonify({
        'sample_size': 50,
        'random_forest_predictions': [round(float(x), 4) for x in rf_pred],
        'neural_network_predictions': [round(float(x), 4) for x in nn_pred],
        'actual_values': [round(float(x), 4) for x in actual],
        'rf_mse': round(float(mean_squared_error(actual, rf_pred)), 4),
        'nn_mse': round(float(mean_squared_error(actual, nn_pred)), 4)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_trained': rf_model is not None and nn_model is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
