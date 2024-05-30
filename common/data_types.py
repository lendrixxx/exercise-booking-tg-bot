import calendar
import pytz
from copy import copy
from datetime import datetime, timedelta
from enum import Enum

class studio_type(str, Enum):
  All = 'All'
  AbsoluteSpin = 'Absolute (Spin)'
  AbsolutePilates = 'Absolute (Pilates)'
  AllySpin = 'Ally (Spin)'
  AllyPilates = 'Ally (Pilates)'
  Barrys = 'Barrys'
  Rev = 'Rev'
  Null = 'Null'

class studio_location(str, Enum):
  All = 'All'
  Orchard = 'Orchard'
  TJPG = 'TJPG'
  Bugis = 'Bugis'
  Suntec = 'Suntec'
  Raffles = 'Raffles'
  Centrepoint = 'Centrepoint'
  i12 = 'i12'
  MilleniaWalk = 'Millenia Walk'
  StarVista = 'Star Vista'
  GreatWorld = 'Great World'
  CrossStreet = 'Cross Street'
  Null = 'Null'

class class_availability(str, Enum):
  Available = 'Available'
  Waitlist = 'Waitlist'
  Full = 'Full'
  Null = 'Null'

studio_locations_map = {
  studio_type.Rev: [studio_location.Orchard, studio_location.TJPG, studio_location.Bugis, studio_location.Suntec],
  studio_type.Barrys: [studio_location.Orchard, studio_location.Raffles],
  studio_type.AbsoluteSpin: [studio_location.Centrepoint, studio_location.i12, studio_location.MilleniaWalk, studio_location.Raffles, studio_location.StarVista],
  studio_type.AbsolutePilates: [studio_location.Centrepoint, studio_location.GreatWorld, studio_location.i12, studio_location.Raffles, studio_location.StarVista],
  studio_type.AllySpin: [studio_location.CrossStreet],
  studio_type.AllyPilates: [studio_location.CrossStreet],
}

response_availability_map = {
  'bookable' : class_availability.Available,
  'classfull' : class_availability.Waitlist,
  'waitlistfull' : class_availability.Full,
}

sorted_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class class_data:
  def __init__(self, studio:studio_type, location:studio_location, name:str, instructor:str, time:str, availability:class_availability):
    self.studio = studio
    self.location = location
    self.name = name
    self.instructor = instructor
    self.time = time
    self.availability = availability

  def set_time(self, time:str):
    last_pos = time.find('M') + 1
    self.time = time[:last_pos]

  def __eq__(self, other: 'class_data') -> bool:
    return self.studio == other.studio and self.location == other.location and self.name == other.name and self.instructor == other.instructor and self.time == other.time

  def __lt__(self, other: 'class_data') -> bool:
    self_time = datetime.strptime(self.time,'%I:%M %p')
    other_time = datetime.strptime(other.time,'%I:%M %p')
    return self_time < other_time

class studio_data:
  def __init__(self, locations: list[studio_location]=None, instructors: list[str]=None):
    self.locations = locations
    self.instructors = [] if instructors is None else instructors

