import calendar
import pytz
from copy import copy
from datetime import datetime, timedelta
from enum import Enum

class StudioType(str, Enum):
  All = "All"
  AbsoluteSpin = "Absolute (Spin)"
  AbsolutePilates = "Absolute (Pilates)"
  AllySpin = "Ally (Spin)"
  AllyPilates = "Ally (Pilates)"
  AllyRecovery = "Ally (Recovery)"
  Anarchy = "Anarchy"
  Barrys = "Barrys"
  Rev = "Rev"
  Null = "Null"

class StudioLocation(str, Enum):
  All = "All"
  Orchard = "Orchard"
  TJPG = "TJPG"
  Bugis = "Bugis"
  Raffles = "Raffles"
  Centrepoint = "Centrepoint"
  i12 = "i12"
  MilleniaWalk = "Millenia Walk"
  StarVista = "Star Vista"
  GreatWorld = "Great World"
  CrossStreet = "Cross Street"
  Robinson = "Robinson"
  Null = "Null"

class ClassAvailability(str, Enum):
  Available = "Available"
  Waitlist = "Waitlist"
  Full = "Full"
  Cancelled = "Cancelled"
  Null = "Null"

STUDIO_LOCATIONS_MAP = {
  StudioType.Rev: [StudioLocation.Orchard, StudioLocation.TJPG, StudioLocation.Bugis],
  StudioType.Barrys: [StudioLocation.Orchard, StudioLocation.Raffles],
  StudioType.AbsoluteSpin: [StudioLocation.Centrepoint, StudioLocation.i12, StudioLocation.MilleniaWalk, StudioLocation.Raffles, StudioLocation.StarVista],
  StudioType.AbsolutePilates: [StudioLocation.Centrepoint, StudioLocation.GreatWorld, StudioLocation.i12, StudioLocation.Raffles, StudioLocation.StarVista],
  StudioType.AllySpin: [StudioLocation.CrossStreet],
  StudioType.AllyPilates: [StudioLocation.CrossStreet],
  StudioType.AllyRecovery: [StudioLocation.CrossStreet],
  StudioType.Anarchy: [StudioLocation.Robinson],
}

RESPONSE_AVAILABILITY_MAP = {
  "bookable" : ClassAvailability.Available,
  "classfull" : ClassAvailability.Waitlist,
  "waitlistfull" : ClassAvailability.Full,
  "open" : ClassAvailability.Available,
  "waitlist" : ClassAvailability.Waitlist,
  "full" : ClassAvailability.Waitlist, # TODO: Confirm session status string
  "closed" : ClassAvailability.Available,
  "scheduleCancelled" : ClassAvailability.Cancelled,
  "cancelled" : ClassAvailability.Cancelled
}

SORTED_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class CapacityInfo:
  def __init__(self, has_info:bool=False, capacity:int=0, remaining:int=0, waitlist_capacity:int=0, waitlist_reserved:int=0) -> None:
    self.has_info = has_info
    self.capacity = capacity
    self.remaining = remaining
    self.waitlist_capacity = waitlist_capacity
    self.waitlist_reserved = waitlist_reserved

class ClassData:
  def __init__(
    self,
    studio:StudioType,
    location:StudioLocation,
    name:str,
    instructor:str,
    time:str,
    availability:ClassAvailability,
    capacity_info:CapacityInfo
  ) -> None:
    self.studio = studio
    self.location = location
    self.name = name.replace("*", "\*").replace("_", "\_").replace("`", "\`")
    self.instructor = instructor
    self.time = time
    self.availability = availability
    self.capacity_info = capacity_info

  def __eq__(self, other: "ClassData") -> bool:
    return self.studio == other.studio and self.location == other.location and self.name == other.name and self.instructor == other.instructor and self.time == other.time

  def __lt__(self, other: "ClassData") -> bool:
    self_time = datetime.strptime(self.time,"%I:%M %p")
    other_time = datetime.strptime(other.time,"%I:%M %p")
    return self_time < other_time


