#!flask/bin/python
from __future__ import print_function

import logging

from flask import Flask, request
from google_flight import google_flight_api

app = Flask(__name__)
qpx = google_flight_api.GoogleFlight(open("apikey.key", "r").read())  # Google QPX lib


@app.route('/')
def index():
    return 'try /flights'


@app.route('/flights')
def flights():
    flight_data = flight_data_obj()
    flight_data.budget = request.args.get('budget')
    flight_data.seg = request.args.get('seg')
    flight_data.orig1 = request.args.get('origin1')
    flight_data.dest1 = request.args.get('dest1')
    flight_data.date1 = request.args.get('date1')

    logging.warning(
        "Budget:%s, Segment: %s\nOrigin1:%s, Destination1:%s, Date1:%s",
        flight_data.budget,
        flight_data.seg,
        flight_data.orig1,
        flight_data.dest1,
        flight_data.date1)

    data = {
        "request": {
            "slice": [
                dict(origin=flight_data.orig1, destination=flight_data.dest1, date=flight_data.date1),
            ],
            "passengers": dict(adultCount=1),
            "refundable": 'false'
        }
    }
    get_flights(data)

    return "/flights/?budget=xxx&seg=x&origin1=xxx&dest1=xxx&date1=xxxx-xx-xx"


def get_flights(raw_input):
    qpx.get(raw_input)

    logging.warning(qpx.data)
    print(qpx.data, file=open('latest_query.log', 'w+'))


class flight_data_obj(object):
    """
    A class used to store flight data from user's raw input.
    """
    pass


if __name__ == '__main__':
    app.run(debug=True)