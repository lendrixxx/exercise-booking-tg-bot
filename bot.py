import absolute
import barrys
import os
import rev
import telebot
from absolute.absolute import get_absolute_schedule
from common.bot_utils import get_default_days_buttons_map, get_default_studios_locations_buttons_map
from common.data_types import query_data, result_data, sorted_days, studio_data, studio_location, studio_locations_map, studio_type
from copy import copy
from barrys.barrys import get_barrys_schedule
from rev.rev import get_rev_schedule

# Global variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
start_command = telebot.types.BotCommand(command='start', description='Check schedules')
bot.set_my_commands([start_command])

current_query_data = query_data(studios={}, current_studio=studio_type.Null, weeks=0, days=[])
cached_result_data = result_data()

# Locations buttons
locations_selection_message = None
locations_select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"locations": "All", "step": "locations"}')
locations_unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"locations": "Null", "step": "locations"}')
locations_select_more_studios_button = telebot.types.InlineKeyboardButton('◀️ Select More', callback_data='{"step": "locations-select-more-studios"}')
locations_next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "studios-next"}')

# Locations buttons map
studios_locations_buttons_map = get_default_studios_locations_buttons_map()

# Days buttons
days_selection_message = None
days_select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"days": "All", "step": "days"}')
days_unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"days": "None", "step": "days"}')
days_back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "days-back"}')
days_next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "days-next"}')

# Days buttons map
days_buttons_map = get_default_days_buttons_map()

def get_locations_keyboard() -> telebot.types.InlineKeyboardMarkup:
  global current_query_data
  locations_keyboard = telebot.types.InlineKeyboardMarkup()
  if current_query_data.current_studio == 'Rev':
    locations_keyboard.add(studios_locations_buttons_map['Rev']['Bugis'], studios_locations_buttons_map['Rev']['Orchard'])
    locations_keyboard.add(studios_locations_buttons_map['Rev']['Suntec'], studios_locations_buttons_map['Rev']['TJPG'])
  elif current_query_data.current_studio == 'Barrys':
    locations_keyboard.add(studios_locations_buttons_map['Barrys']['Orchard'], studios_locations_buttons_map['Barrys']['Raffles'])
  elif current_query_data.current_studio == 'Absolute (Spin)':
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Spin)']['Centrepoint'], studios_locations_buttons_map['Absolute (Spin)']['i12'])
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Spin)']['Star Vista'], studios_locations_buttons_map['Absolute (Spin)']['Raffles'])
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Spin)']['Millenia Walk'])
  elif current_query_data.current_studio == 'Absolute (Pilates)':
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Pilates)']['Centrepoint'], studios_locations_buttons_map['Absolute (Pilates)']['i12'])
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Pilates)']['Star Vista'], studios_locations_buttons_map['Absolute (Pilates)']['Raffles'])
    locations_keyboard.add(studios_locations_buttons_map['Absolute (Pilates)']['Great World'])
  locations_keyboard.add(locations_select_all_button, locations_unselect_all_button)
  locations_keyboard.add(locations_select_more_studios_button, locations_next_button)
  return locations_keyboard

def get_days_keyboard() -> telebot.types.InlineKeyboardMarkup:
  global current_query_data
  days_keyboard = telebot.types.InlineKeyboardMarkup()
  days_keyboard.add(days_buttons_map['Monday'], days_buttons_map['Tuesday'])
  days_keyboard.add(days_buttons_map['Wednesday'], days_buttons_map['Thursday'])
  days_keyboard.add(days_buttons_map['Friday'], days_buttons_map['Saturday'])
  days_keyboard.add(days_buttons_map['Sunday'])
  days_keyboard.add(days_select_all_button, days_unselect_all_button)
  days_keyboard.add(days_back_button, days_next_button)
  return days_keyboard

