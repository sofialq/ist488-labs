import requests
import streamlit as st

api_key = st.secrets['OPENWEATHER_API_KEY']

def get_current_weather(location, api_key, units='imperial'):

    '''
    location: in form City, State, Country
    e.g. Syracuse, NY, US

    default units is degrees Fahrenheit 
    '''

    url = (
    f'http://api.openweathermap.org/data/2.5/weather'
    f'?q={location}&appid={api_key}&units={units}'
    )

    response = requests.get(url)
    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key. (401 Unauthorized)')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')

    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']

    return {
        'location': location,
        'temperature': round(temp, 2),
        'feels_like': round(feels_like, 2),
        'temp_min': round(temp_min, 2),
        'temp_max': round(temp_max, 2),
        'humidity': humidity
    }

syracuse_weather = get_current_weather('Lima, Peru', api_key)
st.write(f"Current weather in {syracuse_weather['location']}:")
st.write(f"Temperature: {syracuse_weather['temperature']} °F")
st.write(f"Feels like: {syracuse_weather['feels_like']} °F")
st.write(f"Min temperature: {syracuse_weather['temp_min']} °F")
st.write(f"Max temperature: {syracuse_weather['temp_max']} °F")
st.write(f"Humidity: {syracuse_weather['humidity']}%")  