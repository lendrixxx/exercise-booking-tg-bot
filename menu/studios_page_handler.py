from common.data_types import StudioData, StudioLocation, StudioType, STUDIO_LOCATIONS_MAP
from copy import copy

def studios_selection_callback_query_handler(query: "telebot.types.CallbackQuery", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  query_data_dict = eval(query.data)
  query_data = chat_manager.get_query_data(query.message.chat.id)
  text = "*Currently selected studio(s)*\n"
  text += query_data.get_query_str(include_studio=True)

  sent_msg = chat_manager.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=keyboard_manager.get_studios_keyboard(query_data), delete_sent_msg_in_future=True)
  chat_manager.update_button_data_studios_selection_message(query.message.chat.id, sent_msg)

def studios_callback_query_handler(query: "telebot.types.CallbackQuery", bot: "telebot.TeleBot", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager") -> None:
  query_data_dict = eval(query.data)
  selected_studio = StudioType[query_data_dict["studios"]]
  if selected_studio == StudioType.Null:
    chat_manager.update_query_data_studios(query.message.chat.id, {})
  elif selected_studio == StudioType.All:
    chat_manager.update_query_data_select_all_studios(query.message.chat.id)
  elif selected_studio == StudioType.AllySpin or selected_studio == StudioType.AllyPilates or selected_studio == StudioType.AllyRecovery:
    chat_manager.update_query_data_current_studio(query.message.chat.id, selected_studio)
    select_location_handler(query.message, StudioLocation.CrossStreet, chat_manager)
  elif selected_studio == StudioType.Anarchy:
    chat_manager.update_query_data_current_studio(query.message.chat.id, selected_studio)
    select_location_handler(query.message, StudioLocation.Robinson, chat_manager)
  else:
    chat_manager.update_query_data_current_studio(query.message.chat.id, selected_studio)
    locations_handler(query.message, chat_manager, keyboard_manager)
    return

  query_data = chat_manager.get_query_data(query.message.chat.id)
  text = "*Currently selected studio(s)*\n"
  text += query_data.get_query_str(include_studio=True)

  studios_selection_message = chat_manager.get_studios_selection_message(query.message.chat.id)
  bot.edit_message_text(
    chat_id=studios_selection_message.chat.id,
    message_id=studios_selection_message.id,
    text=text,
    reply_markup=keyboard_manager.get_studios_keyboard(query_data),
    parse_mode="Markdown")

def locations_handler(message: "telebot.types.Message", chat_manager: "ChatManager", keyboard_manager: "KeyboardManager"):
  query_data = chat_manager.get_query_data(message.chat.id)
  text = "*Currently selected studio(s)*\n"
  text += query_data.get_query_str(include_studio=True)

  sent_msg = chat_manager.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard_manager.get_locations_keyboard(query_data), delete_sent_msg_in_future=True)
  chat_manager.update_button_data_locations_selection_message(message.chat.id, sent_msg)

def select_location_handler(message: "telebot.types.Message", selected_studio_location: StudioLocation, chat_manager: "ChatManager") -> None:
  query_data = chat_manager.get_query_data(message.chat.id)
  if selected_studio_location == StudioLocation.Null:
    query_data.studios.pop(query_data.current_studio)
    chat_manager.update_query_data_studios(message.chat.id, query_data.studios)
  elif selected_studio_location == StudioLocation.All:
    if query_data.current_studio not in query_data.studios:
      new_studio = {query_data.current_studio: StudioData(locations=copy(STUDIO_LOCATIONS_MAP[query_data.current_studio]))}
      query_data.studios = {**query_data.studios, **new_studio}
      chat_manager.update_query_data_studios(message.chat.id, query_data.studios)
    else:
      query_data.studios[query_data.current_studio].locations = copy(STUDIO_LOCATIONS_MAP[query_data.current_studio])
      chat_manager.update_query_data_studios(message.chat.id, query_data.studios)
  else:
    if query_data.current_studio not in query_data.studios:
      new_studio = {query_data.current_studio: StudioData(locations=[selected_studio_location])}
      query_data.studios = {**query_data.studios, **new_studio}
      chat_manager.update_query_data_studios(message.chat.id, query_data.studios)
    elif selected_studio_location in query_data.studios[query_data.current_studio].locations:
      query_data.studios[query_data.current_studio].locations.remove(selected_studio_location)
      if len(query_data.studios[query_data.current_studio].locations) == 0:
        query_data.studios.pop(query_data.current_studio)
      chat_manager.update_query_data_studios(message.chat.id, query_data.studios)
    else:
      query_data.studios[query_data.current_studio].locations.append(selected_studio_location)
      chat_manager.update_query_data_studios(message.chat.id, query_data.studios)

def locations_callback_query_handler(
  query: "telebot.types.CallbackQuery",
  bot: "telebot.TeleBot",
  chat_manager: "ChatManager",
  keyboard_manager: "KeyboardManager"
) -> None:
  query_data_dict = eval(query.data)
  query_data = chat_manager.get_query_data(query.message.chat.id)
  select_location_handler(query.message, StudioLocation[query_data_dict["location"]], chat_manager)
  text = "*Currently selected studio(s)*\n"
  text += query_data.get_query_str(include_studio=True)

  locations_selection_message = chat_manager.get_locations_selection_message(query.message.chat.id)
  bot.edit_message_text(
    chat_id=locations_selection_message.chat.id,
    message_id=locations_selection_message.id,
    text=text,
    reply_markup=keyboard_manager.get_locations_keyboard(query_data),
    parse_mode="Markdown")
