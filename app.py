#!flask/bin/python
from __future__ import print_function

import flight_parser
import hotel_parser

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from iata_codes.cities import IATACodesClient
from geopy.geocoders import Nominatim

app = Flask(__name__)
CORS(app)

# IATA database, convert between airport IATA and city name
iata_client = IATACodesClient(open("iata.key", "r").read())
# example: iata_client.get(code='MOW')), iata_client.get(name='Moscow'))

# convert city name to geo
geo = Nominatim()

each_option_num = 2


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/packages')
def packages():
    flight_result = flight()
    package_data = dict()
    # cheapest flight& cheapest hotel(2 packages)
    index = 0
    for x in range(index + each_option_num):
        package_data['flight_%d' % x] = flight_result['option_0']
        package_data['hotel_%d' % x] = hotels_package(flight_result, 0, x, 1)
    index += each_option_num

    # 50% flight& 50% hotel(2 packages)
    percent_flight_index = 'option_0'
    flag = 1
    for key, value in flight_result.iteritems():
        if float(value['price'][3:]) >= float(request.args.get('budget')) / 2:
            percent_flight_index = key
            flag = 0
            break
    if flag == 1:
        percent_flight_index = 'option_%d' % (len(flight_result) - 1)
    for x in range(index + each_option_num):
        package_data['flight_%d' % x] = flight_result[percent_flight_index]
        package_data['hotel_%d' % x] = hotels_package(
            flight_result, int(percent_flight_index[7:]), x, 0.5)
    index += each_option_num
    # 70% flight& 30% hotel(2 packages)
    percent_flight_index = 'option_0'
    flag = 1
    for key, value in flight_result.iteritems():
        if float(value['price'][3:]) >= float(request.args.get('budget')) * 7 / 10:
            percent_flight_index = key
            flag = 0
            break
    if flag == 1:
        percent_flight_index = 'option_%d' % (len(flight_result) - 1)
    for x in range(index + each_option_num):
        package_data['flight_%d' % x] = flight_result[percent_flight_index]
        package_data['hotel_%d' % x] = hotels_package(
            flight_result, int(percent_flight_index[7:]), x, 0.3)

    return jsonify(package_data)


def hotels_package(flight_result, option_num, hotel_option_num, percent):
    """
    option_num : corresponding flight option number
    hotel_option_num : which hotel should we return- for example : first and second one
    percent: price constrain for the hotel option

    example query:
    http://127.0.0.1:5000/packages?budget=2000&seg=3&origin1=nyc&dest1=sfo&date1=2017-11-15&origin2=sfo&dest2=lax&date2=2017-11-20&origin3=lax&dest3=nyc&date3=2017-11-25
    """
    hotel_results = dict()
    for x in range(len(flight_result['option_%d' % option_num]['trips']) - 1):
        trip_cur = flight_result['option_%d' %
                                 option_num]['trips']['trip_%d' % x]
        trip_next = flight_result['option_%d' %
                                  option_num]['trips']['trip_%d' % (x + 1)]
        hotel_data = hotel_data_obj()
        hotel_data.checkin_date = trip_cur[
            'stop_%d' % (len(trip_cur) - 2)]['arrivalTime'][:10]
        hotel_data.checkout_date = trip_next['stop_0']['departureTime'][:10]
        location = geo.geocode(request.args.get('dest%d' % x))
        hotel_data.latitude = location.latitude
        hotel_data.longitude = location.longitude
        hotel_result = hotel_parser.search_hotels(hotel_data)
        if percent == 1:
            hotel_results['trip_%d' % x] = hotel_result[
                'hotel_%d' % hotel_option_num]
        else:
            flag = 1
            percent_hotel_index = 'hotel_0'
            for key, value in hotel_result.iteritems():
                if float(value['rateWithTax'][3:]) >= float(request.args.get('budget')) * percent:
                    percent_hotel_index = key
                    flag = 0
                    break
            if flag == 1:
                percent_hotel_index = 'hotel_%d' % (len(hotel_result) - 1)
            final_hotel_index = 'hotel_%d' % (
                int(percent_hotel_index[7:]) + hotel_option_num)
            hotel_results['trip_%d' % x] = hotel_result[final_hotel_index]
    return hotel_results


def flight():
    # initialize data from RESTful call by construct a flight_data_obj
    #
    # Create a constructor which could dynamically construct the
    # flight_data_obj by the given segment number. Each segment should contain
    # a orig, dest, and date.
    flight_data = flight_data_obj()
    flight_data.budget = "USD" + request.args.get('budget')
    flight_data.seg = request.args.get('seg')

    flight_data.orig = []
    flight_data.dest = []
    flight_data.date = []
    for x in range(1, int(flight_data.seg) + 1):
        flight_data.orig.append(request.args.get('origin%d' % x))
        flight_data.dest.append(request.args.get('dest%d' % x))
        flight_data.date.append(request.args.get('date%d' % x))

    # based on the len(constructed_data), add each segment
    # into the request body as dict.
    slice = [dict(origin=flight_data.orig[x], destination=flight_data.dest[x],
                  date=flight_data.date[x]) for x in range(0, int(flight_data.seg))]
    data = {
        "request": {
            "slice": slice,
            "passengers": dict(adultCount=1),
            "refundable": 'false',
            "maxPrice": flight_data.budget
        }
    }

    return flight_parser.get_flights(data)


@app.route('/flights')
def flights():
    # initialize data from RESTful call by construct a flight_data_obj
    #
    # Create a constructor which could dynamically construct the
    # flight_data_obj by the given segment number. Each segment should contain
    # a orig, dest, and date.
    flight_data = flight_data_obj()
    flight_data.budget = "USD" + request.args.get('budget')
    flight_data.seg = request.args.get('seg')

    flight_data.orig = []
    flight_data.dest = []
    flight_data.date = []
    for x in range(1, int(flight_data.seg) + 1):
        flight_data.orig.append(request.args.get('origin%d' % x))
        flight_data.dest.append(request.args.get('dest%d' % x))
        flight_data.date.append(request.args.get('date%d' % x))

    # based on the len(constructed_data), add each segment
    # into the request body as dict.
    slice = [dict(origin=flight_data.orig[x], destination=flight_data.dest[x],
                  date=flight_data.date[x]) for x in range(0, int(flight_data.seg))]
    data = {
        "request": {
            "slice": slice,
            "passengers": dict(adultCount=1),
            "refundable": 'false',
            "maxPrice": flight_data.budget
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
    app.run(host='127.0.0.1', port=5000, debug=True)
