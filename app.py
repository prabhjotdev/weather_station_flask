from flask import Flask, render_template, request, jsonify
import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Get Weather Data
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return None, None, city
    temp = round(response['main']['temp'])
    condition = response['weather'][0]['description']
    return temp, condition, city

# Generate AI Responses
def get_ai_response(prompt, role):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message["content"].strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form.get("city", "Toronto")
    else:
        city = "Toronto"
    temp, condition, city_name = get_weather(city)
    if temp is None:
        error = f"Could not retrieve weather for '{city}'. Please check the city name."
        return render_template("index.html", error=error)
    return render_template("index.html", temp=temp, condition=condition, city=city_name)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    temp = data["temp"]
    condition = data["condition"]
    city = data["city"]
    action = data["action"]

    if action == "summary":
        role = "You are a helpful assistant that summarizes weather."
        prompt = f"The weather in {city} is {temp}°C with {condition}. Write a friendly and casual summary."
    elif action == "suggestion":
        role = "You suggest creative and safe activities based on the weather."
        prompt = f"It's {temp}°C and {condition} in {city}. Suggest a cozy or fun activity to do."
    elif action == "story":
        role = "You create short and whimsical stories based on weather conditions."
        prompt = f"Write a short, whimsical story based on the weather being {temp}°C and {condition} in {city}."
    else:
        return jsonify({"result": "Invalid action."})

    result = get_ai_response(prompt, role)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
