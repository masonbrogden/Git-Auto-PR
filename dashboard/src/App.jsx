import { useState, useEffect } from 'react'
import ReviewTable from './components/ReviewTable'
import Charts from './components/Charts'
import './App.css'

const API_URL = window.API_URL || 'http://localhost:8000'

export default function App() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/reviews`)
      .then(r => r.json())
      .then(data => { setReviews(data); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  const total = reviews.length
  const avgCoverage = total
    ? (reviews.reduce((s, r) => s + (r.coverage_pct || 0), 0) / total).toFixed(1)
    : 0
  const linterPassRate = total
    ? Math.round(reviews.filter(r => r.linter_passed).length / total * 100)
    : 0
  const testPassRate = total
    ? Math.round(reviews.filter(r => r.tests_passed).length / total * 100)
    : 0

  if (loading) return <div className="center">Loading…</div>
  if (error) return <div className="center error">Error: {error}</div>

  return (
    <div className="app">
      <header>
        <h1>Git-Auto-PR</h1>
        <span className="subtitle">Automated PR Review Dashboard</span>
      </header>

      <div className="stats">
        <StatCard label="Total Reviews" value={total} />
        <StatCard label="Avg Coverage" value={`${avgCoverage}%`} />
        <StatCard label="Linter Pass" value={`${linterPassRate}%`} />
        <StatCard label="Tests Pass" value={`${testPassRate}%`} />
      </div>

      <Charts reviews={reviews} />
      <ReviewTable reviews={reviews} />
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
