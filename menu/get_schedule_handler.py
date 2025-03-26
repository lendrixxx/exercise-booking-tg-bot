import global_variables
import telebot
from common.data_types import SORTED_DAYS
from menu.main_page_handler import main_page_handler

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "get-schedule")
def get_schedule_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  if len(query_data.studios) == 0:
    text = "No studio(s) selected. Please select the studio(s) to get schedule for"
    sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode="Markdown")
    main_page_handler(query.from_user.id, query.message)
    return

  if len(query_data.days) == 0:
    text = "No day(s) selected. Please select the day(s) to get schedule for"
    sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode="Markdown")
    main_page_handler(query.from_user.id, query.message)
    return

  send_results(query)

def send_results(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  result = global_variables.CACHED_RESULT_DATA.get_data(query_data)
  global_variables.USER_MANAGER.reset_query_data(query.from_user.id, query.message.chat.id)

  # Send string as messages
  schedule_str = result.get_result_str()
  if len(schedule_str) > 4095:
    shortened_message = ""
    for line in schedule_str.splitlines():
      shortened_message_len = len(shortened_message)
      # String of day is bolded which starts with "*", so we want to check from the second character
      is_new_day = line[1:].startswith(tuple(SORTED_DAYS)) and shortened_message_len > 0
      max_len_reached = shortened_message_len + len(line) > 4095
      if is_new_day or max_len_reached:
        global_variables.BOT.send_message(query.message.chat.id, shortened_message, parse_mode="Markdown")
        shortened_message = line + "\n"
      else:
        shortened_message += line + "\n"

    if len(shortened_message) > 0:
      global_variables.BOT.send_message(query.message.chat.id, shortened_message, parse_mode="Markdown")
  else:
    global_variables.BOT.send_message(query.message.chat.id, schedule_str, parse_mode="Markdown")
