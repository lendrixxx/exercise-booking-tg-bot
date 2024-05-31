import absolute
import ally
import barrys
import os
import rev
import telebot
import schedule
from absolute.absolute import get_absolute_schedule
from absolute.data import PILATES_INSTRUCTOR_NAMES as ABSOLUTE_PILATES_INSTRUCTOR_NAMES
from absolute.data import SPIN_INSTRUCTOR_NAMES as ABSOLUTE_SPIN_INSTRUCTOR_NAMES
from ally.ally import get_ally_schedule
from ally.data import PILATES_INSTRUCTOR_NAMES as ALLY_PILATES_INSTRUCTOR_NAMES
from ally.data import SPIN_INSTRUCTOR_NAMES as ALLY_SPIN_INSTRUCTOR_NAMES
from barrys.barrys import get_barrys_schedule
from barrys.data import INSTRUCTOR_NAMES as BARRYS_INSTRUCTOR_NAMES
from common.bot_utils import get_default_days_buttons_map, get_default_studios_locations_buttons_map
from common.data_types import QueryData, ResultData, SORTED_DAYS, StudioData, StudioLocation, STUDIO_LOCATIONS_MAP, StudioType
from copy import copy
from rev.data import INSTRUCTOR_NAMES as REV_INSTRUCTOR_NAMES
from rev.rev import get_rev_schedule

# Global variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT = telebot.TeleBot(BOT_TOKEN)
START_COMMAND = telebot.types.BotCommand(command='start', description='Check schedules')
NERD_COMMAND = telebot.types.BotCommand(command='nerd', description='Nerd mode')
INSTRUCTORS_COMMAND = telebot.types.BotCommand(command='instructors', description='Show list of instructors')
BOT.set_my_commands([START_COMMAND, NERD_COMMAND, INSTRUCTORS_COMMAND])

CURRENT_QUERY_DATA = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])
CACHED_RESULT_DATA = ResultData()

# Locations buttons
LOCATIONS_SELECTION_MESSAGE = None
LOCATIONS_SELECT_ALL_BUTTON = telebot.types.InlineKeyboardButton('Select All', callback_data='{"locations": "All", "step": "locations"}')
LOCATIONS_UNSELECT_ALL_BUTTON = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"locations": "Null", "step": "locations"}')
LOCATIONS_SELECT_MORE_STUDIOS_BUTTON = telebot.types.InlineKeyboardButton('◀️ Select More', callback_data='{"step": "locations-select-more-studios"}')
LOCATIONS_NEXT_BUTTON = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "studios-next"}')

# Locations buttons map
STUDIOS_LOCATIONS_BUTTONS_MAP = get_default_studios_locations_buttons_map()

# Days buttons
DAYS_SELECTION_MESSAGE = None
DAYS_SELECT_ALL_BUTTON = telebot.types.InlineKeyboardButton('Select All', callback_data='{"days": "All", "step": "days"}')
DAYS_UNSELECT_ALL_BUTTON = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"days": "None", "step": "days"}')
DAYS_BACK_BUTTON = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "days-back"}')
DAYS_NEXT_BUTTON = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "days-next"}')

# Days buttons map
DAYS_BUTTONS_MAP = get_default_days_buttons_map()

