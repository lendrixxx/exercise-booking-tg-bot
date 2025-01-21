import global_variables
import telebot
from datetime import datetime

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection')
def time_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_handler(query.from_user.id, query.message)

def time_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
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
  sent_msg = global_variables.BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-add')
def time_selection_add_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time_selection_handler(query.from_user.id, query.message)

def start_time_selection_handler(user_id: int, message: telebot.types.Message) -> None:
  text = 'Enter range of timeslot to check\ne.g. *0700-0830*'
  sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
  global_variables.BOT.register_next_step_handler(sent_msg, start_time_input_handler, user_id)

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
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  if start_time_to < start_time_from:
    text = f'Start time to must be later than or equal start time from. Start time from: {query_data.start_time_from.strftime("%H%M")}'
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)

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
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
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
        sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
        time_selection_handler(user_id, message)
        return


  if not is_valid_start_time_to:
    text = f'End time "{start_time_to_str}" conflicts with existing timeslot "{conflicting_start_time_from_str} - {conflicting_start_time_to_str}"'
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
    time_selection_handler(user_id, message)
    return

  query_data.start_times.append((start_time_from, start_time_to))
  query_data.start_times = sorted(query_data.start_times)
  time_selection_handler(user_id, message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-remove')
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_remove_handler(query.message, query.from_user.id)

def time_selection_remove_handler(message: telebot.types.Message, user_id: int) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
  if len(query_data.start_times) == 0:
    text = 'No timeslot to remove'
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, parse_mode='Markdown')
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
    sent_msg = global_variables.BOT.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='Markdown')

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'remove-timeslot')
def time_selection_remove_timeslot_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time_from = eval(query.data)['from']
  start_time_to = eval(query.data)['to']
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  query_data.start_times.remove((datetime.strptime(start_time_from, '%H%M'), datetime.strptime(start_time_to, '%H%M')))
  time_selection_handler(query.from_user.id, query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'time-selection-reset')
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  query_data.start_times = []
  time_selection_handler(query.from_user.id, query.message)
