import global_variables
import telebot
import time
from common.data_types import StudioType
from menu.main_page_handler import main_page_handler

@global_variables.BOT.message_handler(commands=["instructors"])
def instructors_list_handler(message: telebot.types.Message) -> None:
  global_variables.HISTORY_HANDLER.add(int(time.time()), message.from_user.id, message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, "instructors")
  text = "*Rev Instructors:* " + ", ".join(global_variables.REV_INSTRUCTOR_NAMES) + "\n\n"
  text += "*Barrys Instructors:* " + ", ".join(global_variables.BARRYS_INSTRUCTOR_NAMES) + "\n\n"
  text += "*Absolute Instructors:* " + ", ".join(global_variables.ABSOLUTE_INSTRUCTOR_NAMES) + "\n\n"
  text += "*Ally Instructors:* " + ", ".join(global_variables.ALLY_INSTRUCTOR_NAMES) + "\n\n"
  text += "*Anarchy Instructors:* " + ", ".join(global_variables.ANARCHY_INSTRUCTOR_NAMES) + "\n\n"

  global_variables.CHAT_MANAGER.add_message_id_to_delete(message.chat.id, message.id)
  global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "instructors-selection")
def instructors_selection_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data_dict = eval(query.data)
  instructors_selection_handler(query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "show-instructors")
def show_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(query.message.chat.id)
  text = ""
  if StudioType.Rev in query_data.studios:
    text += "*Rev Instructors:* " + ", ".join(global_variables.REV_INSTRUCTOR_NAMES) + "\n\n"
  if StudioType.Barrys in query_data.studios:
    text += "*Barrys Instructors:* " + ", ".join(global_variables.BARRYS_INSTRUCTOR_NAMES) + "\n\n"
  if StudioType.AbsoluteSpin in query_data.studios or StudioType.AbsolutePilates in query_data.studios:
    text += "*Absolute Instructors:* " + ", ".join(global_variables.ABSOLUTE_INSTRUCTOR_NAMES) + "\n\n"
  if StudioType.AllySpin in query_data.studios or StudioType.AllyPilates in query_data.studios:
    text += "*Ally Instructors:* " + ", ".join(global_variables.ALLY_INSTRUCTOR_NAMES) + "\n\n"
  if StudioType.AllyRecovery in query_data.studios:
    text += "No instructors for *Ally (Recovery)\n\n"
  if StudioType.Anarchy in query_data.studios:
    text += "*Anarchy Instructors:* " + ", ".join(global_variables.ANARCHY_INSTRUCTOR_NAMES) + "\n\n"

  global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
  instructors_selection_handler(query.message)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "rev-instructors")
def rev_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *chloe*, *jerlyn*, *zai*\nEnter '*all*' to check for all instructors"

  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Rev")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.REV_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "barrys-instructors")
def barrys_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *ria*, *gino*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Barrys")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.BARRYS_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "absolute-spin-instructors")
def absolute_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *chin*, *ria*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Absolute (Spin)")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.ABSOLUTE_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "absolute-pilates-instructors")
def absolute_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *daniella*, *vnex*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Absolute (Pilates)")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.ABSOLUTE_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "ally-spin-instructors")
def ally_spin_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *samuel*, *jasper*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Ally (Spin)")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.ALLY_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "ally-pilates-instructors")
def ally_pilates_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *candice*, *ruth*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Ally (Pilates)")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.ALLY_INSTRUCTORID_MAP)

@global_variables.BOT.callback_query_handler(func=lambda query: eval(query.data)["step"] == "anarchy-instructors")
def anarchy_instructors_callback_query_handler(query: telebot.types.CallbackQuery) -> None:
  text = "Enter instructor names separated by a comma\ne.g.: *lyon*, *isabelle*\nEnter '*all*' to check for all instructors"
  global_variables.CHAT_MANAGER.update_query_data_current_studio(query.message.chat.id, "Anarchy")
  sent_msg = global_variables.CHAT_MANAGER.send_prompt(chat_id=query.message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=True)
  global_variables.BOT.register_next_step_handler(sent_msg, instructors_input_handler, global_variables.ANARCHY_INSTRUCTORID_MAP)