def get_locations_keyboard() -> telebot.types.InlineKeyboardMarkup:
  global CURRENT_QUERY_DATA
  locations_keyboard = telebot.types.InlineKeyboardMarkup()
  if CURRENT_QUERY_DATA.current_studio == 'Rev':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Rev']['Bugis'], STUDIOS_LOCATIONS_BUTTONS_MAP['Rev']['Orchard'])
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Rev']['Suntec'], STUDIOS_LOCATIONS_BUTTONS_MAP['Rev']['TJPG'])
  elif CURRENT_QUERY_DATA.current_studio == 'Barrys':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Barrys']['Orchard'], STUDIOS_LOCATIONS_BUTTONS_MAP['Barrys']['Raffles'])
  elif CURRENT_QUERY_DATA.current_studio == 'Absolute (Spin)':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Spin)']['Centrepoint'], STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Spin)']['i12'])
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Spin)']['Star Vista'], STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Spin)']['Raffles'])
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Spin)']['Millenia Walk'])
  elif CURRENT_QUERY_DATA.current_studio == 'Absolute (Pilates)':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Pilates)']['Centrepoint'], STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Pilates)']['i12'])
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Pilates)']['Star Vista'], STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Pilates)']['Raffles'])
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Absolute (Pilates)']['Great World'])
  elif CURRENT_QUERY_DATA.current_studio == 'Ally (Spin)':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Ally (Spin)']['Cross Street'])
  elif CURRENT_QUERY_DATA.current_studio == 'Ally (Pilates)':
    locations_keyboard.add(STUDIOS_LOCATIONS_BUTTONS_MAP['Ally (Pilates)']['Cross Street'])
  locations_keyboard.add(LOCATIONS_SELECT_ALL_BUTTON, LOCATIONS_UNSELECT_ALL_BUTTON)
  locations_keyboard.add(LOCATIONS_SELECT_MORE_STUDIOS_BUTTON, LOCATIONS_NEXT_BUTTON)
  return locations_keyboard

def get_days_keyboard() -> telebot.types.InlineKeyboardMarkup:
  global CURRENT_QUERY_DATA
  days_keyboard = telebot.types.InlineKeyboardMarkup()
  days_keyboard.add(DAYS_BUTTONS_MAP['Monday'], DAYS_BUTTONS_MAP['Tuesday'])
  days_keyboard.add(DAYS_BUTTONS_MAP['Wednesday'], DAYS_BUTTONS_MAP['Thursday'])
  days_keyboard.add(DAYS_BUTTONS_MAP['Friday'], DAYS_BUTTONS_MAP['Saturday'])
  days_keyboard.add(DAYS_BUTTONS_MAP['Sunday'])
  days_keyboard.add(DAYS_SELECT_ALL_BUTTON, DAYS_UNSELECT_ALL_BUTTON)
  days_keyboard.add(DAYS_BACK_BUTTON, DAYS_NEXT_BUTTON)
  return days_keyboard

def send_results(query: telebot.types.CallbackQuery) -> None:
  global CACHED_RESULT_DATA, CURRENT_QUERY_DATA
  result = CACHED_RESULT_DATA.get_data(CURRENT_QUERY_DATA)
  CURRENT_QUERY_DATA = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])

  # Send string as messages
  schedule_str = result.get_result_str()
  if len(schedule_str) > 4095:
    shortened_message = ''
    for line in schedule_str.splitlines():
      is_new_day = any(day in line for day in SORTED_DAYS) and len(shortened_message) > 0
      max_len_reached = len(shortened_message) + len(line) > 4095
      if is_new_day or max_len_reached:
        BOT.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
        shortened_message = line + '\n'
      else:
        shortened_message += line + '\n'

    if len(shortened_message) > 0:
      BOT.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
  else:
    BOT.send_message(query.message.chat.id, schedule_str, parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios')
def studios_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  query_data_dict = eval(query.data)
  studios_selected = query_data_dict['studios']
  if studios_selected == 'All':
    CURRENT_QUERY_DATA.studios = {
      'Rev': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Rev]),
      'Barrys': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Barrys]),
      'Absolute (Spin)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsoluteSpin]),
      'Absolute (Pilates)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsolutePilates]),
      'Ally (Spin)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllySpin]),
      'Ally (Pilates)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyPilates]),
    }
    studios_handler(query.message)
  elif studios_selected == 'None':
    CURRENT_QUERY_DATA.studios = {}
    studios_handler(query.message)
  else:
    CURRENT_QUERY_DATA.current_studio = studios_selected
    locations_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations')