def send_results(query: telebot.types.CallbackQuery) -> None:
  global cached_result_data, current_query_data
  result = cached_result_data.get_data(current_query_data)
  current_query_data = query_data(studios={}, current_studio=studio_type.Null, weeks=0, days=[])

  # Send string as messages
  schedule_str = result.get_result_str()
  if len(schedule_str) > 4095:
    shortened_message = ''
    for line in schedule_str.split('\n'):
      is_new_day = any(day in line for day in sorted_days) and len(shortened_message) > 0
      max_len_reached = len(shortened_message) + len(line) > 4095
      if is_new_day or max_len_reached:
        bot.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
        shortened_message = line + '\n'
      else:
        shortened_message += line + '\n'

    if len(shortened_message) > 0:
      bot.send_message(query.message.chat.id, shortened_message, parse_mode='Markdown')
  else:
    bot.send_message(query.message.chat.id, schedule_str, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios')
def studios_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  query_data_dict = eval(query.data)
  studios_selected = query_data_dict['studios']
  if studios_selected == 'All':
    current_query_data.studios = {
      'Rev': studio_data(locations=studio_locations_map[studio_type.Rev]),
      'Barrys': studio_data(locations=studio_locations_map[studio_type.Barrys]),
      'Absolute (Spin)': studio_data(locations=studio_locations_map[studio_type.AbsoluteSpin]),
      'Absolute (Pilates)': studio_data(locations=studio_locations_map[studio_type.AbsolutePilates]),
    }
    studios_handler(query.message)
  elif studios_selected == 'None':
    current_query_data.studios = {}
    studios_handler(query.message)
  else:
    current_query_data.current_studio = studios_selected
    locations_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations')
def locations_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data, studios_locations_buttons_map
  query_data_dict = eval(query.data)
  selected_studio_location = studio_location[query_data_dict['locations']]
  if selected_studio_location == studio_location.Null:
    for location in studios_locations_buttons_map[current_query_data.current_studio]:
      studios_locations_buttons_map[current_query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location, callback_data=studios_locations_buttons_map[current_query_data.current_studio][location].callback_data)
    current_query_data.studios.pop(current_query_data.current_studio)
  elif selected_studio_location == studio_location.All:
    for location in studios_locations_buttons_map[current_query_data.current_studio]:
      studios_locations_buttons_map[current_query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location + ' ✅', callback_data=studios_locations_buttons_map[current_query_data.current_studio][location].callback_data)
    if current_query_data.current_studio not in current_query_data.studios:
      new_studio = {current_query_data.current_studio: studio_data(locations=copy(studio_locations_map[current_query_data.current_studio]))}
      current_query_data.studios = {**current_query_data.studios, **new_studio}
    else:
      current_query_data.studios[current_query_data.current_studio].locations = copy(studio_locations_map[current_query_data.current_studio])
  else:
    if current_query_data.current_studio not in current_query_data.studios:
      studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location + ' ✅',
          callback_data=studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location].callback_data)
      new_studio = {current_query_data.current_studio: studio_data(locations=[selected_studio_location])}
      current_query_data.studios = {**current_query_data.studios, **new_studio}
    elif selected_studio_location in current_query_data.studios[current_query_data.current_studio].locations:
      studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location,
          callback_data=studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location].callback_data)
      current_query_data.studios[current_query_data.current_studio].locations.remove(selected_studio_location)
      if len(current_query_data.studios[current_query_data.current_studio].locations) == 0:
        current_query_data.studios.pop(current_query_data.current_studio)
    else:
      studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location] = telebot.types.InlineKeyboardButton(selected_studio_location + ' ✅', callback_data=studios_locations_buttons_map[current_query_data.current_studio][selected_studio_location].callback_data)
      current_query_data.studios[current_query_data.current_studio].locations.append(selected_studio_location)

  text = current_query_data.get_query_str(include_studio=True)
  text += '*Select the location(s) to check*'

  global locations_selection_message
  bot.edit_message_text(
    chat_id=locations_selection_message.chat.id,
    message_id=locations_selection_message.id,
    text=text,
    reply_markup=get_locations_keyboard(),
    parse_mode='Markdown')

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations-select-more-studios')
def locations_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  studios_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios-next')
def studios_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  if len(current_query_data.studios) == 0:
    text = 'Please select a studio'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    studios_handler(query.message)
  else:
    instructors_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks')
def weeks_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  query_data_dict = eval(query.data)
  current_query_data.weeks = query_data_dict['weeks']
  days_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks-back')
def weeks_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  studios_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days')
def days_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  query_data_dict = eval(query.data)
  selected_day = query_data_dict['days']
  if selected_day == 'None':
    for day in days_buttons_map:
      days_buttons_map[day] = telebot.types.InlineKeyboardButton(day, callback_data=days_buttons_map[day].callback_data)
    current_query_data.days = []
  elif selected_day == 'All':
    for day in days_buttons_map:
      days_buttons_map[day] = telebot.types.InlineKeyboardButton(day + ' ✅', callback_data=days_buttons_map[day].callback_data)
    current_query_data.days = sorted_days
  else:
    if selected_day in current_query_data.days:
      days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day, callback_data=days_buttons_map[selected_day].callback_data)
      current_query_data.days.remove(selected_day)
    else:
      days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day + ' ✅', callback_data=days_buttons_map[selected_day].callback_data)
      current_query_data.days.append(selected_day)
      current_query_data.days = sorted(current_query_data.days, key=sorted_days.index)

  text = current_query_data.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True)
  text += '*Select the day(s) to show classes of*'

  global days_selection_message
  bot.edit_message_text(
    chat_id=days_selection_message.chat.id,
    message_id=days_selection_message.id,
    text=text,
    reply_markup=get_days_keyboard(),
    parse_mode='Markdown')

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-back')
def days_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  weeks_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-next')
def days_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  if len(current_query_data.days) == 0:
    text = 'Please select a day'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    days_handler(query.message)
    return

  send_results(query)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'rev-instructors')
