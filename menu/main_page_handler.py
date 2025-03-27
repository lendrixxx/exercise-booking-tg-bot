import global_variables
import telebot

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "main-page-handler")
def main_page_handler_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  main_page_handler(query.message)

def main_page_handler(message: telebot.types.Message) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  text = "*Schedule to check*\n"
  text += query_data.get_query_str(include_studio=True, include_instructors=True, include_weeks=True, include_days=True, include_time=True, include_class_name_filter=True)

  studios_button = telebot.types.InlineKeyboardButton("Studios", callback_data="{'step': 'studios-selection'}")
  instructors_button = telebot.types.InlineKeyboardButton("Instructors", callback_data="{'step': 'instructors-selection'}")
  weeks_button = telebot.types.InlineKeyboardButton("Weeks", callback_data="{'step': 'weeks-selection'}")
  days_button = telebot.types.InlineKeyboardButton("Days", callback_data="{'step': 'days-selection'}")
  time_button = telebot.types.InlineKeyboardButton("Time", callback_data="{'step': 'time-selection'}")
  class_name_button = telebot.types.InlineKeyboardButton("Class Name", callback_data="{'step': 'class-name-filter-selection'}")
  next_button = telebot.types.InlineKeyboardButton("Get Schedule ▶️", callback_data="{'step': 'get-schedule'}")

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(studios_button, instructors_button)
  keyboard.add(weeks_button, days_button)
  keyboard.add(time_button, class_name_button)
  keyboard.add(next_button)

  global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)
