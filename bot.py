import absolute
import ally
import barrys
from datetime import datetime
import logging
import os
import rev
import telebot
import time
import threading
import schedule
from absolute.absolute import get_absolute_schedule
from absolute.absolute import get_instructorid_map as get_absolute_instructorid_map
from ally.ally import get_ally_schedule
from ally.ally import get_instructorid_map as get_ally_instructorid_map
from barrys.barrys import get_barrys_schedule
from barrys.barrys import get_instructorid_map as get_barrys_instructorid_map
from common.data_types import QueryData, ResultData, SORTED_DAYS, StudioData, StudioLocation, STUDIO_LOCATIONS_MAP, StudioType
from copy import copy
from rev.rev import get_rev_schedule
from rev.rev import get_instructorid_map as get_rev_instructorid_map
from user_manager import UserManager

# Global variables
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
  format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)-1s] %(message)s',
  level=logging.INFO,
  datefmt='%d-%m-%Y %H:%M:%S')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT = telebot.TeleBot(BOT_TOKEN)
START_COMMAND = telebot.types.BotCommand(command='start', description='Check schedules')
NERD_COMMAND = telebot.types.BotCommand(command='nerd', description='Nerd mode')
INSTRUCTORS_COMMAND = telebot.types.BotCommand(command='instructors', description='Show list of instructors')
BOT.set_my_commands([START_COMMAND, NERD_COMMAND, INSTRUCTORS_COMMAND])

USER_MANAGER = UserManager()
CACHED_RESULT_DATA = ResultData()
ABSOLUTE_INSTRUCTORID_MAP = {}
ABSOLUTE_INSTRUCTOR_NAMES = []
ALLY_INSTRUCTORID_MAP = {}
ALLY_INSTRUCTOR_NAMES = []
BARRYS_INSTRUCTORID_MAP = {}
BARRYS_INSTRUCTOR_NAMES = []
REV_INSTRUCTORID_MAP = {}
REV_INSTRUCTOR_NAMES = []

def get_studios_keyboard(user_id: int, chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  query_data = USER_MANAGER.get_query_data(user_id, chat_id)
  button_data = USER_MANAGER.get_button_data(user_id, chat_id)
  studios_keyboard = telebot.types.InlineKeyboardMarkup()
  studios_keyboard.add(button_data.studios_buttons_map['Rev'], button_data.studios_buttons_map['Barrys'])
  studios_keyboard.add(button_data.studios_buttons_map['Absolute (Spin)'], button_data.studios_buttons_map['Absolute (Pilates)'])
  studios_keyboard.add(button_data.studios_buttons_map['Ally (Spin)'], button_data.studios_buttons_map['Ally (Pilates)'])
  studios_keyboard.add(button_data.studios_select_all_button, button_data.studios_unselect_all_button)
  studios_keyboard.add(button_data.studios_next_button)
  return studios_keyboard

def get_locations_keyboard(user_id: int, chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  query_data = USER_MANAGER.get_query_data(user_id, chat_id)
  button_data = USER_MANAGER.get_button_data(user_id, chat_id)
  locations_keyboard = telebot.types.InlineKeyboardMarkup()
  if query_data.current_studio == 'Rev':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Rev']['Bugis'], button_data.studios_locations_buttons_map['Rev']['Orchard'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Rev']['TJPG'])
  elif query_data.current_studio == 'Barrys':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Barrys']['Orchard'], button_data.studios_locations_buttons_map['Barrys']['Raffles'])
  elif query_data.current_studio == 'Absolute (Spin)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Centrepoint'], button_data.studios_locations_buttons_map['Absolute (Spin)']['i12'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Star Vista'], button_data.studios_locations_buttons_map['Absolute (Spin)']['Raffles'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Millenia Walk'])
  elif query_data.current_studio == 'Absolute (Pilates)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Centrepoint'], button_data.studios_locations_buttons_map['Absolute (Pilates)']['i12'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Star Vista'], button_data.studios_locations_buttons_map['Absolute (Pilates)']['Raffles'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Great World'])
  elif query_data.current_studio == 'Ally (Spin)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Ally (Spin)']['Cross Street'])
  elif query_data.current_studio == 'Ally (Pilates)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Ally (Pilates)']['Cross Street'])
  locations_keyboard.add(button_data.locations_select_all_button, button_data.locations_unselect_all_button)
  locations_keyboard.add(button_data.locations_select_more_studios_button, button_data.locations_next_button)
  return locations_keyboard

