from flask import Flask, render_template, request, jsonify
import requests
import googlemaps

app = Flask(__name__)
gmaps = googlemaps.Client(key='API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_popular_time', methods=['POST'])
def fetch_popular_time():
    destination = request.json['destination']

    # Retrieve the address from Google Maps API
    geocode_result = gmaps.geocode(destination)
    if not geocode_result:
        return jsonify({'error': 'Invalid location'})

    # Extract address components from geocode result
    address_components = geocode_result[0]['address_components']
    neighborhood = get_address_component(address_components, 'neighborhood')
    city = get_address_component(address_components, 'locality')
    country = get_address_component(address_components, 'country')
    formatted_address = f"{neighborhood}, {city}, {country}"

    url = "https://besttime.app/api/v1/forecasts/live"
    params = {
        'api_key_private': 'BEST_TIME_API_KEY',  # replace with your actual key
        'venue_name': destination,
        'venue_address': formatted_address
    }

    response = requests.post(url, params=params)
    data = response.json()

    if 'analysis' in data:
        popular_time = data['analysis']['popular_times'][0]['data'][0]
    else:
        popular_time = 'Not available'

    return jsonify({'popular_time': popular_time})


def get_address_component(address_components, component_type):
    for component in address_components:
        types = component.get('types', [])
        if component_type in types:
            return component['long_name']
    return ''


if __name__ == '__main__':
    app.run(debug=True)
