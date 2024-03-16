import calendar
import requests
from bs4 import BeautifulSoup
from common.data_types import class_data, result_data, studio_location, studio_type
from copy import copy
from datetime import datetime, timedelta
from absolute.data import pilates_instructorid_map, spin_instructorid_map, location_map

def send_get_schedule_request(location: studio_location, week: int, instructor: str):
    url = 'https://absoluteboutiquefitness.zingfit.com/reserve/index.cfm?action=Reserve.chooseClass'
    params = {'wk': week, 'site': location_map[location]}
    if instructor != 'All':
      params = {**params, **{'instructorid': instructorid_map[instructor]}}

    return requests.get(url=url, params=params)


def parse_get_schedule_response(response, week: int, days: str, location: studio_location) -> dict[datetime.date, list[class_data]]:
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
    class_details = class_data(studio=studio_type.AbsoluteSpin, location=location, name='', instructor='', time='')
    for reserve_table_data_span in reserve_table_data.find_all('span'):
      reserve_table_data_span_class_list = reserve_table_data_span.get('class')
      if len(reserve_table_data_span_class_list) == 0:
        print('[W] Failed to get schedule - Table data span class is null')
        continue

      reserve_table_data_span_class = reserve_table_data_span_class_list[0]
      if reserve_table_data_span_class == 'scheduleClass':
        class_details.name = str(reserve_table_data_span.contents[0].strip())
      elif reserve_table_data_span_class == 'scheduleInstruc':
        class_details.instructor = str(reserve_table_data_span.contents[0].strip())
      elif reserve_table_data_span_class == 'scheduleTime':
        if len(reserve_table_data_span_class_list) != 2:
          continue

        if reserve_table_data_span_class_list[1] != 'active':
          class_details = class_data(studio=studio_type.AbsoluteSpin, location=location, name='', instructor='', time='')
          continue

        if len(class_details.name) == 0:
          class_details = class_data(studio=studio_type.AbsoluteSpin, location=location, name='', instructor='', time='')
          continue

        class_details.set_time(str(reserve_table_data_span.contents[0].strip()))
        class_details.studio = studio_type.AbsoluteSpin if 'CYCLE' in class_details.name else studio_type.AbsolutePilates
        result_dict[current_date].append(copy(class_details))
        class_details = class_data(studio=studio_type.AbsoluteSpin, location=location, name='', instructor='', time='')

    if len(result_dict[current_date]) == 0:
      result_dict.pop(current_date)
    current_date = current_date + timedelta(days=1)

  return result_dict

def get_absolute_schedule(locations: list[studio_location], weeks: int, days: str, instructors: list[str]) -> result_data:
  result = result_data()
  # REST API does not return location info in class name
  i = 0
  for location in locations:
    # REST API can only select one instructor at a time
    for instructor in instructors:
      # REST API can only select one week at a time
      for week in range(0, weeks):
        get_schedule_response = send_get_schedule_request(location=location, instructor=instructor, week=week)
        date_class_data_list_dict = parse_get_schedule_response(get_schedule_response, week=week, days=days, location=location)
        result.add_classes(date_class_data_list_dict)

  return result
