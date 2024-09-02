import calendar
import json
import logging
import os
import pytz
import requests
from bs4 import BeautifulSoup
from common.data_types import ClassAvailability, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta
from rev.data import ROOM_NAME_TO_STUDIO_LOCATION_MAP, SITE_ID_MAP

LOGGER = logging.getLogger(__name__)
SECURITY_TOKEN = os.environ.get('BOOKING_BOT_REV_SECURITY_TOKEN')

def send_get_schedule_request(location: StudioLocation, start_date: str, end_date: str, instructorid_map: dict[str, int]) -> requests.models.Response:
  url = 'https://widgetapi.hapana.com/v2/wAPI/site/sessions?sessionCategory=classes'
  params = {'siteID': SITE_ID_MAP[location], 'startDate': start_date, 'endDate': end_date}
  headers = {
    'Content-Type': 'application/json',
    'Securitytoken': SECURITY_TOKEN,
  }
  return requests.get(url=url, params=params, headers=headers)


def parse_get_schedule_response(response: requests.models.Response, days: list[str]) -> dict[datetime.date, list[ClassData]]:
  if response.status_code != 200:
    LOGGER.warning(f'Failed to get schedule - API callback error {response.status_code}')
    return {}

  result_dict = {}
  try:
    response_json = json.loads(response.text)
    if response_json['success'] == False:
      LOGGER.warning(f'Failed to get schedule - API callback failed')
      return {}

    for data in response_json['data']:
      if data['sessionStatus'] == 'complete':
        continue

      class_date = datetime.strptime(data['sessionDate'], '%Y-%m-%d').date()
      if 'All' not in days and calendar.day_name[class_date.weekday()] not in days:
        continue

      instructors = []
      for instructorData in data['instructorData']:
        instructors.append(instructorData['instructorName'])
      instructor_str = ' / '.join(instructors)

      class_name = data['sessionName']
      class_name_location_split_pos = class_name.find(' @ ')
      class_name = class_name[:class_name_location_split_pos]

      class_time = datetime.strptime(data['startTime'], '%H:%M:%S')

      class_details = ClassData(
        studio=StudioType.Rev,
        location=ROOM_NAME_TO_STUDIO_LOCATION_MAP[data['roomName']],
        name=class_name,
        instructor=instructor_str,
        time=datetime.strftime(class_time, '%I:%M %p'),
        availability=RESPONSE_AVAILABILITY_MAP[data['sessionStatus']])

      if class_date not in result_dict:
        result_dict[class_date] = []
      result_dict[class_date].append(copy(class_details))

    result_dict = {key:val for key, val in result_dict.items() if val}

  except Exception as e:
    LOGGER.warning(f'Failed to get schedule - {e}')
    return {}

  return result_dict


def get_rev_schedule(locations: list[StudioLocation], start_date: str, end_date: str, days: str, instructorid_map: dict[str, int]) -> ResultData:
  result = ResultData()
  # REST API can only select one location at a time
  if 'All' in locations:
    locations = ['Bugis', 'Orchard', 'TJPG']

  if start_date == '':
    start_date = datetime.now(pytz.timezone('Asia/Singapore'))
    start_date_str = start_date.strftime('%Y-%m-%d')

  if end_date == '':
    end_date = start_date + timedelta(weeks=4)
    end_date_str = end_date.strftime('%Y-%m-%d')

  for location in locations:
    get_schedule_response = send_get_schedule_request(location=location, start_date=start_date, end_date=end_date, instructorid_map=instructorid_map)
    date_class_data_list_dict = parse_get_schedule_response(response=get_schedule_response, days=days)
    result.add_classes(date_class_data_list_dict)

  return result

def get_instructorid_map() -> dict[str, int]:
  url = 'https://widgetapi.hapana.com/v2/wAPI/site/instructor?siteID=WHplM0YwQjVCUmZic3RvV3oveFFSQT09'
  headers = {
    'Content-Type': 'application/json',
    'Securitytoken': SECURITY_TOKEN,
  }
  response = requests.get(url=url, headers=headers)
  if response.status_code != 200:
    LOGGER.warning(f'Failed to get list of instructors - API callback error {response.status_code}')
    return instructorid_map

  try:
    response_json = json.loads(response.text)
    instructorid_map = {}
    if response_json['success'] == False:
      LOGGER.warning(f'Failed to get list of instructors - API callback failed')
      return instructorid_map

    for data in response_json['data']:
      instructorid_map[data['instructorName'].lower()] = data['instructorID']

  except Exception as e:
    LOGGER.warning(f'Failed to get list of instructors - {e}')
    return instructorid_map

  return instructorid_map
