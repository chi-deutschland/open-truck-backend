import uuid
import time
import json

from .app_models import GeoLocation


class MeasurementsGeoloc:
    def __init__(self, geo_location: GeoLocation) -> None:
        self.id = f"{uuid.uuid4()}"
        self.measurement_id = f"{uuid.uuid4()}"
        self.latitude = float(geo_location.latitude)
        self.longitude = float(geo_location.longitude)
        self.timestamp = int(time.time())

    def to_json(self) -> str:
        geo_data = {
            "@id": self.id,
            "@type": [
                "https://onerecord.iata.org/Measurements",
                "https://onerecord.iata.org/MeasurementsGeoloc"],
            "https://onerecord.iata.org/MeasurementsGeoloc#geolocationMeasurement": {
                "@id": self.measurement_id,
                "@type": [
                    "https://onerecord.iata.org/Geolocation"],
                "https://onerecord.iata.org/Geolocation#latitude": self.latitude,
                "https://onerecord.iata.org/Geolocation#longitude": self.longitude, },
            "https://onerecord.iata.org/Measurements#measurementTimestamp": self.timestamp}
        return json.dumps(geo_data)


class Operation:
    def __init__(self) -> None:
        self.key_operations = 'https://onerecord.iata.org/api/PatchRequest#operations'
        self.key_operation = "https://onerecord.iata.org/api/Operation#o"
        self.key_transport_means = "https://onerecord.iata.org/api/OperationObject#transportMeansValue"
        self.operation = {
            "@type": ["https://onerecord.iata.org/api/PatchRequest"],
            "https://onerecord.iata.org/api/PatchRequest#description": "Add TransportMeans",
            "https://onerecord.iata.org/api/PatchRequest#operations": [{
                "@type": ["https://onerecord.iata.org/api/Operation"],
                "https://onerecord.iata.org/api/Operation#o": {
                  "@type": ["https://onerecord.iata.org/api/OperationObject"],
                  "https://onerecord.iata.org/api/OperationObject#datatype": "https://onerecord.iata.org/TransportMeans",
                  "https://onerecord.iata.org/api/OperationObject#parentId": "www.schenker.com/Segments/AppleWH-FRA",
                  "https://onerecord.iata.org/api/OperationObject#transportMeansValue": {
                    "@id": "",
                    "@type": ""}},
                "https://onerecord.iata.org/api/Operation#op": "add",
                "https://onerecord.iata.org/api/Operation#p": "https://onerecord.iata.org/TransportMovement#transportMeans"}]}

    def add_person(self, person_id: str):
        self.operation[self.key_operations]
        [0]
        [self.key_operation]
        [self.key_transport_means]["@id"] = person_id
        self.operation[self.key_operations]
        [0]
        [self.key_operation]
        [self.key_transport_means]["@type"] = "https://onerecord.iata.org/Person"
        return self

    def add_truck(self, truck_id):
        self.operation[self.key_operations]
        [0]
        [self.key_operation]
        [self.key_transport_means]["@id"] = truck_id
        self.operation[self.key_operations]
        [0]
        [self.key_operation]
        [self.key_transport_means]["@type"] = "https://onerecord.iata.org/TransportMeans"
        return self

    def to_json(self) -> str:
        return json.dumps(self.operation)
