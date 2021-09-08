import os
import json
import requests

from flask import Flask, request
from google.cloud import datastore
from marshmallow.exceptions import ValidationError

from logger import init_stackdriver
from backend import parse_piece_to_piece_model
from backend.models import GeoLocation, QrCode


app = Flask(__name__)
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
    return piece.Schema().dump(piece), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
