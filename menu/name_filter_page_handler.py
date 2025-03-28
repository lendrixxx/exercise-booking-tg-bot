import telebot

def class_name_filter_selection_callback_query_handler(query: telebot.types.CallbackQuery, chat_manager: "ChatManager") -> None:
  class_name_filter_selection_handler(query.message, chat_manager)

def class_name_filter_selection_handler(message: telebot.types.Message, chat_manager: "ChatManager") -> None:
  query_data = chat_manager.get_query_data(message.chat.id)
  text = "*Current filter*\n"
  text += query_data.get_query_str(include_class_name_filter=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  set_filter_button = telebot.types.InlineKeyboardButton("Add Filter", callback_data="{'step': 'class-name-filter-add'}")
  reset_filter_button = telebot.types.InlineKeyboardButton("Reset Filter", callback_data="{'step': 'class-name-filter-reset'}")
  next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")

  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.add(set_filter_button, reset_filter_button)
  keyboard.add(next_button)

  chat_manager.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)

def class_name_filter_set_callback_query_handler(query: telebot.types.CallbackQuery, bot: telebot.TeleBot, chat_manager: "ChatManager") -> None:
  text = "Enter name of class to filter (non-case sensitive)\ne.g. *essential*"
  sent_msg = chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  bot.register_next_step_handler(sent_msg, class_name_filter_input_handler, chat_manager)

def class_name_filter_input_handler(message: telebot.types.Message, chat_manager: "ChatManager") -> None:
  query_data = chat_manager.get_query_data(message.chat.id)
  query_data.class_name_filter = message.text
  class_name_filter_selection_handler(message, chat_manager)

def class_name_filter_reset_callback_query_handler(query: telebot.types.CallbackQuery, chat_manager: "ChatManager") -> None:
  query_data = chat_manager.get_query_data(query.message.chat.id)
  query_data.class_name_filter = ""
  class_name_filter_selection_handler(query.message, chat_manager)
