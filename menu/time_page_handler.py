import global_variables
import telebot
from datetime import datetime

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection")
def time_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_handler(query.message)

def time_selection_handler(message: telebot.types.Message) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  text = "*Currently selected timings(s)*\n"
  text += query_data.get_query_str(include_time=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  add_timeslot_button = telebot.types.InlineKeyboardButton("Add Timeslot", callback_data="{'step': 'time-selection-add'}")
  remove_timeslot_button = telebot.types.InlineKeyboardButton("Remove Timeslot", callback_data="{'step': 'time-selection-remove'}")
  reset_all_timeslot_button = telebot.types.InlineKeyboardButton("Reset All Timeslot(s)", callback_data="{'step': 'time-selection-reset'}")
  next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(add_timeslot_button)
  keyboard.add(remove_timeslot_button)
  keyboard.add(reset_all_timeslot_button)
  keyboard.add(next_button)

  global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-add")
def time_selection_add_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time_selection_handler(query.message)

def start_time_selection_handler(message: telebot.types.Message) -> None:
  text = "Enter range of timeslot to check\ne.g. *0700-0830*"
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, start_time_input_handler)

def start_time_input_handler(message: telebot.types.Message) -> None:
  try:
    message_without_whitespace = "".join(message.text.split())
    split_message_without_whitespace = message_without_whitespace.split("-")
    if len(split_message_without_whitespace) != 2:
      raise Exception("Input has invalid format")

    start_time_str = split_message_without_whitespace[0]
    end_time_str = split_message_without_whitespace[1]

    if len(start_time_str) != 4:
      raise Exception("Start time has invalid length")

    if len(end_time_str) != 4:
      raise Exception("End time has invalid length")

    start_time = datetime.strptime(start_time_str, "%H%M")
    end_time = datetime.strptime(end_time_str, "%H%M")
  except Exception as e:
    global_variables.LOGGER.warning(f"Invalid time '{message.text}' entered: {str(e)}")
    text = f"Invalid timeslot range '{message.text}' entered"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    time_selection_handler(message)
    return

  if end_time < start_time:
    text = f"End time must be later than or equal start time. Start time: {start_time.strftime('%H%M')}, End time: {end_time.strftime('%H%M')}"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    time_selection_handler(message)
    return

  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)

  # Start time should be at least one minute before existing start time or greater than or equal existing end time
  is_valid_start_time = True
  for existing_start_time, existing_end_time in query_data.start_times:
    at_least_one_minute_before_existing_start_time = start_time.hour < existing_start_time.hour or start_time.hour == existing_start_time.hour and start_time.minute < existing_start_time.minute
    greater_than_or_equal_existing_end_time = start_time >= existing_end_time
    if not at_least_one_minute_before_existing_start_time and not greater_than_or_equal_existing_end_time:
      conflicting_start_time_str = existing_start_time.strftime("%H%M")
      conflicting_end_time_str = existing_end_time.strftime("%H%M")
      is_valid_start_time = False
      break

    # Edge case where existing timeslot start time and end time are the same
    if existing_start_time.hour == existing_end_time.hour and existing_start_time.minute == existing_end_time.minute:
      if start_time.hour == existing_start_time.hour and start_time.minute == existing_start_time.minute:
        conflicting_start_time_str = existing_start_time.strftime("%H%M")
        conflicting_end_time_str = existing_end_time.strftime("%H%M")
        is_valid_start_time = False
        break

  if not is_valid_start_time:
    text = f"Start time '{start_time_str}' conflicts with existing timeslot '{conflicting_start_time_str} - {conflicting_end_time_str}'"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    time_selection_handler(message)
    return

  # End time should be less than or equal to existing start time or greater than existing end time
  is_valid_end_time = True
  for existing_start_time, existing_end_time in query_data.start_times:
    less_than_or_equal_existing_start_time = end_time <= existing_start_time
    greater_than_existing_end_time = end_time > existing_end_time
    if not less_than_or_equal_existing_start_time and not greater_than_existing_end_time:
      conflicting_start_time_str = existing_start_time.strftime("%H%M")
      conflicting_end_time_str = existing_end_time.strftime("%H%M")
      is_valid_end_time = False
      break

    # If end time is greater than existing end time, start time must also be greater than existing end time
    if greater_than_existing_end_time:
      if start_time < existing_end_time:
        conflicting_start_time_str = existing_start_time.strftime("%H%M")
        conflicting_end_time_str = existing_end_time.strftime("%H%M")
        text = f"Time range '{start_time_str} - {end_time_str}' conflicts with existing timeslot '{conflicting_start_time_str} - {conflicting_end_time_str}'"
        global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
        time_selection_handler(message)
        return

  if not is_valid_end_time:
    text = f"End time '{end_time_str}' conflicts with existing timeslot '{conflicting_start_time_str} - {conflicting_end_time_str}'"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    time_selection_handler(message)
    return

  query_data.start_times.append((start_time, end_time))
  query_data.start_times = sorted(query_data.start_times)
  time_selection_handler(message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-remove")
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  time_selection_remove_handler(query.message)

def time_selection_remove_handler(message: telebot.types.Message) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  if len(query_data.start_times) == 0:
    text = "No timeslot to remove"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    time_selection_handler(message)
  else:
    text = "*Select timeslot to remove*"
    keyboard = telebot.types.InlineKeyboardMarkup()
    buttons = []
    for start_time, end_time in query_data.start_times:
      start_time_str = start_time.strftime("%H%M")
      end_time_str = end_time.strftime("%H%M")
      remove_timeslot_button = telebot.types.InlineKeyboardButton(f"{start_time_str} - {end_time_str}", callback_data=f"{{'step': 'remove-timeslot', 'start':'{start_time_str}', 'end':'{end_time_str}'}}")
      buttons.append(remove_timeslot_button)
      keyboard.add(buttons[-1])

    back_button = telebot.types.InlineKeyboardButton("◀️ Back", callback_data="{'step': 'time-selection'}")
    keyboard.add(back_button)
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "remove-timeslot")
def time_selection_remove_timeslot_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  start_time = eval(query.data)["start"]
  end_time = eval(query.data)["end"]
  query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
  query_data.start_times.remove((datetime.strptime(start_time, "%H%M"), datetime.strptime(end_time, "%H%M")))
  time_selection_handler(query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-reset")
def time_selection_remove_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
  query_data.start_times = []
  time_selection_handler(query.message)
