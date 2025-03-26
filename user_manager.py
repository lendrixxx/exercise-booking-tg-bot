from common.data_types import SORTED_DAYS, STUDIO_LOCATIONS_MAP, StudioData, StudioLocation, StudioType, QueryData
from telebot.types import InlineKeyboardButton

class ButtonData:
  def __init__(self):
    # Studios buttons
    self.studios_selection_message = None
    self.studios_select_all_button = InlineKeyboardButton("Select All", callback_data="{'studios': 'All', 'step': 'studios'}")
    self.studios_unselect_all_button = InlineKeyboardButton("Unselect All", callback_data="{'studios': 'Null', 'step': 'studios'}")
    self.studios_next_button = InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")
    self.studios_buttons_map = self.__get_default_studios_buttons_map()

    # Locations buttons
    self.locations_selection_message = None
    self.locations_select_all_button = InlineKeyboardButton("Select All", callback_data="{'location': 'All', 'step': 'locations'}")
    self.locations_unselect_all_button = InlineKeyboardButton("Unselect All", callback_data="{'location': 'Null', 'step': 'locations'}")
    self.locations_select_more_studios_button = InlineKeyboardButton("◀️ Select More", callback_data="{'step': 'studios-selection'}")
    self.locations_next_button = InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map()

    # Days buttons
    self.days_selection_message = None
    self.days_select_all_button = InlineKeyboardButton("Select All", callback_data="{'days': 'All', 'step': 'days'}")
    self.days_unselect_all_button = InlineKeyboardButton("Unselect All", callback_data="{'days': 'None', 'step': 'days'}")
    self.days_next_button = InlineKeyboardButton("Next ▶️", callback_data="{'step': 'days-next'}")
    self.days_buttons_map = self.__get_default_days_buttons_map()

  def reset_studios_buttons_map(self):
    self.studios_buttons_map = self.__get_default_studios_buttons_map()

  def reset_studios_locations_buttons_map(self):
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map()

  def reset_days_buttons_map(self):
    self.days_buttons_map = self.__get_default_days_buttons_map()

  def select_all_studios_locations_buttons_map(self):
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map(selected=True)

  def __get_default_studios_buttons_map(self) -> dict[str, InlineKeyboardButton]:
    return {
      "Rev" : InlineKeyboardButton("Rev", callback_data="{'studios': 'Rev', 'step': 'studios'}"),
      "Barrys" : InlineKeyboardButton("Barrys", callback_data="{'studios': 'Barrys', 'step': 'studios'}"),
      "Absolute (Spin)" : InlineKeyboardButton("Absolute (Spin)", callback_data="{'studios': 'AbsoluteSpin', 'step': 'studios'}"),
      "Absolute (Pilates)" : InlineKeyboardButton("Absolute (Pilates)", callback_data="{'studios': 'AbsolutePilates', 'step': 'studios'}"),
      "Ally (Spin)" : InlineKeyboardButton("Ally (Spin)", callback_data="{'studios': 'AllySpin', 'step': 'studios'}"),
      "Ally (Pilates)" : InlineKeyboardButton("Ally (Pilates)", callback_data="{'studios': 'AllyPilates', 'step': 'studios'}"),
      "Ally (Recovery)" : InlineKeyboardButton("Ally (Recovery)", callback_data="{'studios': 'AllyRecovery', 'step': 'studios'}"),
      "Anarchy" : InlineKeyboardButton("Anarchy", callback_data="{'studios': 'Anarchy', 'step': 'studios'}"),
    }

  def __get_default_studios_locations_buttons_map(self, selected: bool=False) -> dict[StudioType, dict[StudioLocation, InlineKeyboardButton]]:
    return {
      "Rev" : {
        "Bugis" : InlineKeyboardButton("Bugis ✅" if selected else "Bugis", callback_data="{'location': 'Bugis', 'step': 'locations'}"),
        "Orchard" : InlineKeyboardButton("Orchard ✅" if selected else "Orchard", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "TJPG" : InlineKeyboardButton("TJPG ✅" if selected else "TJPG", callback_data="{'location': 'TJPG', 'step': 'locations'}"),
      },
      "Barrys" : {
        "Orchard" : InlineKeyboardButton("Orchard ✅" if selected else "Orchard", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "Raffles" : InlineKeyboardButton("Raffles ✅" if selected else "Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
      },
      "Absolute (Spin)" : {
        "Centrepoint" : InlineKeyboardButton("Centrepoint ✅" if selected else "Centrepoint", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : InlineKeyboardButton("i12 ✅" if selected else "i12", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : InlineKeyboardButton("Star Vista ✅" if selected else "Star Vista", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : InlineKeyboardButton("Raffles ✅" if selected else "Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Millenia Walk" : InlineKeyboardButton("Millenia Walk ✅" if selected else "Millenia Walk", callback_data="{'location': 'MilleniaWalk', 'step': 'locations'}"),
      },
      "Absolute (Pilates)" : {
        "Centrepoint" : InlineKeyboardButton("Centrepoint ✅" if selected else "Centrepoint", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : InlineKeyboardButton("i12 ✅" if selected else "i12", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : InlineKeyboardButton("Star Vista ✅" if selected else "Star Vista", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : InlineKeyboardButton("Raffles ✅" if selected else "Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Great World" : InlineKeyboardButton("Great World ✅" if selected else "Great World", callback_data="{'location': 'GreatWorld', 'step': 'locations'}"),
      },
      "Ally (Spin)" : {
        "Cross Street" : InlineKeyboardButton("Cross Street ✅" if selected else "Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Pilates)" : {
        "Cross Street" : InlineKeyboardButton("Cross Street ✅" if selected else "Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Recovery)" : {
        "Cross Street" : InlineKeyboardButton("Cross Street ✅" if selected else "Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Anarchy" : {
        "Robinson" : InlineKeyboardButton("Robinson ✅" if selected else "Robinson", callback_data="{'location': 'Robinson', 'step': 'locations'}"),
      },
    }

  def __get_default_days_buttons_map(self) -> dict[str, InlineKeyboardButton]:
    return {
      "Monday" : InlineKeyboardButton("Monday ✅", callback_data="{'days': 'Monday', 'step': 'days'}"),
      "Tuesday" : InlineKeyboardButton("Tuesday ✅", callback_data="{'days': 'Tuesday', 'step': 'days'}"),
      "Wednesday" : InlineKeyboardButton("Wednesday ✅", callback_data="{'days': 'Wednesday', 'step': 'days'}"),
      "Thursday" : InlineKeyboardButton("Thursday ✅", callback_data="{'days': 'Thursday', 'step': 'days'}"),
      "Friday" : InlineKeyboardButton("Friday ✅", callback_data="{'days': 'Friday', 'step': 'days'}"),
      "Saturday" : InlineKeyboardButton("Saturday ✅", callback_data="{'days': 'Saturday', 'step': 'days'}"),
      "Sunday" : InlineKeyboardButton("Sunday ✅", callback_data="{'days': 'Sunday', 'step': 'days'}"),
    }


class UserManager:
  def __init__(self):
    self.user_query_data = {}
    self.user_button_data = {}

  def reset_query_data(self, user_id, chat_id):
    self.user_query_data[(user_id, chat_id)] = QueryData(studios={}, current_studio=StudioType.Null, weeks=1, days=SORTED_DAYS, start_times=[], class_name_filter="")

  def reset_button_data(self, user_id, chat_id):
    self.user_button_data[(user_id, chat_id)] = ButtonData()

  def reset_button_data_days_buttons_map(self, user_id, chat_id):
    self.user_button_data[(user_id, chat_id)].reset_days_buttons_map()

  def reset_button_data_studios_locations_buttons_map(self, user_id, chat_id):
    self.user_button_data[(user_id, chat_id)].reset_studios_locations_buttons_map()

  def update_query_data_current_studio(self, user_id, chat_id, current_studio):
    self.user_query_data[(user_id, chat_id)].current_studio = current_studio

  def update_query_data_studios(self, user_id, chat_id, studios):
    self.user_query_data[(user_id, chat_id)].studios = studios

  def update_query_data_select_all_studios(self, user_id, chat_id):
    self.user_query_data[(user_id, chat_id)].studios = {
      StudioType.Rev : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Rev]),
      StudioType.Barrys : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Barrys]),
      StudioType.AbsoluteSpin : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsoluteSpin]),
      StudioType.AbsolutePilates : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsolutePilates]),
      StudioType.AllySpin : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllySpin]),
      StudioType.AllyPilates : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyPilates]),
      StudioType.AllyRecovery : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyRecovery]),
      StudioType.Anarchy : StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Anarchy]),
    }

  def update_query_data_days(self, user_id, chat_id, days):
    self.user_query_data[(user_id, chat_id)].days = days

  def update_query_data_weeks(self, user_id, chat_id, weeks):
    self.user_query_data[(user_id, chat_id)].weeks = weeks

  def update_button_data_studios_selection_message(self, user_id, chat_id, studios_selection_message):
    self.user_button_data[(user_id, chat_id)].studios_selection_message = studios_selection_message

  def update_button_data_locations_selection_message(self, user_id, chat_id, locations_selection_message):
    self.user_button_data[(user_id, chat_id)].locations_selection_message = locations_selection_message

  def update_button_data_days_selection_message(self, user_id, chat_id, days_selection_message):
    self.user_button_data[(user_id, chat_id)].days_selection_message = days_selection_message

  def update_button_data_select_all_studios_locations_buttons_map(self, user_id, chat_id):
    self.user_button_data[(user_id, chat_id)].select_all_studios_locations_buttons_map()

  def update_button_data_studios_buttons_map(self, user_id, chat_id, studios_buttons_map):
    self.user_button_data[(user_id, chat_id)].studios_buttons_map = studios_buttons_map

  def update_button_data_studios_locations_buttons_map(self, user_id, chat_id, studios_locations_buttons_map):
    self.user_button_data[(user_id, chat_id)].studios_locations_buttons_map = studios_locations_buttons_map

  def update_button_data_days_buttons_map(self, user_id, chat_id, days_buttons_map):
    self.user_button_data[(user_id, chat_id)].days_buttons_map = days_buttons_map

  def get_query_data(self, user_id, chat_id):
    return self.user_query_data[(user_id, chat_id)]

  def get_button_data(self, user_id, chat_id):
    return self.user_button_data[(user_id, chat_id)]