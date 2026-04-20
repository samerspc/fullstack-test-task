import { Badge } from "react-bootstrap";

type Variant = "success" | "warning" | "danger" | "secondary";

function pickVariant(status: string): Variant {
  if (status === "failed") return "danger";
  if (status === "processing") return "warning";
  if (status === "processed") return "success";
  return "secondary";
}

export function ProcessingBadge({ status }: { status: string }) {
  return <Badge bg={pickVariant(status)}>{status}</Badge>;
}
