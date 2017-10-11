#!flask/bin/python
from __future__ import print_function

import logging

import flight_parser

from flask import Flask, request
from google_flight import google_flight_api

app = Flask(__name__)

# Google QPX lib
qpx = google_flight_api.GoogleFlight(open("apikey.key", "r").read())


@app.route('/')
def index():
    return 'TRY /flights OR /flights?budget=xxx&seg=x&origin1=xxx&dest1=xxx&date1=xxxx-xx-xx'


@app.route('/flights')
def flights():
    # initialize data from RESTful call by construct a flight_data_obj
    #
    # Create a constructor which could dynamically construct the
    # flight_data_obj by the given segment number. Each segment should contain
    # a orig, dest, and date.
    flight_data = flight_data_obj()
    flight_data.budget = request.args.get('budget')
    flight_data.seg = request.args.get('seg')

    flight_data.orig = []
    flight_data.dest = []
    flight_data.date = []
    for x in range(1, int(flight_data.seg) + 1):
        flight_data.orig.append(request.args.get('origin%d' % x))
        flight_data.dest.append(request.args.get('dest%d' % x))
        flight_data.date.append(request.args.get('date%d' % x))

    logging.warning(
        "Budget:%s, Segment: %s\nOrigin1:%s, Destination1:%s, Date1:%s" % (flight_data.budget,
                                                                           flight_data.seg,
                                                                           str(flight_data.orig),
                                                                           str(flight_data.dest),
                                                                           str(flight_data.date)))

    # based on the len(constructed_data), add each segment
    # into the request body as dict.
    slice = [dict(origin=flight_data.orig[x], destination=flight_data.dest[x],
                  date=flight_data.date[x]) for x in range(0, int(flight_data.seg))]
    data = {
        "request": {
            "slice": slice,
            "passengers": dict(adultCount=1),
            "refundable": 'false'
        }
    }

    flight_parser.get_flights(data)

    return "/flights?budget=xxx&seg=x&origin1=xxx&dest1=xxx&date1=xxxx-xx-xx"


class flight_data_obj(object):
    """
    A class used to store flight data from user's raw input.
    """

    def __init__(self):
        pass

if __name__ == '__main__':
    app.run(debug=True)
