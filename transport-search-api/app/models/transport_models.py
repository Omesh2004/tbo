from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import datetime


class SearchRequest(BaseModel):
    origin: str = Field(..., examples=["Kolkata"])
    destination: str = Field(..., examples=["Delhi"])
    travel_date: datetime.date = Field(..., alias="date", examples=["2026-03-20"])
    adults: int = Field(default=1, ge=1, le=9)
    sort_by: str = Field(default="price")

    model_config = {"populate_by_name": True}

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        if v not in ("price", "duration"):
            raise ValueError("sort_by must be 'price' or 'duration'")
        return v


class TransportOption(BaseModel):
    type: str  # "flight" | "train" | "bus"
    provider: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    currency: str = "INR"

    # Flight-specific (optional)
    flight_number: Optional[str] = None
    cabin_class: Optional[str] = None
    stops: Optional[int] = None
    airline_code: Optional[str] = None

    # Train-specific (optional)
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    train_class: Optional[str] = None

    # Bus-specific (optional)
    bus_type: Optional[str] = None
    amenities: Optional[List[str]] = None


class SearchResponse(BaseModel):
    origin: str
    destination: str
    date: str
    total_results: int
    sort_by: str
    transport_options: List[TransportOption]
