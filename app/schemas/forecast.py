from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SeriesPoint(BaseModel):
    t: int = Field(description="Indice temporal relativo")
    votes: int = Field(ge=0, description="Conteo acumulado agregado")


class ForecastRequest(BaseModel):
    election_id: str = Field(alias="electionId", min_length=1, max_length=128)
    horizon: int = Field(default=5, ge=1, le=100)
    series: list[SeriesPoint] = Field(default_factory=list)
    start_time: Optional[datetime] = Field(alias="startTime", default=None)
    cap: Optional[int] = Field(default=None, description="Padron total para modelo logistico")

    model_config = {"populate_by_name": True}


class ForecastResponse(BaseModel):
    election_id: str = Field(serialization_alias="electionId")
    model: str
    projection: list[SeriesPoint]
    congestion_projection: list[SeriesPoint] = Field(serialization_alias="congestionProjection", default_factory=list)
    dropoff_projection: list[SeriesPoint] = Field(serialization_alias="dropoffProjection", default_factory=list)
    projected_total: int = Field(serialization_alias="projectedTotal")

    model_config = {"populate_by_name": True}
