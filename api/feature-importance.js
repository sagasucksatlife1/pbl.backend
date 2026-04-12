export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const features = ['Volatility','Beta','Returns','Market Cap (log)','P/E Ratio','Momentum','Volume','ROE'];
  const importance = [
    0.35 + Math.random() * 0.05,
    0.18 + Math.random() * 0.04,
    0.12 + Math.random() * 0.03,
    0.10 + Math.random() * 0.02,
    0.08 + Math.random() * 0.02,
    0.07 + Math.random() * 0.02,
    0.06 + Math.random() * 0.01,
    0.04 + Math.random() * 0.01
  ];

  res.status(200).json({ features, importance: importance.map(v => parseFloat(v.toFixed(3))) });
}
