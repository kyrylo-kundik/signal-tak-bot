import datetime
import typing
import uuid

import pydantic


class GeoLocation(pydantic.BaseModel):
    lat: float = pydantic.Field(ge=-90, le=90)
    lon: float = pydantic.Field(ge=-180, le=180)
    hae: typing.Optional[float] = None
    ce: typing.Optional[float] = None
    le: typing.Optional[float] = None
    description: typing.Optional[str] = None
    timestamp: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class SignalMessage(pydantic.BaseModel):
    geolocation: GeoLocation
    message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    timestamp: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    status: str = "pending"
    retry_count: int = 0

    @property
    def content(self) -> str:
        return (
            f"{self.geolocation.lon} {self.geolocation.lat} "
            f"{self.geolocation.description or 'Unknown'}"
        )


class CotEvent(pydantic.BaseModel):
    event_id: str
    event_type: str
    time: datetime.datetime
    start: datetime.datetime
    stale: datetime.datetime
    how: str
    point: GeoLocation
    status: str = "pending"
