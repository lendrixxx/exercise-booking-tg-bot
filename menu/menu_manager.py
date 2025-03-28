from common.data_types import ResultData
from menu import (
  days_page_handler,
  get_schedule_handler,
  instructors_page_handler,
  main_page_handler,
  name_filter_page_handler,
  nerd_page_handler,
  start_page_handler,
  studios_page_handler,
  time_page_handler,
  weeks_page_handler,
)

class MenuManager:
  def __init__(
    self,
    logger: "logging.Logger",
    bot: "telebot.TeleBot",
    chat_manager: "ChatManager",
    keyboard_manager: "KeyboardManager",
    studios_manager: "StudiosManager",
    history_manager: "HistoryManager"
  ) -> None:
    self.logger = logger
    self.bot = bot
    self.chat_manager = chat_manager
    self.keyboard_manager = keyboard_manager
    self.studios_manager = studios_manager
    self.history_manager = history_manager
    self.cached_result_data = ResultData()

    self.setup_message_handlers()
    self.setup_callback_query_handlers()

  def setup_callback_query_handlers(self) -> None:
    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "main-page-handler")
    def main_page_handler_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      main_page_handler.main_page_handler_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "studios")
    def studios_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      studios_page_handler.studios_callback_query_handler(query, self.bot, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "studios-selection")
    def studios_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      studios_page_handler.studios_selection_callback_query_handler(query, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "locations")
    def locations_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      studios_page_handler.locations_callback_query_handler(query, self.bot, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "instructors-selection")
    def instructors_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.instructors_selection_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "show-instructors")
    def show_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.show_instructors_callback_query_handler(query, self.chat_manager, self.studios_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "rev-instructors")
    def rev_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.rev_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Rev"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "barrys-instructors")
    def barrys_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.barrys_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Barrys"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "absolute-spin-instructors")
    def absolute_spin_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.absolute_spin_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Absolute"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "absolute-pilates-instructors")
    def absolute_pilates_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.absolute_pilates_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Absolute"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "ally-spin-instructors")
    def ally_spin_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.ally_spin_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Ally"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "ally-pilates-instructors")
    def ally_pilates_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.ally_pilates_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Ally"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "anarchy-instructors")
    def anarchy_instructors_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      instructors_page_handler.anarchy_instructors_callback_query_handler(query, self.chat_manager, self.bot, self.studios_manager.studios["Anarchy"].instructorid_map)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "weeks-selection")
    def weeks_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      weeks_page_handler.weeks_selection_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "weeks")
    def weeks_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      weeks_page_handler.weeks_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days")
    def days_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      days_page_handler.days_callback_query_handler(query, self.bot, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days-selection")
    def days_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      days_page_handler.days_selection_callback_query_handler(query, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "days-next")
    def days_next_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      days_page_handler.days_next_callback_query_handler(query, self.chat_manager, self.keyboard_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection")
    def time_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      time_page_handler.time_selection_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-add")
    def time_selection_add_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      time_page_handler.time_selection_add_callback_query_handler(query, self.logger, self.bot, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-remove")
    def time_selection_remove_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      time_page_handler.time_selection_remove_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "remove-timeslot")
    def time_selection_remove_timeslot_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      time_page_handler.time_selection_remove_timeslot_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "time-selection-reset")
    def time_selection_reset_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      time_page_handler.time_selection_reset_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "class-name-filter-selection")
    def class_name_filter_selection_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      name_filter_page_handler.class_name_filter_selection_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "class-name-filter-add")
    def class_name_filter_set_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      name_filter_page_handler.class_name_filter_set_callback_query_handler(query, self.bot, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "class-name-filter-reset")
    def class_name_filter_reset_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      name_filter_page_handler.class_name_filter_reset_callback_query_handler(query, self.chat_manager)

    @self.bot.callback_query_handler(func=lambda query: eval(query.data)["step"] == "get-schedule")
    def get_schedule_callback_query_handler(query: "telebot.types.CallbackQuery") -> None:
      get_schedule_handler.get_schedule_callback_query_handler(query, self.chat_manager, self.cached_result_data)

  def setup_message_handlers(self) -> None:
    @self.bot.message_handler(commands=["start"])
    def start_message_handler(message: "telebot.types.Message") -> None:
      start_page_handler.start_message_handler(message, self.chat_manager, self.history_manager)

    @self.bot.message_handler(commands=["nerd"])
    def nerd_message_handler(message: "telebot.types.Message") -> None:
      nerd_page_handler.nerd_message_handler(message, self.logger, self.bot, self.chat_manager, self.history_manager, self.studios_manager, self.cached_result_data)

    @self.bot.message_handler(commands=["instructors"])
    def instructors_message_handler(message: "telebot.types.Message") -> None:
      instructors_page_handler.instructors_message_handler(message, self.chat_manager, self.history_manager, self.studios_manager)
