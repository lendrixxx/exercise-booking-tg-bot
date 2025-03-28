import time
from menu.main_page_handler import main_page_handler

def start_message_handler(message: "telebot.types.Message", chat_manager: "ChatManager", history_manager: "HistoryManager") -> None:
    history_manager.add(int(time.time()), message.from_user.id, message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, "start")
    chat_manager.reset_query_and_messages_to_edit_data(message.chat.id)
    chat_manager.add_message_id_to_delete(message.chat.id, message.id)
    main_page_handler(message, chat_manager)
