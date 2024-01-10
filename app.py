from flask import Flask, request, render_template, redirect, url_for
from models import db, WeatherData  
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

api_key = '8c59fc25cdbade9a29d0957745f34863'
blue_color = '\033[94m'

def get_current_weather(city_name, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'
    response = requests.get(url)
    weather_data = response.json()

    if 'main' in weather_data and 'weather' in weather_data:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        return temperature, description
    else:
        return None, None

def get_7_day_forecast(city_name, api_key):
      url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric'
      response = requests.get(url)
      forecast_data = response.json()

      forecast = defaultdict(list)

      if 'list' in forecast_data:
        for item in forecast_data['list']:
            date_time = item['dt_txt']
            date = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
            temperature = item['main']['temp']
            description = item['weather'][0]['description']
            
            forecast[date.date()].append({
                "time": date.strftime('%H:%M'),
                "description": description,
                "temperature": temperature
            })

      return forecast
def get_hail_chance(city_name, api_key):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric'
    response = requests.get(url)
    forecast_data = response.json()

    if 'list' in forecast_data:
        for item in forecast_data['list']:
            date_time = item['dt_txt']
            date = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
            if date > datetime.now() + timedelta(hours=7):
                hail_percentage = item.get('pop', 0) * 100
                return hail_percentage

    return None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return redirect(url_for('registration_success'))

    return render_template('registration.html')

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return redirect(url_for('info'))
    
    return render_template('login.html')


@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        city_name = request.form.get('city_name', '')
        data_type = request.form['data_type']

        if city_name:
            weather_data_entry = WeatherData(city_name=city_name, data_type=data_type)
            db.session.add(weather_data_entry)
            db.session.commit()

            if data_type == 'current_weather':
                temperature, description = get_current_weather(city_name, api_key)
                if temperature is not None and description is not None:
                    weather_data = {
                        "description": description,
                        "temperature": temperature
                    }
                    return render_template('info.html', weather_data=weather_data)
                else:
                    error_message = "Weather data not available."
                    return render_template('info.html', error_message=error_message)
            
            elif data_type == '7_day_forecast':
                seven_day_forecast = get_7_day_forecast(city_name, api_key)
                if seven_day_forecast:
                    return render_template('info.html', seven_day_forecast=seven_day_forecast)
                else:
                    error_message = "7-Day forecast not available."
                    return render_template('info.html', error_message=error_message)
            
            elif data_type == 'hail_chance':
                hail_chance = get_hail_chance(city_name, api_key)
                if hail_chance is not None:
                    return render_template('info.html', hail_chance=hail_chance)
                else:
                    error_message = "Hail chance data not available."
                    return render_template('info.html', error_message=error_message)

        else:
            error_message = "City name not provided."
            return render_template('info.html', error_message=error_message)

    return render_template('info.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)