def locations_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA, STUDIOS_LOCATIONS_BUTTONS_MAP
  query_data_dict = eval(query.data)
  selected_studio_location = StudioLocation[query_data_dict['locations']]
  if selected_studio_location == StudioLocation.Null:
    for location in STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio]:
      STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][location] = telebot.types.InlineKeyboardButton(location, callback_data=STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][location].callback_data)
    CURRENT_QUERY_DATA.studios.pop(CURRENT_QUERY_DATA.current_studio)
  elif selected_studio_location == StudioLocation.All:
    for location in STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio]:
      STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][location] = telebot.types.InlineKeyboardButton(location + ' ✅', callback_data=STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][location].callback_data)
    if CURRENT_QUERY_DATA.current_studio not in CURRENT_QUERY_DATA.studios:
      new_studio = {CURRENT_QUERY_DATA.current_studio: StudioData(locations=copy(STUDIO_LOCATIONS_MAP[CURRENT_QUERY_DATA.current_studio]))}
      CURRENT_QUERY_DATA.studios = {**CURRENT_QUERY_DATA.studios, **new_studio}
    else:
      CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].locations = copy(STUDIO_LOCATIONS_MAP[CURRENT_QUERY_DATA.current_studio])
  else:
    if CURRENT_QUERY_DATA.current_studio not in CURRENT_QUERY_DATA.studios:
      STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location + ' ✅',
          callback_data=STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location].callback_data)
      new_studio = {CURRENT_QUERY_DATA.current_studio: StudioData(locations=[selected_studio_location])}
      CURRENT_QUERY_DATA.studios = {**CURRENT_QUERY_DATA.studios, **new_studio}
    elif selected_studio_location in CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].locations:
      STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location,
          callback_data=STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location].callback_data)
      CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].locations.remove(selected_studio_location)
      if len(CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].locations) == 0:
        CURRENT_QUERY_DATA.studios.pop(CURRENT_QUERY_DATA.current_studio)
    else:
      STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location] = telebot.types.InlineKeyboardButton(selected_studio_location + ' ✅', callback_data=STUDIOS_LOCATIONS_BUTTONS_MAP[CURRENT_QUERY_DATA.current_studio][selected_studio_location].callback_data)
      CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].locations.append(selected_studio_location)

  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True)
  text += '*Select the location(s) to check*'

  global LOCATIONS_SELECTION_MESSAGE
  BOT.edit_message_text(
    chat_id=LOCATIONS_SELECTION_MESSAGE.chat.id,
    message_id=LOCATIONS_SELECTION_MESSAGE.id,
    text=text,
    reply_markup=get_locations_keyboard(),
    parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations-select-more-studios')
def locations_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  studios_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios-next')
def studios_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  if len(CURRENT_QUERY_DATA.studios) == 0:
    text = 'Please select a studio'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    studios_handler(query.message)
  else:
    instructors_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks')
def weeks_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  query_data_dict = eval(query.data)
  CURRENT_QUERY_DATA.weeks = query_data_dict['weeks']
  days_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks-back')
def weeks_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  instructors_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days')
def days_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  query_data_dict = eval(query.data)
  selected_day = query_data_dict['days']
  if selected_day == 'None':
    for day in DAYS_BUTTONS_MAP:
      DAYS_BUTTONS_MAP[day] = telebot.types.InlineKeyboardButton(day, callback_data=DAYS_BUTTONS_MAP[day].callback_data)
    CURRENT_QUERY_DATA.days = []
  elif selected_day == 'All':
    for day in DAYS_BUTTONS_MAP:
      DAYS_BUTTONS_MAP[day] = telebot.types.InlineKeyboardButton(day + ' ✅', callback_data=DAYS_BUTTONS_MAP[day].callback_data)
    CURRENT_QUERY_DATA.days = SORTED_DAYS
  else:
    if selected_day in CURRENT_QUERY_DATA.days:
      DAYS_BUTTONS_MAP[selected_day] = telebot.types.InlineKeyboardButton(selected_day, callback_data=DAYS_BUTTONS_MAP[selected_day].callback_data)
      CURRENT_QUERY_DATA.days.remove(selected_day)
    else:
      DAYS_BUTTONS_MAP[selected_day] = telebot.types.InlineKeyboardButton(selected_day + ' ✅', callback_data=DAYS_BUTTONS_MAP[selected_day].callback_data)
      CURRENT_QUERY_DATA.days.append(selected_day)
      CURRENT_QUERY_DATA.days = sorted(CURRENT_QUERY_DATA.days, key=SORTED_DAYS.index)

  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True)
  text += '*Select the day(s) to show classes of*'

  global DAYS_SELECTION_MESSAGE
  BOT.edit_message_text(
    chat_id=DAYS_SELECTION_MESSAGE.chat.id,
    message_id=DAYS_SELECTION_MESSAGE.id,
    text=text,
    reply_markup=get_days_keyboard(),
    parse_mode='Markdown')

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-back')
def days_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  weeks_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-next')
def days_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  if len(CURRENT_QUERY_DATA.days) == 0:
    text = 'Please select a day'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    days_handler(query.message)
    return

  send_results(query)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'rev-instructors')
