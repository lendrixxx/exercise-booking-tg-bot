import absolute
import barrys
import os
import rev
import telebot
from absolute.absolute import get_absolute_schedule
from common.data_types import query_data, result_data, sorted_days, studio_data, studio_location, studio_locations_map, studio_type
from copy import copy
from barrys.barrys import get_barrys_schedule
from rev.rev import get_rev_schedule

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
start_command = telebot.types.BotCommand(command='start', description='Check schedules')
refresh_command = telebot.types.BotCommand(command='refresh', description='Refresh cached schedules')
bot.set_my_commands([start_command, refresh_command])

current_query_data = query_data(studios={}, current_studio=studio_type.Null, weeks=0, days=[])
cached_result_data = result_data()

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios')
def studios_callback_query_handler(query):
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
def locations_callback_query_handler(query):
  global current_query_data
  query_data_dict = eval(query.data)
  studio_location_selected = studio_location[query_data_dict['locations']]
  if studio_location_selected == studio_location.Null:
    current_query_data.studios.pop(current_query_data.current_studio)
  elif studio_location_selected == studio_location.All:
    if current_query_data.current_studio not in current_query_data.studios:
      new_studio = {current_query_data.current_studio: studio_data(locations=copy(studio_locations_map[current_query_data.current_studio]))}
      current_query_data.studios = {**current_query_data.studios, **new_studio}
    else:
      current_query_data.studios[current_query_data.current_studio].locations = copy(studio_locations_map[current_query_data.current_studio])
  else:
    if current_query_data.current_studio not in current_query_data.studios:
      new_studio = {current_query_data.current_studio: studio_data(locations=[studio_location_selected])}
      current_query_data.studios = {**current_query_data.studios, **new_studio}
    elif studio_location_selected in current_query_data.studios[current_query_data.current_studio].locations:
      current_query_data.studios[current_query_data.current_studio].locations.remove(studio_location_selected)
      if len(current_query_data.studios[current_query_data.current_studio].locations) == 0:
        current_query_data.studios.pop(current_query_data.current_studio)
    else:
      current_query_data.studios[current_query_data.current_studio].locations.append(studio_location_selected)
  locations_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations-next')
def locations_next_callback_query_handler(query):
  studios_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios-next')
def studios_next_callback_query_handler(query):
  global current_query_data
  if len(current_query_data.studios) == 0:
    text = 'Please select a studio'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    studios_handler(query.message)
  else:
    weeks_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks')
def weeks_callback_query_handler(query):
  global current_query_data
  query_data_dict = eval(query.data)
  current_query_data.weeks = query_data_dict['weeks']
  days_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'weeks-back')
def weeks_back_callback_query_handler(query):
  studios_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days')
def days_callback_query_handler(query):
  global current_query_data
  query_data_dict = eval(query.data)
  if query_data_dict['days'] == 'None':
    current_query_data.days = []
  elif query_data_dict['days'] == 'All':
    current_query_data.days = sorted_days
  else:
    if query_data_dict['days'] in current_query_data.days:
      current_query_data.days.remove(query_data_dict['days'])
    else:
      current_query_data.days.append(query_data_dict['days'])
      current_query_data.days = sorted(current_query_data.days, key=sorted_days.index)
  days_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-back')
def days_back_callback_query_handler(query):
  weeks_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'days-next')
def days_next_callback_query_handler(query):
  global current_query_data
  if len(current_query_data.days) == 0:
    text = 'Please select a day'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    days_handler(query.message)
  else:
    instructors_handler(query.message)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'rev-instructors')
def rev_instructors_callback_query_handler(query):
  global current_query_data
  text = 'Which instructor would you like to check?\nOptions: *chloe*, *jerlyn*, *zai*, *all*, etc\nMultiple options e.g.: *chloe, jerlyn*'
  current_query_data.current_studio = 'Rev'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
  bot.register_next_step_handler(sent_msg, instructors_input_handler, rev.data.instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'barrys-instructors')
