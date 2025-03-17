import global_variables
import telebot
from common.data_types import StudioData, StudioLocation, StudioType, STUDIO_LOCATIONS_MAP
from copy import copy

def get_studios_keyboard(user_id: int, chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, chat_id)
  button_data = global_variables.USER_MANAGER.get_button_data(user_id, chat_id)
  studios_keyboard = telebot.types.InlineKeyboardMarkup()
  studios_keyboard.add(button_data.studios_buttons_map['Rev'], button_data.studios_buttons_map['Barrys'])
  studios_keyboard.add(button_data.studios_buttons_map['Absolute (Spin)'], button_data.studios_buttons_map['Absolute (Pilates)'])
  studios_keyboard.add(button_data.studios_buttons_map['Ally (Spin)'], button_data.studios_buttons_map['Ally (Pilates)'], button_data.studios_buttons_map['Ally (Recovery)'])
  studios_keyboard.add(button_data.studios_select_all_button, button_data.studios_unselect_all_button)
  studios_keyboard.add(button_data.studios_next_button)
  return studios_keyboard

def get_locations_keyboard(user_id: int, chat_id: int) -> telebot.types.InlineKeyboardMarkup:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, chat_id)
  button_data = global_variables.USER_MANAGER.get_button_data(user_id, chat_id)
  locations_keyboard = telebot.types.InlineKeyboardMarkup()
  if query_data.current_studio == 'Rev':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Rev']['Bugis'], button_data.studios_locations_buttons_map['Rev']['Orchard'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Rev']['TJPG'])
  elif query_data.current_studio == 'Barrys':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Barrys']['Orchard'], button_data.studios_locations_buttons_map['Barrys']['Raffles'])
  elif query_data.current_studio == 'Absolute (Spin)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Centrepoint'], button_data.studios_locations_buttons_map['Absolute (Spin)']['i12'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Star Vista'], button_data.studios_locations_buttons_map['Absolute (Spin)']['Raffles'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Spin)']['Millenia Walk'])
  elif query_data.current_studio == 'Absolute (Pilates)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Centrepoint'], button_data.studios_locations_buttons_map['Absolute (Pilates)']['i12'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Star Vista'], button_data.studios_locations_buttons_map['Absolute (Pilates)']['Raffles'])
    locations_keyboard.add(button_data.studios_locations_buttons_map['Absolute (Pilates)']['Great World'])
  elif query_data.current_studio == 'Ally (Spin)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Ally (Spin)']['Cross Street'])
  elif query_data.current_studio == 'Ally (Pilates)':
    locations_keyboard.add(button_data.studios_locations_buttons_map['Ally (Pilates)']['Cross Street'])
  locations_keyboard.add(button_data.locations_select_all_button, button_data.locations_unselect_all_button)
  locations_keyboard.add(button_data.locations_select_more_studios_button, button_data.locations_next_button)
  return locations_keyboard

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios-selection')
def studios_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  sent_msg = global_variables.BOT.send_message(query.message.chat.id, text, reply_markup=get_studios_keyboard(query.from_user.id, query.message.chat.id), parse_mode='Markdown')
  global_variables.USER_MANAGER.update_button_data_studios_selection_message(query.from_user.id, query.message.chat.id, sent_msg)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'studios')
def studios_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  button_data = global_variables.USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  query_data_dict = eval(query.data)
  selected_studio = StudioType[query_data_dict['studios']]
  if selected_studio == StudioType.Null:
    for studio in button_data.studios_buttons_map:
      button_data.studios_buttons_map[studio] = telebot.types.InlineKeyboardButton(studio, callback_data=button_data.studios_buttons_map[studio].callback_data)
    global_variables.USER_MANAGER.update_button_data_studios_buttons_map(query.from_user.id, query.message.chat.id, button_data.studios_buttons_map)
    global_variables.USER_MANAGER.update_query_data_studios(query.from_user.id, query.message.chat.id, {})
    global_variables.USER_MANAGER.reset_button_data_studios_locations_buttons_map(query.from_user.id, query.message.chat.id)
  elif selected_studio == StudioType.All:
    for studio in button_data.studios_buttons_map:
      button_data.studios_buttons_map[studio] = telebot.types.InlineKeyboardButton(studio + ' ✅', callback_data=button_data.studios_buttons_map[studio].callback_data)
    global_variables.USER_MANAGER.update_button_data_studios_buttons_map(query.from_user.id, query.message.chat.id, button_data.studios_buttons_map)
    global_variables.USER_MANAGER.update_query_data_select_all_studios(query.from_user.id, query.message.chat.id)
    global_variables.USER_MANAGER.update_button_data_select_all_studios_locations_buttons_map(query.from_user.id, query.message.chat.id)
  elif selected_studio == StudioType.AllySpin or selected_studio == StudioType.AllyPilates or selected_studio == StudioType.AllyRecovery:
    global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, selected_studio)
    select_location_handler(query.from_user.id, query.message, StudioLocation.CrossStreet)
  else:
    global_variables.USER_MANAGER.update_query_data_current_studio(query.from_user.id, query.message.chat.id, selected_studio)
    locations_handler(query.from_user.id, query.message)
    return

  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  global_variables.BOT.edit_message_text(
    chat_id=button_data.studios_selection_message.chat.id,
    message_id=button_data.studios_selection_message.id,
    text=text,
    reply_markup=get_studios_keyboard(query.from_user.id, query.message.chat.id),
    parse_mode='Markdown')

