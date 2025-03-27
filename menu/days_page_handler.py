import global_variables
import telebot
from common.data_types import SORTED_DAYS
from menu.main_page_handler import main_page_handler

def get_days_keyboard(chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  button_data = global_variables.CHAT_MANAGER.get_button_data(chat_id)
  days_keyboard = telebot.types.InlineKeyboardMarkup()
  days_keyboard.add(button_data.days_buttons_map["Monday"], button_data.days_buttons_map["Tuesday"])
  days_keyboard.add(button_data.days_buttons_map["Wednesday"], button_data.days_buttons_map["Thursday"])
  days_keyboard.add(button_data.days_buttons_map["Friday"], button_data.days_buttons_map["Saturday"])
  days_keyboard.add(button_data.days_buttons_map["Sunday"])
  days_keyboard.add(button_data.days_select_all_button, button_data.days_unselect_all_button)
  days_keyboard.add(button_data.days_next_button)
  return days_keyboard

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days")
def days_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  button_data = global_variables.CHAT_MANAGER.get_button_data(query.message.chat.id)
  query_data_dict = eval(query.data)
  selected_day = query_data_dict["days"]
  if selected_day == "None":
    for day in button_data.days_buttons_map:
      button_data.days_buttons_map[day] = telebot.types.InlineKeyboardButton(day, callback_data=button_data.days_buttons_map[day].callback_data)
    global_variables.CHAT_MANAGER.update_button_data_days_buttons_map(query.message.chat.id, button_data.days_buttons_map)
    global_variables.CHAT_MANAGER.update_query_data_days(query.message.chat.id, [])
  elif selected_day == "All":
    for day in button_data.days_buttons_map:
      button_data.days_buttons_map[day] = telebot.types.InlineKeyboardButton(day + " ✅", callback_data=button_data.days_buttons_map[day].callback_data)
    global_variables.CHAT_MANAGER.update_button_data_days_buttons_map(query.message.chat.id, button_data.days_buttons_map)
    global_variables.CHAT_MANAGER.update_query_data_days(query.message.chat.id, SORTED_DAYS)
  else:
    query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
    if selected_day in query_data.days:
      button_data.days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day, callback_data=button_data.days_buttons_map[selected_day].callback_data)
      global_variables.CHAT_MANAGER.update_button_data_days_buttons_map(query.message.chat.id, button_data.days_buttons_map)
      query_data.days.remove(selected_day)
      global_variables.CHAT_MANAGER.update_query_data_days(query.message.chat.id, query_data.days)
    else:
      button_data.days_buttons_map[selected_day] = telebot.types.InlineKeyboardButton(selected_day + " ✅", callback_data=button_data.days_buttons_map[selected_day].callback_data)
      global_variables.CHAT_MANAGER.update_button_data_days_buttons_map(query.message.chat.id, button_data.days_buttons_map)
      query_data.days.append(selected_day)
      query_data.days = sorted(query_data.days, key=SORTED_DAYS.index)
      global_variables.CHAT_MANAGER.update_query_data_days(query.message.chat.id, query_data.days)

  query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
  text = "*Currently selected day(s)*\n"
  text += query_data.get_query_str(include_days=True)

  button_data = global_variables.CHAT_MANAGER.get_button_data(query.message.chat.id)
  global_variables.BOT.edit_message_text(
    chat_id=button_data.days_selection_message.chat.id,
    message_id=button_data.days_selection_message.id,
    text=text,
    reply_markup=get_days_keyboard(query.message.chat.id),
    parse_mode="Markdown")

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days-selection")
def days_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  days_selection_handler(query.message)

def days_selection_handler(message: telebot.types.Message) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  text = "*Currently selected day(s)*\n"
  text += query_data.get_query_str(include_days=True)

  sent_msg = global_variables.BOT.send_message(message.chat.id, text, reply_markup=get_days_keyboard(message.chat.id), parse_mode="Markdown")
  global_variables.CHAT_MANAGER.update_button_data_days_selection_message(message.chat.id, sent_msg)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days-next")
def days_next_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
  if len(query_data.days) == 0:
    text = "No day(s) selected. Please select the day(s) to get schedule for"
    sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, parse_mode="Markdown")
    days_selection_handler(query.message)
    return

  main_page_handler(query.message)
