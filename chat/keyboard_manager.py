import telebot
from common.data_types import StudioLocation, StudioType

class KeyboardManager:
  def __init__(self) -> None:
    # Studios buttons
    self.studios_select_all_button = telebot.types.InlineKeyboardButton("Select All", callback_data="{'studios': 'All', 'step': 'studios'}")
    self.studios_unselect_all_button = telebot.types.InlineKeyboardButton("Unselect All", callback_data="{'studios': 'Null', 'step': 'studios'}")
    self.studios_next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")
    self.studios_buttons_unselected_map = {
      "Rev" : telebot.types.InlineKeyboardButton("Rev", callback_data="{'studios': 'Rev', 'step': 'studios'}"),
      "Barrys" : telebot.types.InlineKeyboardButton("Barrys", callback_data="{'studios': 'Barrys', 'step': 'studios'}"),
      "Absolute (Spin)" : telebot.types.InlineKeyboardButton("Absolute (Spin)", callback_data="{'studios': 'AbsoluteSpin', 'step': 'studios'}"),
      "Absolute (Pilates)" : telebot.types.InlineKeyboardButton("Absolute (Pilates)", callback_data="{'studios': 'AbsolutePilates', 'step': 'studios'}"),
      "Ally (Spin)" : telebot.types.InlineKeyboardButton("Ally (Spin)", callback_data="{'studios': 'AllySpin', 'step': 'studios'}"),
      "Ally (Pilates)" : telebot.types.InlineKeyboardButton("Ally (Pilates)", callback_data="{'studios': 'AllyPilates', 'step': 'studios'}"),
      "Ally (Recovery)" : telebot.types.InlineKeyboardButton("Ally (Recovery)", callback_data="{'studios': 'AllyRecovery', 'step': 'studios'}"),
      "Anarchy" : telebot.types.InlineKeyboardButton("Anarchy", callback_data="{'studios': 'Anarchy', 'step': 'studios'}"),
    }
    self.studios_buttons_selected_map = {
      "Rev" : telebot.types.InlineKeyboardButton("Rev ✅", callback_data="{'studios': 'Rev', 'step': 'studios'}"),
      "Barrys" : telebot.types.InlineKeyboardButton("Barrys ✅", callback_data="{'studios': 'Barrys', 'step': 'studios'}"),
      "Absolute (Spin)" : telebot.types.InlineKeyboardButton("Absolute (Spin) ✅", callback_data="{'studios': 'AbsoluteSpin', 'step': 'studios'}"),
      "Absolute (Pilates)" : telebot.types.InlineKeyboardButton("Absolute (Pilates) ✅", callback_data="{'studios': 'AbsolutePilates', 'step': 'studios'}"),
      "Ally (Spin)" : telebot.types.InlineKeyboardButton("Ally (Spin) ✅", callback_data="{'studios': 'AllySpin', 'step': 'studios'}"),
      "Ally (Pilates)" : telebot.types.InlineKeyboardButton("Ally (Pilates) ✅", callback_data="{'studios': 'AllyPilates', 'step': 'studios'}"),
      "Ally (Recovery)" : telebot.types.InlineKeyboardButton("Ally (Recovery) ✅", callback_data="{'studios': 'AllyRecovery', 'step': 'studios'}"),
      "Anarchy" : telebot.types.InlineKeyboardButton("Anarchy ✅", callback_data="{'studios': 'Anarchy', 'step': 'studios'}"),
    }

    # Locations buttons
    self.locations_select_all_button = telebot.types.InlineKeyboardButton("Select All", callback_data="{'location': 'All', 'step': 'locations'}")
    self.locations_unselect_all_button = telebot.types.InlineKeyboardButton("Unselect All", callback_data="{'location': 'Null', 'step': 'locations'}")
    self.locations_select_more_studios_button = telebot.types.InlineKeyboardButton("◀️ Select More", callback_data="{'step': 'studios-selection'}")
    self.locations_next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'main-page-handler'}")
    self.studios_locations_buttons_unselected_map = {
      "Rev" : {
        "Bugis" : telebot.types.InlineKeyboardButton("Bugis", callback_data="{'location': 'Bugis', 'step': 'locations'}"),
        "Orchard" : telebot.types.InlineKeyboardButton("Orchard", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "TJPG" : telebot.types.InlineKeyboardButton("TJPG", callback_data="{'location': 'TJPG', 'step': 'locations'}"),
      },
      "Barrys" : {
        "Orchard" : telebot.types.InlineKeyboardButton("Orchard", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
      },
      "Absolute (Spin)" : {
        "Centrepoint" : telebot.types.InlineKeyboardButton("Centrepoint", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : telebot.types.InlineKeyboardButton("i12", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : telebot.types.InlineKeyboardButton("Star Vista", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Millenia Walk" : telebot.types.InlineKeyboardButton("Millenia Walk", callback_data="{'location': 'MilleniaWalk', 'step': 'locations'}"),
      },
      "Absolute (Pilates)" : {
        "Centrepoint" : telebot.types.InlineKeyboardButton("Centrepoint", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : telebot.types.InlineKeyboardButton("i12", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : telebot.types.InlineKeyboardButton("Star Vista", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Great World" : telebot.types.InlineKeyboardButton("Great World", callback_data="{'location': 'GreatWorld', 'step': 'locations'}"),
      },
      "Ally (Spin)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Pilates)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Recovery)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Anarchy" : {
        "Robinson" : telebot.types.InlineKeyboardButton("Robinson", callback_data="{'location': 'Robinson', 'step': 'locations'}"),
      },
    }
    self.studios_locations_buttons_selected_map = {
      "Rev" : {
        "Bugis" : telebot.types.InlineKeyboardButton("Bugis ✅", callback_data="{'location': 'Bugis', 'step': 'locations'}"),
        "Orchard" : telebot.types.InlineKeyboardButton("Orchard ✅", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "TJPG" : telebot.types.InlineKeyboardButton("TJPG ✅", callback_data="{'location': 'TJPG', 'step': 'locations'}"),
      },
      "Barrys" : {
        "Orchard" : telebot.types.InlineKeyboardButton("Orchard ✅", callback_data="{'location': 'Orchard', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles ✅", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
      },
      "Absolute (Spin)" : {
        "Centrepoint" : telebot.types.InlineKeyboardButton("Centrepoint ✅", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : telebot.types.InlineKeyboardButton("i12 ✅", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : telebot.types.InlineKeyboardButton("Star Vista ✅", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles ✅", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Millenia Walk" : telebot.types.InlineKeyboardButton("Millenia Walk ✅", callback_data="{'location': 'MilleniaWalk', 'step': 'locations'}"),
      },
      "Absolute (Pilates)" : {
        "Centrepoint" : telebot.types.InlineKeyboardButton("Centrepoint ✅", callback_data="{'location': 'Centrepoint', 'step': 'locations'}"),
        "i12" : telebot.types.InlineKeyboardButton("i12 ✅", callback_data="{'location': 'i12', 'step': 'locations'}"),
        "Star Vista" : telebot.types.InlineKeyboardButton("Star Vista ✅", callback_data="{'location': 'StarVista', 'step': 'locations'}"),
        "Raffles" : telebot.types.InlineKeyboardButton("Raffles ✅", callback_data="{'location': 'Raffles', 'step': 'locations'}"),
        "Great World" : telebot.types.InlineKeyboardButton("Great World ✅", callback_data="{'location': 'GreatWorld', 'step': 'locations'}"),
      },
      "Ally (Spin)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street ✅", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Pilates)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street ✅", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Ally (Recovery)" : {
        "Cross Street" : telebot.types.InlineKeyboardButton("Cross Street ✅", callback_data="{'location': 'CrossStreet', 'step': 'locations'}"),
      },
      "Anarchy" : {
        "Robinson" : telebot.types.InlineKeyboardButton("Robinson ✅", callback_data="{'location': 'Robinson', 'step': 'locations'}"),
      },
    }

    # Days buttons
    self.days_select_all_button = telebot.types.InlineKeyboardButton("Select All", callback_data="{'days': 'All', 'step': 'days'}")
    self.days_unselect_all_button = telebot.types.InlineKeyboardButton("Unselect All", callback_data="{'days': 'None', 'step': 'days'}")
    self.days_next_button = telebot.types.InlineKeyboardButton("Next ▶️", callback_data="{'step': 'days-next'}")
    self.days_buttons_unselected_map = {
      "Monday" : telebot.types.InlineKeyboardButton("Monday", callback_data="{'days': 'Monday', 'step': 'days'}"),
      "Tuesday" : telebot.types.InlineKeyboardButton("Tuesday", callback_data="{'days': 'Tuesday', 'step': 'days'}"),
      "Wednesday" : telebot.types.InlineKeyboardButton("Wednesday", callback_data="{'days': 'Wednesday', 'step': 'days'}"),
      "Thursday" : telebot.types.InlineKeyboardButton("Thursday", callback_data="{'days': 'Thursday', 'step': 'days'}"),
      "Friday" : telebot.types.InlineKeyboardButton("Friday", callback_data="{'days': 'Friday', 'step': 'days'}"),
      "Saturday" : telebot.types.InlineKeyboardButton("Saturday", callback_data="{'days': 'Saturday', 'step': 'days'}"),
      "Sunday" : telebot.types.InlineKeyboardButton("Sunday", callback_data="{'days': 'Sunday', 'step': 'days'}"),
    }
    self.days_buttons_selected_map = {
      "Monday" : telebot.types.InlineKeyboardButton("Monday ✅", callback_data="{'days': 'Monday', 'step': 'days'}"),
      "Tuesday" : telebot.types.InlineKeyboardButton("Tuesday ✅", callback_data="{'days': 'Tuesday', 'step': 'days'}"),
      "Wednesday" : telebot.types.InlineKeyboardButton("Wednesday ✅", callback_data="{'days': 'Wednesday', 'step': 'days'}"),
      "Thursday" : telebot.types.InlineKeyboardButton("Thursday ✅", callback_data="{'days': 'Thursday', 'step': 'days'}"),
      "Friday" : telebot.types.InlineKeyboardButton("Friday ✅", callback_data="{'days': 'Friday', 'step': 'days'}"),
      "Saturday" : telebot.types.InlineKeyboardButton("Saturday ✅", callback_data="{'days': 'Saturday', 'step': 'days'}"),
      "Sunday" : telebot.types.InlineKeyboardButton("Sunday ✅", callback_data="{'days': 'Sunday', 'step': 'days'}"),
    }

  def get_studios_keyboard(self, query: "QueryData") -> telebot.types.InlineKeyboardMarkup:
    studios_keyboard = telebot.types.InlineKeyboardMarkup()

    studio_buttons = {
      StudioType.Rev : self.studios_buttons_unselected_map["Rev"],
      StudioType.Barrys : self.studios_buttons_unselected_map["Barrys"],
      StudioType.AbsoluteSpin : self.studios_buttons_unselected_map["Absolute (Spin)"],
      StudioType.AbsolutePilates : self.studios_buttons_unselected_map["Absolute (Pilates)"],
      StudioType.AllySpin : self.studios_buttons_unselected_map["Ally (Spin)"],
      StudioType.AllyPilates : self.studios_buttons_unselected_map["Ally (Pilates)"],
      StudioType.AllyRecovery : self.studios_buttons_unselected_map["Ally (Recovery)"],
      StudioType.Anarchy : self.studios_buttons_unselected_map["Anarchy"],
    }

    for studio in studio_buttons:
      if studio in query.studios:
        studio_buttons[studio] = self.studios_buttons_selected_map[studio.value]

    studios_keyboard.add(studio_buttons[StudioType.Rev], studio_buttons[StudioType.Barrys])
    studios_keyboard.add(studio_buttons[StudioType.AbsoluteSpin], studio_buttons[StudioType.AbsolutePilates])
    studios_keyboard.add(studio_buttons[StudioType.AllySpin], studio_buttons[StudioType.AllyPilates])
    studios_keyboard.add(studio_buttons[StudioType.AllyRecovery], studio_buttons[StudioType.Anarchy])
    studios_keyboard.add(self.studios_select_all_button, self.studios_unselect_all_button)
    studios_keyboard.add(self.studios_next_button)
    return studios_keyboard

  def get_locations_keyboard(self, query: "QueryData") -> telebot.types.InlineKeyboardMarkup:
    locations_keyboard = telebot.types.InlineKeyboardMarkup()
    studio_locations_buttons = {
      StudioType.Rev : {
        StudioLocation.Bugis: self.studios_locations_buttons_unselected_map["Rev"]["Bugis"],
        StudioLocation.Orchard: self.studios_locations_buttons_unselected_map["Rev"]["Orchard"],
        StudioLocation.TJPG: self.studios_locations_buttons_unselected_map["Rev"]["TJPG"],
      },
      StudioType.Barrys : {
        StudioLocation.Orchard: self.studios_locations_buttons_unselected_map["Barrys"]["Orchard"],
        StudioLocation.Raffles: self.studios_locations_buttons_unselected_map["Barrys"]["Raffles"],
      },
      StudioType.AbsoluteSpin : {
        StudioLocation.Centrepoint: self.studios_locations_buttons_unselected_map["Absolute (Spin)"]["Centrepoint"],
        StudioLocation.i12: self.studios_locations_buttons_unselected_map["Absolute (Spin)"]["i12"],
        StudioLocation.StarVista: self.studios_locations_buttons_unselected_map["Absolute (Spin)"]["Star Vista"],
        StudioLocation.Raffles: self.studios_locations_buttons_unselected_map["Absolute (Spin)"]["Raffles"],
        StudioLocation.MilleniaWalk: self.studios_locations_buttons_unselected_map["Absolute (Spin)"]["Millenia Walk"],
      },
      StudioType.AbsolutePilates : {
        StudioLocation.Centrepoint: self.studios_locations_buttons_unselected_map["Absolute (Pilates)"]["Centrepoint"],
        StudioLocation.i12: self.studios_locations_buttons_unselected_map["Absolute (Pilates)"]["i12"],
        StudioLocation.StarVista: self.studios_locations_buttons_unselected_map["Absolute (Pilates)"]["Star Vista"],
        StudioLocation.Raffles: self.studios_locations_buttons_unselected_map["Absolute (Pilates)"]["Raffles"],
        StudioLocation.GreatWorld: self.studios_locations_buttons_unselected_map["Absolute (Pilates)"]["Great World"],
      },
    }

    if query.current_studio in query.studios:
      current_studio_data = query.studios[query.current_studio]
      for location in studio_locations_buttons[query.current_studio]:
        if location in current_studio_data.locations:
          studio_locations_buttons[query.current_studio][location] = self.studios_locations_buttons_selected_map[query.current_studio.value][location.value]

    if query.current_studio == "Rev":
      locations_keyboard.add(studio_locations_buttons["Rev"]["Bugis"], studio_locations_buttons["Rev"]["Orchard"])
      locations_keyboard.add(studio_locations_buttons["Rev"]["TJPG"])
    elif query.current_studio == "Barrys":
      locations_keyboard.add(studio_locations_buttons["Barrys"]["Orchard"], studio_locations_buttons["Barrys"]["Raffles"])
    elif query.current_studio == "Absolute (Spin)":
      locations_keyboard.add(studio_locations_buttons["Absolute (Spin)"]["Centrepoint"], studio_locations_buttons["Absolute (Spin)"]["i12"])
      locations_keyboard.add(studio_locations_buttons["Absolute (Spin)"]["Star Vista"], studio_locations_buttons["Absolute (Spin)"]["Raffles"])
      locations_keyboard.add(studio_locations_buttons["Absolute (Spin)"]["Millenia Walk"])
    elif query.current_studio == "Absolute (Pilates)":
      locations_keyboard.add(studio_locations_buttons["Absolute (Pilates)"]["Centrepoint"], studio_locations_buttons["Absolute (Pilates)"]["i12"])
      locations_keyboard.add(studio_locations_buttons["Absolute (Pilates)"]["Star Vista"], studio_locations_buttons["Absolute (Pilates)"]["Raffles"])
      locations_keyboard.add(studio_locations_buttons["Absolute (Pilates)"]["Great World"])
    locations_keyboard.add(self.locations_select_all_button, self.locations_unselect_all_button)
    locations_keyboard.add(self.locations_select_more_studios_button, self.locations_next_button)
    return locations_keyboard

  def get_days_keyboard(self, query: "QueryData") -> telebot.types.InlineKeyboardMarkup:
    days_keyboard = telebot.types.InlineKeyboardMarkup()

    days_buttons = {
      "Monday" : self.days_buttons_unselected_map["Monday"],
      "Tuesday" : self.days_buttons_unselected_map["Tuesday"],
      "Wednesday" : self.days_buttons_unselected_map["Wednesday"],
      "Thursday" : self.days_buttons_unselected_map["Thursday"],
      "Friday" : self.days_buttons_unselected_map["Friday"],
      "Saturday" : self.days_buttons_unselected_map["Saturday"],
      "Sunday" : self.days_buttons_unselected_map["Sunday"],
    }

    for day in days_buttons:
      if day in query.days:
        days_buttons[day] = self.days_buttons_selected_map[day]

    days_keyboard.add(days_buttons["Monday"], days_buttons["Tuesday"])
    days_keyboard.add(days_buttons["Wednesday"], days_buttons["Thursday"])
    days_keyboard.add(days_buttons["Friday"], days_buttons["Saturday"])
    days_keyboard.add(days_buttons["Sunday"])
    days_keyboard.add(self.days_select_all_button, self.days_unselect_all_button)
    days_keyboard.add(self.days_next_button)
    return days_keyboard
