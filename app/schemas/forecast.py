from pydantic import BaseModel, Field


class SeriesPoint(BaseModel):
    t: int = Field(description="Indice temporal relativo")
    votes: int = Field(ge=0, description="Conteo acumulado agregado")


class ForecastRequest(BaseModel):
    election_id: str = Field(alias="electionId", min_length=1, max_length=128)
    horizon: int = Field(default=5, ge=1, le=100)
    series: list[SeriesPoint] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ForecastResponse(BaseModel):
    election_id: str = Field(serialization_alias="electionId")
    model: str
    projection: list[SeriesPoint]
    projected_total: int = Field(serialization_alias="projectedTotal")

    model_config = {"populate_by_name": True}