def locations_handler(user_id: int, message: telebot.types.Message):
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  sent_msg = global_variables.BOT.send_message(
    message.chat.id, text, reply_markup=get_locations_keyboard(user_id, message.chat.id), parse_mode='Markdown')
  global_variables.USER_MANAGER.update_button_data_locations_selection_message(user_id, message.chat.id, sent_msg)

def select_location_handler(user_id: int, message: telebot.types.Message, selected_studio_location: StudioLocation) -> None:
  query_data = global_variables.USER_MANAGER.get_query_data(user_id, message.chat.id)
  button_data = global_variables.USER_MANAGER.get_button_data(user_id, message.chat.id)
  if selected_studio_location == StudioLocation.Null:
    for location in button_data.studios_locations_buttons_map[query_data.current_studio]:
      button_data.studios_locations_buttons_map[query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location, callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][location].callback_data)
    button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio, callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
    global_variables.USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
    query_data.studios.pop(query_data.current_studio)
    global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
  elif selected_studio_location == StudioLocation.All:
    for location in button_data.studios_locations_buttons_map[query_data.current_studio]:
      button_data.studios_locations_buttons_map[query_data.current_studio][location] = telebot.types.InlineKeyboardButton(location + ' ✅', callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][location].callback_data)
    button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
    global_variables.USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
    if query_data.current_studio not in query_data.studios:
      new_studio = {query_data.current_studio: StudioData(locations=copy(STUDIO_LOCATIONS_MAP[query_data.current_studio]))}
      query_data.studios = {**query_data.studios, **new_studio}
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    else:
      query_data.studios[query_data.current_studio].locations = copy(STUDIO_LOCATIONS_MAP[query_data.current_studio])
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
  else:
    if query_data.current_studio not in query_data.studios:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location + ' ✅',
          callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      global_variables.USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      global_variables.USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      new_studio = {query_data.current_studio: StudioData(locations=[selected_studio_location])}
      query_data.studios = {**query_data.studios, **new_studio}
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    elif selected_studio_location in query_data.studios[query_data.current_studio].locations:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = \
        telebot.types.InlineKeyboardButton(
          selected_studio_location,
          callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      global_variables.USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      global_variables.USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      query_data.studios[query_data.current_studio].locations.remove(selected_studio_location)
      if len(query_data.studios[query_data.current_studio].locations) == 0:
        query_data.studios.pop(query_data.current_studio)
        button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio, callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)
    else:
      button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location] = telebot.types.InlineKeyboardButton(selected_studio_location + ' ✅', callback_data=button_data.studios_locations_buttons_map[query_data.current_studio][selected_studio_location].callback_data)
      button_data.studios_buttons_map[query_data.current_studio] = telebot.types.InlineKeyboardButton(query_data.current_studio + ' ✅', callback_data=button_data.studios_buttons_map[query_data.current_studio].callback_data)
      global_variables.USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      global_variables.USER_MANAGER.update_button_data_studios_locations_buttons_map(user_id, message.chat.id, button_data.studios_locations_buttons_map)
      global_variables.USER_MANAGER.update_button_data_studios_buttons_map(user_id, message.chat.id, button_data.studios_buttons_map)
      query_data.studios[query_data.current_studio].locations.append(selected_studio_location)
      global_variables.USER_MANAGER.update_query_data_studios(user_id, message.chat.id, query_data.studios)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)['step'] == 'locations')
def locations_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  query_data = global_variables.USER_MANAGER.get_query_data(query.from_user.id, query.message.chat.id)
  button_data = global_variables.USER_MANAGER.get_button_data(query.from_user.id, query.message.chat.id)
  select_location_handler(query.from_user.id, query.message, StudioLocation[query_data_dict['location']])
  text = '*Currently selected studio(s)*\n'
  text += query_data.get_query_str(include_studio=True)

  global_variables.BOT.edit_message_text(
    chat_id=button_data.locations_selection_message.chat.id,
    message_id=button_data.locations_selection_message.id,
    text=text,
    reply_markup=get_locations_keyboard(query.from_user.id, query.message.chat.id),
    parse_mode='Markdown')
