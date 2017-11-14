#!flask/bin/python
from __future__ import print_function

import flight_parser
import hotel_parser
import pdb
import geocoder
import os

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from iata_codes.cities import IATACodesClient
from geopy.geocoders import Nominatim
from collections import OrderedDict


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# IATA database, convert between airport IATA and city name
iata_client = IATACodesClient(open("iata.key", "r").read())
# example: iata_client.get(code='MOW')), iata_client.get(name='Moscow'))

# number of package for different category
each_option_num = 2


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/packages')
def packages():
    '''
    example query:
    http://0.0.0.0:80/packages?budget=2000&seg=3&origin1=nyc&dest1=sfo&date1=2017-11-15&origin2=sfo&dest2=lax&date2=2017-11-20&origin3=lax&dest3=nyc&date3=2017-11-25
    
    '''
    flight_result = flight()
    package_data = dict()

    # cheapest flight& cheapest hotel(2 packages)
    package_data_hotel = hotels_package(flight_result, 0, each_option_num, 1, "find_cheapest")
    for x in range(each_option_num):
        package_detail = dict()
        package_detail['flight'] = flight_result['option_0']
        package_detail['hotel'] = package_data_hotel[x]
        package_detail['totalPrice'] = float(package_detail['flight']['price'][3:].replace(',', '')) + package_detail['hotel']['price']
        package_data['package_%d' % x] = package_detail

    # cheapest flight with non stopover && cheapest hotel with closest distance to the center 
    nonstop_flight_index = 'option_0'
    for key, value in flight_result.iteritems():
        nonstop = True
        for x in range(len(flight_result[key]['trips'])):
            if flight_result[key]['trips']['trip_%d' % x]['stop_number'] > 1 :
                nonstop = False
                break
        if nonstop:
            nonstop_flight_index = key
            break
    package_data_hotel = hotels_package(flight_result, int(nonstop_flight_index[7:]), each_option_num, 1, "find_closest")
    for x in range(each_option_num):
        package_detail = dict()
        package_detail['flight'] = flight_result[nonstop_flight_index]
        package_detail['hotel'] = package_data_hotel[x]
        package_detail['totalPrice'] = float(package_detail['flight']['price'][3:].replace(',', '')) + package_detail['hotel']['price']
        package_data['package_%d' % (x + each_option_num)] = package_detail

    # shortest flight && starRating more than 3 hotel
    shortest_flight_index = 'option_0'
    shortest_time = float('inf')
    for key, value in flight_result.iteritems():
        if float(flight_result[key]['duration']) < shortest_time :
            shortest_time = float(flight_result[key]['duration'])
            shortest_flight_index = key
    package_data_hotel = hotels_package(flight_result, int(shortest_flight_index[7:]), each_option_num, 1, "find_star")
    for x in range(each_option_num):
        package_detail = dict()
        package_detail['flight'] = flight_result[shortest_flight_index]
        package_detail['hotel'] = package_data_hotel[x]
        package_detail['totalPrice'] = float(package_detail['flight']['price'][3:].replace(',', '')) + package_detail['hotel']['price']
        package_data['package_%d' % (x + each_option_num * 2)] = package_detail

    return jsonify(package_data)

'''
    - This part of code is for the price distribution diversity for both flight& hotel.
    - save it for later

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
'''

