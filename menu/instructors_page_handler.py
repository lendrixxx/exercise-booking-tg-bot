import global_variables
import telebot
from menu.main_page_handler import main_page_handler

@global_variables.BOT.message_handler(commands=['instructors'])
def instructors_list_handler(message: telebot.types.Message) -> None:
  text = '*Rev Instructors:* ' + ', '.join(global_variables.REV_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Barrys Instructors:* ' + ', '.join(global_variables.BARRYS_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Absolute Instructors:* ' + ', '.join(global_variables.ABSOLUTE_INSTRUCTOR_NAMES) + '\n\n'
  text += '*Ally Instructors:* ' + ', '.join(global_variables.ALLY_INSTRUCTOR_NAMES) + '\n\n'
  sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'instructors-selection')
def instructors_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  instructors_selection_handler(query.from_user.id, query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'show-instructors')
def show_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = ''
  if 'Rev' in query_data.studios:
    text += '*Rev Instructors:* ' + ', '.join(global_variables.REV_INSTRUCTOR_NAMES) + '\n\n'
  if 'Barrys' in query_data.studios:
    text += '*Barrys Instructors:* ' + ', '.join(global_variables.BARRYS_INSTRUCTOR_NAMES) + '\n\n'
  if 'Absolute (Spin)' in query_data.studios or 'Absolute (Pilates)' in query_data.studios:
    text += '*Absolute Instructors:* ' + ', '.join(global_variables.ABSOLUTE_INSTRUCTOR_NAMES) + '\n\n'
  if 'Ally (Spin)' in query_data.studios or 'Ally (Pilates)' in query_data.studios:
    text += '*Ally Instructors:* ' + ', '.join(global_variables.ALLY_INSTRUCTOR_NAMES) + '\n\n'

  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  instructors_selection_handler(query.from_user.id, query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'rev-instructors')
def rev_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *chloe*, *jerlyn*, *zai*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Rev')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.REV_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'barrys-instructors')
def barrys_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *ria*, *gino*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Barrys')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.BARRYS_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-spin-instructors')
def absolute_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *chin*, *ria*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Absolute (Spin)')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.ABSOLUTE_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'absolute-pilates-instructors')
def absolute_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *daniella*, *vnex*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Absolute (Pilates)')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.ABSOLUTE_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-spin-instructors')
def ally_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *samuel*, *jasper*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Ally (Spin)')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.ALLY_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'ally-pilates-instructors')
def ally_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = 'Enter instructor names separated by a comma\ne.g.: *candice*, *ruth*\nEnter "*all*" to check for all instructors'
  global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, 'Ally (Pilates)')
  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, query.from_user.id, global_variables.ALLY_INSTRUCTORID_MAP)

def instructors_input_handler(message: telebot.types.Message, user_id: int, instructorid_map: dict[str, int]) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
  updated_instructors_list = [x.strip() for x in message.text.lower().split(',')]
  if 'all' in updated_instructors_list:
    query_data.studios[query_data.current_studio].instructors = ['All']
    global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
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
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
      text = f'Failed to find instructor(s): {", ".join(invalid_instructors)}'
      sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')

    if len(updated_instructors_list) > 0:
      query_data.studios[query_data.current_studio].instructors = updated_instructors_list

  instructors_selection_handler(user_id, message)

def instructors_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
  if len(query_data.studios) == 0:
    text = 'No studio(s) selected. Please select the studio(s) first'
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
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
  sent_msg = global_variables.BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')
