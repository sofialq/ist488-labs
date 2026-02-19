import requests
import streamlit as st
from openai import OpenAI
import json


api_key = st.secrets['OPENWEATHER_API_KEY']

# create client
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this unit from the forecast location..",
                    },
                },
                "required": ["location", "format"],
            },
        }
    }
]

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

def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-4o"):
    try:
        response = st.session_state.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


# Show title and description.
st.title("Lab 5")
st.write(" ")
st.title("'What to Wear' Bot")
st.write("Input a city name and the bot will output a suggestion on what you should wear there!")

# get user input for location.
location = st.text_input("Enter a location (City, State, Country): ", value = "Syracuse, NY, US")

# make chat completion request to get weather information for the location.
messages = []
messages.append({"role": "system", 
                 "content": "Don't make assumptions about what values to plug into functions. "
                 "Always use Fahrenheit for temperature. "
                 "When reporting weather, always include the current temperature, feels like, "
                 "temperature minimum, temperature maximum, and humidity in your response. "
                 "Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": f"What is the weather like in {location} today? Use Farenheit for temperature"})
chat_response = chat_completion_request(messages, tools=tools)

# call the tool and use information in the response to the user.
if location:
    chat_response = chat_completion_request(messages, tools=tools)
    assistant_message = chat_response.choices[0].message

    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        units = 'imperial'
        weather_info = get_current_weather(args['location'], api_key, units)

        messages.append(assistant_message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(weather_info)
        })

        final_response = chat_completion_request(messages)
        weather_summary = final_response.choices[0].message.content

        suggestion_messages = [ 
            {"role": "system", "content": "You are a helpful assistant that gives clothing and activity suggestions based on the weather."},
            {"role": "user", "content": f"The current weather in {location} is: {weather_summary}. What should I wear today and what're some outdoor activities I can do?"}
        ]

        suggestion_response = chat_completion_request(suggestion_messages)
        suggestion = suggestion_response.choices[0].message.content

        
        st.subheader(f"Weather in {location}:")
        st.write(weather_summary)
        st.subheader("Clothing and Activity Suggestions:")
        st.write(suggestion)