class query_data:
  def __init__(self, studios: dict[str, studio_data], current_studio: studio_type, weeks: int, days: list[str]):
    self.studios = {} if studios is None else studios
    self.current_studio = current_studio
    self.weeks = weeks
    self.days = days

  def get_studio_locations(self, studio_name: str) -> list[studio_location]:
    if studio_name not in self.studios:
      return []

    if self.studios[studio_name].locations is None:
      return []

    return self.studios[studio_name].locations

  def get_selected_studios_str(self) -> str:
    if len(self.studios) == 0:
      return 'None'

    studios_selected = ""
    for studio in self.studios:
      studios_selected += f"{studio} - {', '.join(self.studios[studio].locations)}\n"
    return studios_selected[:-1]

  def get_selected_days_str(self) -> str:
    if len(self.days) == 0:
      return 'None'

    return ', '.join(self.days)

  def get_selected_instructors_str(self) -> str:
    if len(self.studios) == 0:
      return 'None'

    instructors_selected = ""
    for studio in self.studios:
      instructor_names = ', '.join(self.studios[studio].instructors)
      instructors_selected += f"{studio}: {instructor_names if len(instructor_names) > 0 else 'None'}\n"
    return instructors_selected.rstrip()

  def get_query_str(self, include_studio: bool=False, include_instructors: bool=False, include_weeks: bool=False, include_days: bool=False) -> str:
    text = '*Schedule to check*\n'
    if include_studio:
      text += f'Studio(s):\n{self.get_selected_studios_str()}\n\n'

    if include_instructors:
      text += f'Instructor(s)\n{self.get_selected_instructors_str()}\n\n'

    if include_weeks:
      text += f'Week(s): {self.weeks}\n\n'

    if include_days:
      text += f'Day(s): {self.get_selected_days_str()}\n\n'

    return text

  def is_rev_in_query(self) -> bool:
    return "Rev" in self.studios

  def is_barrys_in_query(self) -> bool:
    return "Barrys" in self.studios

  def has_instructors_selected(self) -> bool:
    if self.is_rev_in_query():
      if len(self.studios['Rev'].instructors) == 0:
        return False
    if self.is_barrys_in_query():
      if len(self.studios['Barrys'].instructors) == 0:
        return False

    return True



class result_data:
  def __init__(self, classes: dict[datetime.date, list[class_data]]=None):
    self.classes = {} if classes is None else classes

  def add_class(self, date: datetime.date, data: class_data) -> None:
    if date not in self.classes:
      self.classes[date] = []

    self.classes[date].append(data)

  def add_classes(self, classes: dict[datetime.date, list[class_data]]) -> None:
    if classes is None:
      return

    if self.classes is None:
      self.classes = {}

    for date in classes:
      if date in self.classes:
        self.classes[date] += classes[date]
      else:
        self.classes[date] = copy(classes[date])

  def get_data(self, query: query_data) -> 'result_data':
    if self.classes is None:
      return result_data()

    classes = {}
    current_sg_time = datetime.now(pytz.timezone('Asia/Singapore'))
    for week in range(0, query.weeks):
      date_to_check = datetime.now().date() + timedelta(weeks=week)
      for day in range(7):
        if 'All' not in query.days and calendar.day_name[date_to_check.weekday()] not in query.days:
          date_to_check = date_to_check + timedelta(days=1)
          continue

        if date_to_check in self.classes:
          for class_details in self.classes[date_to_check]:
            if class_details.studio not in query.studios:
              continue

            query_locations = query.get_studio_locations(class_details.studio)
            if studio_location.All not in query_locations and class_details.location not in query_locations:
              continue

            is_by_instructor = 'All' in query.studios[class_details.studio].instructors \
              or any(instructor.lower() == class_details.instructor.lower() for instructor in query.studios[class_details.studio].instructors) \
              or any(instructor.lower() in class_details.instructor.lower().split(' ') for instructor in query.studios[class_details.studio].instructors)
            if not is_by_instructor:
              continue

            if week == 0 and day == 0: # Skip classes that have already ended
              class_time = datetime.strptime(class_details.time,'%I:%M %p')
              if current_sg_time.hour > class_time.hour or current_sg_time.hour == class_time.hour and current_sg_time.minute > class_time.minute:
                continue

            classes.setdefault(date_to_check, []).append(class_details)
        date_to_check = date_to_check + timedelta(days=1)

    result = result_data(classes)
    return result

  def get_result_str(self) -> str:
    if len(self.classes) == 0:
      return 'No classes found'

    result_str = ''
    for date in sorted(self.classes):
      date_str = "*" + calendar.day_name[date.weekday()] + ", " + date.strftime('%d %B') + "*"
      result_str += f'{date_str}\n'

      for class_details in sorted(self.classes[date]):
        availability_str = ''
        if class_details.availability == class_availability.Waitlist:
          availability_str = '[W] '
        elif class_details.availability == class_availability.Full:
          availability_str = '[F] '

        result_str += f'*{availability_str + class_details.time}* - {class_details.name} @ {class_details.location} ({class_details.instructor})\n'
      result_str += '\n'

    return result_str

  def __add__(self, other: 'result_data') -> 'result_data':
    result = self
    result.add_classes(other.classes)
    return result