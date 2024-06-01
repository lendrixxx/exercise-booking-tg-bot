import calendar
import requests
from bs4 import BeautifulSoup
from common.data_types import ClassAvailability, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta
from ally.data import INSTRUCTORID_MAP

def send_get_schedule_request(week: int, instructor: str):
    url = 'https://ally.zingfit.com/reserve/index.cfm?action=Reserve.chooseClass'
    params = {'wk': week, 'site': 1} # Ally only has 1 location currently

    if instructor != 'All':
      params = {**params, **{'instructorid': INSTRUCTORID_MAP[instructor]}}

    return requests.get(url=url, params=params)

def parse_get_schedule_response(response, week: int, days: list[str]) -> dict[datetime.date, list[ClassData]]:
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

  # Get yesterday's date and update date at the start of each loop
  current_date = datetime.now().date() + timedelta(weeks=week) - timedelta(days=1)
  result_dict = {}
  for reserve_table_data in reserve_table_datas:
    current_date = current_date + timedelta(days=1)
    if 'All' not in days and calendar.day_name[current_date.weekday()] not in days:
      continue

    result_dict[current_date] = []
    reserve_table_data_div_list = reserve_table_data.find_all('div')
    if len(reserve_table_data_div_list) == 0:
      # Reserve table data div might be empty because schedule is only shown up to 1.5 weeks in advance
      continue

    for reserve_table_data_div in reserve_table_data_div_list:
      reserve_table_data_div_class_list = reserve_table_data_div.get('class')
      if len(reserve_table_data_div_class_list) < 2:
        availability = ClassAvailability.Null
      else:
        availability = RESPONSE_AVAILABILITY_MAP[reserve_table_data_div_class_list[1]]

      class_details = ClassData(studio=StudioType.AllySpin, location=StudioLocation.CrossStreet, name='', instructor='', time='', availability=availability)
      for reserve_table_data_div_span in reserve_table_data_div.find_all('span'):
        reserve_table_data_div_span_class_list = reserve_table_data_div_span.get('class')
        if len(reserve_table_data_div_span_class_list) == 0:
          print('[W] Failed to get schedule - Table data span class is null')
          continue

        reserve_table_data_div_span_class = reserve_table_data_div_span_class_list[0]
        if reserve_table_data_div_span_class == 'scheduleClass':
          class_details.name = str(reserve_table_data_div_span.contents[0].strip())
        elif reserve_table_data_div_span_class == 'scheduleInstruc':
          class_details.instructor = str(reserve_table_data_div_span.contents[-1].strip())
        elif reserve_table_data_div_span_class == 'scheduleTime':
          if len(class_details.name) == 0:
            continue

          class_details.set_time(str(reserve_table_data_div_span.contents[0].strip()))
          class_details.studio = StudioType.AllySpin if 'RIDE' in class_details.name else StudioType.AllyPilates
          result_dict[current_date].append(copy(class_details))

    if len(result_dict[current_date]) == 0:
      result_dict.pop(current_date)

  return result_dict

def get_ally_schedule(weeks: int, days: list[str], instructors: list[str]) -> ResultData:
  result = ResultData()
  # REST API can only select one instructor at a time
  for instructor in instructors:
    # REST API can only select one week at a time
    for week in range(0, weeks):
      get_schedule_response = send_get_schedule_request(instructor=instructor, week=week)
      date_class_data_list_dict = parse_get_schedule_response(get_schedule_response, week=week, days=days)
      result.add_classes(date_class_data_list_dict)
  return result