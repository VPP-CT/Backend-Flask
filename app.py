#!flask/bin/python
from __future__ import print_function

import logging
import json

import flight_parser
import hotel_parser

from flask import Flask, jsonify, Response, request
from iata_codes.cities import IATACodesClient
from geopy.geocoders import Nominatim

app = Flask(__name__)

# IATA database, convert between airport IATA and city name
iata_client = IATACodesClient(open("iata.key", "r").read())
# example: iata_client.get(code='MOW')), iata_client.get(name='Moscow'))

# convert city name to geo
geo = Nominatim()


@app.route('/')
def index():
    usage = """
    /flights?budget=xxx&seg=x&origin1=xxx&dest1=xxx&date1=xxxx-xx-xx<br>
    /hotels?city=xxx&checkin=xxxx-xx-xx&checkout=xxxx-xx-xx<br><br>
    ex:<br>
    /hotels?city=new%20york&checkin=2017-11-05&checkout=2017-11-10<br>
    /flights?budget=2000&seg=1&origin1=nyc&dest1=sfo&date1=2017-10-31<br>
    """
    return usage


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

    return jsonify(flight_parser.get_flights(data))


@app.route('/hotels')
def hotels():
    """Use hotel parser to fetch hotel data from APIs

    This function would get basic information from user input, then utilize
    hotel_parser lib to pass those data to API for get hotel data.

    Args:

    Returns:
        A json contains all possible hotel options.

    """
    hotel_data = hotel_data_obj()
    hotel_data.checkin_date = request.args.get('checkin')
    hotel_data.checkout_date = request.args.get('checkout')

    location = geo.geocode(request.args.get('city'))
    hotel_data.latitude = location.latitude
    hotel_data.longitude = location.longitude

    return jsonify(hotel_parser.search_hotels(hotel_data))


class flight_data_obj(object):
    """
    A class used to store flight data from user's raw input.
    """

    def __init__(self):
        pass


class hotel_data_obj(object):
    """
    A class used to store hotel data from user's raw input.
    """

    def __init__(self):
        pass

if __name__ == '__main__':
    app.run(debug=True)
