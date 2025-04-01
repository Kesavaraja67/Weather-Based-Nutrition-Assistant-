from flask import Flask, render_template, request
import mysql.connector
import requests

app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="#Your_Host_ADDRESS ",
    user="YOUR_USER_NAME",
    password="#Your_MySqL_Password",  # Replace with your actual MySQL password
    database="Your_DB_NAME"
)

cursor = db.cursor(dictionary=True)

# OpenWeather API Key
API_KEY = "#Your_API_ID"  # Replace with your actual API key

# Function to determine temperature range
def get_temperature_range(temp):
    if temp <= 5:
        return "0-5°C"
    elif temp <= 10:
        return "5-10°C"
    elif temp <= 15:
        return "10-15°C"
    elif temp <= 20:
        return "15-20°C"
    elif temp <= 25:
        return "20-25°C"
    elif temp <= 30:
        return "25-30°C"
    elif temp <= 35:
        return "30-35°C"
    else:
        return "35-40°C"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    district = request.form.get('district')

    if not district:
        return render_template('index.html', error="Please enter a valid district name.")

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={district}&appid={API_KEY}&units=metric"
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return render_template('index.html', error="Invalid district or API issue.")

    weather_data = weather_response.json()
    temperature = weather_data['main']['temp']
    temperature_range = get_temperature_range(temperature)

    recommendations = {"Breakfast": [], "Lunch": [], "Dinner": []}

    for meal_time in recommendations.keys():
        query = """
            SELECT food_name, category, benefits, COALESCE(protein, 0.0) AS protein,
            COALESCE(fiber, 0.0) AS fiber, COALESCE(fat, 0.0) AS fat, COALESCE(carbs, 0.0) AS carbs
            FROM food_recommendations
            WHERE temperature_range = %s AND city = %s AND meal_time = %s
        """
        cursor.execute(query, (temperature_range, district, meal_time))
        recommendations[meal_time] = cursor.fetchall()

    return render_template('index.html', recommendations=recommendations,
                           temperature=temperature, district=district,
                           temperature_range=temperature_range)

if __name__ == '__main__':
    app.run(debug=True)