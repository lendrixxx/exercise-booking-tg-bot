from common.data_types import SORTED_DAYS
from menu.main_page_handler import main_page_handler

def get_schedule_callback_query_handler(query: "telebot.types.CallbackQuery", chat_manager: "ChatManager", result_data: "ResultData") -> None:
  query_data = chat_manager.get_query_data(query.message.chat.id)
  if len(query_data.studios) == 0:
    text = "No studio selected. Please select a studio to get schedule for"
    chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    main_page_handler(query.message, chat_manager)
    return

  if len(query_data.days) == 0:
    text = "No day selected. Please select the day to get schedule for"
    chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    main_page_handler(query.message, chat_manager)
    return

  send_results(query, chat_manager, result_data)

def send_results(query: "telebot.types.CallbackQuery", chat_manager: "ChatManager", result_data: "ResultData") -> None:
  query_data = chat_manager.get_query_data(query.message.chat.id)
  result = result_data.get_data(query_data)
  chat_manager.reset_query_and_messages_to_edit_data(query.message.chat.id)

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
        chat_manager.send_prompt(chat_id=query.message.chat.id, text=shortened_message, reply_markup=None, delete_sent_msg_in_future=False)
        shortened_message = line + "\n"
      else:
        shortened_message += line + "\n"

    if len(shortened_message) > 0:
      chat_manager.send_prompt(chat_id=query.message.chat.id, text=shortened_message, reply_markup=None, delete_sent_msg_in_future=False)
  else:
    chat_manager.send_prompt(chat_id=query.message.chat.id, text=schedule_str, reply_markup=None, delete_sent_msg_in_future=False)