def rev_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  text = 'Enter instructor names separated by a comma\ne.g.: *chloe*, *jerlyn*, *zai*\nEnter "*all*" to check for all instructors'
  current_query_data.current_studio = 'Rev'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
  bot.register_next_step_handler(sent_msg, instructors_input_handler, rev.data.instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'barrys-instructors')
def barrys_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  text = 'Enter instructor names separated by a comma\ne.g.: *ria*, *gino*\nEnter "*all*" to check for all instructors'
  current_query_data.current_studio = 'Barrys'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
  bot.register_next_step_handler(sent_msg, instructors_input_handler, barrys.data.instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-spin-instructors')
def absolute_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  text = 'Enter instructor names separated by a comma\ne.g.: *chin*, *ria*\nEnter "*all*" to check for all instructors'
  current_query_data.current_studio = 'Absolute (Spin)'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
  bot.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.spin_instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-pilates-instructors')
def absolute_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  text = 'Enter instructor names separated by a comma\ne.g.: *daniella*, *vnex*\nEnter "*all*" to check for all instructors'
  current_query_data.current_studio = 'Absolute (Pilates)'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
  bot.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.pilates_instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'show-instructors')
def show_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data
  text = ''
  if 'Rev' in current_query_data.studios:
    text += '*Rev Instructors:* ' + ', '.join(rev.data.instructor_names) + '\n\n'
  if 'Barrys' in current_query_data.studios:
    text += '*Barrys Instructors:* ' + ', '.join(barrys.data.instructor_names) + '\n\n'
  if 'Absolute (Spin)' in current_query_data.studios:
    text += '*Absolute (Spin) Instructors:* ' + ', '.join(absolute.data.spin_instructor_names) + '\n\n'
  if 'Absolute (Pilates)' in current_query_data.studios:
    text += '*Absolute (Pilates) Instructors:* ' + ', '.join(absolute.data.pilates_instructor_names) + '\n\n'

  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
  instructors_handler(query.message)

def instructors_input_handler(message: telebot.types.Message, instructorid_map: dict[str, int]) -> None:
  global current_query_data
  current_query_data.studios[current_query_data.current_studio].instructors = [x.strip() for x in message.text.lower().split(",")]
  if 'all' in current_query_data.studios[current_query_data.current_studio].instructors:
    current_query_data.studios[current_query_data.current_studio].instructors = ['All']
  else:
    invalid_instructors = []
    for instructor in current_query_data.studios[current_query_data.current_studio].instructors:
      instructor_in_map = (any(instructor in instructor_in_map.split(' ') for instructor_in_map in instructorid_map)
        or any(instructor == instructor_in_map for instructor_in_map in instructorid_map))
      if not instructor_in_map:
        invalid_instructors.append(instructor)

    if len(invalid_instructors) > 0:
      current_query_data.studios[current_query_data.current_studio].instructors = [
        instructor for instructor
        in current_query_data.studios[current_query_data.current_studio].instructors
        if instructor not in invalid_instructors
      ]
      text = f'Failed to find instructors: {", ".join(invalid_instructors)}'
      sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')

  instructors_handler(message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-next')
def instructors_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  global current_query_data, cached_result_data
  if not current_query_data.has_instructors_selected():
    text = 'Please select at least one instructor'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    instructors_handler(query.message)
  else:
    weeks_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-back')
def instructors_back_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  days_handler(query.message)

@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message) -> None:
  global current_query_data, studios_locations_buttons_map
  current_query_data = query_data(studios={}, current_studio=studio_type.Null, weeks=0, days=[])
  studios_locations_buttons_map = get_default_studios_locations_buttons_map()
  days_buttons_map = get_default_days_buttons_map()
  studios_handler(message)

