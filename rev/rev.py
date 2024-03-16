import calendar
import requests
from bs4 import BeautifulSoup
from common.data_types import class_data, result_data, studio_location, studio_type
from copy import copy
from datetime import datetime, timedelta
from rev.data import instructorid_map, location_map, response_location_to_studio_location_map

def send_get_schedule_request(locations: list[studio_location], week: int, instructor: str):
    url = 'https://rhythmstudios.zingfit.com/reserve/index.cfm?action=Reserve.chooseClass'
    params = {'wk': week}

    if 'All' in locations:
      params = {**params, **{'site': 2, 'site2': 3, 'site3': 4, 'site4': 5, 'site5': 6}}
    else:
      site_param_name = 'site'
      for location in locations:
        params[site_param_name] = location_map[location]
        if site_param_name == 'site':
          site_param_name = 'site2'
        elif site_param_name != 'site5':
          site_param_name = site_param_name[:-1] + str(int(site_param_name[-1]) + 1)
        else:
          break

    if instructor != 'All':
      params = {**params, **{'instructorid': instructorid_map[instructor]}}

    return requests.get(url=url, params=params)


def parse_get_schedule_response(response, week: int, days: str) -> dict[datetime.date, list[class_data]]:
  soup = BeautifulSoup(response.text, 'html.parser')
  reserve_table_list = [table for table in soup.find_all('table') if table.get('id') == 'reserve']
  reserve_table_list_len = len(reserve_table_list)
  if reserve_table_list_len != 1:
    print(f'[W] Failed to get schedule - Expected 1 reserve table, got {reserve_table_list_len} instead')
    return {}

  reserve_table = reserve_table_list[0]
  if reserve_table.tbody is None:
    return {}

  reserve_table_rows = reserve_table.tbody.find_all('tr')
  reserve_table_rows_len = len(reserve_table_rows)
  if reserve_table_rows_len != 1:
    print(f'[W] Failed to get schedule - Expected 1 schedule row, got {reserve_table_rows_len} rows instead')
    return {}

  reserve_table_datas = reserve_table_rows[0].find_all('td')
  if len(reserve_table_datas) == 0:
    print('[W] Failed to get schedule - Table data is null')
    return {}

  current_date = datetime.now().date() + timedelta(weeks=week)
  result_dict = {}
  for reserve_table_data in reserve_table_datas:
    if days != 'All' and days != calendar.day_name[current_date.weekday()]:
      current_date = current_date + timedelta(days=1)
      continue

    result_dict[current_date] = []
    class_details = class_data(studio=studio_type.Rev, location=studio_location.Null, name='', instructor='', time='')
    for reserve_table_data_span in reserve_table_data.find_all('span'):
      reserve_table_data_span_class_list = reserve_table_data_span.get('class')
      if len(reserve_table_data_span_class_list) == 0:
        print('[W] Failed to get schedule - Table data span class is null')
        continue

      reserve_table_data_span_class = reserve_table_data_span_class_list[0]
      if reserve_table_data_span_class == 'scheduleClass':
        schedule_class_str = str(reserve_table_data_span.contents[0].strip())
        name_location_split_pos = schedule_class_str.find(' @ ')
        class_name = schedule_class_str[:name_location_split_pos]
        class_details.name = class_name
        class_location_str = schedule_class_str[name_location_split_pos + 3:]
        if class_location_str in response_location_to_studio_location_map:
          class_details.location = response_location_to_studio_location_map[class_location_str]
        else:
          class_location_list = [value for key, value in response_location_to_studio_location_map.items() if key in class_location_str]
          class_details.location = class_location_list[0]
      elif reserve_table_data_span_class == 'scheduleInstruc':
        class_details.instructor = str(reserve_table_data_span.contents[0].strip())
      elif reserve_table_data_span_class == 'scheduleTime':
        class_details.set_time(str(reserve_table_data_span.contents[0].strip()))
        result_dict[current_date].append(copy(class_details))
        class_details = class_data(studio=studio_type.Rev, location=studio_location.Null, name='', instructor='', time='')

    if len(result_dict[current_date]) == 0:
      result_dict.pop(current_date)
    current_date = current_date + timedelta(days=1)

  return result_dict

def get_rev_schedule(locations: list[studio_location], weeks: int, days: str, instructors: list[str]) -> result_data:
  result = result_data()
  # REST API can only select one instructor at a time
  for instructor in instructors:
    # REST API can only select one week at a time
    for week in range(0, weeks):
      get_schedule_response = send_get_schedule_request(locations=locations, instructor=instructor, week=week)
      date_class_data_list_dict = parse_get_schedule_response(get_schedule_response, week=week, days=days)
      result.add_classes(date_class_data_list_dict)

  return result
