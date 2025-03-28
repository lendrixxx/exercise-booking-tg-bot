from common.data_types import SORTED_DAYS
from menu.main_page_handler import main_page_handler

def days_callback_query_handler(query: "telebot.types.CallbackQuery", bot: "telebot.TeleBot", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  query_data_dict = eval(query.data)
  selected_day = query_data_dict["days"]
  if selected_day == "None":
    chat_manager.update_query_data_days(query.message.chat.id, [])
  elif selected_day == "All":
    chat_manager.update_query_data_days(query.message.chat.id, SORTED_DAYS)
  else:
    query_data = chat_manager.get_query_data(query.message.chat.id)
    if selected_day in query_data.days:
      query_data.days.remove(selected_day)
      chat_manager.update_query_data_days(query.message.chat.id, query_data.days)
    else:
      query_data.days.append(selected_day)
      query_data.days = sorted(query_data.days, key=SORTED_DAYS.index)
      chat_manager.update_query_data_days(query.message.chat.id, query_data.days)

  query_data = chat_manager.get_query_data(query.message.chat.id)
  text = "*Currently selected day(s)*\n"
  text += query_data.get_query_str(include_days=True)

  days_selection_message = chat_manager.get_days_selection_message(query.message.chat.id)
  bot.edit_message_text(
    chat_id=days_selection_message.chat.id,
    message_id=days_selection_message.id,
    text=text,
    reply_markup=keyboard_manager.get_days_keyboard(query_data),
    parse_mode="Markdown")

def days_selection_callback_query_handler(query: "telebot.types.CallbackQuery", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  days_selection_handler(query.message, chat_manager, keyboard_manager)

def days_selection_handler(message: "telebot.types.Message", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  query_data = chat_manager.get_query_data(message.chat.id)
  text = "*Currently selected day(s)*\n"
  text += query_data.get_query_str(include_days=True)

  sent_msg = chat_manager.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard_manager.get_days_keyboard(query_data), delete_sent_msg_in_future=True)
  chat_manager.update_button_data_days_selection_message(message.chat.id, sent_msg)

def days_next_callback_query_handler(query: "telebot.types.CallbackQuery", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  query_data = chat_manager.get_query_data(query.message.chat.id)
  if len(query_data.days) == 0:
    text = "No day(s) selected. Please select the day(s) to get schedule for"
    chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    days_selection_handler(query.message, chat_manager, keyboard_manager)
    return

  main_page_handler(query.message, chat_manager)
