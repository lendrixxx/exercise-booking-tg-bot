from flask import Flask
import requests
import global_variables

app = Flask(__name__)

@app.route('/')
def home():
  return "Dummy Server is running"

@app.route("/health", methods=["GET"])
def health_check():
  return "OK", 200  

def ping_dummy_server():
  DUMMY_SERVER_URL = "https://exercise-booking-tg-bot.onrender.com/health"  
  try:
    response = requests.get(DUMMY_SERVER_URL)
    if response.status_code == 200:
      global_variables.LOGGER.info("Successfully pinged the dummy server.")
    else:
      global_variables.LOGGER.warning(f"Unexpected response from server: {response.status_code}")
  except requests.exceptions.RequestException as e:
    global_variables.LOGGER.error(f"Failed to reach dummy server: {e}")

def start_server():
  app.run(host='0.0.0.0', port=5000)