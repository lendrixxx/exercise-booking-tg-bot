from common.data_types import STUDIO_LOCATIONS_MAP, StudioData, StudioLocation, StudioType, QueryData
from telebot.types import InlineKeyboardButton

class ButtonData:
  def __init__(self):
    # Locations buttons
    self.locations_selection_message = None
    self.locations_select_all_button = InlineKeyboardButton('Select All', callback_data='{"locations": "All", "step": "locations"}')
    self.locations_unselect_all_button = InlineKeyboardButton('Unselect All', callback_data='{"locations": "Null", "step": "locations"}')
    self.locations_select_more_studios_button = InlineKeyboardButton('◀️ Select More', callback_data='{"step": "locations-select-more-studios"}')
    self.locations_next_button = InlineKeyboardButton('Next ▶️', callback_data='{"step": "studios-next"}')
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map()

    # Days buttons
    self.days_selection_message = None
    self.days_select_all_button = InlineKeyboardButton('Select All', callback_data='{"days": "All", "step": "days"}')
    self.days_unselect_all_button = InlineKeyboardButton('Unselect All', callback_data='{"days": "None", "step": "days"}')
    self.days_back_button = InlineKeyboardButton('◀️ Back', callback_data='{"step": "days-back"}')
    self.days_next_button = InlineKeyboardButton('Next ▶️', callback_data='{"step": "days-next"}')
    self.days_buttons_map = self.__get_default_days_buttons_map()

  def reset_days_buttons_map(self):
    self.days_buttons_map = self.__get_default_days_buttons_map()

  def reset_studios_locations_buttons_map(self):
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map()

  def select_all_studios_locations_buttons_map(self):
    self.studios_locations_buttons_map = self.__get_default_studios_locations_buttons_map(selected=True)

  def __get_default_studios_locations_buttons_map(self, selected: bool=False) -> dict[StudioType, dict[StudioLocation, InlineKeyboardButton]]:
    return {
      'Rev' : {
        'Bugis' : InlineKeyboardButton('Bugis ✅' if selected else 'Bugis', callback_data='{"locations": "Bugis", "step": "locations"}'),
        'Orchard' : InlineKeyboardButton('Orchard ✅' if selected else 'Orchard', callback_data='{"locations": "Orchard", "step": "locations"}'),
        'Suntec' : InlineKeyboardButton('Suntec ✅' if selected else 'Suntec', callback_data='{"locations": "Suntec", "step": "locations"}'),
        'TJPG' : InlineKeyboardButton('TJPG ✅' if selected else 'TJPG', callback_data='{"locations": "TJPG", "step": "locations"}'),
      },
      'Barrys' : {
        'Orchard' : InlineKeyboardButton('Orchard ✅' if selected else 'Orchard', callback_data='{"locations": "Orchard", "step": "locations"}'),
        'Raffles' : InlineKeyboardButton('Raffles ✅' if selected else 'Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
      },
      'Absolute (Spin)' : {
        'Centrepoint' : InlineKeyboardButton('Centrepoint ✅' if selected else 'Centrepoint', callback_data='{"locations": "Centrepoint", "step": "locations"}'),
        'i12' : InlineKeyboardButton('i12 ✅' if selected else 'i12', callback_data='{"locations": "i12", "step": "locations"}'),
        'Star Vista' : InlineKeyboardButton('Star Vista ✅' if selected else 'Star Vista', callback_data='{"locations": "StarVista", "step": "locations"}'),
        'Raffles' : InlineKeyboardButton('Raffles ✅' if selected else 'Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
        'Millenia Walk' : InlineKeyboardButton('Millenia Walk ✅' if selected else 'Millenia Walk', callback_data='{"locations": "MilleniaWalk", "step": "locations"}'),
      },
      'Absolute (Pilates)' : {
        'Centrepoint' : InlineKeyboardButton('Centrepoint ✅' if selected else 'Centrepoint', callback_data='{"locations": "Centrepoint", "step": "locations"}'),
        'i12' : InlineKeyboardButton('i12 ✅' if selected else 'i12', callback_data='{"locations": "i12", "step": "locations"}'),
        'Star Vista' : InlineKeyboardButton('Star Vista ✅' if selected else 'Star Vista', callback_data='{"locations": "StarVista", "step": "locations"}'),
        'Raffles' : InlineKeyboardButton('Raffles ✅' if selected else 'Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
        'Great World' : InlineKeyboardButton('Great World ✅' if selected else 'Great World', callback_data='{"locations": "GreatWorld", "step": "locations"}'),
      },
      'Ally (Spin)' : {
        'Cross Street' : InlineKeyboardButton('Cross Street ✅' if selected else 'Cross Street', callback_data='{"locations": "CrossStreet", "step": "locations"}'),
      },
      'Ally (Pilates)' : {
        'Cross Street' : InlineKeyboardButton('Cross Street ✅' if selected else 'Cross Street', callback_data='{"locations": "CrossStreet", "step": "locations"}'),
      },
    }

  def __get_default_days_buttons_map(self) -> dict[str, InlineKeyboardButton]:
    return {
      'Monday' : InlineKeyboardButton('Monday', callback_data='{"days": "Monday", "step": "days"}'),
      'Tuesday' : InlineKeyboardButton('Tuesday', callback_data='{"days": "Tuesday", "step": "days"}'),
      'Wednesday' : InlineKeyboardButton('Wednesday', callback_data='{"days": "Wednesday", "step": "days"}'),
      'Thursday' : InlineKeyboardButton('Thursday', callback_data='{"days": "Thursday", "step": "days"}'),
      'Friday' : InlineKeyboardButton('Friday', callback_data='{"days": "Friday", "step": "days"}'),
      'Saturday' : InlineKeyboardButton('Saturday', callback_data='{"days": "Saturday", "step": "days"}'),
      'Sunday' : InlineKeyboardButton('Sunday', callback_data='{"days": "Sunday", "step": "days"}'),
    }


class UserManager:
  def __init__(self):
    self.user_query_data = {}
    self.user_button_data = {}

  def reset_query_data(self, user_id, chat_id):
    self.user_query_data[(user_id, chat_id)] = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])

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
      'Rev': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Rev]),
      'Barrys': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.Barrys]),
      'Absolute (Spin)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsoluteSpin]),
      'Absolute (Pilates)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AbsolutePilates]),
      'Ally (Spin)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllySpin]),
      'Ally (Pilates)': StudioData(locations=STUDIO_LOCATIONS_MAP[StudioType.AllyPilates]),
    }

  def update_query_data_days(self, user_id, chat_id, days):
    self.user_query_data[(user_id, chat_id)].days = days

  def update_query_data_weeks(self, user_id, chat_id, weeks):
    self.user_query_data[(user_id, chat_id)].weeks = weeks

  def update_button_data_locations_selection_message(self, user_id, chat_id, locations_selection_message):
    self.user_button_data[(user_id, chat_id)].locations_selection_message = locations_selection_message

  def update_button_data_days_selection_message(self, user_id, chat_id, days_selection_message):
    self.user_button_data[(user_id, chat_id)].days_selection_message = days_selection_message

  def update_button_data_select_all_studios_locations_buttons_map(self, user_id, chat_id):
    self.user_button_data[(user_id, chat_id)].select_all_studios_locations_buttons_map()

  def update_button_data_studios_locations_buttons_map(self, user_id, chat_id, studios_locations_buttons_map):
    self.user_button_data[(user_id, chat_id)].studios_locations_buttons_map = studios_locations_buttons_map

  def update_button_data_days_buttons_map(self, user_id, chat_id, days_buttons_map):
    self.user_button_data[(user_id, chat_id)].days_buttons_map = days_buttons_map

  def get_query_data(self, user_id, chat_id):
    return self.user_query_data[(user_id, chat_id)]

  def get_button_data(self, user_id, chat_id):
    return self.user_button_data[(user_id, chat_id)]