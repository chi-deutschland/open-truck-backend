import json

from .models import Piece, Value, Dimensions, ServiceRequest, Item, Product, Shipment, WayBillNumber


def parse_piece_to_piece_model(json_ld: str) -> Piece:
    d = json.loads(json_ld)
    height = d\
        .get("https://onerecord.iata.org/Piece#dimensions", "")\
        .get("https://onerecord.iata.org/Dimensions#height", "")
    width = d \
        .get("https://onerecord.iata.org/Piece#dimensions", "") \
        .get("https://onerecord.iata.org/Dimensions#width", "")
    length = d \
        .get("https://onerecord.iata.org/Piece#dimensions", "") \
        .get("https://onerecord.iata.org/Dimensions#length", "")
    dims = Dimensions(
        id='',
        height=Value(
            id=height.get('@id', ''),
            value=height.get("https://onerecord.iata.org/Value#value", ''),
            unit=height.get("https://onerecord.iata.org/Value#unit", ''),),
        length=Value(
            id=length.get('@id', ''),
            value=length.get("https://onerecord.iata.org/Value#value", ''),
            unit=length.get("https://onerecord.iata.org/Value#unit", ''),),
        width=Value(
            id=width.get('@id', ''),
            value=width.get("https://onerecord.iata.org/Value#value", ''),
            unit=width.get("https://onerecord.iata.org/Value#unit", ''),),)
    gross_weight = Value(id='',
                         value=d
                             .get('https://onerecord.iata.org/Piece#grossWeight', '')
                             .get('https://onerecord.iata.org/Value#value', 0.0),
                         unit=d
                             .get('https://onerecord.iata.org/Piece#grossWeight', '')
                             .get('https://onerecord.iata.org/Value#value', 0.0), )
    service_requests = []
    for srv_req in d.get("https://onerecord.iata.org/Piece#serviceRequest", ""):
        service_requests.append(ServiceRequest(
            id=srv_req.get("@id", ""),
            type=srv_req.get("https://onerecord.iata.org/ServiceRequest#serviceRequestDescription", "")))

    contained_items = []
    for pieces in d.get("https://onerecord.iata.org/Piece#containedPieces", []):
        for item in pieces.get("https://onerecord.iata.org/Piece#containedItems", []):
            contained_items.append(
                Item(
                    id=item.get("@id", ""),
                    batch_number=item.get("https://onerecord.iata.org/Item#batchNumber", ""),
                    product=Product(
                        id=item
                            .get("https://onerecord.iata.org/Item#product", "")
                            .get("@id", ""),
                        description=item
                            .get("https://onerecord.iata.org/Item#product", "")
                            .get("https://onerecord.iata.org/Product#productDescription", ""),
                        identifier=item
                            .get("https://onerecord.iata.org/Item#product", "")
                            .get("https://onerecord.iata.org/Product#productIdentifier", ""),),),)
    shp = d.get("https://onerecord.iata.org/Piece#shipment", "")
    way_bill = shp.get("https://onerecord.iata.org/Shipment#waybillNumber", "")
    booking = way_bill.get("https://onerecord.iata.org/Waybill#booking")
    shipment = Shipment(
        id=shp.get("@id", ""),
        gross_weight=Value(id='',
                           value=shp
                           .get("https://onerecord.iata.org/Shipment#totalGrossWeight", "")
                           .get("https://onerecord.iata.org/Value#value", ""),
                           unit=shp
                           .get("https://onerecord.iata.org/Shipment#totalGrossWeight", "")
                           .get("https://onerecord.iata.org/Value#unit", ""),),
        waybill_number=WayBillNumber(id=way_bill.get("@id", ""),
                                     type=way_bill
                                     .get("https://onerecord.iata.org/Waybill#waybillType", ""),
                                     prefix=way_bill
                                     .get("https://onerecord.iata.org/Waybill#waybillPrefix", 0),
                                     number=way_bill
                                     .get("https://onerecord.iata.org/Waybill#waybillNumber", 0),))
    piece = Piece(
        id=d.get('@id', ''),
        gross_weight=gross_weight,
        dimensions=dims,
        stackable=d.get('https://onerecord.iata.org/Piece#stackable', False),
        service_requests=service_requests,
        items=contained_items,
        shipment=shipment,)
    return piece
