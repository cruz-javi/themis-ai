from fastapi import APIRouter, Depends

from app.core.security import require_service_token
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecast_service import ForecastService

router = APIRouter()
service = ForecastService()


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_service_token)],
    summary="Proyecta el resultado a partir de conteos agregados",
)
def create_forecast(payload: ForecastRequest) -> ForecastResponse:
    return service.run(payload)
