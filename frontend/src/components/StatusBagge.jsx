import "./StatusBadge.css";

function StatusBadge({ priority }) {
  const label = (priority || "unknown").toUpperCase();

  let className = "status-badge low";
  if (label === "HIGH") className = "status-badge high";
  if (label === "MEDIUM") className = "status-badge medium";

  return <span className={className}>{label}</span>;
}

export default StatusBadge;