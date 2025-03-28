from typing import Callable

class StudioManager:
  def __init__(self, logger: "logging.Logger", get_schedule_and_instructorid_map_func: Callable[["logging.Logger"], tuple["ResultData", dict[str, int]]]) -> None:
    self.logger = logger
    self.instructorid_map = {}
    self.instructor_names = []
    self.get_schedule_and_instructorid_map_func = get_schedule_and_instructorid_map_func

  def get_schedule(self) -> "ResultData":
    schedule, self.instructorid_map = self.get_schedule_and_instructorid_map_func(self.logger)
    self.instructor_names = sorted([instructor.lower() for instructor in list(self.instructorid_map)])
    return schedule

class StudiosManager:
  def __init__(self, studios: dict["StudioType", "StudioManager"]) -> None:
    self.studios = studios
