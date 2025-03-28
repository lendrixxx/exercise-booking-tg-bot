import telebot
from menu.main_page_handler import main_page_handler

def weeks_selection_callback_query_handler(query: telebot.types.CallbackQuery, chat_manager: "ChatManager") -> None:
  query_data_dict = eval(query.data)
  query_data = chat_manager.get_query_data(query.message.chat.id)
  text = "*Currently selected week(s)*\n"
  text += query_data.get_query_str(include_weeks=True)
  text += "\nAbsolute shows up to 1.5 weeks\nAlly shows up to 2 weeks\nAnarchy shows up to 2.5 weeks\nBarrys shows up to 3 weeks\nRev shows up to 4 weeks\n"

  one_button = telebot.types.InlineKeyboardButton("1", callback_data="{'weeks': 1, 'step': 'weeks'}")
  two_button = telebot.types.InlineKeyboardButton("2", callback_data="{'weeks': 2, 'step': 'weeks'}")
  three_button = telebot.types.InlineKeyboardButton("3", callback_data="{'weeks': 3, 'step': 'weeks'}")
  four_button = telebot.types.InlineKeyboardButton("4", callback_data="{'weeks': 4, 'step': 'weeks'}")
  back_button = telebot.types.InlineKeyboardButton("◀️ Back", callback_data="{'step': 'main-page-handler'}")

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(one_button, two_button)
  keyboard.add(three_button, four_button)
  keyboard.add(back_button)

  chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)

def weeks_callback_query_handler(query: telebot.types.CallbackQuery, chat_manager: "ChatManager") -> None:
  query_data_dict = eval(query.data)
  chat_manager.update_query_data_weeks(query.message.chat.id, query_data_dict["weeks"])
  main_page_handler(query.message, chat_manager)
