"""Module for hotel searching and parsing.

This module would process hotel related data, and return filtered result to the
server.
"""
from __future__ import print_function

import requests
import json

returnedNum = 200  # only return top 50 hotel data


def search_hotels(hotel_data):
    # type: (str) -> object
    """Send query to Expedia to get hotel information in given area.

    This function will utilize the Expedia API to query hotel information. It
    would send a GET request to the API, and catch the result as JSON text.

    Args:
        location: string, the city or location to search.
    Returns:
        A JSON object which contains hotel information.

    """
    param = {'sortOrder': 'price',
             'pageIndex': 0,
             'enableSponsoredListings': 'false',
             'room1': 1,
             'filterUnavailable': 'true',
             'checkInDate': hotel_data.checkin_date,
             'checkOutDate': hotel_data.checkout_date,
             'latitude': hotel_data.latitude,
             'longitude': hotel_data.longitude,
             'resultsPerPage': returnedNum
             }

    raw_response = requests.get("https://www.expedia.com/m/api/hotel/search/v3",
                                params=param)

    return parse_hotel(json.loads(raw_response.text))


def parse_hotel(raw_data):
    # type: (object, str) -> object
    """Parser for hotel data JSON object.

    This function would extract important information from the raw data, and
    parse it.

    Args:
        raw_data: dict, data from API call.
        location: string, the city or location to search.
    Returns:

    """
    return_data = dict()
    # return_data['availableHotelCount'] = raw_data['availableHotelCount']
    # return_data['numberOfRoomsRequested'] = raw_data['numberOfRoomsRequested']
    for x in range(len(raw_data['hotelList'])):
        hotel = dict()
        hotel['city'] = raw_data['hotelList'][x]['city']
        hotel['name'] = raw_data['hotelList'][x]['localizedName']
        hotel['hotelId'] = raw_data['hotelList'][x]['hotelId']
        hotel['address'] = raw_data['hotelList'][x]['address']
        hotel['description'] = raw_data['hotelList'][x]['shortDescription']
        hotel['availability'] = raw_data['hotelList'][x]['isHotelAvailable']
        hotel['roomsLeft'] = raw_data['hotelList'][x]['roomsLeftAtThisRate']
        hotel['totalReviews'] = raw_data['hotelList'][x]['totalReviews']
        hotel['guestRating'] = raw_data['hotelList'][x]['hotelGuestRating']
        hotel['starRating'] = raw_data['hotelList'][x]['hotelStarRating']
        hotel['rateWithTax'] = raw_data['hotelList'][x]['lowRateInfo']['formattedTotalPriceWithMandatoryFees']
        hotel['distanceFromCenter'] = raw_data['hotelList'][x]['proximityDistanceInMiles']
        return_data['hotel_%d' % x] = hotel

    """ For debug only

    formated_return_data = json.dumps(
       return_data, sort_keys=True, indent=4, separators=(',', ': '))
    print(formated_return_data, file=open('top_query_hotels.log', 'w+'))
    logging.warning(raw_data)"""

    return return_data
