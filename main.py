import global_variables
import menu.days_page_handler
import menu.get_schedule_handler
import menu.main_page_handler
import menu.name_filter_page_handler
import menu.nerd_handler
import menu.instructors_page_handler
import menu.studios_page_handler
import menu.time_page_handler
import menu.weeks_page_handler
import telebot
import time
import threading
import schedule
from absolute.absolute import get_absolute_schedule
from absolute.absolute import get_instructorid_map as get_absolute_instructorid_map
from ally.ally import get_ally_schedule
from ally.ally import get_instructorid_map as get_ally_instructorid_map
from anarchy.anarchy import get_anarchy_schedule
from anarchy.anarchy import get_instructorid_map as get_anarchy_instructorid_map
from barrys.barrys import get_barrys_schedule
from barrys.barrys import get_instructorid_map as get_barrys_instructorid_map
from common.data_types import ResultData, StudioLocation
from rev.rev import get_rev_schedule
from rev.rev import get_instructorid_map as get_rev_instructorid_map

@global_variables.BOT.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message) -> None:
  global_variables.HISTORY_HANDLER.add(int(time.time()), message.from_user.id, message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'start')
  global_variables.USER_MANAGER.reset_query_data(message.from_user.id, message.chat.id)
  global_variables.USER_MANAGER.reset_button_data(message.from_user.id, message.chat.id)
  menu.main_page_handler.main_page_handler(message.from_user.id, message)

def update_cached_result_data() -> None:
  def _get_absolute_schedule(mutex, updated_cached_result_data):
    global_variables.ABSOLUTE_INSTRUCTORID_MAP = get_absolute_instructorid_map()
    global_variables.ABSOLUTE_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(global_variables.ABSOLUTE_INSTRUCTORID_MAP)]
    absolute_schedule = get_absolute_schedule(locations=[StudioLocation.All], weeks=2, days=['All'], instructors=['All'], instructorid_map=global_variables.ABSOLUTE_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += absolute_schedule

  def _get_ally_schedule(mutex, updated_cached_result_data):
    global_variables.ALLY_INSTRUCTORID_MAP = get_ally_instructorid_map()
    global_variables.ALLY_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(global_variables.ALLY_INSTRUCTORID_MAP)]
    ally_schedule = get_ally_schedule(weeks=2, days=['All'], instructors=['All'], instructorid_map=global_variables.ALLY_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += ally_schedule

  def _get_anarchy_schedule(mutex, updated_cached_result_data):
    global_variables.ANARCHY_INSTRUCTORID_MAP = get_anarchy_instructorid_map()
    global_variables.ANARCHY_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(global_variables.ANARCHY_INSTRUCTORID_MAP)]
    anarchy_schedule = get_anarchy_schedule(weeks=3, days=['All'], instructors=['All'], instructorid_map=global_variables.ANARCHY_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += anarchy_schedule

  def _get_barrys_schedule(mutex, updated_cached_result_data):
    global_variables.BARRYS_INSTRUCTORID_MAP = get_barrys_instructorid_map()
    global_variables.BARRYS_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(global_variables.BARRYS_INSTRUCTORID_MAP)]
    barrys_schedule = get_barrys_schedule(locations=[StudioLocation.All], weeks=3, days=['All'], instructors=['All'], instructorid_map=global_variables.BARRYS_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += barrys_schedule

  def _get_rev_schedule(mutex, updated_cached_result_data):
    global_variables.REV_INSTRUCTORID_MAP = get_rev_instructorid_map()
    global_variables.REV_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(global_variables.REV_INSTRUCTORID_MAP)]
    rev_schedule = get_rev_schedule(locations=[StudioLocation.All], start_date='', end_date='', days=['All'], instructorid_map=global_variables.REV_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += rev_schedule

  global_variables.LOGGER.info('Updating cached result data...')
  updated_cached_result_data = ResultData()
  mutex = threading.Lock()
  absolute_thread = threading.Thread(target=_get_absolute_schedule, name='absolute_thread', args=(mutex, updated_cached_result_data,))
  ally_thread = threading.Thread(target=_get_ally_schedule, name='ally_thread', args=(mutex, updated_cached_result_data,))
  anarchy_thread = threading.Thread(target=_get_anarchy_schedule, name='anarchy_thread', args=(mutex, updated_cached_result_data,))
  barrys_thread = threading.Thread(target=_get_barrys_schedule, name='barrys_thread', args=(mutex, updated_cached_result_data,))
  rev_thread = threading.Thread(target=_get_rev_schedule, name='rev_thread', args=(mutex, updated_cached_result_data,))

  absolute_thread.start()
  ally_thread.start()
  anarchy_thread.start()
  barrys_thread.start()
  rev_thread.start()
  absolute_thread.join()
  ally_thread.join()
  anarchy_thread.join()
  barrys_thread.join()
  rev_thread.join()

  global_variables.CACHED_RESULT_DATA = updated_cached_result_data
  global_variables.LOGGER.info('Successfully updated cached result data!')

def schedule_update_cached_result_data(stop_event) -> None:
  schedule.every().day.at('00:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('06:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('12:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('18:00', 'Asia/Singapore').do(update_cached_result_data)
  while not stop_event.is_set():
    schedule.run_pending()
    time.sleep(1)

if __name__ =="__main__":
  # Load existing history
  global_variables.HISTORY_HANDLER.start()

  # Create threads
  stop_event = threading.Event()
  update_schedule_thread = threading.Thread(target=schedule_update_cached_result_data, args=[stop_event])
  update_schedule_thread.start()

  # Get current schedule and store in cache
  global_variables.LOGGER.info('Starting bot...')
  update_cached_result_data()
  global_variables.LOGGER.info('Bot started!')

  # Start bot
  global_variables.BOT.infinity_polling()

  # Stop threads
  stop_event.set()
  update_schedule_thread.join()