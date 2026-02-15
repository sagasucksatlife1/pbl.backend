// api/metrics.js
export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Simulate portfolio metrics
  const mlReturn = 15 + Math.random() * 6;
  const tradReturn = 11 + Math.random() * 4;
  const sharpeImprovement = 18 + Math.random() * 10;
  
  res.status(200).json({
    ml_return: parseFloat(mlReturn.toFixed(1)),
    traditional_return: parseFloat(tradReturn.toFixed(1)),
    sharpe_improvement: parseFloat(sharpeImprovement.toFixed(0))
  });
}