def get_days_keyboard(user_id: int, chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  button_data = USER_MANAGER.get_button_data(user_id, chat_id)
  days_keyboard = telebot.types.InlineKeyboardMarkup()
  days_keyboard.add(button_data.days_buttons_map['Monday'], button_data.days_buttons_map['Tuesday'])
  days_keyboard.add(button_data.days_buttons_map['Wednesday'], button_data.days_buttons_map['Thursday'])
  days_keyboard.add(button_data.days_buttons_map['Friday'], button_data.days_buttons_map['Saturday'])
  days_keyboard.add(button_data.days_buttons_map['Sunday'])
  days_keyboard.add(button_data.days_select_all_button, button_data.days_unselect_all_button)
  days_keyboard.add(button_data.days_next_button)
  return days_keyboard

def send_results(query: telebot.types.CallbackQuery) -> None:
  global CACHED_RESULT_DATA
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  result = CACHED_RESULT_DATA.get_data(query_data)
  USER_MANAGER.reset_query_data(query.from_user.id, query.message.chat.id)

  # Send string as messages
  schedule_str = result.get_result_str()
  if len(schedule_str) > 4095:
    shortened_message = ''
    for line in schedule_str.splitlines():
      shortened_message_len = len(shortened_message)
      # String of day is bolded which starts with '*', so we want to check from the second character
      is_new_day = line[1:].startswith(tuple(SORTED_DAYS)) and shortened_message_len > 0
      max_len_reached = shortened_message_len + len(line) > 4095
      if is_new_day or max_len_reached:
        BOT.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
        shortened_message = line + '\n'
      else:
        shortened_message += line + '\n'

    if len(shortened_message) > 0:
      BOT.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
  else:
    BOT.send_message(query.message.chat.id, schedule_str, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios-selection')
def studios_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  sent_msg = BOT.send_message(query.message.chat.id, text, reply_markup=get_studios_keyboard(query.from_user.id, query.message.chat.id), parse_mode='Markdown')
  USER_MANAGER.update_button_data_studios_selection_message(query.from_user.id, query.message.chat.id, sent_msg)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-selection')
def instructors_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  instructors_selection_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks-selection')
def weeks_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected week(s)*\n'
  text += query_data.get_query_str(include_weeks=True)
  text += '\nAbsolute shows up to 1.5 weeks\nAlly shows up to 2 weeks\nBarrys shows up to 3 weeks\nRev shows up to 4 weeks\n'

  one_button = telebot.types.InlineKeyboardButton('1', callback_data='{"weeks": 1, "step": "weeks"}')
  two_button = telebot.types.InlineKeyboardButton('2', callback_data='{"weeks": 2, "step": "weeks"}')
  three_button = telebot.types.InlineKeyboardButton('3', callback_data='{"weeks": 3, "step": "weeks"}')
  four_button = telebot.types.InlineKeyboardButton('4', callback_data='{"weeks": 4, "step": "weeks"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "main-page-handler"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(one_button, two_button)
  keyboard.add(three_button, four_button)
  keyboard.add(back_button)
  sent_msg = BOT.send_message(query.message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-selection')
def days_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  days_selection_handler(query.from_user.id, query.message)

def days_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Currently selected day(s)*\n'
  text += query_data.get_query_str(include_days=True)

  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=get_days_keyboard(user_id, message.chat.id), parse_mode='Markdown')
  USER_MANAGER.update_button_data_days_selection_message(user_id, message.chat.id, sent_msg)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection')
def time_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_handler(query.from_user.id, query.message)

def time_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Currently selected timings(s)*\n'
  text += query_data.get_query_str(include_time=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  add_timeslot_button = telebot.types.InlineKeyboardButton('Add Timeslot', callback_data='{"step": "time-selection-add"}')
  remove_timeslot_button = telebot.types.InlineKeyboardButton('Remove Timeslot', callback_data='{"step": "time-selection-remove"}')
  reset_all_timeslot_button = telebot.types.InlineKeyboardButton('Reset All Timeslot(s)', callback_data='{"step": "time-selection-reset"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "main-page-handler"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(add_timeslot_button)
  keyboard.add(remove_timeslot_button)
  keyboard.add(reset_all_timeslot_button)
  keyboard.add(next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-add')
def time_selection_add_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time_selection_handler(query.from_user.id, query.message)

def start_time_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  text = 'Enter range of timeslot to check\ne.g. *0700-0830*'
  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, start_time_input_handler, user_id)

def start_time_input_handler(message: telebot.types.Message, user_id: int) -> None:
  try:
    message_without_whitespace = ''.join(message.text.split())
    split_message_without_whitespace = message_without_whitespace.split('-')
    if len(split_message_without_whitespace) != 2:
      raise Exception('Input has invalid format')

    start_time_from_str = split_message_without_whitespace[0]
    start_time_to_str = split_message_without_whitespace[1]

    if len(start_time_from_str) != 4:
      raise Exception('Start time from has invalid length')

    if len(start_time_to_str) != 4:
      raise Exception('Start time to has invalid length')

    start_time_from = datetime.strptime(start_time_from_str, '%H%M')
    start_time_to = datetime.strptime(start_time_to_str, '%H%M')
  except Exception as e:
    print(f'Invalid time "{message.text}" entered: {str(e)}')
    text = f'Invalid time "{message.text}" entered'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  if start_time_to < start_time_from:
    text = f'Start time to must be later than or equal start time from. Start time from: {query_data.start_time_from.strftime("%H%M")}'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)

  # Start time from should be at least one minute before existing start time from or greater than or equal existing start time to
  is_valid_start_time_from = True
  for existing_start_time_from, existing_start_time_to in query_data.start_times:
    at_least_one_minute_before_existing_start_time_from = start_time_from.hour < existing_start_time_from.hour or start_time_from.hour == existing_start_time_from.hour and start_time_from.minute < existing_start_time_from.minute
    greater_than_or_equal_existing_start_time_to = start_time_from >= existing_start_time_to
    if not at_least_one_minute_before_existing_start_time_from and not greater_than_or_equal_existing_start_time_to:
      conflicting_start_time_from_str = existing_start_time_from.strftime("%H%M")
      conflicting_start_time_to_str = existing_start_time_to.strftime("%H%M")
      is_valid_start_time_from = False
      break

    # Edge case where existing timeslot start time from and to are the same
    if existing_start_time_from.hour == existing_start_time_to.hour and existing_start_time_from.minute == existing_start_time_to.minute:
      if start_time_from.hour == existing_start_time_from.hour and start_time_from.minute == existing_start_time_from.minute:
        conflicting_start_time_from_str = existing_start_time_from.strftime("%H%M")
        conflicting_start_time_to_str = existing_start_time_to.strftime("%H%M")
        is_valid_start_time_from = False
        break

  if not is_valid_start_time_from:
    text = f'Start time "{start_time_from_str}" conflicts with existing timeslot "{conflicting_start_time_from_str} - {conflicting_start_time_to_str}"'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  # Start time to should be less than or equal to existing start time from or greater than existing start time to
  is_valid_start_time_to = True
  for existing_start_time_from, existing_start_time_to in query_data.start_times:
    less_than_or_equal_existing_start_time_from = start_time_to <= existing_start_time_from
    greater_than_existing_start_time_to = start_time_to > existing_start_time_to
    if not less_than_or_equal_existing_start_time_from and not greater_than_existing_start_time_to:
      conflicting_start_time_from_str = existing_start_time_from.strftime("%H%M")
      conflicting_start_time_to_str = existing_start_time_to.strftime("%H%M")
      is_valid_start_time_to = False
      break

    # If start time to is greated than existing start time to, start time from must also be greater than existing start time to
    if greater_than_existing_start_time_to:
      if start_time_from < existing_start_time_to:
        conflicting_start_time_from_str = existing_start_time_from.strftime("%H%M")
        conflicting_start_time_to_str = existing_start_time_to.strftime("%H%M")
        text = f'Time range "{start_time_from_str} - {start_time_to_str}" conflicts with existing timeslot "{conflicting_start_time_from_str} - {conflicting_start_time_to_str}"'
        sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
        time_selection_handler(user_id, message)
        return


  if not is_valid_start_time_to:
    text = f'End time "{start_time_to_str}" conflicts with existing timeslot "{conflicting_start_time_from_str} - {conflicting_start_time_to_str}"'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  query_data.start_times.append((start_time_from, start_time_to))
  query_data.start_times = sorted(query_data.start_times)
  time_selection_handler(user_id, message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-remove')
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_remove_handler(query.message, query.from_user.id)

def time_selection_remove_handler(message: telebot.types.Message, user_id: int) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  if len(query_data.start_times) == 0:
    text = 'No timeslot to remove'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
  else:
    text = '*Select timeslot to remove*'
    keyboard = telebot.types.InlineKeyboardMarkup()
    buttons = []
    for start_time_from, start_time_to in query_data.start_times:
      start_time_from_str = start_time_from.strftime("%H%M")
      start_time_to_str = start_time_to.strftime("%H%M")
      remove_timeslot_button = telebot.types.InlineKeyboardButton(f'{start_time_from_str} - {start_time_to_str}', callback_data=f'{{"step": "remove-timeslot", "from":"{start_time_from_str}", "to":"{start_time_to_str}"}}')
      buttons.append(remove_timeslot_button)
      keyboard.add(buttons[-1])

    back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "time-selection"}')
    keyboard.add(back_button)
    sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'remove-timeslot')
def time_selection_remove_timeslot_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time_from = eval(query.data)['from']
  start_time_to = eval(query.data)['to']
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  query_data.start_times.remove((datetime.strptime(start_time_from, '%H%M'), datetime.strptime(start_time_to, '%H%M')))
  time_selection_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-reset')
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  query_data.start_times = []
  time_selection_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'class-name-filter-selection')
def class_name_filter_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  class_name_filter_selection_handler(query.from_user.id, query.message)

def class_name_filter_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Current filter*\n'
  text += query_data.get_query_str(include_class_name_filter=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  set_filter_button = telebot.types.InlineKeyboardButton('Set Filter', callback_data='{"step": "class-name-filter-set"}')
  reset_filter_button = telebot.types.InlineKeyboardButton('Reset Filter', callback_data='{"step": "class-name-filter-reset"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "main-page-handler"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(set_filter_button, reset_filter_button)
  keyboard.add(next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'class-name-filter-set')
def class_name_filter_set_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter name of class to filter (non-case sensitive)\ne.g. *essential*'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, class_name_filter_input_handler, query.from_user.id)

def class_name_filter_input_handler(message: telebot.types.Message, user_id: int) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  query_data.class_name_filter = message.text
  class_name_filter_selection_handler(user_id, message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'class-name-filter-reset')
def class_name_filter_reset_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  query_data.class_name_filter = ''
  class_name_filter_selection_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'get-schedule')
def get_schedule_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  if len(query_data.studios) == 0:
    text = 'No studio(s) selected. Please select the studio(s) to get schedule for'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    main_page_handler(query.from_user.id, query.message)
    return

  if len(query_data.days) == 0:
    text = 'No day(s) selected. Please select the day(s) to get schedule for'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    main_page_handler(query.from_user.id, query.message)
    return

  send_results(query)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios')
def studios_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  button_data = USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  query_data_dict = eval(query.data)
  selected_studio = StudioType[query_data_dict['studios']]
  if selected_studio == StudioType.Null:
    for studio in button_data.studios_buttons_map:
      button_data.studios_buttons_map[studio] = telebot.types.InlineKeyboardButton(studio, callback_data=button_data.studios_buttons_map[studio].callback_data)
    USER_MANAGER.update_button_data_studios_buttons_map(query.from_user.id, query.message.chat.id, button_data.studios_buttons_map)
    USER_MANAGER.update_query_data_studios(query.from_user.id, query.message.chat.id, {})
    USER_MANAGER.reset_button_data_studios_locations_buttons_map(query.from_user.id, query.message.chat.id)
  elif selected_studio == StudioType.All:
    for studio in button_data.studios_buttons_map:
      button_data.studios_buttons_map[studio] = telebot.types.InlineKeyboardButton(studio + ' ✅', callback_data=button_data.studios_buttons_map[studio].callback_data)
    USER_MANAGER.update_button_data_studios_buttons_map(query.from_user.id, query.message.chat.id, button_data.studios_buttons_map)
    USER_MANAGER.update_query_data_select_all_studios(query.from_user.id, query.message.chat.id)
    USER_MANAGER.update_button_data_select_all_studios_locations_buttons_map(query.from_user.id, query.message.chat.id)
  elif selected_studio == StudioType.AllySpin or selected_studio == StudioType.AllyPilates:
    USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, selected_studio)
    select_location_handler(query.from_user.id, query.message, StudioLocation.CrossStreet)
  else:
    USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, selected_studio)
    locations_handler(query.from_user.id, query.message)
    return

  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  BOT.edit_message_text(
    chat_id=button_data.studios_selection_message.chat.id,
    message_id=button_data.studios_selection_message.id,
    text=text,
    reply_markup=get_studios_keyboard(query.from_user.id, query.message.chat.id),
    parse_mode='Markdown')

def select_location_handler(user_id: int, message: telebot.types.Message, selected_studio_location: StudioLocation) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  button_data = USER_MANAGER.get_button_data(user_id, message.chat.id)
  if selected_studio_location == StudioLocation.Null:
    for location in button_data.studios_locations_buttons_map[query_data.current_studio]:
      button_data.studios_locations_buttons_map[query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location, callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][location].callback_data)
    button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio, callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
    USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
    query_data.studios.pop(query_data.current_studio)
    USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
  elif selected_studio_location == StudioLocation.All:
    for location in button_data.studios_locations_buttons_map[query_data.current_studio]:
      button_data.studios_locations_buttons_map[query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location + ' ✅', callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][location].callback_data)
    button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
    USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
    if query_data.current_studio not in query_data.studios:
      new_studio = {query_data.current_studio: StudioData(locations=copy(STUDIO_LOCATIONS_MAP[query_data.current_studio]))}
      query_data.studios = {**query_data.studios, **new_studio}
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    else:
      query_data.studios[query_data.current_studio].locations = copy(STUDIO_LOCATIONS_MAP[query_data.current_studio])
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
  else:
    if query_data.current_studio not in query_data.studios:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location + ' ✅',
          callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      new_studio = {query_data.current_studio: StudioData(locations=[selected_studio_location])}
      query_data.studios = {**query_data.studios, **new_studio}
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    elif selected_studio_location in query_data.studios[query_data.current_studio].locations:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location,
          callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      query_data.studios[query_data.current_studio].locations.remove(selected_studio_location)
      if len(query_data.studios[query_data.current_studio].locations) == 0:
        query_data.studios.pop(query_data.current_studio)
        button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio, callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    else:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = telebot.types.InlineKeyboardButton(selected_studio_location + ' ✅', callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      query_data.studios[query_data.current_studio].locations.append(selected_studio_location)
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)


