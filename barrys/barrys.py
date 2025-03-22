import calendar
import global_variables
import requests
from bs4 import BeautifulSoup
from common.data_types import CapacityInfo, ClassAvailability, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta
from barrys.data import LOCATION_MAP, RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP

def send_get_schedule_request(week: int) -> requests.models.Response:
  url = 'https://apac.barrysbootcamp.com.au/reserve/index.cfm?action=Reserve.chooseClass'
  params = {'wk': max(0, min(week, 2)), 'site': 1, 'site2': 12}
  return requests.get(url=url, params=params)

def parse_get_schedule_response(response: requests.models.Response, week: int) -> dict[datetime.date, list[ClassData]]:
  soup = BeautifulSoup(response.text, 'html.parser')
  result_dict = {}
  # Get yesterday's date and update date at the start of each loop
  current_date = datetime.now().date() + timedelta(weeks=week) - timedelta(days=1)
  for _ in range(7):
    current_date = current_date + timedelta(days=1)
    div_id = f'day{current_date.strftime("%Y%m%d")}'
    schedule_pane_div_list = [div for div in soup.find_all('div') if div.get('id') == div_id]
    schedule_pane_div_list_len = len(schedule_pane_div_list)
    if schedule_pane_div_list_len != 1:
      continue

    result_dict[current_date] = []
    schedule_pane_div = schedule_pane_div_list[0]
    schedule_block_div_list = schedule_pane_div.find_all('div')
    if schedule_block_div_list is None:
      continue

    for schedule_block_div in schedule_block_div_list:
      schedule_block_div_class_list = schedule_block_div.get('class')
      if len(schedule_block_div_class_list) < 2:
        availability = ClassAvailability.Null
      else:
        availability_str = schedule_block_div_class_list[1]
        if availability_str == 'empty': # No classes available for the day
          continue
        availability = RESPONSE_AVAILABILITY_MAP[availability_str]

      class_details = ClassData(
        studio=StudioType.Barrys,
        location=StudioLocation.Null,
        name='',
        instructor='',
        time='',
        availability=availability,
        capacity_info=CapacityInfo())
      for schedule_block_div_span in schedule_block_div.find_all('span'):
        schedule_block_div_span_class = schedule_block_div_span.get('class')
        if schedule_block_div_span_class is None:
          continue

        if 'scheduleTime' in schedule_block_div_span_class:
          class_details.set_time(str(schedule_block_div_span.contents[0].get_text()))
        if 'scheduleSite' in schedule_block_div_span_class:
          location_str = str(schedule_block_div_span.contents[0].get_text())
          class_details.location = RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP[location_str]
        elif 'scheduleClass' in schedule_block_div_span_class:
          class_details.name = str(schedule_block_div_span.contents[0].get_text())
        elif 'scheduleInstruc' in schedule_block_div_span_class:
          class_details.instructor = str(schedule_block_div_span.contents[0].get_text())
          if class_details not in result_dict[current_date]:
            result_dict[current_date].append(copy(class_details))

    if len(result_dict[current_date]) == 0:
      result_dict.pop(current_date)

  return result_dict

def get_barrys_schedule() -> ResultData:
  result = ResultData()
  # REST API can only select one week at a time
  # Barrys schedule only shows up to 3 weeks in advance
  for week in range(0, 3):
    get_schedule_response = send_get_schedule_request(week=week)
    date_class_data_list_dict = parse_get_schedule_response(response=get_schedule_response, week=week)
    result.add_classes(date_class_data_list_dict)

  return result

def get_instructorid_map() -> dict[str, int]:
  def _get_instructorid_map_internal(response: requests.models.Response) -> dict[str, int]:
    soup = BeautifulSoup(response.text, 'html.parser')
    reserve_filters_list = [list_item for list_item in soup.find_all('ul') if list_item.get('id') == 'reserveFilter']
    reserve_filters_list_len = len(reserve_filters_list)
    if reserve_filters_list_len != 1:
      global_variables.LOGGER.warning(f'Failed to get list of instructors - Expected 1 reserve filter list, got {reserve_filters_list_len} instead')
      return {}

    reserve_filters = reserve_filters_list[0]
    instructor_filter_list = [list_item for list_item in reserve_filters.find_all('li') if list_item.get('id') == 'reserveFilter1']
    instructor_filter_list_len = len(instructor_filter_list)
    if instructor_filter_list_len != 1:
      global_variables.LOGGER.warning(f'Failed to get list of instructors - Expected 1 instructor filter list, got {instructor_filter_list_len} instead')
      return {}

    instructorid_map = {}
    instructorid_prefix = 'instructorid='
    instructorid_prefix_len = len(instructorid_prefix)
    instructorid_len = 19
    for instructor in instructor_filter_list[0].find_all('li'):
      instructor_name = instructor.string
      link = instructor.a.get('href')
      start_pos = link.find('instructorid=')
      instructorid = link[start_pos + instructorid_prefix_len:start_pos + instructorid_prefix_len + instructorid_len]
      instructorid_map[instructor_name.lower()] = instructorid
    return instructorid_map

  # REST API can only select one week at a time
  instructorid_map = {}
  for week in range(0, 3):
    get_schedule_response = send_get_schedule_request(week=week)
    current_instructorid_map = _get_instructorid_map_internal(response=get_schedule_response)
    instructorid_map = {**instructorid_map, **current_instructorid_map}

  return instructorid_map
