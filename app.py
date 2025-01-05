import requests
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import io
import base64
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# OpenWeather API Key
API_KEY = st.secrets["OpenWeather_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
BASE_URL_GEOCODE = "http://api.openweathermap.org/geo/1.0/direct"
BASE_URL_AQI = "http://api.openweathermap.org/data/2.5/air_pollution"
BASE_URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather"

# Simulated health risks based on AQI levels
def simulate_health_risk(aqi):
    if aqi <= 50:
        return "Low Risk"
    elif aqi <= 100:
        return "Moderate Risk"
    elif aqi <= 150:
        return "High Risk"
    else:
        return "Very High Risk"

# Fetch Weather and AQI data
def fetch_weather_and_aqi_for_area(city, area):
    try:
        # Step 1: Get Latitude and Longitude of the specific area
        geocode_url = f"{BASE_URL_GEOCODE}?q={area},{city}&limit=1&appid={API_KEY}"
        geocode_response = requests.get(geocode_url)

        if geocode_response.status_code != 200:
            return f"Error fetching geocode data: {geocode_response.text}"

        geocode_data = geocode_response.json()
        
        if len(geocode_data) == 0:
            return f"No geocode data found for the specified area: {area}, {city}. Please ensure that the location is correct."

        lat = geocode_data[0]["lat"]
        lon = geocode_data[0]["lon"]

        # Step 2: Fetch Weather Data
        weather_url = f"{BASE_URL_WEATHER}?lat={lat}&lon={lon}&appid={API_KEY}"
        weather_response = requests.get(weather_url)

        if weather_response.status_code != 200:
            return f"Error fetching weather: {weather_response.text}"

        weather_data = weather_response.json()
        weather_details = weather_data.get("weather", [{}])[0].get("description", "No weather info")

        # Step 3: Fetch AQI Data
        aqi_url = f"{BASE_URL_AQI}?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_response = requests.get(aqi_url)

        if aqi_response.status_code != 200:
            return f"Error fetching AQI: {aqi_response.text}"

        aqi_data = aqi_response.json()
        aqi_value = aqi_data["list"][0]["components"]["pm2_5"]

        return weather_details, aqi_value

    except Exception as e:
        return f"Error occurred: {str(e)}"

# Simulated past and forecast AQI data for the last and next 30 days
def generate_aqi_data():
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    past_aqi = np.random.randint(20, 200, size=30)  # Simulating past AQI data
    forecast_aqi = np.random.randint(20, 200, size=30)  # Simulating forecasted AQI data
    return dates, past_aqi, forecast_aqi

# Convert plot to image for Streamlit display
def plot_to_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return Image.open(buf)

# Plotting Functions
def plot_aqi_health_risk(dates, past_aqi):
    health_risks = [simulate_health_risk(aqi) for aqi in past_aqi]
    plt.figure(figsize=(10, 6))
    plt.scatter(dates, past_aqi, c=[['green', 'yellow', 'orange', 'red'][['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'].index(risk)] for risk in health_risks])
    plt.title('AQI vs Health Risk')
    plt.xlabel('Date')
    plt.ylabel('AQI Level')
    plt.xticks(rotation=45)
    plt.colorbar(label='Health Risk')
    fig = plt.gcf()
    plt.close()
    return plot_to_image(fig)

def plot_weather_vs_aqi(dates, past_aqi):
    # Simulating weather data
    temperatures = np.random.randint(10, 35, size=30)
    humidity = np.random.randint(30, 90, size=30)
    wind_speed = np.random.randint(1, 15, size=30)

    plt.figure(figsize=(10, 6))
    plt.scatter(temperatures, past_aqi, label='Temperature vs AQI', color='blue')
    plt.scatter(humidity, past_aqi, label='Humidity vs AQI', color='green')
    plt.scatter(wind_speed, past_aqi, label='Wind Speed vs AQI', color='red')
    plt.title('Weather Parameters vs AQI')
    plt.xlabel('Weather Parameter')
    plt.ylabel('AQI Level')
    plt.legend()
    fig = plt.gcf()
    plt.close()
    return plot_to_image(fig)

def plot_aqi_categories(dates, past_aqi):
    categories = ['Good', 'Moderate', 'Unhealthy', 'Hazardous']
    category_colors = ['green', 'yellow', 'orange', 'red']
    category_counts = {cat: 0 for cat in categories}

    for aqi in past_aqi:
        if aqi <= 50:
            category_counts['Good'] += 1
        elif aqi <= 100:
            category_counts['Moderate'] += 1
        elif aqi <= 150:
            category_counts['Unhealthy'] += 1
        else:
            category_counts['Hazardous'] += 1

    plt.figure(figsize=(10, 6))
    plt.bar(category_counts.keys(), category_counts.values(), color=category_colors)
    plt.title('AQI Categories with Color-Coding')
    plt.xlabel('AQI Category')
    plt.ylabel('Frequency')
    fig = plt.gcf()
    plt.close()
    return plot_to_image(fig)

def plot_health_recommendation_distribution(dates, past_aqi):
    recommendations = ['Stay Indoors', 'Wear Mask', 'Take Medication', 'No Action']
    recommendation_probs = [0.5, 0.3, 0.1, 0.1]  # Probability distribution

    plt.figure(figsize=(10, 6))
    plt.hist(past_aqi, bins=10, density=True, alpha=0.6, color='b', label='AQI Distribution')
    plt.title('Health Recommendation Probability Distribution')
    plt.xlabel('AQI Level')
    plt.ylabel('Density')
    fig = plt.gcf()
    plt.close()
    return plot_to_image(fig)

def plot_forecast_confidence_interval(dates, past_aqi, forecast_aqi):
    # Confidence interval simulated as ±10 AQI units around forecast
    lower_bound = forecast_aqi - 10
    upper_bound = forecast_aqi + 10

    plt.figure(figsize=(10, 6))
    plt.plot(dates, forecast_aqi, label='Forecasted AQI', color='blue')
    plt.fill_between(dates, lower_bound, upper_bound, color='lightblue', alpha=0.3, label='Confidence Interval')
    plt.title('AQI Forecast with Confidence Interval')
    plt.xlabel('Date')
    plt.ylabel('AQI Level')
    plt.legend()
    plt.xticks(rotation=45)
    fig = plt.gcf()
    plt.close()
    return plot_to_image(fig)

# Get Groq API Response
def get_groq_response(prompt):
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
        stream=False,
    )

    return chat_completion.choices[0].message.content