@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations')
def locations_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  button_data = USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  select_location_handler(query.from_user.id, query.message, StudioLocation[query_data_dict['location']])
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  BOT.edit_message_text(
    chat_id=button_data.locations_selection_message.chat.id,
    message_id=button_data.locations_selection_message.id,
    text=text,
    reply_markup=get_locations_keyboard(query.from_user.id, query.message.chat.id),
    parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'main-page-handler')
def main_page_handler_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  main_page_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks')
def weeks_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  USER_MANAGER.update_query_data_weeks(query.from_user.id, query.message.chat.id, query_data_dict['weeks'])
  main_page_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days')
def days_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  button_data = USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  query_data_dict = eval(query.data)
  selected_day = query_data_dict['days']
  if selected_day == 'None':
    for day in button_data.days_buttons_map:
      button_data.days_buttons_map[day] = telebot.types.InlineKeyboardButton(day, callback_data=button_data.days_buttons_map[day].callback_data)
    USER_MANAGER.update_button_data_days_buttons_map(query.from_user.id, query.message.chat.id, button_data.days_buttons_map)
    USER_MANAGER.update_query_data_days(query.from_user.id, query.message.chat.id, [])
  elif selected_day == 'All':
    for day in button_data.days_buttons_map:
      button_data.days_buttons_map[day] = telebot.types.InlineKeyboardButton(day + ' ✅', callback_data=button_data.days_buttons_map[day].callback_data)
    USER_MANAGER.update_button_data_days_buttons_map(query.from_user.id, query.message.chat.id, button_data.days_buttons_map)
    USER_MANAGER.update_query_data_days(query.from_user.id, query.message.chat.id, SORTED_DAYS)
  else:
    query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
    if selected_day in query_data.days:
      button_data.days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day, callback_data=button_data.days_buttons_map[selected_day].callback_data)
      USER_MANAGER.update_button_data_days_buttons_map(query.from_user.id, query.message.chat.id, button_data.days_buttons_map)
      query_data.days.remove(selected_day)
      USER_MANAGER.update_query_data_days(query.from_user.id, query.message.chat.id, query_data.days)
    else:
      button_data.days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day + ' ✅', callback_data=button_data.days_buttons_map[selected_day].callback_data)
      USER_MANAGER.update_button_data_days_buttons_map(query.from_user.id, query.message.chat.id, button_data.days_buttons_map)
      query_data.days.append(selected_day)
      query_data.days = sorted(query_data.days, key=SORTED_DAYS.index)
      USER_MANAGER.update_query_data_days(query.from_user.id, query.message.chat.id, query_data.days)

  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected day(s)*\n'
  text += query_data.get_query_str(include_days=True)

  button_data = USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  BOT.edit_message_text(
    chat_id=button_data.days_selection_message.chat.id,
    message_id=button_data.days_selection_message.id,
    text=text,
    reply_markup=get_days_keyboard(query.from_user.id, query.message.chat.id),
    parse_mode='Markdown')


