export function formatDateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function statusClass(value) {
  if (["online", "approved", "success", "resolved"].includes(value)) return "success";
  if (["open", "high", "denied", "offline", "rejected"].includes(value)) return "danger";
  if (["processing", "pending", "maintenance", "medium"].includes(value)) return "warning";
  return "neutral";
}
