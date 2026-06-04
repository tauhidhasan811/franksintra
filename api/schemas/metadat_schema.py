from typing import List, Optional, Literal
from pydantic import BaseModel


class LocationMetadata(BaseModel):
    GPSLatitude: float
    GPSLatitudeRef: Literal["N", "S"]
    GPSLongitude: float
    GPSLongitudeRef: Literal["E", "W"]


class ImageMetadata(BaseModel):
    file_name: str
    title: str
    caption: str
    description: str
    SEO_keywords: List[str]
    # copyright: Optional[str] = None
    assign_location: Optional[LocationMetadata] = None