@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-next')
def days_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  if len(query_data.days) == 0:
    text = 'No day(s) selected. Please select the day(s) to get schedule for'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    days_selection_handler(query.from_user.id, query.message)
    return

  main_page_handler(query.from_user.id, query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'rev-instructors')
def rev_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *chloe*, *jerlyn*, *zai*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Rev')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, REV_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'barrys-instructors')
def barrys_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *ria*, *gino*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Barrys')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, BARRYS_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-spin-instructors')
def absolute_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *chin*, *ria*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Absolute (Spin)')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, ABSOLUTE_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-pilates-instructors')
def absolute_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *daniella*, *vnex*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Absolute (Pilates)')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, ABSOLUTE_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-spin-instructors')
def ally_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *samuel*, *jasper*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Ally (Spin)')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, ALLY_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-pilates-instructors')
def ally_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *candice*, *ruth*\nEnter "*all*" to check for all instructors'
  USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Ally (Pilates)')
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, ALLY_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'show-instructors')
def show_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global ABSOLUTE_INSTRUCTOR_NAMES, ALLY_INSTRUCTOR_NAMES, BARRYS_INSTRUCTOR_NAMES, REV_INSTRUCTOR_NAMES
  query_data = USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = ''
  if 'Rev' in query_data.studios:
    text += '*Rev Instructors:* ' + ', '.join(REV_INSTRUCTOR_NAMES) + '\n\n'
  if 'Barrys' in query_data.studios:
    text += '*Barrys Instructors:* ' + ', '.join(BARRYS_INSTRUCTOR_NAMES) + '\n\n'
  if 'Absolute (Spin)' in query_data.studios or 'Absolute (Pilates)' in query_data.studios:
    text += '*Absolute Instructors:* ' + ', '.join(ABSOLUTE_INSTRUCTOR_NAMES) + '\n\n'
  if 'Ally (Spin)' in query_data.studios or 'Ally (Pilates)' in query_data.studios:
    text += '*Ally Instructors:* ' + ', '.join(ALLY_INSTRUCTOR_NAMES) + '\n\n'

  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  instructors_selection_handler(query.from_user.id, query.message)

