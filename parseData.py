from __future__ import print_function

import logging
import json

from google_flight import google_flight_api

returnedNum = 50

def get_flights(raw_input):
    # Google QPX lib
    qpx = google_flight_api.GoogleFlight(open("apikey.key", "r").read())

    file = qpx.get(raw_input)
    logging.warning(qpx.data)
    # re-formated JSON returned data
    return_data = dict()
    # only return top 50 flight data 
    for x in range(returnedNum):
        option = dict()
        option['price'] = qpx.data['trips']['tripOption'][x]['saleTotal']
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
                stops["stop%d" % z] = stop
            segment['trip%d' % y] = stops
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