def studios_handler(message: telebot.types.Message) -> None:
  global current_query_data
  text = current_query_data.get_query_str(include_studio=True)
  text += '*Select the studio(s) to check*'

  rev_button = telebot.types.InlineKeyboardButton('Rev', callback_data='{"studios": "Rev", "step": "studios"}')
  barrys_button = telebot.types.InlineKeyboardButton('Barrys', callback_data='{"studios": "Barrys", "step": "studios"}')
  absolute_spin_button = telebot.types.InlineKeyboardButton('Absolute (Spin)', callback_data='{"studios": "Absolute (Spin)", "step": "studios"}')
  absolute_pilates_button = telebot.types.InlineKeyboardButton('Absolute (Pilates)', callback_data='{"studios": "Absolute (Pilates)", "step": "studios"}')
  select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"studios": "All", "step": "studios"}')
  unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"studios": "None", "step": "studios"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "studios-next"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(rev_button, barrys_button)
  keyboard.add(absolute_spin_button, absolute_pilates_button)
  keyboard.add(select_all_button, unselect_all_button)
  keyboard.add(next_button)
  sent_msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['refresh'])
def refresh_handler(message: telebot.types.Message) -> None:
  global current_query_data
  text = 'Updating cached schedules...'
  sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
  update_cached_result_data()
  text = 'Finished updating schedules'
  sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')

def locations_handler(message: telebot.types.Message):
  global current_query_data
  text = current_query_data.get_query_str(include_studio=True)
  text += '*Select the location(s) to check*'

  global locations_selection_message
  locations_selection_message = bot.send_message(message.chat.id, text, reply_markup=get_locations_keyboard(), parse_mode='Markdown')

def weeks_handler(message: telebot.types.Message) -> None:
  global current_query_data
  text = current_query_data.get_query_str(include_studio=True, include_instructors=True, include_weeks=True)
  text += '*Select the number of weeks of classes to show*\n'
  text += 'Rev shows up to 4 weeks\nBarrys shows up to 3 weeks\nAbsolute shows up to 1.5 weeks\n'

  one_button = telebot.types.InlineKeyboardButton('1', callback_data='{"weeks": 1, "step": "weeks"}')
  two_button = telebot.types.InlineKeyboardButton('2', callback_data='{"weeks": 2, "step": "weeks"}')
  three_button = telebot.types.InlineKeyboardButton('3', callback_data='{"weeks": 3, "step": "weeks"}')
  four_button = telebot.types.InlineKeyboardButton('4', callback_data='{"weeks": 4, "step": "weeks"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "weeks-back"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(one_button, two_button)
  keyboard.add(three_button, four_button)
  keyboard.add(back_button)
  sent_msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def days_handler(message: telebot.types.Message) -> None:
  global current_query_data
  text = current_query_data.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True)
  text += '*Select the day(s) to show classes of*'

  global days_selection_message
  days_selection_message = bot.send_message(message.chat.id, text, reply_markup=get_days_keyboard(), parse_mode='Markdown')

def instructors_handler(message: telebot.types.Message) -> None:
  global current_query_data
  text = current_query_data.get_query_str(include_studio=True, include_instructors=True)
  text += '*Select the studio to choose instructors*'

  keyboard = telebot.types.InlineKeyboardMarkup()
  if 'Rev' in current_query_data.studios:
    rev_instructors_button = telebot.types.InlineKeyboardButton('Enter Rev Instructor(s)', callback_data='{"step": "rev-instructors"}')
    keyboard.add(rev_instructors_button)
  if 'Barrys' in current_query_data.studios:
    barrys_instructors_button = telebot.types.InlineKeyboardButton('Enter Barrys Instructor(s)', callback_data='{"step": "barrys-instructors"}')
    keyboard.add(barrys_instructors_button)
  if 'Absolute (Spin)' in current_query_data.studios:
    absolute_spin_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Spin) Instructor(s)', callback_data='{"step": "absolute-spin-instructors"}')
    keyboard.add(absolute_spin_instructors_button)
  if 'Absolute (Pilates)' in current_query_data.studios:
    absolute_pilates_instructors_button = telebot.types.InlineKeyboardButton('Enter Absolute (Pilates) Instructor(s)', callback_data='{"step": "absolute-pilates-instructors"}')
    keyboard.add(absolute_pilates_instructors_button)

  show_instructors_button = telebot.types.InlineKeyboardButton('Show Names of Instructors', callback_data='{"step": "show-instructors"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "instructors-next"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "instructors-back"}')
  keyboard.add(show_instructors_button)
  keyboard.add(back_button, next_button)
  sent_msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def update_cached_result_data() -> None:
  global cached_result_data
  cached_result_data = get_rev_schedule(locations=[studio_location.All], weeks=4, days=['All'], instructors=['All'])
  cached_result_data += get_barrys_schedule(locations=[studio_location.All], weeks=3, days=['All'], instructors=['All'])
  cached_result_data += get_absolute_schedule(locations=list(absolute.data.location_map), weeks=2, days=['All'], instructors=['All'])

print('Starting bot...')
update_cached_result_data()
print('Bot started!')

bot.infinity_polling()