def rev_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *chloe*, *jerlyn*, *zai*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Rev'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, rev.data.INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'barrys-instructors')
def barrys_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *ria*, *gino*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Barrys'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, barrys.data.INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-spin-instructors')
def absolute_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *chin*, *ria*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Absolute (Spin)'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.SPIN_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-pilates-instructors')
def absolute_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *daniella*, *vnex*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Absolute (Pilates)'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.PILATES_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-spin-instructors')
def ally_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *samuel*, *jasper*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Ally (Spin)'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, ally.data.SPIN_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-pilates-instructors')
def ally_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = 'Enter instructor names separated by a comma\ne.g.: *candice*, *ruth*\nEnter "*all*" to check for all instructors'
  CURRENT_QUERY_DATA.current_studio = 'Ally (Pilates)'
  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, instructors_input_handler, ally.data.PILATES_INSTRUCTORID_MAP)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'show-instructors')
def show_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA
  text = ''
  if 'Rev' in CURRENT_QUERY_DATA.studios:
    text += '*Rev Instructors:* ' + ', '.join(rev.data.INSTRUCTOR_NAMES) + '\n\n'
  if 'Barrys' in CURRENT_QUERY_DATA.studios:
    text += '*Barrys Instructors:* ' + ', '.join(barrys.data.INSTRUCTOR_NAMES) + '\n\n'
  if 'Absolute (Spin)' in CURRENT_QUERY_DATA.studios:
    text += '*Absolute (Spin) Instructors:* ' + ', '.join(absolute.data.SPIN_INSTRUCTOR_NAMES) + '\n\n'
  if 'Absolute (Pilates)' in CURRENT_QUERY_DATA.studios:
    text += '*Absolute (Pilates) Instructors:* ' + ', '.join(absolute.data.PILATES_INSTRUCTOR_NAMES) + '\n\n'
  if 'Ally (Spin)' in CURRENT_QUERY_DATA.studios:
    text += '*Ally (Spin) Instructors:* ' + ', '.join(ally.data.SPIN_INSTRUCTOR_NAMES) + '\n\n'
  if 'Ally (Pilates)' in CURRENT_QUERY_DATA.studios:
    text += '*Ally (Pilates) Instructors:* ' + ', '.join(ally.data.PILATES_INSTRUCTOR_NAMES) + '\n\n'

  sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  instructors_handler(query.message)

