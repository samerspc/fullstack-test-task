import { Badge } from "react-bootstrap";

type Props = {
  status: string | null;
  requiresAttention: boolean;
  details: string | null;
};

export function ScanBadge({ status, requiresAttention, details }: Props) {
  return (
    <div className="d-flex flex-column gap-1">
      <Badge bg={requiresAttention ? "warning" : status ? "success" : "secondary"}>
        {status ?? "pending"}
      </Badge>
      <span className="small text-secondary">{details ?? "Ожидает обработки"}</span>
    </div>
  );
}
