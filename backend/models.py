from typing import List
from dataclasses import field

from marshmallow_dataclass import dataclass


@dataclass
class GeoLocation:
    latitude: str = field(metadata={'required': True})
    longitude: str = field(metadata={'required': True})


@dataclass
class QrCode:
    text: str = field(metadata={'required': True})


@dataclass
class OneRecordObject:
    id: str = field(metadata={'required': True})


@dataclass
class Product(OneRecordObject):
    description: str
    identifier: str


@dataclass
class Item(OneRecordObject):
    batch_number: str
    product: Product


@dataclass
class Value(OneRecordObject):
    value: float
    unit: str


@dataclass
class Dimensions(OneRecordObject):
    height: Value
    length: Value
    width: Value


@dataclass
class ServiceRequest(OneRecordObject):
    type: str


@dataclass
class WayBillNumber(OneRecordObject):
    type: str
    prefix: int
    number: int


@dataclass
class Shipment(OneRecordObject):
    gross_weight: Value
    waybill_number: WayBillNumber


@dataclass
class Piece(OneRecordObject):
    gross_weight: Value
    items: List[Item]
    stackable: bool
    dimensions: Dimensions
    service_requests: List[ServiceRequest]
    shipment: Shipment
