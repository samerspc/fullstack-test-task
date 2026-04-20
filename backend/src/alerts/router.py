from fastapi import APIRouter, Depends

from src.alerts.schemas import AlertItem
from src.alerts.service import AlertService
from src.api.deps import get_alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
async def list_alerts(service: AlertService = Depends(get_alert_service)) -> list[AlertItem]:
    items = await service.list_alerts()
    return [AlertItem.model_validate(item) for item in items]
