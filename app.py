from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# API KEYS
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
    
@app.route('/resume_keywords', methods=['POST'])
def get_resume_keywords():
    if 'resume' not in request.files:
        return jsonify({'error': 'Resume file is required'}), 400

    try:
        resume_file = request.files['resume']

        # Send file to Resume App's analyze_resume endpoint
        resume_api_url = 'http://16.171.154.178:5000/analyze_resume'
        files = {'resume': (resume_file.filename, resume_file.stream, resume_file.mimetype)}
        response = requests.post(resume_api_url, files=files)

        return jsonify({
            'source': 'Resume Analyzer API',
            'analyzed_data': response.json()
        })

    except Exception as e:
        return jsonify({'error': f'Failed to fetch resume keywords: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)

    
