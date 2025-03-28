import logging
import os
import telebot
import threading
import time
import schedule
from chat.chat_manager import ChatManager
from chat.keyboard_manager import KeyboardManager
from common.data_types import ResultData
from history.history_manager import HistoryManager
from menu.menu_manager import MenuManager
from server.server import Server
from studios.absolute.absolute import get_absolute_schedule_and_instructorid_map
from studios.ally.ally import get_ally_schedule_and_instructorid_map
from studios.anarchy.anarchy import get_anarchy_schedule_and_instructorid_map
from studios.barrys.barrys import get_barrys_schedule_and_instructorid_map
from studios.rev.rev import get_rev_schedule_and_instructorid_map
from studios.studios_manager import StudioManager, StudiosManager

class App:
  def __init__(self) -> None:
    self.logger = logging.getLogger(__name__)
    logging.basicConfig(
      format="%(asctime)s %(filename)s:%(lineno)d [%(levelname)-1s] %(message)s",
      level=logging.INFO,
      datefmt="%d-%m-%Y %H:%M:%S")

    bot_token = os.environ.get("BOT_TOKEN")
    self.bot = telebot.TeleBot(bot_token)
    start_command = telebot.types.BotCommand(command="start", description="Check schedules")
    nerd_command = telebot.types.BotCommand(command="nerd", description="Nerd mode")
    instructors_command = telebot.types.BotCommand(command="instructors", description="Show list of instructors")
    self.bot.set_my_commands([start_command, nerd_command, instructors_command])

    self.keyboard_manager = KeyboardManager()
    self.chat_manager = ChatManager(self.bot)
    self.studios_manager = StudiosManager(
      {
        "Absolute" : StudioManager(self.logger, get_absolute_schedule_and_instructorid_map),
        "Ally" : StudioManager(self.logger, get_ally_schedule_and_instructorid_map),
        "Anarchy" : StudioManager(self.logger, get_anarchy_schedule_and_instructorid_map),
        "Barrys" : StudioManager(self.logger, get_barrys_schedule_and_instructorid_map),
        "Rev" : StudioManager(self.logger, get_rev_schedule_and_instructorid_map)
      })

    self.history_manager = HistoryManager(self.logger)
    self.server = Server(self.logger)
    self.menu_manager = MenuManager(self.logger, self.bot, self.chat_manager, self.keyboard_manager, self.studios_manager, self.history_manager)

  def update_cached_result_data(self) -> None:
    def _get_absolute_schedule(self, mutex: threading.Lock, updated_cached_result_data: ResultData) -> None:
      absolute_schedule = self.studios_manager.studios["Absolute"].get_schedule()
      with mutex:
        updated_cached_result_data += absolute_schedule

    def _get_ally_schedule(self, mutex: threading.Lock, updated_cached_result_data: ResultData) -> None:
      ally_schedule = self.studios_manager.studios["Ally"].get_schedule()
      with mutex:
        updated_cached_result_data += ally_schedule

    def _get_anarchy_schedule(self, mutex: threading.Lock, updated_cached_result_data: ResultData) -> None:
      anarchy_schedule = self.studios_manager.studios["Anarchy"].get_schedule()
      with mutex:
        updated_cached_result_data += anarchy_schedule

    def _get_barrys_schedule(self, mutex: threading.Lock, updated_cached_result_data: ResultData) -> None:
      barrys_schedule = self.studios_manager.studios["Barrys"].get_schedule()
      with mutex:
        updated_cached_result_data += barrys_schedule

    def _get_rev_schedule(self, mutex: threading.Lock, updated_cached_result_data: ResultData) -> None:
      rev_schedule = self.studios_manager.studios["Rev"].get_schedule()
      with mutex:
        updated_cached_result_data += rev_schedule

    self.logger.info("Updating cached result data...")
    updated_cached_result_data = ResultData()
    mutex = threading.Lock()

    threads = []
    for func, name in [
      (_get_absolute_schedule, "absolute_thread"),
      (_get_ally_schedule, "ally_thread"),
      (_get_anarchy_schedule, "anarchy_thread"),
      (_get_barrys_schedule, "barrys_thread"),
      (_get_rev_schedule, "rev_thread")
    ]:
      thread = threading.Thread(target=func, name=name, args=(self, mutex, updated_cached_result_data,))
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()

    self.menu_manager.cached_result_data = updated_cached_result_data
    self.logger.info("Successfully updated cached result data!")

  def schedule_update_cached_result_data(self, stop_event: threading.Event) -> None:
    schedule.every(10).minutes.do(self.update_cached_result_data)
    schedule.every(10).minutes.do(self.server.ping_dummy_server)

    while not stop_event.is_set():
      schedule.run_pending()
      time.sleep(1)

  def start_bot_polling(self) -> None:
    self.bot.infinity_polling()

  def run(self) -> None:
    # Load existing history
    self.history_manager.start()

    # Create threads
    self.stop_event = threading.Event()

    # Thread for scheduled updates and server pings
    self.update_schedule_thread = threading.Thread(target=self.schedule_update_cached_result_data, args=[self.stop_event])
    self.update_schedule_thread.start()

    # Start the Flask app in a separate thread
    self.flask_thread = threading.Thread(target=self.server.start_server)
    self.flask_thread.daemon = True  # This allows the thread to exit when the main program ends
    self.flask_thread.start()

    # Get current schedule and store in cache
    self.logger.info("Starting bot...")
    self.update_cached_result_data()
    self.logger.info("Bot started!")

    # Start bot polling in a separate thread
    self.bot_polling_thread = threading.Thread(target=self.start_bot_polling, daemon=True)
    self.bot_polling_thread.start()

    # Wait for bot to handle messages
    self.bot_polling_thread.join()

    # Stop threads
    self.stop_event.set()
    self.update_schedule_thread.join()