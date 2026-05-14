import {
  AreaChart, Area,
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

export default function Charts({ reviews }) {
  const coverageData = [...reviews].reverse().map(r => ({
    pr: `#${r.pr_number}`,
    coverage: r.coverage_pct != null ? parseFloat(r.coverage_pct.toFixed(1)) : 0,
  }))

  const passFailData = [
    {
      name: 'Linter',
      Passed: reviews.filter(r => r.linter_passed).length,
      Failed: reviews.filter(r => !r.linter_passed).length,
    },
    {
      name: 'Tests',
      Passed: reviews.filter(r => r.tests_passed).length,
      Failed: reviews.filter(r => !r.tests_passed).length,
    },
  ]

  return (
    <div className="charts">
      <div className="chart-card">
        <h2>Coverage % Over Time</h2>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={coverageData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
            <XAxis dataKey="pr" stroke="#64748b" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 12 }} unit="%" />
            <Tooltip
              contentStyle={{ background: '#1e1e2e', border: '1px solid #2d2d3d', borderRadius: 6 }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Area type="monotone" dataKey="coverage" stroke="#6366f1" fill="#6366f122" name="Coverage %" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h2>Pass / Fail Counts</h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={passFailData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
            <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 12 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 12 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ background: '#1e1e2e', border: '1px solid #2d2d3d', borderRadius: 6 }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Passed" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Failed" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