def hotels_package(flight_result, option_num, hotel_option_num, percent, purpose):
    """
    option_num : corresponding flight option number
    hotel_option_num : which hotel should we return- for example : first and second one
    percent: price constrain for the hotel option

    """
    package_data_hotel = []
    hotel_results0 = dict()
    hotel_results1 = dict()
    hotel_price0 = 0.0
    hotel_price1 = 0.0
    for x in range(len(flight_result['option_%d' % option_num]['trips']) - 1):
        trip_cur = flight_result['option_%d' % option_num]['trips']['trip_%d' % x]
        trip_next = flight_result['option_%d' % option_num]['trips']['trip_%d' % (x + 1)]
        hotel_data = hotel_data_obj()
        hotel_data.checkin_date = trip_cur['stop_%d' % (len(trip_cur) - 2)]['arrivalTime'][:10]
        hotel_data.checkout_date = trip_next['stop_0']['departureTime'][:10]
        dess = iata_client.get(code=trip_cur['stop_%d' % (len(trip_cur) -2)]['destination'])
        g = geocoder.google(dess[0]['name'])
        hotel_data.latitude = g.latlng[0]
        hotel_data.longitude = g.latlng[1]
        hotel_result = hotel_parser.search_hotels(hotel_data)

        if purpose == "find_cheapest":
            hotel_results0['trip_%d' % x] = hotel_result['hotel_0']
            hotel_price0 = hotel_price0 + float(hotel_results0['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
            hotel_results1['trip_%d' % x] = hotel_result['hotel_1']
            hotel_price1 = hotel_price0 + float(hotel_results1['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
        hotel_results0['price'] = hotel_price0
        hotel_results1['price'] = hotel_price1

        if purpose == "find_closest":
            closest_hotel_index = []
            closest_hotel_index.append('hotel_0')
            closest_hotel_index.append('hotel_0')            
            minimal_distance_hotel = float('inf')
            secminimal_distance_hotel = float('inf')
            for key, value in hotel_result.iteritems():
                if minimal_distance_hotel >=4.0 and float(hotel_result[key]['distanceFromCenter']) < minimal_distance_hotel:
                    closest_hotel_index[0] = key
                    minimal_distance_hotel = float(hotel_result[key]['distanceFromCenter'])
                elif secminimal_distance_hotel >= 4.0 and float(hotel_result[key]['distanceFromCenter']) < secminimal_distance_hotel:
                    closest_hotel_index[1] = key
                    secminimal_distance_hotel = float(hotel_result[key]['distanceFromCenter'])
                if minimal_distance_hotel < 4.0 and secminimal_distance_hotel < 4.0:
                    break
            hotel_results0['trip_%d' % x] = hotel_result['hotel_%d' % (int(closest_hotel_index[0][6:]))]
            hotel_results1['trip_%d' % x] = hotel_result['hotel_%d' % (int(closest_hotel_index[1][6:]))]
            hotel_price0 = hotel_price0 + float(hotel_results0['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
            hotel_price1 = hotel_price0 + float(hotel_results1['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
        hotel_results0['price'] = hotel_price0
        hotel_results1['price'] = hotel_price1
        
        if purpose == "find_star":
            # pdb.set_trace()
            star_hotel_index = []
            star_hotel_index.append('hotel_0')
            star_hotel_index.append('hotel_0')
            first = False
            small = 0.0
            secsmall = 0.0
            for key, value in hotel_result.iteritems():
                if small < 3.0 and float(hotel_result[key]['starRating']) > small :
                    star_hotel_index[0] = key
                    small = float(hotel_result[key]['starRating'])
                elif secsmall < 3.0 and float(hotel_result[key]['starRating']) > secsmall:    
                    star_hotel_index[1] = key
                    secsmall = float(hotel_result[key]['starRating'])
                if small >= 3.0 and secsmall >= 3.0:
                    break
            hotel_results0['trip_%d' % x] = hotel_result['hotel_%d' % (int(star_hotel_index[0][6:]))]
            hotel_results1['trip_%d' % x] = hotel_result['hotel_%d' % (int(star_hotel_index[1][6:]))]
            hotel_price0 = hotel_price0 + float(hotel_results0['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
            hotel_price1 = hotel_price0 + float(hotel_results1['trip_%d' % x]['rateWithTax'][2:].replace(',', ''))
        hotel_results0['price'] = hotel_price0
        hotel_results1['price'] = hotel_price1

    package_data_hotel.append(hotel_results0)
    package_data_hotel.append(hotel_results1)    

    return package_data_hotel


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
    flights_result = flight_parser.get_flights(data)
    flights_ordered = [OrderedDict(sorted(flights_result.iteritems(), key=lambda k : int(k[0][7:])))]
    return jsonify(flights_ordered)


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

    hotels_result = hotel_parser.search_hotels(hotel_data)
    hotels_ordered = [OrderedDict(sorted(hotels_result.iteritems(), key=lambda k : int(k[0][6:])))]

    return jsonify(hotels_ordered)


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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)), debug=True)
