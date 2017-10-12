"""Module for hotel searching and parsing.

This module would process hotel related data, and return filtered result to the
server.
"""
from __future__ import print_function

import requests
import logging
import json
# from pygeocoder import Geocoder
import geocoder

returnedNum = 50 # only return top 50 flight data


def search_hotels(location):
    # type: (str) -> object
    """Send query to Expedia to get hotel information in given area.

    This function will utilize the Expedia API to query hotel information. It
    would send a GET request to the API, and catch the result as JSON text.

    Args:
        location: string, the city or location to search.
    Returns:
        A JSON object which contains hotel information.
    """
    # TODO: The Expedia API only allows location as latitude and longitude input
    # Find a way to convert location str input into the GEO data.
    g = geocoder.google(location)

    param = {'sortOrder': 'price',
             'pageIndex': 0,
             'enableSponsoredListings': 'false',
             'room1': 1,
             'filterUnavailable': 'true',
             'checkInDate': '2017-10-13',
             'checkOutDate': '2017-10-14',
             # 'latitude': '40.7128',
             # 'longitude': '74.0060',
             'latitude': g.latlng[0],  # location
             'longitude': g.latlng[1],  # location
             'resultsPerPage': returnedNum}

    raw_response = requests.get("https://www.expedia.com/m/api/hotel/search/v3",
                                params=param)
    # log the result for debug
    return json.loads(raw_response.text)


def parse_hotel(raw_data, location):
    # type: (object, str) -> object
    """Parser for hotel data JSON object.

    This function would extract important information from the raw data, and
    parse it.

    Args:
        location: string, the city or location to search.
    Returns:

    """
    # TODO: Parse the data, make sure it is ready for constructing package.
    return_data = dict()
    return_data['availableHotelCount'] = raw_data['availableHotelCount']
    return_data['numberOfRoomsRequested'] = raw_data['numberOfRoomsRequested']
    hotel_list = dict()
    for x in range(returnedNum):
            hotel = dict()
            hotel['country'] = raw_data['hotelList'][x]['countryName']
            hotel['city'] = raw_data['hotelList'][x]['city']
            hotel['name'] = raw_data['hotelList'][x]['localizedName']
            hotel['hotelId'] = raw_data['hotelList'][x]['hotelId']
            # hotel['locationId'] = raw_data['hotelList'][x]['locationId']
            hotel['address'] = raw_data['hotelList'][x]['address']
            hotel['description'] = raw_data['hotelList'][x]['shortDescription']
            hotel['availability'] =raw_data['hotelList'][x]['isHotelAvailable']
            hotel['roomsLeft'] = raw_data['hotelList'][x]['roomsLeftAtThisRate']
            hotel['totalReviews'] = raw_data['hotelList'][x]['totalReviews']
            hotel['guestRating'] = raw_data['hotelList'][x]['hotelGuestRating']
            hotel['starRating'] = raw_data['hotelList'][x]['hotelStarRating']
            hotel_list['hotel%d' % x] = hotel
    return_data['hotel_list'] = hotel_list
    formated_return_data = json.dumps(return_data, sort_keys=True, indent=4, separators=(',', ': '))
    print(formated_return_data, file=open('top_query_hotels.log', 'w+'))
    # logging.warning(raw_data)


if __name__ == '__main__':
    raw_data = search_hotels("Mountain View, CA")
    parse_hotel(raw_data, "Mountain View, CA")
