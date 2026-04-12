export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const months = 24;
  const labels = [];
  for (let i = 0; i < months; i++) {
    const d = new Date(2024, i % 12, 1);
    labels.push(d.toLocaleString('default', { month: 'short', year: '2-digit' }));
  }

  // Generate portfolio values
  const mlPort = [100], tradPort = [100];
  for (let i = 1; i < months; i++) {
    mlPort.push(mlPort[i-1] * (1 + (Math.random() - 0.38) * 0.025));
    tradPort.push(tradPort[i-1] * (1 + (Math.random() - 0.42) * 0.022));
  }

  // Compute drawdowns
  const calcDrawdown = (prices) => {
    let peak = prices[0];
    return prices.map(p => {
      if (p > peak) peak = p;
      return parseFloat(((p - peak) / peak * 100).toFixed(2));
    });
  };

  // Compute rolling Sharpe (window=3 months, annualized)
  const calcRollingSharpe = (prices) => {
    const returns = prices.slice(1).map((p, i) => (p - prices[i]) / prices[i]);
    const sharpes = [null, null];
    for (let i = 2; i < returns.length; i++) {
      const window = returns.slice(i - 2, i + 1);
      const mean = window.reduce((a, b) => a + b, 0) / 3;
      const std = Math.sqrt(window.reduce((a, b) => a + (b - mean) ** 2, 0) / 3);
      sharpes.push(std === 0 ? 0 : parseFloat(((mean / std) * Math.sqrt(12)).toFixed(3)));
    }
    return sharpes;
  };

  res.status(200).json({
    labels,
    ml_drawdown: calcDrawdown(mlPort),
    trad_drawdown: calcDrawdown(tradPort),
    ml_sharpe: calcRollingSharpe(mlPort),
    trad_sharpe: calcRollingSharpe(tradPort),
    ml_portfolio: mlPort.map(v => parseFloat(v.toFixed(2))),
    trad_portfolio: tradPort.map(v => parseFloat(v.toFixed(2)))
  });
}
