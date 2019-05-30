# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.

Sample usage of the program:
python sample.py --term="bars" --location="San Francisco, CA"
"""
from __future__ import print_function
from pandas.io.json import json_normalize
import os.path
import argparse
import json
import pprint
import requests
import sys
import urllib
import csv



# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

API_KEY= 'GET YOUR OWN' 

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'tattoo removal'
DEFAULT_LOCATION = 'Sacramento, CA'
SEARCH_LIMIT = 10
cities = ['San Francisco, CA', 'San Jose, CA', 'Santa Cruz, CA', 'Salinas, CA', 'Vacaville, CA', 'Sacramento, CA', 'Truckee, CA', 
          'Stockton, CA',  'Modesto, CA', 'Merced, CA', 'Fresno, CA', 'Santa Rosa, CA', 'Humboldt, CA', 'Redding, CA', 'Chico, CA', 'Marysville, CA']

#cities = ['Sacramento, CA']

def request(host, path, api_key, url_params=None):

    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    #print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):

    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(term, location):

    response = search(API_KEY, term, location)

    business(response)

    #Save .json to a file
    #with open('data.json', 'w') as openfile:
    #    json.dump(response, openfile, sort_keys=True, indent=4)

def business(response):
    
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    for i in range(SEARCH_LIMIT):
        try:
            business_id = businesses[i]['id']
            print(business_id)
            response = get_business(API_KEY, business_id)

            create_csv(response)
        except:
            continue
        

def create_csv(business_info):

    csv_header = ['Business Name', 'Business Phone', 'Business Rating', 'Business Address', 'City', 'Yelp Website']
    bizList = []

    biz = json.dumps(business_info)
    bizInfo = json.loads(biz)
    
    address = bizInfo['location']
    name = str(bizInfo['name'])
    phone = str(bizInfo['phone'])
    rating = str(bizInfo['rating'])
    url = str(bizInfo['url'])
    city1 = str(address['city'])
    location = create_address(address)

    bizList.append(name)
    bizList.append(phone)
    bizList.append(rating)
    bizList.append(location)
    bizList.append(city1)
    bizList.append(url)
    
    if os.path.exists('YelpScrapper.csv'):
        with open('YelpScrapper.csv', 'ab') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([bizList])
    else:
        with open('YelpScrapper.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([csv_header])
            writer.writerows([bizList])

def create_address(address):

    street = str(address['address1'])
    city = str(address['city'])
    state = str(address['state'])
    zipcode = str(address['zip_code'])

    fullAddress = street + ', ' + city + ', ' + state + ' ' + zipcode

    return fullAddress

def rmv_dups():
    inFile = open('YelpScrapper.csv','r')
    outFile = open('YelpBusinesses.csv','w')

    listLines = []

    for line in inFile:
        if line in listLines:
            continue
        else:
            outFile.write(line)
            listLines.append(line)

    outFile.close()
    inFile.close()
    os.remove('YelpScrapper.csv')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        for i in range(len(cities)):
            print(cities[i])
            query_api('tattoo removal', cities[i])
        #query_api(input_values.term, input_values.location)

        rmv_dups()

    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
