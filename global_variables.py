import logging
import os
import telebot
from chat_manager import ChatManager
from common.data_types import ResultData
from history_handler import HistoryHandler

# Global variables
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
  format="%(asctime)s %(filename)s:%(lineno)d [%(levelname)-1s] %(message)s",
  level=logging.INFO,
  datefmt="%d-%m-%Y %H:%M:%S")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT = telebot.TeleBot(BOT_TOKEN)
START_COMMAND = telebot.types.BotCommand(command="start", description="Check schedules")
NERD_COMMAND = telebot.types.BotCommand(command="nerd", description="Nerd mode")
INSTRUCTORS_COMMAND = telebot.types.BotCommand(command="instructors", description="Show list of instructors")
BOT.set_my_commands([START_COMMAND, NERD_COMMAND, INSTRUCTORS_COMMAND])

CHAT_MANAGER = ChatManager()
CACHED_RESULT_DATA = ResultData()
ABSOLUTE_INSTRUCTORID_MAP = {}
ABSOLUTE_INSTRUCTOR_NAMES = []
ALLY_INSTRUCTORID_MAP = {}
ALLY_INSTRUCTOR_NAMES = []
ANARCHY_INSTRUCTORID_MAP = {}
ANARCHY_INSTRUCTOR_NAMES = []
BARRYS_INSTRUCTORID_MAP = {}
BARRYS_INSTRUCTOR_NAMES = []
REV_INSTRUCTORID_MAP = {}
REV_INSTRUCTOR_NAMES = []

HISTORY_HANDLER = HistoryHandler()