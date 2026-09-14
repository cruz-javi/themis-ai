from app.models.baseline import BaselineProjection
from app.schemas.forecast import ForecastRequest, ForecastResponse, SeriesPoint


class ForecastService:
    def __init__(self, model: BaselineProjection | None = None) -> None:
        self._model = model or BaselineProjection()

    def run(self, request: ForecastRequest) -> ForecastResponse:
        ordered = sorted(request.series, key=lambda point: point.t)
        t = [point.t for point in ordered]
        votes = [point.votes for point in ordered]

        future_t, predicted = self._model.fit_predict(t, votes, request.horizon)

        projection = [
            SeriesPoint(t=step, votes=value)
            for step, value in zip(future_t, predicted, strict=True)
        ]

        projected_total = projection[-1].votes if projection else 0

        return ForecastResponse(
            election_id=request.election_id,
            model=self._model.name,
            projection=projection,
            projected_total=projected_total,
        )
