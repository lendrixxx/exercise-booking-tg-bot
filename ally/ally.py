import calendar
import global_variables
import re
import requests
from ally.data import ROOM_ID_TO_STUDIO_TYPE_MAP
from bs4 import BeautifulSoup
from common.data_types import CapacityInfo, ClassAvailability, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta

def send_get_schedule_request(week: int) -> requests.models.Response:
  url = 'https://ally.zingfit.com/reserve/index.cfm?action=Reserve.chooseClass'
  params = {'wk': week, 'site': 1} # Ally only has 1 location currently
  return requests.get(url=url, params=params)

def parse_get_schedule_response(response: requests.models.Response, week: int) -> dict[datetime.date, list[ClassData]]:
  soup = BeautifulSoup(response.text, 'html.parser')
  schedule_table = soup.find('table', id='reserve', class_='scheduleTable')
  if schedule_table is None:
    global_variables.LOGGER.warning(f'Failed to get schedule - Schedule table not found: {soup}')
    return {}

  if schedule_table.tbody is None:
    global_variables.LOGGER.warning(f'Failed to get schedule - Schedule table tbody not found: {schedule_table}')
    return {}

  schedule_table_row = schedule_table.tbody.find('tr')
  if schedule_table_row is None:
    global_variables.LOGGER.warning(f'Failed to get schedule - Schedule table row not found: {schedule_table}')
    return {}

  schedule_table_data_list = schedule_table_row.find_all('td')
  if len(schedule_table_data_list) == 0:
    global_variables.LOGGER.warning(f'Failed to get schedule - Schedule table data is null: {schedule_table_row}')
    return {}

  # Get yesterday's date and update date at the start of each loop
  current_date = datetime.now().date() + timedelta(weeks=week) - timedelta(days=1)
  result_dict = {}
  for schedule_table_data in schedule_table_data_list:
    current_date = current_date + timedelta(days=1)
    reserve_table_data_div_list = schedule_table_data.find_all('div')
    if len(reserve_table_data_div_list) == 0:
      # Reserve table data div might be empty because schedule is only shown up to 2 weeks in advance
      continue

    for reserve_table_data_div in reserve_table_data_div_list:
      reserve_table_data_div_class_list = reserve_table_data_div.get('class')
      if len(reserve_table_data_div_class_list) < 2:
        availability = ClassAvailability.Null # Class is over
      else:
        availability = RESPONSE_AVAILABILITY_MAP[reserve_table_data_div_class_list[1]]

      schedule_class_span = reserve_table_data_div.find('span', class_='scheduleClass')
      if schedule_class_span is None:
        # Check if class was cancelled or is an actual error
        is_cancelled = reserve_table_data_div.find('span', class_='scheduleCancelled')
        if is_cancelled is None:
          global_variables.LOGGER.warning(f'Failed to get session name: {reserve_table_data_div}')
        continue

      schedule_instruc_span = reserve_table_data_div.find('span', class_='scheduleInstruc')
      if schedule_instruc_span is None:
        global_variables.LOGGER.warning(f'Failed to get session instructor: {reserve_table_data_div}')
        continue

      schedule_time_span = reserve_table_data_div.find('span', class_='scheduleTime')
      if schedule_time_span is None:
        global_variables.LOGGER.warning(f'Failed to get session time: {reserve_table_data_div}')
        continue
      schedule_time = schedule_time_span.get_text().strip()
      schedule_time = schedule_time[:schedule_time.find('M') + 1]

      room = reserve_table_data_div.get('data-room')
      if room is None:
        global_variables.LOGGER.warning(f'Failed to get session room: {reserve_table_data_div}')
        continue

      class_details = ClassData(
        studio=ROOM_ID_TO_STUDIO_TYPE_MAP[room],
        location=StudioLocation.CrossStreet,
        name=schedule_class_span.get_text().strip(),
        instructor=schedule_instruc_span.get_text().strip(),
        time=schedule_time,
        availability=availability,
        capacity_info=CapacityInfo())

      if current_date not in result_dict:
        result_dict[current_date] = [copy(class_details)]
      else:
        result_dict[current_date].append(copy(class_details))

  return result_dict

def get_ally_schedule() -> ResultData:
  result = ResultData()
  # REST API can only select one week at a time
  # Ally schedule only shows up to 2 weeks in advance
  for week in range(0, 2):
    get_schedule_response = send_get_schedule_request(week=week)
    date_class_data_list_dict = parse_get_schedule_response(response=get_schedule_response, week=week)
    result.add_classes(date_class_data_list_dict)
  return result

def get_instructorid_map() -> dict[str, int]:
  def _get_instructorid_map_internal(response: requests.models.Response) -> dict[str, int]:
    soup = BeautifulSoup(response.text, 'html.parser')
    reserve_filter = soup.find('ul', id='reserveFilter')
    if reserve_filter is None:
      global_variables.LOGGER.warning(f'Failed to get list of instructors - Reserve filter not found: {soup}')
      return {}

    instructor_filter = reserve_filter.find('li', id='reserveFilter1')
    if instructor_filter is None:
      global_variables.LOGGER.warning(f'Failed to get list of instructors - Instructor filter not found: {reserve_filter}')
      return {}

    instructorid_map = {}
    for instructor in instructor_filter.find_all('li'):
      instructor_name = instructor.string
      if instructor.a is None:
        global_variables.LOGGER.warning(f'Failed to get id of instructor {instructor_name} - A tag is null: {instructor}')
        continue

      href = instructor.a.get('href')
      if href is None:
        global_variables.LOGGER.warning(f'Failed to get id of instructor {instructor_name} - Href is null: {instructor.a}')
        continue

      match = re.search(r'instructorid=(\d+)', href)
      if match is None:
        global_variables.LOGGER.warning(f'Failed to get id of instructor {instructor_name} - Regex failed to match: {href}')
        continue

      instructorid_map[instructor_name.lower()] = match.group(1)

    return instructorid_map

  # REST API can only select one week at a time
  instructorid_map = {}
  for week in range(0, 2):
    get_schedule_response = send_get_schedule_request(week=week)
    current_instructorid_map = _get_instructorid_map_internal(response=get_schedule_response)
    instructorid_map = {**instructorid_map, **current_instructorid_map}

  return instructorid_map
