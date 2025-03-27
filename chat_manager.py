import global_variables
from common.data_types import SORTED_DAYS, STUDIO_LOCATIONS_MAP, StudioData, StudioLocation, StudioType, QueryData
from telebot.types import InlineKeyboardButton

class ChatManager:
  class MessagesToEdit:
    def __init__(self):
      self.days_selection_message = None
      self.studios_selection_message = None
      self.locations_selection_message = None

  def __init__(self):
    self.chat_query_data = {}
    self.chat_message_ids_to_delete = {}
    self.chat_messages_to_edit = {}

  def reset_query_and_messages_to_edit_data(self, chat_id):
    self.chat_query_data[chat_id] = QueryData(studios={}, current_studio=StudioType.Null, weeks=1, days=SORTED_DAYS, start_times=[], class_name_filter="")
    self.chat_messages_to_edit[chat_id] = ChatManager.MessagesToEdit()

  def update_query_data_current_studio(self, chat_id, current_studio):
    self.chat_query_data[chat_id].current_studio = current_studio

  def update_query_data_studios(self, chat_id, studios):
    self.chat_query_data[chat_id].studios = studios

  def update_query_data_select_all_studios(self, chat_id):
    self.chat_query_data[chat_id].studios = {
      StudioType.Rev : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Rev]),
      StudioType.Barrys : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Barrys]),
      StudioType.AbsoluteSpin : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsoluteSpin]),
      StudioType.AbsolutePilates : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsolutePilates]),
      StudioType.AllySpin : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllySpin]),
      StudioType.AllyPilates : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyPilates]),
      StudioType.AllyRecovery : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyRecovery]),
      StudioType.Anarchy : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Anarchy]),
    }

  def update_query_data_days(self, chat_id, days):
    self.chat_query_data[chat_id].days = days

  def update_query_data_weeks(self, chat_id, weeks):
    self.chat_query_data[chat_id].weeks = weeks

  def update_button_data_studios_selection_message(self, chat_id, studios_selection_message):
    self.chat_messages_to_edit[chat_id].studios_selection_message = studios_selection_message

  def update_button_data_locations_selection_message(self, chat_id, locations_selection_message):
    self.chat_messages_to_edit[chat_id].locations_selection_message = locations_selection_message

  def update_button_data_days_selection_message(self, chat_id, days_selection_message):
    self.chat_messages_to_edit[chat_id].days_selection_message = days_selection_message

  def add_message_id_to_delete(self, chat_id, message_id):
    if chat_id in self.chat_message_ids_to_delete:
      self.chat_message_ids_to_delete[chat_id].append(message_id)
    else:
      self.chat_message_ids_to_delete[chat_id] = [message_id]

  def get_query_data(self, chat_id):
    return self.chat_query_data[chat_id]

  def get_days_selection_message(self, chat_id):
    return self.chat_messages_to_edit[chat_id].days_selection_message

  def get_studios_selection_message(self, chat_id):
    return self.chat_messages_to_edit[chat_id].studios_selection_message

  def get_locations_selection_message(self, chat_id):
    return self.chat_messages_to_edit[chat_id].locations_selection_message

  def send_prompt(self, chat_id, text, reply_markup, delete_sent_msg_in_future):
    message_ids_to_delete = self.chat_message_ids_to_delete.pop(chat_id, None)
    if message_ids_to_delete is not None:
      global_variables.BOT.delete_messages(chat_id, message_ids_to_delete)

    sent_msg = global_variables.BOT.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="Markdown")
    if delete_sent_msg_in_future:
      self.add_message_id_to_delete(chat_id, sent_msg.id)

    return sent_msg