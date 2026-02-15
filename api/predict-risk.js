// api/predict-risk.js
export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const {
    returns = 0.01,
    volatility = 0.15,
    volume = 1000000,
    momentum = 0.05,
    beta = 1.0,
    market_cap_log = 10,
    pe_ratio = 20,
    roe = 0.12
  } = req.body;
  
  // Simulate Random Forest prediction (good model)
  // Risk increases with volatility, beta, and their interactions
  const rfPrediction = (
    0.4 * volatility +
    0.2 * Math.abs(returns) +
    0.15 * beta +
    0.1 * Math.log(volume / 1e6) * volatility +
    0.05 * momentum * volatility +
    0.05 * (pe_ratio / 20) * volatility +
    (Math.random() - 0.5) * 0.01
  );
  
  // Simulate Neural Network prediction (poor model - highly unstable)
  const nnPrediction = rfPrediction * (10 + Math.random() * 100) * (Math.random() > 0.5 ? 1 : -1);
  
  // Ensemble is average
  const ensemble = (rfPrediction + nnPrediction) / 2;
  
  res.status(200).json({
    random_forest_prediction: parseFloat(Math.abs(rfPrediction).toFixed(4)),
    neural_network_prediction: parseFloat(nnPrediction.toFixed(4)),
    ensemble_prediction: parseFloat(ensemble.toFixed(4)),
    input_features: {
      returns,
      volatility,
      volume,
      momentum,
      beta,
      market_cap_log,
      pe_ratio,
      roe
    }
  });
}
