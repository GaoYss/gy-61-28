export function MetricCard({ label, value, tone = "blue" }) {
  return (
    <div className={`metric-card tone-${tone}`}>
      <span>{label}</span>
      <strong>{value ?? "-"}</strong>
    </div>
  );
}