def instructors_input_handler(message: telebot.types.Message, instructorid_map: dict[str, int]) -> None:
  global CURRENT_QUERY_DATA
  CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors = [x.strip() for x in message.text.lower().split(',')]
  if 'all' in CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors:
    CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors = ['All']
  else:
    invalid_instructors = []
    for instructor in CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors:
      instructor_in_map = (any(instructor in instructor_in_map.split(' ') for instructor_in_map in instructorid_map)
        or any(instructor == instructor_in_map for instructor_in_map in instructorid_map))
      if not instructor_in_map:
        invalid_instructors.append(instructor)

    if len(invalid_instructors) > 0:
      CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors = [
        instructor for instructor
        in CURRENT_QUERY_DATA.studios[CURRENT_QUERY_DATA.current_studio].instructors
        if instructor not in invalid_instructors
      ]
      text = f'Failed to find instructor(s): {", ".join(invalid_instructors)}'
      sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

  instructors_handler(message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-next')
def instructors_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global CURRENT_QUERY_DATA, CACHED_RESULT_DATA
  if not CURRENT_QUERY_DATA.has_instructors_selected():
    text = 'Please select at least one instructor'
    sent_msg = BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
    instructors_handler(query.message)
  else:
    weeks_handler(query.message)

@BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-back')
def instructors_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  studios_handler(query.message)

@BOT.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA, STUDIOS_LOCATIONS_BUTTONS_MAP
  CURRENT_QUERY_DATA = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])
  STUDIOS_LOCATIONS_BUTTONS_MAP = get_default_studios_locations_buttons_map()
  DAYS_BUTTONS_MAP = get_default_days_buttons_map()
  studios_handler(message)