class StudioData:
  def __init__(self, locations: list[StudioLocation]=None, instructors: list[str]=None) -> None:
    self.locations = locations
    self.instructors = ["All"] if instructors is None else instructors


class QueryData:
  def __init__(
    self,
    studios: dict[StudioType, StudioData],
    current_studio: StudioType,
    weeks: int,
    days: list[str],
    start_times: list[tuple[datetime.date, datetime.date]],
    class_name_filter: str
  ) -> None:
    self.studios = {} if studios is None else copy(studios)
    self.current_studio = current_studio
    self.weeks = weeks
    self.days = copy(days)
    self.start_times = copy(start_times)
    self.class_name_filter = class_name_filter

  def get_studio_locations(self, studio: StudioType) -> list[StudioLocation]:
    if studio not in self.studios:
      return []

    if self.studios[studio].locations is None:
      return []

    return self.studios[studio].locations

  def get_selected_studios_str(self) -> str:
    if len(self.studios) == 0:
      return "None"

    studios_selected = ""
    for studio in self.studios:
      studios_selected += f"{studio.value} - {', '.join(self.studios[studio].locations)}\n"
    return studios_selected.rstrip()

  def get_selected_days_str(self) -> str:
    if len(self.days) == 0:
      return "None"

    if len(self.days) == 7:
      return "All"

    return ", ".join(self.days)

  def get_selected_time_str(self) -> str:
    if len(self.start_times) == 0:
      return "All"

    selected_times = ""
    for start_time_from, start_time_to in self.start_times:
      selected_times += f"{start_time_from.strftime('%H%M')} - {start_time_to.strftime('%H%M')}\n"
    return selected_times.rstrip()

  def get_selected_class_name_filter_str(self) -> str:
    if self.class_name_filter == "":
      return "None"

    return self.class_name_filter

  def get_selected_instructors_str(self) -> str:
    if len(self.studios) == 0:
      return "None"

    instructors_selected = ""
    for studio in self.studios:
      INSTRUCTOR_NAMES = ", ".join(self.studios[studio].instructors)
      instructors_selected += f"{studio.value}: {INSTRUCTOR_NAMES if len(INSTRUCTOR_NAMES) > 0 else 'None'}\n"
    return instructors_selected.rstrip()

  def get_query_str(self, include_studio: bool=False, include_instructors: bool=False, include_weeks: bool=False, include_days: bool=False, include_time: bool=False, include_class_name_filter: bool=False) -> str:
    query_str_list = []
    if include_studio:
      query_str_list.append(f"Studio(s):\n{self.get_selected_studios_str()}\n")

    if include_instructors:
      query_str_list.append(f"Instructor(s):\n{self.get_selected_instructors_str()}\n")

    if include_weeks:
      query_str_list.append(f"Week(s): {self.weeks}\n")

    if include_days:
      query_str_list.append(f"Day(s): {self.get_selected_days_str()}\n")

    if include_time:
      query_str_list.append(f"Timeslot(s):\n{self.get_selected_time_str()}\n")

    if include_class_name_filter:
      query_str_list.append(f"Class Name Filter: {self.get_selected_class_name_filter_str()}\n")

    return "\n".join(query_str_list)


