export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const months = parseInt(req.query.months) || 12;
  const mlPortfolio = [100], tradPortfolio = [100];

  for (let i = 1; i < months; i++) {
    mlPortfolio.push(mlPortfolio[i-1] * (1 + (Math.random() - 0.4) * 0.024));
    tradPortfolio.push(tradPortfolio[i-1] * (1 + (Math.random() - 0.45) * 0.02));
  }

  const labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].slice(0, months);
  res.status(200).json({
    labels,
    ml_portfolio: mlPortfolio.map(v => parseFloat(v.toFixed(2))),
    traditional_portfolio: tradPortfolio.map(v => parseFloat(v.toFixed(2)))
  });
}
