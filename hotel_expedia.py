import requests
import logging
from __future__ import print_function


def search_hotels():
    param = {'sortOrder': 'price',
             'pageIndex': 0,
             'enableSponsoredListings': 'false',
             'room1': 1,
             'filterUnavailable': 'true',
             'checkInDate': '2017-09-30',
             'checkOutDate': '2017-10-01',
             'latitude': '35.675',
             'longitude': '139.76'}

    logging.w
    r = requests.get(
        "https://www.expedia.com/m/api/hotel/search/v3", params=param)

    print r.text

if __name__ == '__main__':
