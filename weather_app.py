import os
import pytz
import pyowm
import streamlit as st
import pandas as pd
from matplotlib import dates
from datetime import datetime
from matplotlib import pyplot as plt
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.owm import OWM
import numpy as np

# default API key
# b043c52e3bd4c80792ae9b21b4b4eee1

owm=OWM('b043c52e3bd4c80792ae9b21b4b4eee1')
mgr=owm.weather_manager()

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
        owm=OWM('a10b96314bef87ecbccfaa69732ea6fc')
        mgr=owm.weather_manager()

        # place='Ontario'
        # country='CA'

        reg = owm.city_id_registry()
        list_of_locations = reg.locations_for(place, country= country)
        location = list_of_locations[0]
        lat = location.lat
        lon = location.lon

        one_call = mgr.one_call(lat, lon)

        data=[]
        temp_min = []
        temp_max = []
        date = []
        days = []

        for x in range (0,5):
            One_call = one_call.forecast_daily[x].temperature('celsius')
            data.append(One_call)
            temp_min.append(data[x]['min'])
            temp_max.append(data[x]['max'])
            sunrise_date = one_call.forecast_daily[x].sunrise_time(timeformat='date')
            date.append(datetime.date(sunrise_date))
            days.append(data[x]['day'])


        if(g_type=="Line Graph"):
            x = np.arange(len(date))
            width = 0.35

            fig, ax = plt.subplots()
            rects1 = ax.bar(x - width/2, temp_max, width, label='Max')
            rects2 = ax.bar(x + width/2, temp_min, width, label='Min')

            ax.set_ylabel('Temperature')
            ax.set_xlabel('Date')
            ax.set_title('Min and Max temperature')
            ax.set_xticks(x, date)
            ax.legend()

            ax.bar_label(rects1, padding=3)
            ax.bar_label(rects2, padding=3)

            fig.tight_layout()

            st.pyplot(fig)

        else:
            ##Line plot 

            data_1 = temp_max
            data_2 = temp_min
            fig1, ax1 = plt.subplots()  

            ax1.plot(x,data_1)
            ax1.plot(x,data_2)
            
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