class ResultData:
  def __init__(self, classes: dict[datetime.date, list[ClassData]]=None) -> None:
    self.classes = {} if classes is None else classes

  def add_class(self, date: datetime.date, data: ClassData) -> None:
    if date not in self.classes:
      self.classes[date] = []

    self.classes[date].append(data)

  def add_classes(self, classes: dict[datetime.date, list[ClassData]]) -> None:
    if classes is None:
      return

    if self.classes is None:
      self.classes = {}

    for date in classes:
      if date in self.classes:
        self.classes[date] += classes[date]
      else:
        self.classes[date] = copy(classes[date])

  def get_data(self, query: QueryData) -> "ResultData":
    if self.classes is None:
      return ResultData()

    classes = {}
    current_sg_time = datetime.now(pytz.timezone("Asia/Singapore"))
    for week in range(0, query.weeks):
      date_to_check = datetime.now().date() + timedelta(weeks=week)
      for day in range(7):
        if "All" not in query.days and calendar.day_name[date_to_check.weekday()] not in query.days:
          date_to_check = date_to_check + timedelta(days=1)
          continue

        if date_to_check in self.classes:
          for class_details in self.classes[date_to_check]:
            if class_details.studio not in query.studios:
              continue

            if query.class_name_filter != "" and query.class_name_filter.lower() not in class_details.name.lower():
              continue

            query_locations = query.get_studio_locations(class_details.studio)
            if StudioLocation.All not in query_locations and class_details.location not in query_locations:
              continue

            is_by_instructor = ("All" in query.studios[class_details.studio].instructors
              or class_details.studio == StudioType.AllyRecovery
              or any(instructor.lower() == class_details.instructor.lower() for instructor in query.studios[class_details.studio].instructors)
              or any(instructor.lower() in class_details.instructor.lower().split(" ") for instructor in query.studios[class_details.studio].instructors)
              or any(instructor.lower() == class_details.instructor.lower().split(".")[0] for instructor in query.studios[class_details.studio].instructors))
            if not is_by_instructor:
              continue

            class_time = datetime.strptime(class_details.time,"%I:%M %p")
            if week == 0 and day == 0: # Skip classes that have already ended
              if current_sg_time.hour > class_time.hour or current_sg_time.hour == class_time.hour and current_sg_time.minute > class_time.minute:
                continue

            if len(query.start_times) > 0:
              within_start_times = False
              for start_time_from, start_time_to in query.start_times:
                class_time_within_query_time_from = class_time.hour > start_time_from.hour or class_time.hour == start_time_from.hour and class_time.minute >= start_time_from.minute
                class_time_within_query_time_to = class_time.hour < start_time_to.hour or class_time.hour == start_time_to.hour and class_time.minute <= start_time_to.minute
                if class_time_within_query_time_from and class_time_within_query_time_to:
                  within_start_times = True
                  break

              if not within_start_times:
                continue

            classes.setdefault(date_to_check, []).append(class_details)
        date_to_check = date_to_check + timedelta(days=1)

    result = ResultData(classes)
    return result

  def get_result_str(self) -> str:
    if len(self.classes) == 0:
      return "No classes found"

    result_str = ""
    for date in sorted(self.classes):
      date_str = f"*{calendar.day_name[date.weekday()]}, {date.strftime('%d %B')}*"
      result_str += f"{date_str}\n"

      for class_details in sorted(self.classes[date]):
        availability_str = ""
        if class_details.availability == ClassAvailability.Waitlist:
          availability_str = "[W] "
        elif class_details.availability == ClassAvailability.Full:
          availability_str = "[F] "
        elif class_details.availability == ClassAvailability.Cancelled:
          availability_str = "[Cancelled] "

        if class_details.location == StudioLocation.Null:
          result_str += f"*{availability_str + class_details.time}* - {class_details.name} ({class_details.instructor})"
        else:
          result_str += f"*{availability_str + class_details.time}* - {class_details.name} @ {class_details.location.value} ({class_details.instructor})"

        if class_details.capacity_info.has_info:
          if class_details.availability == ClassAvailability.Waitlist:
            result_str += f" - {class_details.capacity_info.waitlist_reserved} Rider(s) on Waitlist"
          else:
            result_str += f" - {class_details.capacity_info.remaining} Spot(s) Remaining"

        result_str += "\n"
      result_str += "\n"

    return result_str

  def __add__(self, other: "ResultData") -> "ResultData":
    result = self
    result.add_classes(other.classes)
    return result