def instructors_input_handler(message: telebot.types.Message, instructorid_map: dict[str, int]) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  updated_instructors_list = [x.strip() for x in message.text.lower().split(",")]
  if "all" in updated_instructors_list:
    query_data.studios[query_data.current_studio].instructors = ["All"]
    global_variables.CHAT_MANAGER.update_query_data_studios(message.chat.id, query_data.studios)
  else:
    invalid_instructors = []
    if "/" in updated_instructors_list: # Some names contain "/" which should not be considered as a valid name
      invalid_instructors.append("/")

    for instructor in updated_instructors_list:
      instructor_in_map = (any(instructor in instructor_in_map.split(" ") for instructor_in_map in instructorid_map)
        or any(instructor == instructor_in_map for instructor_in_map in instructorid_map)
        or any(instructor == instructor_in_map.split(".")[0] for instructor_in_map in instructorid_map))
      if not instructor_in_map:
        invalid_instructors.append(instructor)

    if len(invalid_instructors) > 0:
      updated_instructors_list = [
        instructor for instructor
        in updated_instructors_list
        if instructor not in invalid_instructors
      ]
      global_variables.CHAT_MANAGER.update_query_data_studios(message.chat.id, query_data.studios)
      text = f"Failed to find instructor(s): {', '.join(invalid_instructors)}"
      global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)

    if len(updated_instructors_list) > 0:
      query_data.studios[query_data.current_studio].instructors = updated_instructors_list

  instructors_selection_handler(message)

def instructors_selection_handler(message: telebot.types.Message) -> None:
  query_data = global_variables.CHAT_MANAGER.get_query_data(message.chat.id)
  if len(query_data.studios) == 0:
    text = "No studio selected. Please select a studio first"
    global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=None, delete_sent_msg_in_future=False)
    main_page_handler(message)
    return

  text = "*Currently selected instructor(s)*\n"
  text += query_data.get_query_str(include_instructors=True)

  keyboard = telebot.types.InlineKeyboardMarkup()
  if StudioType.Rev in query_data.studios:
    rev_instructors_button = telebot.types.InlineKeyboardButton("Enter Rev Instructor(s)", callback_data="{'step': 'rev-instructors'}")
    keyboard.add(rev_instructors_button)
  if StudioType.Barrys in query_data.studios:
    barrys_instructors_button = telebot.types.InlineKeyboardButton("Enter Barrys Instructor(s)", callback_data="{'step': 'barrys-instructors'}")
    keyboard.add(barrys_instructors_button)
  if StudioType.AbsoluteSpin in query_data.studios:
    absolute_spin_instructors_button = telebot.types.InlineKeyboardButton("Enter Absolute (Spin) Instructor(s)", callback_data="{'step': 'absolute-spin-instructors'}")
    keyboard.add(absolute_spin_instructors_button)
  if StudioType.AbsolutePilates in query_data.studios:
    absolute_pilates_instructors_button = telebot.types.InlineKeyboardButton("Enter Absolute (Pilates) Instructor(s)", callback_data="{'step': 'absolute-pilates-instructors'}")
    keyboard.add(absolute_pilates_instructors_button)
  if StudioType.AllySpin in query_data.studios:
    ally_spin_instructors_button = telebot.types.InlineKeyboardButton("Enter Ally (Spin) Instructor(s)", callback_data="{'step': 'ally-spin-instructors'}")
    keyboard.add(ally_spin_instructors_button)
  if StudioType.AllyPilates in query_data.studios:
    ally_pilates_instructors_button = telebot.types.InlineKeyboardButton("Enter Ally (Pilates) Instructor(s)", callback_data="{'step': 'ally-pilates-instructors'}")
    keyboard.add(ally_pilates_instructors_button)
  if StudioType.Anarchy in query_data.studios:
    anarchy_instructors_button = telebot.types.InlineKeyboardButton("Enter Anarchy Instructor(s)", callback_data="{'step': 'anarchy-instructors'}")
    keyboard.add(anarchy_instructors_button)

  show_instructors_button = telebot.types.InlineKeyboardButton("Show Names of Instructors", callback_data="{'step': 'show-instructors'}")
  next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")
  keyboard.add(show_instructors_button)
  keyboard.add(next_button)

  global_variables.CHAT_MANAGER.send_prompt(chat_id=message.chat.id, text=text, reply_markup=keyboard, delete_sent_msg_in_future=True)