def instructors_input_handler(message: telebot.types.Message, user_id: int, instructorid_map: dict[str, int]) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  updated_instructors_list = [x.strip() for x in message.text.lower().split(',')]
  if 'all' in updated_instructors_list:
    query_data.studios[query_data.current_studio].instructors = ['All']
    USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
  else:
    invalid_instructors = []
    for instructor in updated_instructors_list:
      instructor_in_map = (any(instructor in instructor_in_map.split(' ') for instructor_in_map in instructorid_map)
        or any(instructor == instructor_in_map for instructor_in_map in instructorid_map))
      if not instructor_in_map:
        invalid_instructors.append(instructor)

    if len(invalid_instructors) > 0:
      updated_instructors_list = [
        instructor for instructor
        in updated_instructors_list
        if instructor not in invalid_instructors
      ]
      USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
      text = f'Failed to find instructor(s): {", ".join(invalid_instructors)}'
      sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

    if len(updated_instructors_list) > 0:
      query_data.studios[query_data.current_studio].instructors = updated_instructors_list

  instructors_selection_handler(user_id, message)

@BOT.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message) -> None:
  USER_MANAGER.reset_query_data(message.from_user.id, message.chat.id)
  USER_MANAGER.reset_button_data(message.from_user.id, message.chat.id)
  main_page_handler(message.from_user.id, message)

