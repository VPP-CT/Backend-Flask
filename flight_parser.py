from __future__ import print_function

from google_flight import google_flight_api

import arrow

returnedNum = 200  # only return top 50 flight data


def get_flights(raw_input):
    # type: (str) -> dict
    """Re-format the data into JSON format.

    This function will remove all unnecessary fields, and append a ranking
    field into it.

    Args:
        raw_input: string, the orignal output from QPX.
    Returns:
        A Dict object which contains flights information ordered by price.

    """
    # Google QPX lib
    qpx = google_flight_api.GoogleFlight(open("apikey.key", "r").read())
    qpx.get(raw_input)

    return_data = dict()
    for x in range(len(qpx.data['trips']['tripOption'])):
        duration = 0
        option = dict()
        option['price'] = qpx.data['trips']['tripOption'][x]['saleTotal']
        segment = dict()

        for y in range(len(qpx.data['trips']['tripOption'][x]['slice'])):
            stops = dict()
            for z in range(len(qpx.data['trips']['tripOption'][x]['slice'][y]['segment'])):
                segs = qpx.data['trips']['tripOption'][
                    x]['slice'][y]['segment'][z]
                stop = dict()
                stop['carrier'] = segs['flight']['carrier']
                stop['flight_number'] = segs['flight']['number']
                stop['arrivalTime'] = segs['leg'][0]['arrivalTime']
                stop['departureTime'] = segs['leg'][0]['departureTime']
                stop['origin'] = segs['leg'][0]['origin']
                stop['destination'] = segs['leg'][0]['destination']
                stops["stop_%d" % z] = stop
            stops["stop_number"] = len(qpx.data['trips']['tripOption'][x]['slice'][y]['segment'])
            segment['trip_%d' % y] = stops
        for i in range(len(segment)):
            start = arrow.get(segment['trip_%d' % i]['stop_0']['departureTime']).datetime
            end = arrow.get(segment['trip_%d' % i]['stop_%d' % (len(segment['trip_%d' % i]) - 2)]['arrivalTime'])
            minutes_differ = (end - start).total_seconds() / 60.0
            duration += minutes_differ
        option['duration'] = duration
        option['trips'] = segment
        return_data['option_%d' % x] = option

    """ For debug only

    formated_return_data = json.dumps(
         return_data, sort_keys=True, indent=4, separators=(',', ': '))
    print(formated_return_data, file=open('top_query.log', 'w+')) """

    return return_data
