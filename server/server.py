from flask import Flask
import logging
import os
import requests

class Server:
  def __init__(self, logger: logging.Logger) -> None:
    self.app = Flask(__name__)
    self.logger = logger
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.WARNING)
    self.setup_routes()

  def setup_routes(self) -> None:
    @self.app.route("/")
    def home():
      return "Dummy Server is running"

    @self.app.route("/health", methods=["GET"])
    def health_check():
      return "OK", 200

  def ping_dummy_server(self) -> None:
    DUMMY_SERVER_URL = f"{os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')}/health"
    try:
      response = requests.get(DUMMY_SERVER_URL)
      if response.status_code == 200:
        self.logger.info(f"Successfully pinged the dummy server {DUMMY_SERVER_URL}.")
      else:
        self.logger.warning(f"Unexpected response from server: {response.status_code}")
    except requests.exceptions.RequestException as e:
      self.logger.error(f"Failed to reach dummy server: {e}")

  def start_server(self) -> None:
    self.app.run(host="0.0.0.0", port=5000)