def main_page_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Schedule to check*\n'
  text += query_data.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True, include_time=True, include_class_name_filter=True)

  studios_button = telebot.types.InlineKeyboardButton('Studios', callback_data='{"step": "studios-selection"}')
  instructors_button = telebot.types.InlineKeyboardButton('Instructors', callback_data='{"step": "instructors-selection"}')
  weeks_button = telebot.types.InlineKeyboardButton('Weeks', callback_data='{"step": "weeks-selection"}')
  days_button = telebot.types.InlineKeyboardButton('Days', callback_data='{"step": "days-selection"}')
  time_button = telebot.types.InlineKeyboardButton('Time', callback_data='{"step": "time-selection"}')
  class_name_button = telebot.types.InlineKeyboardButton('Class Name', callback_data='{"step": "class-name-filter-selection"}')
  next_button = telebot.types.InlineKeyboardButton('Get Schedule ▶️', callback_data='{"step": "get-schedule"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(studios_button, instructors_button)
  keyboard.add(weeks_button, days_button)
  keyboard.add(time_button, class_name_button)
  keyboard.add(next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@BOT.message_handler(commands=['instructors'])
def instructors_list_handler(message: telebot.types.Message) -> None:
  global ABSOLUTE_INSTRUCTOR_NAMES, ALLY_INSTRUCTOR_NAMES, BARRYS_INSTRUCTOR_NAMES, REV_INSTRUCTOR_NAMES
  text = '*Rev Instructors:* ' + ', '.join(REV_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Barrys Instructors:* ' + ', '.join(BARRYS_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Absolute Instructors:* ' + ', '.join(ABSOLUTE_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Ally Instructors:* ' + ', '.join(ALLY_INSTRUCTOR_NAMES) + '\n\n'
  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

@BOT.message_handler(commands=['nerd'])
def nerd_handler(message: telebot.types.Message) -> None:
  text = "Welcome to nerd mode 🤓\n" \
         "\n" \
         "*Enter your query in the following format:*\n" \
         "Studio name\n" \
         "Studio locations (comma separated)\n" \
         "Instructor names (comma separated)\n" \
         "(Repeat above for multiple studios)\n" \
         "Weeks\n" \
         "Days\n" \
         "Start Time From (24h Format)\n" \
         "Start Time To (24h Format)\n" \
         "Class Name Filter (enter 'nil' to ignore filters)\n" \
         "\n" \
         "*Studio names*: rev, barrys, absolute (spin), absolute (pilates), ally (spin), ally (pilates)\n" \
         "*Studio locations*: orchard, tjpg, bugis, raffles, centrepoint, i12, millenia walk, star vista, great world, cross street\n" \
         "*Instructors*: Use /instructors for list of instructors\n" \
         "\n" \
         "*e.g.*\n" \
         "rev\n" \
         "bugis, orchard\n" \
         "chloe, zai\n" \
         "absolute (spin)\n" \
         "raffles\n" \
         "ria\n" \
         "2\n" \
         "monday, wednesday, saturday\n" \
         "0700\n" \
         "0900\n" \
         "nil\n"

  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, nerd_input_handler)

def nerd_input_handler(message: telebot.types.Message) -> None:
  '''
  See nerd_handler function header for expected message format
  '''
  global ABSOLUTE_INSTRUCTOR_NAMES, ALLY_INSTRUCTOR_NAMES, BARRYS_INSTRUCTOR_NAMES, REV_INSTRUCTOR_NAMES
  input_str_list = message.text.splitlines()

  # Weeks, days, start time from, start time to, and class name filter = 5 items. Remaining items should be divisible by 3 (studio name, locations, instructors)
  if (len(input_str_list) - 5) % 3 != 0:
    BOT.send_message(message.chat.id, 'Failed to handle query. Unexpected format received.', parse_mode='Markdown')
    return

  # Loop through studios
  query = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[], start_time_from='0000', start_time_to='2359', class_name_filter='')
  current_studio = StudioType.Null
  current_studio_locations = []
  for index, input_str in enumerate(input_str_list[:-5]):
    step = index % 3
    if step == 0: # Studio name
      selected_studio = None
      found_studio = False
      for studio in StudioType:
        if input_str.lower() == studio.value.lower():
          current_studio = studio
          found_studio = True
          break
      if not found_studio:
        BOT.send_message(message.chat.id, f'Failed to handle query. Unexpected studio name \'{input_str}\'', parse_mode='Markdown')
        return
    elif step == 1: # Studio locations
      selected_locations = [x.strip() for x in input_str.split(',')]
      for selected_location in selected_locations:
        found_location = False
        for location in StudioLocation:
          if selected_location.lower() == location.value.lower():
            current_studio_locations.append(location)
            found_location = True
            break
        if not found_location:
          BOT.send_message(message.chat.id, f'Failed to handle query. Unexpected studio name \'{selected_location}\'', parse_mode='Markdown')
          return
    elif step == 2: # Studio instructors
      instructor_list = []
      if current_studio == StudioType.Rev:
        instructor_list = REV_INSTRUCTOR_NAMES
      elif current_studio == StudioType.Barrys:
        instructor_list = BARRYS_INSTRUCTOR_NAMES
      elif current_studio == StudioType.AbsolutePilates or current_studio == StudioType.AbsoluteSpin:
        instructor_list = ABSOLUTE_INSTRUCTOR_NAMES
      elif current_studio == StudioType.AllyPilates or current_studio == StudioType.AllySpin:
        instructor_list = ALLY_INSTRUCTOR_NAMES

      selected_instructors = [x.strip().lower() for x in input_str.split(',')]
      invalid_instructors = []
      if 'all' in selected_instructors:
        selected_instructors = ['All']
      else:
        for instructor in selected_instructors:
          found_instructor = (any(instructor in instructor_in_list.split(' ') for instructor_in_list in instructor_list)
            or any(instructor == instructor_in_list for instructor_in_list in instructor_list))
          if not found_instructor:
            invalid_instructors.append(instructor)

      if len(invalid_instructors) > 0:
        selected_instructors = [instructor for instructor in selected_instructors if instructor not in invalid_instructors]
        print('[test]')
        print(instructor_list)
        text = f'Failed to find instructor(s): {", ".join(invalid_instructors)}'
        sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

      if len(selected_instructors) == 0:
        BOT.send_message(message.chat.id, f'Failed to handle query. No instructor selected for {current_studio}', parse_mode='Markdown')
        return

      query.studios[current_studio] = StudioData(locations=current_studio_locations, instructors = selected_instructors)

  # Get number of weeks
  try:
    query.weeks = int(input_str_list[-5])
  except:
    BOT.send_message(message.chat.id, f'Failed to handle query. Invalid input for \'weeks\'. Expected number, got {input_str_list[-2]}', parse_mode='Markdown')
    return

  # Get list of days
  query.days = [x.strip().capitalize() for x in input_str_list[-4].split(',')]
  if 'All' in query.days:
    query.days = ['All']
  else:
    for selected_day in query.days:
      if selected_day.capitalize() not in SORTED_DAYS:
        BOT.send_message(message.chat.id, f'Failed to handle query. Invalid input for \'days\'. Unknown day {selected_day}', parse_mode='Markdown')
        return

  # Get start time from
  query.start_time_from = datetime.strptime(input_str_list[-3], '%H%M')

  # Get start time to
  query.start_time_to = datetime.strptime(input_str_list[-2], '%H%M')

  # Get class name filter
  query.class_name_filter = '' if input_str_list[-1] == 'nil' else input_str_list[-1]

  result = CACHED_RESULT_DATA.get_data(query)

  # Send string as messages
  schedule_str = result.get_result_str()
  if len(schedule_str) > 4095:
    shortened_message = ''
    for line in schedule_str.splitlines():
      is_new_day = any(day in line for day in SORTED_DAYS) and len(shortened_message) > 0
      max_len_reached = len(shortened_message) + len(line) > 4095
      if is_new_day or max_len_reached:
        BOT.send_message(message.chat.id, shortened_message, parse_mode='Markdown')
        shortened_message = line + '\n'
      else:
        shortened_message += line + '\n'

    if len(shortened_message) > 0:
      BOT.send_message(message.chat.id, shortened_message, parse_mode='Markdown')
  else:
    BOT.send_message(message.chat.id, schedule_str, parse_mode='Markdown')

def locations_handler(user_id: int, message: telebot.types.Message):
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  sent_msg = BOT.send_message(
    message.chat.id, text, reply_markup=get_locations_keyboard(user_id, message.chat.id), parse_mode='Markdown')
  USER_MANAGER.update_button_data_locations_selection_message(user_id, message.chat.id, sent_msg)

def instructors_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = USER_MANAGER.get_query_data(user_id, message.chat.id)
  if len(query_data.studios) == 0:
    text = 'No studio(s) selected. Please select the studio(s) first'
    sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    main_page_handler(user_id, message)
    return

  text = '*Currently selected instructor(s)*\n'
  text += query_data.get_query_str(include_instructors=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  if 'Rev' in query_data.studios:
    rev_instructors_button = telebot.types.InlineKeyboardButton('Enter Rev Instructor(s)', callback_data='{"step": "rev-instructors"}')
    keyboard.add(rev_instructors_button)
  if 'Barrys' in query_data.studios:
    barrys_instructors_button = telebot.types.InlineKeyboardButton('Enter Barrys Instructor(s)', callback_data='{"step": "barrys-instructors"}')
    keyboard.add(barrys_instructors_button)
  if 'Absolute (Spin)' in query_data.studios:
    absolute_spin_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Spin) Instructor(s)', callback_data='{"step": "absolute-spin-instructors"}')
    keyboard.add(absolute_spin_instructors_button)
  if 'Absolute (Pilates)' in query_data.studios:
    absolute_pilates_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Pilates) Instructor(s)', callback_data='{"step": "absolute-pilates-instructors"}')
    keyboard.add(absolute_pilates_instructors_button)
  if 'Ally (Spin)' in query_data.studios:
    ally_spin_instructors_button = telebot.types.InlineKeyboardButton('Enter Ally (Spin) Instructor(s)', callback_data='{"step": "ally-spin-instructors"}')
    keyboard.add(ally_spin_instructors_button)
  if 'Ally (Pilates)' in query_data.studios:
    ally_pilates_instructors_button = telebot.types.InlineKeyboardButton('Enter Ally (Pilates) Instructor(s)', callback_data='{"step": "ally-pilates-instructors"}')
    keyboard.add(ally_pilates_instructors_button)

  show_instructors_button = telebot.types.InlineKeyboardButton('Show Names of Instructors', callback_data='{"step": "show-instructors"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "main-page-handler"}')
  keyboard.add(show_instructors_button)
  keyboard.add(next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def update_cached_result_data() -> None:
  def _get_absolute_schedule(mutex, updated_cached_result_data):
    global ABSOLUTE_INSTRUCTORID_MAP, ABSOLUTE_INSTRUCTOR_NAMES
    ABSOLUTE_INSTRUCTORID_MAP = get_absolute_instructorid_map()
    ABSOLUTE_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(ABSOLUTE_INSTRUCTORID_MAP)]
    absolute_schedule = get_absolute_schedule(locations=[StudioLocation.All], weeks=2, days=['All'], instructors=['All'], instructorid_map=ABSOLUTE_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += absolute_schedule


  def _get_ally_schedule(mutex, updated_cached_result_data):
    global ALLY_INSTRUCTORID_MAP, ALLY_INSTRUCTOR_NAMES
    ALLY_INSTRUCTORID_MAP = get_ally_instructorid_map()
    ALLY_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(ALLY_INSTRUCTORID_MAP)]
    ally_schedule = get_ally_schedule(weeks=2, days=['All'], instructors=['All'], instructorid_map=ALLY_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += ally_schedule

  def _get_barrys_schedule(mutex, updated_cached_result_data):
    global BARRYS_INSTRUCTORID_MAP, BARRYS_INSTRUCTOR_NAMES
    BARRYS_INSTRUCTORID_MAP = get_barrys_instructorid_map()
    BARRYS_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(BARRYS_INSTRUCTORID_MAP)]
    barrys_schedule = get_barrys_schedule(locations=[StudioLocation.All], weeks=3, days=['All'], instructors=['All'], instructorid_map=BARRYS_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += barrys_schedule

  def _get_rev_schedule(mutex, updated_cached_result_data):
    global REV_INSTRUCTORID_MAP, REV_INSTRUCTOR_NAMES
    REV_INSTRUCTORID_MAP = get_rev_instructorid_map()
    REV_INSTRUCTOR_NAMES = [instructor.lower() for instructor in list(REV_INSTRUCTORID_MAP)]
    rev_schedule = get_rev_schedule(locations=[StudioLocation.All], start_date='', end_date='', days=['All'], instructorid_map=REV_INSTRUCTORID_MAP)
    with mutex:
      updated_cached_result_data += rev_schedule

  LOGGER.info('Updating cached result data...')
  updated_cached_result_data = ResultData()
  mutex = threading.Lock()
  absolute_thread = threading.Thread(target=_get_absolute_schedule, name='absolute_thread', args=(mutex, updated_cached_result_data,))
  ally_thread = threading.Thread(target=_get_ally_schedule, name='ally_thread', args=(mutex, updated_cached_result_data,))
  barrys_thread = threading.Thread(target=_get_barrys_schedule, name='barrys_thread', args=(mutex, updated_cached_result_data,))
  rev_thread = threading.Thread(target=_get_rev_schedule, name='rev_thread', args=(mutex, updated_cached_result_data,))

  absolute_thread.start()
  ally_thread.start()
  barrys_thread.start()
  rev_thread.start()
  absolute_thread.join()
  ally_thread.join()
  barrys_thread.join()
  rev_thread.join()

  global CACHED_RESULT_DATA
  CACHED_RESULT_DATA = updated_cached_result_data
  LOGGER.info('Successfully updated cached result data!')

def schedule_update_cached_result_data(stop_event) -> None:
  schedule.every().day.at('00:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('06:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('12:00', 'Asia/Singapore').do(update_cached_result_data)
  schedule.every().day.at('18:00', 'Asia/Singapore').do(update_cached_result_data)
  while not stop_event.is_set():
    schedule.run_pending()
    time.sleep(1)

if __name__ =="__main__":
  stop_event = threading.Event()
  update_schedule_thread = threading.Thread(target=schedule_update_cached_result_data, args=[stop_event])
  update_schedule_thread.start()

  LOGGER.info('Starting bot...')
  update_cached_result_data()
  LOGGER.info('Bot started!')

  BOT.infinity_polling()

  stop_event.set()
  update_schedule_thread.join()