export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const features = ['Volatility', 'Beta', 'Returns', 'Market Cap', 'P/E Ratio', 'Momentum'];

  // Realistic correlation matrix (symmetric, diagonal = 1)
  // Volatility-Beta high positive, Returns-Momentum moderate positive, etc.
  const base = [
    [1.00,  0.72, -0.31, -0.45,  0.18,  0.12],
    [0.72,  1.00, -0.22, -0.38,  0.14,  0.09],
    [-0.31,-0.22,  1.00,  0.29, -0.11,  0.61],
    [-0.45,-0.38,  0.29,  1.00, -0.52,  0.17],
    [0.18,  0.14, -0.11, -0.52,  1.00, -0.08],
    [0.12,  0.09,  0.61,  0.17, -0.08,  1.00]
  ];

  // Add small noise to make it look sampled
  const matrix = base.map((row, i) =>
    row.map((val, j) => {
      if (i === j) return 1.0;
      const noisy = val + (Math.random() - 0.5) * 0.06;
      return parseFloat(Math.max(-1, Math.min(1, noisy)).toFixed(3));
    })
  );

  res.status(200).json({ features, matrix });
}
