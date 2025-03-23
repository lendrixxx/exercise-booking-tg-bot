import calendar
import global_variables
import re
import requests
from absolute.data import LOCATION_MAP, LOCATION_STR_MAP, ROOM_ID_TO_STUDIO_TYPE_MAP
from bs4 import BeautifulSoup
from common.data_types import CapacityInfo, ClassAvailability, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta

def send_get_schedule_request(locations: list[StudioLocation], week: int) -> requests.models.Response:
  url = 'https://absoluteboutiquefitness.zingfit.com/reserve/index.cfm?action=Reserve.chooseClass'
  params = {'wk': week}

  if 'All' in locations:
    params = {**params, **{'site': 1, 'site2': 2, 'site3': 3, 'site4': 5, 'site5': 6, 'site6': 8}}
  else:
    site_param_name = 'site'
    for location in locations:
      params[site_param_name] = LOCATION_MAP[location]
      if site_param_name == 'site':
        site_param_name = 'site2'
      elif site_param_name != 'site6':
        site_param_name = site_param_name[:-1] + str(int(site_param_name[-1]) + 1)
      else:
        break

  return requests.get(url=url, params=params)

def get_schedule_from_response_soup(soup: BeautifulSoup, locations: list[StudioLocation], week: int) -> dict[datetime.date, list[ClassData]]:
  schedule_table = soup.find('table', id='reserve', class_='scheduleTable')
  if schedule_table is None:
    global_variables.LOGGER.warning(f'Failed to get schedule - Schedule table not found: {soup}')
    return {}

  if schedule_table.tbody is None:
    # No classes for the week
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
      # Reserve table data div might be empty because schedule is only shown up to 1.5 weeks in advance
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

      # scheduleSite span class is only provided if request has multiple locations
      if len(locations) == 1:
        location = locations[0]
      else:
        schedule_site_span = reserve_table_data_div.find('span', class_='scheduleSite')
        if schedule_site_span is None:
          global_variables.LOGGER.warning(f'Failed to get session location: {reserve_table_data_div}')
          continue
        location = LOCATION_STR_MAP[schedule_site_span.get_text().strip()]

      room = reserve_table_data_div.get('data-room')
      if room is None:
        global_variables.LOGGER.warning(f'Failed to get session room: {reserve_table_data_div}')
        continue

      class_details = ClassData(
        studio=ROOM_ID_TO_STUDIO_TYPE_MAP[room],
        location=location,
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

def get_instructorid_map_from_response_soup(soup: BeautifulSoup) -> dict[str, int]:
  reserve_filter = soup.find('ul', id='reserveFilter')
  if reserve_filter is None:
    # No classes for the week so there is no instructor filter as well
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

def get_absolute_schedule_and_instructorid_map() -> tuple[ResultData, dict[str, int]]:
  result = ResultData()
  instructorid_map = {}
  location_map_list = list(LOCATION_MAP)

  # REST API can only select one week at a time
  # Absolute schedule only shows up to 1.5 weeks in advance
  for week in range(0, 2):
    # REST API can only select maximum of 5 locations at a time, but there are 6 locations
    # Send first request for first location
    locations = location_map_list[0:1]
    get_schedule_response = send_get_schedule_request(locations=locations, week=week)
    soup = BeautifulSoup(get_schedule_response.text, 'html.parser')

    # Get schedule
    date_class_data_list_dict = get_schedule_from_response_soup(soup=soup, locations=locations, week=week)
    result.add_classes(date_class_data_list_dict)

    # Get instructor id map
    current_instructorid_map = get_instructorid_map_from_response_soup(soup=soup)
    instructorid_map = {**instructorid_map, **current_instructorid_map}

    # Send second request for last 5 locations
    locations = location_map_list[1:]
    get_schedule_response = send_get_schedule_request(locations=locations, week=week)

    # Get schedule
    soup = BeautifulSoup(get_schedule_response.text, 'html.parser')
    date_class_data_list_dict = get_schedule_from_response_soup(soup=soup, locations=locations, week=week)
    result.add_classes(date_class_data_list_dict)

    # Get instructor id map
    current_instructorid_map = get_instructorid_map_from_response_soup(soup=soup)
    instructorid_map = {**instructorid_map, **current_instructorid_map}

  return result, instructorid_map