def barrys_instructors_callback_query_handler(query):
  global current_query_data
  text = 'Which instructor would you like to check?\nOptions: *ria*, *gino*, *all*, etc\nMultiple options e.g.: *ria, gino*'
  current_query_data.current_studio = 'Barrys'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
  bot.register_next_step_handler(sent_msg, instructors_input_handler, barrys.data.instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-spin-instructors')
def absolute_spin_instructors_callback_query_handler(query):
  global current_query_data
  text = 'Which instructor would you like to check?\nOptions: *chin*, *ria*, *all*, etc\nMultiple options e.g.: *chin, ria*'
  current_query_data.current_studio = 'Absolute (Spin)'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
  bot.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.spin_instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-pilates-instructors')
def absolute_pilates_instructors_callback_query_handler(query):
  global current_query_data
  text = 'Which instructor would you like to check?\nOptions: *daniella*, *vnex*, *all*, etc\nMultiple options e.g.: *daniella, vnex*'
  current_query_data.current_studio = 'Absolute (Pilates)'
  sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
  bot.register_next_step_handler(sent_msg, instructors_input_handler, absolute.data.pilates_instructorid_map)

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'show-instructors')
def show_instructors_callback_query_handler(query):
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

def instructors_input_handler(message, instructorid_map: dict[str, int]):
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
def instructors_next_callback_query_handler(query):
  global current_query_data, cached_result_data
  if not current_query_data.has_instructors_selected():
    text = 'Please select at least one instructor'
    sent_msg = bot.send_message(query.message.chat.id, text, parse_mode='Markdown')
    instructors_handler(query.message)
    return

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

@bot.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-back')
def instructors_back_callback_query_handler(query):
  days_handler(query.message)

@bot.message_handler(commands=['start'])
def start_handler(message):
  global current_query_data
  current_query_data = query_data(studios={}, current_studio=studio_type.Null, weeks=0, days=[])
  studios_handler(message)

def studios_handler(message):
  global current_query_data
  text = '*Schedule to check*\n'
  text += f'Studio(s):\n{current_query_data.get_selected_studios_str()}\n'
  text += '\n*Select the studio(s) to check*'

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
def refresh_handler(message):
  global current_query_data
  text = 'Updating cached schedules...'
  sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
  update_cached_result_data()
  text = 'Finished updating schedules'
  sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')

