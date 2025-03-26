from flask import Flask
import logging
import global_variables
import os
import requests

app = Flask(__name__)

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.WARNING)

@app.route("/")
def home():
  return "Dummy Server is running"

@app.route("/health", methods=["GET"])
def health_check():
  return "OK", 200

def ping_dummy_server():
  DUMMY_SERVER_URL = f"{os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')}/health"
  try:
    response = requests.get(DUMMY_SERVER_URL)
    if response.status_code == 200:
      global_variables.LOGGER.info(f"Successfully pinged the dummy server {DUMMY_SERVER_URL}.")
    else:
      global_variables.LOGGER.warning(f"Unexpected response from server: {response.status_code}")
  except requests.exceptions.RequestException as e:
    global_variables.LOGGER.error(f"Failed to reach dummy server: {e}")

def start_server():
  app.run(host="0.0.0.0", port=5000)
