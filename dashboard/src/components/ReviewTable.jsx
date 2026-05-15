export default function ReviewTable({ reviews }) {
  if (!reviews.length) return <p className="empty">No reviews yet.</p>

  return (
    <div className="table-wrap">
      <h2>Review History</h2>
      <table>
        <thead>
          <tr>
            <th>Repo</th>
            <th>PR</th>
            <th>Author</th>
            <th>Linter</th>
            <th>Tests</th>
            <th>Coverage</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map(r => (
            <tr key={r.id}>
              <td>{r.repo}</td>
              <td>#{r.pr_number}</td>
              <td>{r.author}</td>
              <td className={r.linter_passed ? 'pass' : 'fail'}>{r.linter_passed ? '✓' : '✗'}</td>
              <td className={r.tests_passed ? 'pass' : 'fail'}>{r.tests_passed ? '✓' : '✗'}</td>
              <td>{r.coverage_pct != null ? `${r.coverage_pct.toFixed(1)}%` : '—'}</td>
              <td>{new Date(r.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