# Streamlit Interface
st.title("Air Aware")
st.write("This tool provides AQI and weather details, as well as health recommendations based on AQI.")

# Input fields
city = st.text_input("City", placeholder="Enter the name of the city")
area = st.text_input("Area", placeholder="Enter the area within the city")
disease = st.text_input("Disease (e.g., asthma, bronchitis)", placeholder="Enter any disease")

if city and area and disease:
    dates, past_aqi, forecast_aqi = generate_aqi_data()

    # Display the plots
    plot_aqi_health_risk_image = plot_aqi_health_risk(dates, past_aqi)
    plot_weather_vs_aqi_image = plot_weather_vs_aqi(dates, past_aqi)
    plot_aqi_categories_image = plot_aqi_categories(dates, past_aqi)
    plot_health_recommendation_distribution_image = plot_health_recommendation_distribution(dates, past_aqi)
    plot_forecast_confidence_interval_image = plot_forecast_confidence_interval(dates, past_aqi, forecast_aqi)

    st.image(plot_aqi_health_risk_image, caption="AQI vs Health Risk", use_container_width=True)
    st.image(plot_weather_vs_aqi_image, caption="Weather vs AQI", use_container_width=True)
    st.image(plot_aqi_categories_image, caption="AQI Categories", use_container_width=True)
    st.image(plot_health_recommendation_distribution_image, caption="Health Recommendation", use_container_width=True)
    st.image(plot_forecast_confidence_interval_image, caption="Forecast with Confidence Interval", use_container_width=True)

    # Fetch and display weather and AQI data
    weather_result = fetch_weather_and_aqi_for_area(city, area)
    if isinstance(weather_result, tuple):
        weather, aqi = weather_result
        prompt = f"I am in {area}, an area of {city}. The weather is {weather} and the AQI is {aqi}. I have {disease}. Please provide immediate precautionary measures."
        groq_response = get_groq_response(prompt)
        st.subheader("Weather & AQI Information")
        st.write(f"Weather: {weather}")
        st.write(f"AQI: {aqi}")
        st.subheader("Precautionary Measures:")
        st.write(groq_response)
    else:
        st.error(weather_result)
