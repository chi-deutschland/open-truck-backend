import datetime
import os
import json
import uuid

import requests

from flask import Flask, request
from flask_cors import CORS
from google.cloud import datastore, storage
from marshmallow.exceptions import ValidationError

from logger import init_stackdriver
from backend import parse_piece_to_piece_model
from backend.app_models import GeoLocation, QrCode
from backend.or_models import MeasurementsGeoloc, Operation


app = Flask(__name__)
CORS(app)
SERVICE_NAME = os.getenv('SERVICE')
API_TOKEN = os.getenv('API_TOKEN')


@app.route('/', methods=['GET'])
def greet():
    return 'Welcome to IATA One Record Hackathon 2021 :-)', 200


@app.route('/geolocation', methods=['POST'])
def update_geolocation():
    log = init_stackdriver(SERVICE_NAME, request)
    try:
        geo_location = GeoLocation.Schema().load(request.json)
        log.info(f'{geo_location}')
    except ValidationError as e:
        log.error(f'{e}')
        return f'{e}', 400

    measurements_geoloc = MeasurementsGeoloc(geo_location)
    client = datastore.Client()
    geo_datastore_key = client.key(KIND_GEOLOCATION)
    geo_datastore = datastore.Entity(geo_datastore_key)
    geo_datastore['created_at'] = datetime.datetime.now()
    geo_datastore['data'] = measurements_geoloc.to_json()
    geo_datastore['truck_id'] = request.args.get('truck_id')
    client.put(geo_datastore)
    return '', 200


@app.route('/piece', methods=['POST'])
def fetch_piece():
    log = init_stackdriver(SERVICE_NAME, request)
    try:
        qr_code = QrCode.Schema().load(request.json)
        log.info(f'{qr_code}')
    except ValidationError as e:
        log.error(f'{e}')
        return f'{e}', 400
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    response = requests.request("GET", qr_code.text, headers=headers)
    log.info(json.loads(response.text))
    piece = parse_piece_to_piece_model(response.text)

    person_id = f"{DOMAIN}/driver/{request.args.get('driver_id')}"
    truck_id = f"{DOMAIN}/driver/{request.args.get('driver_id')}"
    person_operation = Operation().add_person(person_id)
    truck_operation = Operation().add_truck(truck_id)
    # Todo test if it works
    response = requests.request(
        "PATCH",
        qr_code.text,
        headers=headers,
        data=truck_operation.to_json())
    log.info(json.loads(response.text))

    response = requests.request(
        "PATCH",
        qr_code.text,
        headers=headers,
        data=person_operation.to_json())
    log.info(json.loads(response.text))

    return piece.Schema().dump(piece), 200


@app.route('/photo/upload', methods=['POST'])
def upload_photo():
    log = init_stackdriver(SERVICE_NAME, request)
    piece_id = request.headers.get('iata_piece_id')
    temp_file = f'/tmp/{uuid.uuid4()}.jpg'
    with open(temp_file, 'wb') as f:
        f.write(request.data)

    # parse request body base64 encoded image
    # upload image
    object_name = f"{uuid.uuid4()}.jpeg"
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    blob.upload_from_filename(temp_file)
    log.info(f"File {temp_file} uploaded to {object_name}")

    # create IATA Reference Object
    db_id = f'{DOMAIN}/reference/{uuid.uuid4()}'
    data = {
        "https://onerecord.iata.org/Piece#externalReferences": [{
                "@id": db_id,
                "@type": [
                    "https://onerecord.iata.org/ExternalReference"],
                "https://onerecord.iata.org/ExternalReference#documentType": "FOTO",
                "https://onerecord.iata.org/ExternalReference#documentChecksum": "D41D8CD98F00B204E980",
                "https://onerecord.iata.org/ExternalReference#documentLink":
                    f"https://storage.cloud.google.com/{BUCKET_NAME}/{object_name}"}]}
    log.info(f"Created reference object")
    log.info(data)

    # store IATA Reference Object
    client = datastore.Client()
    db_key = client.key(KIND_REFERENCE)
    db_entity = datastore.Entity(db_key)
    db_entity['created_at'] = datetime.datetime.now()
    db_entity['data'] = json.dumps(data)
    db_entity['reference_id'] = db_id
    client.put(db_entity)

    ext_ref = {
      "@type": ["https://onerecord.iata.org/api/PatchRequest"],
      "https://onerecord.iata.org/api/PatchRequest#description": "Add extRef",
      "https://onerecord.iata.org/api/PatchRequest#operations": [{
          "@type": ["https://onerecord.iata.org/api/Operation"],
          "https://onerecord.iata.org/api/Operation#o": {
            "@type": ["https://onerecord.iata.org/api/OperationObject"],
            "https://onerecord.iata.org/api/OperationObject#datatype": "https://onerecord.iata.org/ExternalReference",
            "https://onerecord.iata.org/api/OperationObject#extRefValue": {
              "@id": db_id,
              "@type": ["https://onerecord.iata.org/ExternalReference"]}},

          "https://onerecord.iata.org/api/Operation#op": "add",
          "https://onerecord.iata.org/api/Operation#p": "https://onerecord.iata.org/Piece#externalReferences"}]}

    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    response = requests.request(
        "PATCH",
        piece_id,
        headers=headers,
        data=json.dumps(ext_ref))
    log.info(json.loads(response.text))

    return 'Upload successfully', 200


@app.route('/reference/<reference_id>')
def get_reference(reference_id: str):
    log = init_stackdriver(SERVICE_NAME, request)
    db_id = f'{DOMAIN}/reference/{reference_id}'
    log.info(f"Fetch data form db from id: {db_id}")
    client = datastore.Client()
    query = client.query(kind=KIND_REFERENCE)
    query.add_filter('reference_id', '=', db_id)
    entities = query.fetch()
    log.info("Fetched data form db")
    log.info(entities)
    for e in entities:
        log.info("Fetched results")
        log.info(e)
        return e.get('data'), 200
    return '', 200


@app.route('/Trucks/<truck_id>/IOTDev/GeoSensor', methods=['GET'])
def get_truck_iot_dev_geo_sensor(truck_id: str):
    # fetch data from db
    log = init_stackdriver(SERVICE_NAME, request)
    log.info("Fetch data form db")
    client = datastore.Client()
    query = client.query(kind=KIND_GEOLOCATION)
    query.add_filter('truck_id', '=', truck_id)
    entities = query.fetch()
    result = []
    for e in entities:
        if e.get('data') is not None:
            d = json.loads(e['data'])
            result.append(d)
    log.info("Fetched results")
    log.info(result)
    return json.dumps(result), 200


@app.route('/driver/<driver_id>', methods=['GET'])
def get_driver_information(driver_id: str):
    log = init_stackdriver(SERVICE_NAME, request)
    log.info("Fetch data form db")
    client = datastore.Client()
    query = client.query(kind=KIND_DRIVER)
    query.add_filter('driver_id', '=', driver_id)
    entities = query.fetch()
    for e in entities:
        log.info("Fetched results")
        log.info(e)
        return e.get('data'), 200
    return '', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