def studios_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA
  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True)
  text += '*Select the studio(s) to check*'

  rev_button = telebot.types.InlineKeyboardButton('Rev', callback_data='{"studios": "Rev", "step": "studios"}')
  barrys_button = telebot.types.InlineKeyboardButton('Barrys', callback_data='{"studios": "Barrys", "step": "studios"}')
  absolute_spin_button = telebot.types.InlineKeyboardButton('Absolute (Spin)', callback_data='{"studios": "Absolute (Spin)", "step": "studios"}')
  absolute_pilates_button = telebot.types.InlineKeyboardButton('Absolute (Pilates)', callback_data='{"studios": "Absolute (Pilates)", "step": "studios"}')
  ally_spin_button = telebot.types.InlineKeyboardButton('Ally (Spin)', callback_data='{"studios": "Ally (Spin)", "step": "studios"}')
  ally_pilates_button = telebot.types.InlineKeyboardButton('Ally (Pilates)', callback_data='{"studios": "Ally (Pilates)", "step": "studios"}')
  select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"studios": "All", "step": "studios"}')
  unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"studios": "None", "step": "studios"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "studios-next"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(rev_button, barrys_button)
  keyboard.add(absolute_spin_button, absolute_pilates_button)
  keyboard.add(ally_spin_button, ally_pilates_button)
  keyboard.add(select_all_button, unselect_all_button)
  keyboard.add(next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')


@BOT.message_handler(commands=['instructors'])
def instructors_list_handler(message: telebot.types.Message) -> None:
  text = '*Rev Instructors:* ' + ', '.join(rev.data.INSTRUCTOR_NAMES) + '\n\n'
  text += '*Barrys Instructors:* ' + ', '.join(barrys.data.INSTRUCTOR_NAMES) + '\n\n'
  text += '*Absolute (Spin) Instructors:* ' + ', '.join(absolute.data.SPIN_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Absolute (Pilates) Instructors:* ' + ', '.join(absolute.data.PILATES_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Ally (Spin) Instructors:* ' + ', '.join(ally.data.SPIN_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Ally (Pilates) Instructors:* ' + ', '.join(ally.data.PILATES_INSTRUCTOR_NAMES) + '\n\n'
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
         "\n" \
         "*Studio names*: rev, barrys, absolute (spin), absolute (pilates), ally (spin), ally (pilates)\n" \
         "*Studio locations*: orchard, tjpg, bugis, suntec, raffles, centrepoint, i12, millenia walk, star vista, great world\n" \
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
         "monday, wednesday, saturday\n"

  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
  BOT.register_next_step_handler(sent_msg, nerd_input_handler)

def nerd_input_handler(message: telebot.types.Message) -> None:
  '''
  Expected message format:
  /nerd
  Studio name
  Comma separated studio locations
  Comma separated instructor names
  Studio name (If selecting multiple studios)
  Comma separated studio locations (If selecting multiple studios)
  Comma separated instructor names (If selecting multiple studios)
  Weeks
  Days

  e.g.
  /nerd
  rev
  bugis, orchard
  chloe, zai
  absolute (spin)
  raffles
  ria
  2
  monday, wednesday, saturday
  '''
  input_str_list = message.text.splitlines()

  # Weeks and days = 2 items. Remaining items should be divisible by 3 (studio name, locations, instructors)
  if (len(input_str_list) - 2) % 3 != 0:
    BOT.send_message(message.chat.id, 'Failed to handle query. Unexpected format received.', parse_mode='Markdown')
    return

  # Loop through studios
  query = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])
  current_studio = StudioType.Null
  current_studio_locations = []
  for index, input_str in enumerate(input_str_list[:-2]):
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
      elif current_studio == StudioType.AbsolutePilates:
        instructor_list = ABSOLUTE_PILATES_INSTRUCTOR_NAMES
      elif current_studio == StudioType.AbsoluteSpin:
        instructor_list = ABSOLUTE_SPIN_INSTRUCTOR_NAMES
      elif current_studio == StudioType.AllyPilates:
        instructor_list = ALLY_PILATES_INSTRUCTOR_NAMES
      elif current_studio == StudioType.AllySpin:
        instructor_list = ALLY_SPIN_INSTRUCTOR_NAMES

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
        text = f'Failed to find instructor(s): {", ".join(invalid_instructors)}'
        sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

      if len(selected_instructors) == 0:
        BOT.send_message(message.chat.id, f'Failed to handle query. No instructor selected for {current_studio}', parse_mode='Markdown')
        return

      query.studios[current_studio] = StudioData(locations=current_studio_locations, instructors = selected_instructors)

  # Get number of weeks
  try:
    query.weeks = int(input_str_list[-2])
  except:
    BOT.send_message(message.chat.id, f'Failed to handle query. Invalid input for \'weeks\'. Expected number, got {input_str_list[-2]}', parse_mode='Markdown')
    return

  # Get list of days
  query.days = [x.strip().capitalize() for x in input_str_list[-1].split(',')]
  if 'All' in query.days:
    query.days = ['All']
  else:
    for selected_day in query.days:
      if selected_day.capitalize() not in SORTED_DAYS:
        BOT.send_message(message.chat.id, f'Failed to handle query. Invalid input for \'days\'. Unknown day {selected_day}', parse_mode='Markdown')
        return

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


@BOT.message_handler(commands=['refresh'])
def refresh_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA
  text = 'Updating cached schedules...'
  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')
  update_cached_result_data()
  text = 'Finished updating schedules'
  sent_msg = BOT.send_message(message.chat.id, text, parse_mode='Markdown')

def locations_handler(message: telebot.types.Message):
  global CURRENT_QUERY_DATA
  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True)
  text += '*Select the location(s) to check*'

  global LOCATIONS_SELECTION_MESSAGE
  LOCATIONS_SELECTION_MESSAGE = BOT.send_message(message.chat.id, text, reply_markup=get_locations_keyboard(), parse_mode='Markdown')

