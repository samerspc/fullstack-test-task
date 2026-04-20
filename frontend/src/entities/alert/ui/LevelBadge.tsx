import { Badge } from "react-bootstrap";

function pickVariant(level: string): "danger" | "warning" | "success" {
  if (level === "critical") return "danger";
  if (level === "warning") return "warning";
  return "success";
}

export function LevelBadge({ level }: { level: string }) {
  return <Badge bg={pickVariant(level)}>{level}</Badge>;
}
