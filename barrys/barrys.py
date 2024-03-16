import calendar
import requests
from bs4 import BeautifulSoup
from common.data_types import class_availability, class_data, response_availability_map, result_data, studio_location, studio_type
from copy import copy
from datetime import datetime, timedelta
from barrys.data import instructorid_map, location_map, response_location_to_studio_location_map

def send_get_schedule_request(locations: list[studio_location], week: int, instructor: str):
    url = 'https://apac.barrysbootcamp.com.au/reserve/index.cfm?action=Reserve.chooseClass'
    params = {'wk': max(0, min(week, 2))}

    if 'All' in locations:
      params = {**params, **{'site': 1, 'site2': 12}}
    else:
      site_param_name = 'site'
      for location in locations:
        params[site_param_name] = location_map[location]
        if site_param_name == 'site':
          site_param_name = 'site2'
        else:
          break

    if instructor != 'All':
      params = {**params, **{'instructorid': instructorid_map[instructor]}}

    return requests.get(url=url, params=params)

def parse_get_schedule_response(response, week: int, days: list[str], locations: list[studio_location]) -> dict[datetime.date, list[class_data]]:
  soup = BeautifulSoup(response.text, 'html.parser')
  result_dict = {}
  current_date = datetime.now().date() + timedelta(weeks=week)
  if len(locations) == 1 and studio_location.All not in locations:
    location = locations[0]
  else:
    location = studio_location.Null
  for _ in range(7):
    if 'All' not in days and calendar.day_name[current_date.weekday()] not in days:
      current_date = current_date + timedelta(days=1)
      continue

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
        availability = class_availability.Null
      else:
        availability = response_availability_map[schedule_block_div_class_list[1]]

      class_details = class_data(studio=studio_type.Barrys, location=location, name='', instructor='', time='', availability=availability)
      for schedule_block_div_span in schedule_block_div.find_all('span'):
        schedule_block_div_span_class = schedule_block_div_span.get('class')
        if schedule_block_div_span_class is None:
          continue

        if 'scheduleTime' in schedule_block_div_span_class:
          class_details.set_time(str(schedule_block_div_span.contents[0].get_text()))
        if 'scheduleSite' in schedule_block_div_span_class:
          location_str = str(schedule_block_div_span.contents[0].get_text())
          class_details.location = response_location_to_studio_location_map[location_str]
        elif 'scheduleClass' in schedule_block_div_span_class:
          class_details.name = str(schedule_block_div_span.contents[0].get_text())
        elif 'scheduleInstruc' in schedule_block_div_span_class:
          class_details.instructor = str(schedule_block_div_span.contents[0].get_text())
          if class_details not in result_dict[current_date]:
            result_dict[current_date].append(copy(class_details))

    if len(result_dict[current_date]) == 0:
      result_dict.pop(current_date)
    current_date = current_date + timedelta(days=1)

  return result_dict

def get_barrys_schedule(locations: list[studio_location], weeks: int, days: list[str], instructors: list[str]) -> result_data:
  result = result_data()
  # REST API can only select one instructor at a time
  for instructor in instructors:
    # REST API can only select one week at a time
    for week in range(0, weeks):
      get_schedule_response = send_get_schedule_request(locations=locations, instructor=instructor, week=week)
      date_class_data_list_dict = parse_get_schedule_response(get_schedule_response, week=week, days=days, locations=locations)
      result.add_classes(date_class_data_list_dict)

  return result
