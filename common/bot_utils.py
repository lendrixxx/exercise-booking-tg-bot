import telebot
from common.data_types import StudioLocation, StudioType

def get_default_studios_locations_buttons_map() -> dict[StudioType, dict[StudioLocation, telebot.types.InlineKeyboardButton]]:
  return {
    'Rev' : {
      'Bugis' : telebot.types.InlineKeyboardButton('Bugis', callback_data='{"locations": "Bugis", "step": "locations"}'),
      'Orchard' : telebot.types.InlineKeyboardButton('Orchard', callback_data='{"locations": "Orchard", "step": "locations"}'),
      'Suntec' : telebot.types.InlineKeyboardButton('Suntec', callback_data='{"locations": "Suntec", "step": "locations"}'),
      'TJPG' : telebot.types.InlineKeyboardButton('TJPG', callback_data='{"locations": "TJPG", "step": "locations"}'),
    },
    'Barrys' : {
      'Orchard' : telebot.types.InlineKeyboardButton('Orchard', callback_data='{"locations": "Orchard", "step": "locations"}'),
      'Raffles' : telebot.types.InlineKeyboardButton('Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
    },
    'Absolute (Spin)' : {
      'Centrepoint' : telebot.types.InlineKeyboardButton('Centrepoint', callback_data='{"locations": "Centrepoint", "step": "locations"}'),
      'i12' : telebot.types.InlineKeyboardButton('i12', callback_data='{"locations": "i12", "step": "locations"}'),
      'Star Vista' : telebot.types.InlineKeyboardButton('Star Vista', callback_data='{"locations": "StarVista", "step": "locations"}'),
      'Raffles' : telebot.types.InlineKeyboardButton('Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
      'Millenia Walk' : telebot.types.InlineKeyboardButton('Millenia Walk', callback_data='{"locations": "MilleniaWalk", "step": "locations"}'),
    },
    'Absolute (Pilates)' : {
      'Centrepoint' : telebot.types.InlineKeyboardButton('Centrepoint', callback_data='{"locations": "Centrepoint", "step": "locations"}'),
      'i12' : telebot.types.InlineKeyboardButton('i12', callback_data='{"locations": "i12", "step": "locations"}'),
      'Star Vista' : telebot.types.InlineKeyboardButton('Star Vista', callback_data='{"locations": "StarVista", "step": "locations"}'),
      'Raffles' : telebot.types.InlineKeyboardButton('Raffles', callback_data='{"locations": "Raffles", "step": "locations"}'),
      'Great World' : telebot.types.InlineKeyboardButton('Great World', callback_data='{"locations": "GreatWorld", "step": "locations"}'),
    },
    'Ally (Spin)' : {
      'Cross Street' : telebot.types.InlineKeyboardButton('Cross Street', callback_data='{"locations": "CrossStreet", "step": "locations"}'),
    },
    'Ally (Pilates)' : {
      'Cross Street' : telebot.types.InlineKeyboardButton('Cross Street', callback_data='{"locations": "CrossStreet", "step": "locations"}'),
    },
  }

def get_default_days_buttons_map() -> dict[str, telebot.types.InlineKeyboardButton]:
  return {
    'Monday' : telebot.types.InlineKeyboardButton('Monday', callback_data='{"days": "Monday", "step": "days"}'),
    'Tuesday' : telebot.types.InlineKeyboardButton('Tuesday', callback_data='{"days": "Tuesday", "step": "days"}'),
    'Wednesday' : telebot.types.InlineKeyboardButton('Wednesday', callback_data='{"days": "Wednesday", "step": "days"}'),
    'Thursday' : telebot.types.InlineKeyboardButton('Thursday', callback_data='{"days": "Thursday", "step": "days"}'),
    'Friday' : telebot.types.InlineKeyboardButton('Friday', callback_data='{"days": "Friday", "step": "days"}'),
    'Saturday' : telebot.types.InlineKeyboardButton('Saturday', callback_data='{"days": "Saturday", "step": "days"}'),
    'Sunday' : telebot.types.InlineKeyboardButton('Sunday', callback_data='{"days": "Sunday", "step": "days"}'),
  }