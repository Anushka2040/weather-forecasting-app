import os
import pytz
import pyowm
import streamlit as st
import pandas as pd
from matplotlib import dates
import datetime
from matplotlib import pyplot as plt
from pyowm.utils import config
from pyowm.utils import timestamps,formatting
from pyowm.owm import OWM
import numpy as np
import requests
import json 
import openmeteo_requests
import requests_cache
from retry_requests import retry

# default API key
# b043c52e3bd4c80792ae9b21b4b4eee1

owm=OWM('b3546e071c51bd4fcdb291ca71a7756b')
mgr=owm.weather_manager()

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

with st.form("my_form"):
    st.title("5 Day Weather Forecast")
    st.write("### Write the name of a City and select the Temperature Unit and Graph Type from the sidebar")

    place=st.text_input("NAME OF THE CITY :", "")
    country=st.text_input("NAME OF THE COUNTRY :", "", max_chars = 2, placeholder ='Upper-case only')

    if place == None:
        st.write("Input a CITY!")
    if country == None:
        st.write("Input a COUNTRY!")

    unit=st.selectbox("Select Temperature Unit",("Celsius","Fahrenheit"))

    g_type=st.selectbox("Select Graph Type",("Line Graph","Bar Graph"))


    submitted = st.form_submit_button("Submit")

    if submitted:
        owm=OWM('b3546e071c51bd4fcdb291ca71a7756b')
        mgr=owm.weather_manager()

        reg = owm.city_id_registry()
        list_of_locations = reg.locations_for(place, country= country)
        location = list_of_locations[0]
        lat = location.lat
        lon = location.lon

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": datetime.date.today()-datetime.timedelta(days=5),
            "end_date": datetime.date.today(),
            "daily": ["temperature_2m_max", "temperature_2m_min"]
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True).date(),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True).date(),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_dataframe = pd.DataFrame(data = daily_data)
        plt.rcParams.update({'text.color': "white",
                     'axes.labelcolor': "white"})
        

        if(g_type=="Bar Graph"):
            x = np.arange(6)
            width = 0.2

            fig, ax = plt.subplots()
            rects1 = ax.bar(x - width/2, daily_dataframe['temperature_2m_max'], width, label='Max')
            rects2 = ax.bar(x + width/2, daily_dataframe['temperature_2m_min'], width, label='Min')

            # Background color
            ax.set_facecolor('#35383D')
            fig.set_facecolor('#35383D')
            ax.set_ylabel('Temperature')
            ax.set_xlabel('Date')
            ax.set_title('Min and Max temperature')
            ax.set_xticks(x, daily_dataframe['date'].apply(lambda x: x.strftime('%Y-%m-%d')))
            ax.tick_params(axis='both', colors='white')
            ax.legend()

            ax.bar_label(rects1, padding=3)
            ax.bar_label(rects2, padding=3)

            fig.tight_layout()

            st.pyplot(fig)

        else:
            ##Line plot 
            data_1 = daily_dataframe['temperature_2m_max']
            data_2 = daily_dataframe['temperature_2m_min']
            fig1, ax1 = plt.subplots()  

            # Background color
            ax1.set_facecolor('grey')

            ax1.plot(data_1,marker ='.')
            ax1.plot(data_2,marker ='.')
            
            ax1.set_ylabel('Temperature')
            ax1.set_xlabel('Date')
            
            # Show plot
            st.pyplot(fig1)


        st.write("### Forecast for this week: ")
        weather_at = mgr.forecast_at_coords(lat, lon, '3h') 
        if(weather_at.will_have_rain()):
            st.write('It will rain!')
    
        if(weather_at.will_have_clear()):
            st.write('It will be clear!')
    
        if(weather_at.will_have_fog()):
            st.write('It will be foggy!')
    
        if(weather_at.will_have_clouds()):
            st.write('It will be cloudy!')

        if(weather_at.will_have_snow()):
            st.write('It will snow!')
    
        if(weather_at.will_have_storm()):
            st.write('Will have storm!')
    
        if(weather_at.will_have_tornado()):
            st.write('Will have tornado!')
    
        if(weather_at.will_have_hurricane()):
            st.write('Will have hurricane!')

        observation = mgr.weather_at_coords(lat,lon).weather

        st.write("### Sunrise and Sunset time")
        st.write(observation.sunrise_time(timeformat='iso'))
        st.write(observation.sunset_time(timeformat='iso'))
    
        st.write("### Current humidity, wind speed and cloud coverage ")
        w = mgr.weather_at_coords(lat, lon).weather
        humidity = w.humidity
        st.write('The current humidity is ',humidity,'% !')

        wind = w.wind(unit='meters_sec')
        wind_now = list(wind.items())[0][1]
        st.write('The current wind speed is ',wind_now,'mps !')

        clouds = w.clouds
        st.write('The current clouds coverage is ',clouds,'% !')




