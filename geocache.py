from flask import Flask
from flask import Response
import json
import requests

HERE_APP_ID = ''
HERE_APP_CODE = ''

GOOGLE_API_KEY = ''

HERE_URL = 'https://geocoder.api.here.com/6.2/geocode.json?app_id=%s&app_code=%s&searchtext=%s'

GOOGLE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'

HTTP_OK = 200

class GeoCache:
    def __init__(self):
        self.cache = {}
        pass

    def handle_request(self, address):
        #check cache first
        if address in self.cache:
            print('Returning cached response')
            return self.cache[address]
        try:
            response = self.call_here(address)
            print('Saving %s to cache' % address)
            self.cache[address] = response
            return response
        except Exception as e:
            print(e)
        print('Trying Google API')
        try:
            response = self.call_google(address)
            print('Saving %s to cache' % address)
            self.cache[address] = response
            return response
        except Exception as e:
            print(e)
        return json.dumps({'Message': 'Can\'t find given address'})

    def call_here(self, address):
        url = HERE_URL % (HERE_APP_ID, HERE_APP_CODE, address)
        print('Calling ', url)
        response = requests.get(url)
        #print(response.text)
        if response.status_code != HTTP_OK:
            raise Exception('Here API error %s' % response.status_code)
        response_json = json.loads(response.text)
        locations = []
        try:
            results = response_json['Response']['View'][0]['Result']
            for x in results:
                #print(x)
                lat_lon = x['Location']['DisplayPosition']
                locations.append({
                    'Address': x['Location']['Address']['Label'],
                    'Latitude': lat_lon['Latitude'],
                    'Longitude': lat_lon['Longitude']
                })
        except Exception as e:
            print(e)
        if not locations:
            raise Exception('Invalid address')
        return json.dumps({'Message': 'OK', 'Results': locations})

    def call_google(self, address):
        url = GOOGLE_URL % (address, GOOGLE_API_KEY)
        print('Calling ', url)
        response = requests.get(url)
        #print(response.text)
        if response.status_code != HTTP_OK:
            raise Exception('Google API error %s' % response.status_code)
        response_json = json.loads(response.text)
        locations = []
        try:
            results = response_json['results']
            for x in results:
                #print(x)
                lat_lon = x['geometry']['location']
                locations.append({
                    'Address': x['formatted_address'],
                    'Latitude': lat_lon['lat'],
                    'Longitude': lat_lon['lng']
                })
        except Exception as e:
            print(e)
        if not locations:
            raise Exception('Invalid address')
        return json.dumps({'Message': 'OK', 'Results': locations})

#make sure api params are present
assert HERE_APP_ID, 'Please provide Here app id'
assert HERE_APP_CODE, 'Please provide Here app code'
assert GOOGLE_API_KEY, 'Please provide Google API key'

geocache = GeoCache()
app = Flask(__name__)

@app.route('/<string:address>')
def get(address):
    print(address)
    return Response(geocache.handle_request(address), mimetype='text/json')

app.run()
