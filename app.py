from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Replace with your actual API keys
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'efeccaad7cc9696a66ec646e53d395a6')
AIR_QUALITY_API_KEY = os.getenv('AIR_QUALITY_API_KEY', 'cbd95901-ba9a-4b3f-a9ae-0c88ae94d6d5')

@app.route('/')
def home():
    return jsonify({"message": "Weather and Air Quality Checker API is running."})


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    try:
        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric'
        response = requests.get(weather_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({'error': data.get('message', 'Unable to fetch weather')}), response.status_code

        weather_info = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }

        return jsonify(weather_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/air_quality', methods=['GET'])
def get_air_quality():
    city = request.args.get('city')
    state = request.args.get('state')
    country = request.args.get('country', 'Ireland')  # default to Ireland

    if not city or not state:
        return jsonify({'error': 'city and state parameters are required'}), 400

    try:
        air_quality_url = (
            f'https://api.airvisual.com/v2/city'
            f'?city={city}&state={state}&country={country}&key={AIR_QUALITY_API_KEY}'
        )
        response = requests.get(air_quality_url)
        data = response.json()

        if response.status_code != 200 or data.get('status') != 'success':
            return jsonify({'error': data.get('data', {}).get('message', 'Unable to fetch air quality')}), response.status_code

        pollution = data['data']['current']['pollution']

        air_quality_info = {
            'city': city,
            'state': state,
            'country': country,
            'aqi_us': pollution['aqius'],
            'main_pollutant_us': pollution['mainus'],
            'timestamp': pollution['ts']
        }

        return jsonify(air_quality_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
