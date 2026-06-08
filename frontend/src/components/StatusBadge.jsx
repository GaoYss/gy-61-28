import { statusClass } from "../utils/format";

export function StatusBadge({ value, label }) {
  return <span className={`status-badge ${statusClass(value)}`}>{label || value}</span>;
}