def locations_handler(message):
  global current_query_data
  text = '*Schedule to check*\n'
  text += f'Studio(s):\n{current_query_data.get_selected_studios_str()}\n'
  text += '\n*Select the location(s) to check*'

  # Rev locations
  selected_rev_locations = current_query_data.get_studio_locations('Rev')
  rev_bugis_text = 'Bugis ✅' if 'Bugis' in selected_rev_locations else 'Bugis'
  rev_orchard_text = 'Orchard ✅' if 'Orchard' in selected_rev_locations else 'Orchard'
  rev_suntec_text = 'Suntec ✅' if 'Suntec' in selected_rev_locations else 'Suntec'
  rev_tjpg_text = 'TJPG ✅' if 'TJPG' in selected_rev_locations else 'TJPG'
  rev_bugis_button = telebot.types.InlineKeyboardButton(rev_bugis_text, callback_data='{"locations": "Bugis", "step": "locations"}')
  rev_orchard_button = telebot.types.InlineKeyboardButton(rev_orchard_text, callback_data='{"locations": "Orchard", "step": "locations"}')
  rev_suntec_button = telebot.types.InlineKeyboardButton(rev_suntec_text, callback_data='{"locations": "Suntec", "step": "locations"}')
  rev_tjpg_button = telebot.types.InlineKeyboardButton(rev_tjpg_text, callback_data='{"locations": "TJPG", "step": "locations"}')

  # Barrys locations
  selected_barrys_locations = current_query_data.get_studio_locations('Barrys')
  barrys_orchard_text = 'Orchard ✅' if 'Orchard' in selected_barrys_locations else 'Orchard'
  barrys_raffles_place_text = 'Raffles ✅' if 'Raffles' in selected_barrys_locations else 'Raffles'
  barrys_orchard_button = telebot.types.InlineKeyboardButton(barrys_orchard_text, callback_data='{"locations": "Orchard", "step": "locations"}')
  barrys_raffles_button = telebot.types.InlineKeyboardButton(barrys_raffles_place_text, callback_data='{"locations": "Raffles", "step": "locations"}')

  # Absolute spin locations
  selected_absolute_spin_locations = current_query_data.get_studio_locations('Absolute (Spin)')
  absolute_spin_centrepoint_text = 'Centrepoint ✅' if 'Centrepoint' in selected_absolute_spin_locations else 'Centrepoint'
  absolute_spin_i12_text = 'i12 ✅' if 'i12' in selected_absolute_spin_locations else 'i12'
  absolute_spin_star_vista_text = 'Star Vista ✅' if 'Star Vista' in selected_absolute_spin_locations else 'Star Vista'
  absolute_spin_raffles_text = 'Raffles ✅' if 'Raffles' in selected_absolute_spin_locations else 'Raffles'
  absolute_spin_millenia_walk_text = 'Millenia Walk ✅' if 'Millenia Walk' in selected_absolute_spin_locations else 'Millenia Walk'
  absolute_spin_centrepoint_button = telebot.types.InlineKeyboardButton(absolute_spin_centrepoint_text, callback_data='{"locations": "Centrepoint", "step": "locations"}')
  absolute_spin_i12_button = telebot.types.InlineKeyboardButton(absolute_spin_i12_text, callback_data='{"locations": "i12", "step": "locations"}')
  absolute_spin_star_vista_button = telebot.types.InlineKeyboardButton(absolute_spin_star_vista_text, callback_data='{"locations": "StarVista", "step": "locations"}')
  absolute_spin_raffles_button = telebot.types.InlineKeyboardButton(absolute_spin_raffles_text, callback_data='{"locations": "Raffles", "step": "locations"}')
  absolute_spin_millenia_walk_button = telebot.types.InlineKeyboardButton(absolute_spin_millenia_walk_text, callback_data='{"locations": "MilleniaWalk", "step": "locations"}')

  # Absolute pilates locations
  selected_absolute_pilates_locations = current_query_data.get_studio_locations('Absolute (Pilates)')
  absolute_pilates_centrepoint_text = 'Centrepoint ✅' if 'Centrepoint' in selected_absolute_pilates_locations else 'Centrepoint'
  absolute_pilates_i12_text = 'i12 ✅' if 'i12' in selected_absolute_pilates_locations else 'i12'
  absolute_pilates_star_vista_text = 'Star Vista ✅' if 'Star Vista' in selected_absolute_pilates_locations else 'Star Vista'
  absolute_pilates_raffles_text = 'Raffles ✅' if 'Raffles' in selected_absolute_pilates_locations else 'Raffles'
  absolute_pilates_great_world_text = 'Great World ✅' if 'Great World' in selected_absolute_pilates_locations else 'Great World'
  absolute_pilates_centrepoint_button = telebot.types.InlineKeyboardButton(absolute_pilates_centrepoint_text, callback_data='{"locations": "Centrepoint", "step": "locations"}')
  absolute_pilates_i12_button = telebot.types.InlineKeyboardButton(absolute_pilates_i12_text, callback_data='{"locations": "i12", "step": "locations"}')
  absolute_pilates_star_vista_button = telebot.types.InlineKeyboardButton(absolute_pilates_star_vista_text, callback_data='{"locations": "StarVista", "step": "locations"}')
  absolute_pilates_raffles_button = telebot.types.InlineKeyboardButton(absolute_pilates_raffles_text, callback_data='{"locations": "Raffles", "step": "locations"}')
  absolute_pilates_great_world_button = telebot.types.InlineKeyboardButton(absolute_pilates_great_world_text, callback_data='{"locations": "GreatWorld", "step": "locations"}')

  # Common buttons
  select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"locations": "All", "step": "locations"}')
  unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"locations": "Null", "step": "locations"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "locations-next"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  if current_query_data.current_studio == 'Rev':
    keyboard.add(rev_bugis_button, rev_orchard_button)
    keyboard.add(rev_suntec_button, rev_tjpg_button)
  elif current_query_data.current_studio == 'Barrys':
    keyboard.add(barrys_orchard_button, barrys_raffles_button)
  elif current_query_data.current_studio == 'Absolute (Spin)':
    keyboard.add(absolute_spin_centrepoint_button, absolute_spin_i12_button)
    keyboard.add(absolute_spin_star_vista_button, absolute_spin_raffles_button)
    keyboard.add(absolute_spin_millenia_walk_button)
  elif current_query_data.current_studio == 'Absolute (Pilates)':
    keyboard.add(absolute_pilates_centrepoint_button, absolute_pilates_i12_button)
    keyboard.add(absolute_pilates_star_vista_button, absolute_pilates_raffles_button)
    keyboard.add(absolute_pilates_great_world_button)
  keyboard.add(select_all_button, unselect_all_button)
  keyboard.add(next_button)

  sent_msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def weeks_handler(message):
  global current_query_data
  text = '*Schedule to check*\n'
  text += f'Studio(s):\n{current_query_data.get_selected_studios_str()}\n'
  text += '\n*Select the number of weeks of classes to show*\n'
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

