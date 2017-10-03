#!flask/bin/python
from __future__ import print_function

import logging
import json

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
    # TODO: create a constructor which could dynamically construct the
    # flight_data_obj by the given segment number. Each segment should contain
    # a orig, dest, and date.
    flight_data = flight_data_obj()
    flight_data.budget = request.args.get('budget')
    flight_data.seg = request.args.get('seg')
    # print (type(flight_data.seg))
    flight_data.orig = []
    flight_data.dest = []
    flight_data.date = [] 
    for x in range (1, int(flight_data.seg) + 1):
        flight_data.orig.append(request.args.get('origin%d' % x))
        flight_data.dest.append(request.args.get('dest%d' % x))
        flight_data.date.append(request.args.get('date%d' % x))
    # end TODO

    # TODO: change the logging format accordingly based on the constructor.
    logging.warning(
        "Budget:%s, Segment: %s\nOrigin1:%s, Destination1:%s, Date1:%s" % (flight_data.budget, flight_data.seg, \
            str(flight_data.orig), str(flight_data.dest), str(flight_data.date))
    )

    # TODO: based on the len(constructed_data), add each segment
    # into the request body as dict.
    slice = [dict(origin=flight_data.orig[x],
                     destination=flight_data.dest[x],
                     date=flight_data.date[x]) for x in range(0, int(flight_data.seg))]
    data = {
        "request": {
            "slice": slice,
            "passengers": dict(adultCount=1),
            "refundable": 'false'
        }
    }

    get_flights(data)

    return "/flights?budget=xxx&seg=x&origin1=xxx&dest1=xxx&date1=xxxx-xx-xx"



def get_flights(raw_input):
    file = qpx.get(raw_input)
    logging.warning(qpx.data)
    # re-formated JSON returned data
    return_data = dict()
    # only return top 50 flight data 
    for x in range(200):
        option = dict()
        option['price%d' % x] = qpx.data['trips']['tripOption'][x]['saleTotal']
        segment = dict()
        for y in range(len(qpx.data['trips']['tripOption'][x]['slice'])):
            stops = dict()
            for z in range(len(qpx.data['trips']['tripOption'][x]['slice'][y]['segment'])):
                segs = qpx.data['trips']['tripOption'][x]['slice'][y]['segment'][z]
                stop = dict()
                stop['carrier'] = segs['flight']['carrier']
                stop['flight_number'] = segs['flight']['number']
                stop['arrivalTime']= segs['leg'][0]['arrivalTime']
                stop['departureTime'] = segs['leg'][0]['departureTime']
                stop['origin'] = segs['leg'][0]['origin']
                stop['destination'] = segs['leg'][0]['destination']
                # stop['destinationTerminal'] = segs['leg'][0]['destinationTerminal']
                stops["%d" % z] = stop
            segment['%d' % y] = stops
        option['segment%d' % x] = segment
        return_data['option%d' % x] = option
    formated_return_data = json.dumps(return_data,  sort_keys=True, indent=4, separators=(',', ': '))
    print(formated_return_data, file=open('top_query.log', 'w+'))
    print(qpx.data, file=open('query.log', 'w+'))

    # TODO: re-format the data into JSON format. Remove all unnecessary
    # fields, and append a ranking field into it (now we could use price to
    # rank them.)
    return return_data
    # end TODO


class flight_data_obj(object):
    """
    A class used to store flight data from user's raw input.
    """
    def __init__(self):
        pass

if __name__ == '__main__':
    app.run(debug=True)