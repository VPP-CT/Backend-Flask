"""Module for hotel searching and parsing.

This module would process hotel related data, and return filtered result to the
server.
"""
from __future__ import print_function

import requests
import logging
import json


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
    # TODO: The Expedia API only allows location as latitude and longitude input.
    # Find a way to convert location str input into the GEO data.
    param = {'sortOrder': 'price',
             'pageIndex': 0,
             'enableSponsoredListings': 'false',
             'room1': 1,
             'filterUnavailable': 'true',
             'checkInDate': '2017-09-30',
             'checkOutDate': '2017-10-01',
             'latitude': '35.675',  # location
             'longitude': '139.76',  # location
             'resultsPerPage': '200'}

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
    logging.warning(raw_data)


if __name__ == '__main__':
    raw_data = search_hotels("Tokyo")
    parse_hotel(raw_data, "Tokyo")