def weeks_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA
  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True, include_instructors=True, include_weeks=True)
  text += '*Select the number of weeks of classes to show*\n'
  text += 'Absolute shows up to 1.5 weeks\nAlly shows up to 2 weeks\nBarrys shows up to 3 weeks\nRev shows up to 4 weeks\n'

  one_button = telebot.types.InlineKeyboardButton('1', callback_data='{"weeks": 1, "step": "weeks"}')
  two_button = telebot.types.InlineKeyboardButton('2', callback_data='{"weeks": 2, "step": "weeks"}')
  three_button = telebot.types.InlineKeyboardButton('3', callback_data='{"weeks": 3, "step": "weeks"}')
  four_button = telebot.types.InlineKeyboardButton('4', callback_data='{"weeks": 4, "step": "weeks"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "weeks-back"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(one_button, two_button)
  keyboard.add(three_button, four_button)
  keyboard.add(back_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def days_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA, DAYS_BUTTONS_MAP
  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True)
  text += '*Select the day(s) to show classes of*'
  DAYS_BUTTONS_MAP = get_default_days_buttons_map()

  global DAYS_SELECTION_MESSAGE
  DAYS_SELECTION_MESSAGE = BOT.send_message(message.chat.id, text, reply_markup=get_days_keyboard(), parse_mode='Markdown')

def instructors_handler(message: telebot.types.Message) -> None:
  global CURRENT_QUERY_DATA
  text = CURRENT_QUERY_DATA.get_query_str(include_studio=True, include_instructors=True)
  text += '*Select the studio to choose instructors*'

  keyboard = telebot.types.InlineKeyboardMarkup()
  if 'Rev' in CURRENT_QUERY_DATA.studios:
    rev_instructors_button = telebot.types.InlineKeyboardButton('Enter Rev Instructor(s)', callback_data='{"step": "rev-instructors"}')
    keyboard.add(rev_instructors_button)
  if 'Barrys' in CURRENT_QUERY_DATA.studios:
    barrys_instructors_button = telebot.types.InlineKeyboardButton('Enter Barrys Instructor(s)', callback_data='{"step": "barrys-instructors"}')
    keyboard.add(barrys_instructors_button)
  if 'Absolute (Spin)' in CURRENT_QUERY_DATA.studios:
    absolute_spin_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Spin) Instructor(s)', callback_data='{"step": "absolute-spin-instructors"}')
    keyboard.add(absolute_spin_instructors_button)
  if 'Absolute (Pilates)' in CURRENT_QUERY_DATA.studios:
    absolute_pilates_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Pilates) Instructor(s)', callback_data='{"step": "absolute-pilates-instructors"}')
    keyboard.add(absolute_pilates_instructors_button)
  if 'Ally (Spin)' in CURRENT_QUERY_DATA.studios:
    ally_spin_instructors_button = telebot.types.InlineKeyboardButton('Enter Ally (Spin) Instructor(s)', callback_data='{"step": "ally-spin-instructors"}')
    keyboard.add(ally_spin_instructors_button)
  if 'Ally (Pilates)' in CURRENT_QUERY_DATA.studios:
    ally_pilates_instructors_button = telebot.types.InlineKeyboardButton('Enter Ally (Pilates) Instructor(s)', callback_data='{"step": "ally-pilates-instructors"}')
    keyboard.add(ally_pilates_instructors_button)

  show_instructors_button = telebot.types.InlineKeyboardButton('Show Names of Instructors', callback_data='{"step": "show-instructors"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "instructors-next"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "instructors-back"}')
  keyboard.add(show_instructors_button)
  keyboard.add(back_button, next_button)
  sent_msg = BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def update_cached_result_data() -> None:
  global CACHED_RESULT_DATA
  CACHED_RESULT_DATA = get_absolute_schedule(locations=[StudioLocation.All], weeks=2, days=['All'], instructors=['All'])
  CACHED_RESULT_DATA += get_ally_schedule(weeks=2, days=['All'], instructors=['All'])
  CACHED_RESULT_DATA += get_barrys_schedule(locations=[StudioLocation.All], weeks=3, days=['All'], instructors=['All'])
  CACHED_RESULT_DATA += get_rev_schedule(locations=[StudioLocation.All], weeks=4, days=['All'], instructors=['All'])

print('Starting bot...')
update_cached_result_data()
schedule.every().day.at("00:00").do(update_cached_result_data)
print('Bot started!')

BOT.infinity_polling()