def days_handler(message):
  global current_query_data
  text = '*Schedule to check*\n'
  text += f'Studio(s):\n{current_query_data.get_selected_studios_str()}\n'
  text += f'Week(s): {current_query_data.weeks}\n\n'
  text += f'Days(s): {current_query_data.get_selected_days_str()}\n'
  text += '\n*Select the day(s) to show classes of*'

  monday_text = 'Monday ✅' if 'Monday' in current_query_data.days else 'Monday'
  tuesday_text = 'Tuesday ✅' if 'Tuesday' in current_query_data.days else 'Tuesday'
  wednesday_text = 'Wednesday ✅' if 'Wednesday' in current_query_data.days else 'Wednesday'
  thursday_text = 'Thursday ✅' if 'Thursday' in current_query_data.days else 'Thursday'
  friday_text = 'Friday ✅' if 'Friday' in current_query_data.days else 'Friday'
  saturday_text = 'Saturday ✅' if 'Saturday' in current_query_data.days else 'Saturday'
  sunday_text = 'Sunday ✅' if 'Sunday' in current_query_data.days else 'Sunday'
  monday_button = telebot.types.InlineKeyboardButton(monday_text, callback_data='{"days": "Monday", "step": "days"}')
  tuesday_button = telebot.types.InlineKeyboardButton(tuesday_text, callback_data='{"days": "Tuesday", "step": "days"}')
  wednesday_button = telebot.types.InlineKeyboardButton(wednesday_text, callback_data='{"days": "Wednesday", "step": "days"}')
  thursday_button = telebot.types.InlineKeyboardButton(thursday_text, callback_data='{"days": "Thursday", "step": "days"}')
  friday_button = telebot.types.InlineKeyboardButton(friday_text, callback_data='{"days": "Friday", "step": "days"}')
  saturday_button = telebot.types.InlineKeyboardButton(saturday_text, callback_data='{"days": "Saturday", "step": "days"}')
  sunday_button = telebot.types.InlineKeyboardButton(sunday_text, callback_data='{"days": "Sunday", "step": "days"}')
  select_all_button = telebot.types.InlineKeyboardButton('Select All', callback_data='{"days": "All", "step": "days"}')
  unselect_all_button = telebot.types.InlineKeyboardButton('Unselect All', callback_data='{"days": "None", "step": "days"}')
  back_button = telebot.types.InlineKeyboardButton('◀️ Back', callback_data='{"step": "days-back"}')
  next_button = telebot.types.InlineKeyboardButton('Next ▶️', callback_data='{"step": "days-next"}')

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(monday_button, tuesday_button)
  keyboard.add(wednesday_button, thursday_button)
  keyboard.add(friday_button, saturday_button)
  keyboard.add(sunday_button)
  keyboard.add(select_all_button, unselect_all_button)
  keyboard.add(back_button, next_button)
  sent_msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

def instructors_handler(message):
  global current_query_data
  text = '*Schedule to check*\n'
  text += f'Studio(s):\n{current_query_data.get_selected_studios_str()}\n'
  text += f'Week(s): {current_query_data.weeks}\n'
  text += f'Day(s): {current_query_data.get_selected_days_str()}\n\n'
  text += f'_Instructor(s)_\n{current_query_data.get_selected_instructors_str()}\n'
  text += '\n*Select the studio to choose instructors*'

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

def update_cached_result_data():
  global cached_result_data
  cached_result_data = get_rev_schedule(locations=[studio_location.All], weeks=4, days=['All'], instructors=['All'])
  cached_result_data += get_barrys_schedule(locations=[studio_location.All], weeks=3, days=['All'], instructors=['All'])
  cached_result_data += get_absolute_schedule(locations=list(absolute.data.location_map), weeks=2, days=['All'], instructors=['All'])

print('Starting bot...')
update_cached_result_data()
print('Bot started!')

bot.infinity_polling()