from dataclasses import field

from marshmallow_dataclass import dataclass


@dataclass
class GeoLocation:
    latitude: str = field(metadata={'required': True})
    longitude: str = field(metadata={'required': True})


@dataclass
class Piece:
    id: str = field(metadata={'required': True})
    content: str
    weight: float
