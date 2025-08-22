import streamlit as st
import requests
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key and DB credentials from .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Function to fetch weather.


def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get("cod") != 200:
        return None
    weather = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "condition": data["weather"][0]["description"].title()
    }
    return weather

# Function to fetch food recommendations from DB


def get_food_recommendations(city, temperature, meal_time):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        # Temperature range calculation (bucket every 5°C)
        lower = int(temperature // 5) * 5
        upper = lower + 5
        temp_range = f"{lower}-{upper}°C"

        query = """
        SELECT food, benefits, protein, carbs, fiber, meal_time
        FROM food_recommendations
        WHERE city = %s AND temperature_range = %s AND meal_time = %s
        """
        cursor.execute(query, (city, temp_range, meal_time))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return results
    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")
        return []

# ---------------- Streamlit UI ----------------


st.title("🌦️ AI-Powered Weather-Based Nutrition Assistant")

# Initialize session states
if "weather" not in st.session_state:
    st.session_state.weather = None
if "city" not in st.session_state:
    st.session_state.city = "Chennai"   # default city

# City input
city = st.text_input("Enter City Name:", st.session_state.city)

if st.button("Get Weather"):
    weather = get_weather(city)
    if weather:
        st.session_state.weather = weather
        st.session_state.city = city   # save city to session state
    else:
        st.error("City not found or API error.")

# Show results only if weather is already fetched
if st.session_state.weather:
    weather = st.session_state.weather
    st.subheader(f"🌍 Weather in {weather['city']}")
    st.write(f"Temperature: {weather['temperature']}°C")
    st.write(f"Condition: {weather['condition']}")

    # Meal selection
    meal_time = st.selectbox("Choose Meal Time:", [
                             "Breakfast", "Lunch", "Dinner"])

    # Show recommendations directly when meal_time changes
    recommendations = get_food_recommendations(
        weather["city"], weather["temperature"], meal_time
    )

    if recommendations:
        st.subheader(f"🍴 Food Recommendations for {meal_time}")
        for food in recommendations:
            st.markdown(f"""
            **{food['food']}**  
            *Benefits*: {food['benefits']}  
            **Nutrition:** Protein: {food['protein']}g | Carbs: {food['carbs']}g | Fiber: {food['fiber']}g  
            """)
    else:
        st.warning("No food recommendations found for this temperature range.")
