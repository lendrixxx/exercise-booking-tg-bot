import calendar
import global_variables
import json
import re
import requests
from bs4 import BeautifulSoup
from common.data_types import CapacityInfo, ClassAvailability, ClassData, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta
from html import unescape

def send_get_schedule_request(start_date: datetime.date, end_date: datetime.date) -> requests.models.Response:
  start_date_str = datetime.strftime(start_date,'%Y-%m-%d')
  end_date_str = datetime.strftime(end_date,'%Y-%m-%d')
  url = 'https://widgets.mindbodyonline.com/widgets/schedules/189924/load_markup'
  params = {
    'callback': 'jQuery36403516351979316319_1742526275618',
    'options[start_date]': start_date_str,
    'options[end_date]': end_date_str,
  }

  return requests.get(url=url, params=params)

def get_schedule_from_response_soup(soup: BeautifulSoup) -> dict[datetime.date, list[ClassData]]:
  session_div_list = [div for div in soup.find_all('div') if 'bw-session' in div.get('class', [])]
  result_dict = {}
  for session_div in session_div_list:
    session_time_div = session_div.find('div', class_='bw-session__time')
    if session_time_div is None:
      global_variables.LOGGER.warning(f'Failed to get session time from session info: {session_div}')
      continue

    start_time_tag = session_time_div.find('time', class_='hc_starttime')
    if start_time_tag is None:
      global_variables.LOGGER.warning(f'Failed to get session time: {session_time_div}')
      continue

    start_datetime_str = start_time_tag.get('datetime')
    if start_datetime_str is None:
      global_variables.LOGGER.warning(f'Failed to get session datetime: {start_time_tag}')
      continue

    start_datetime = datetime.fromisoformat(start_datetime_str)
    session_name_div = session_div.find('div', class_='bw-session__name')
    if session_name_div is None:
      global_variables.LOGGER.warning(f'Failed to get session name: {session_div}')
      continue

    session_staff_div = session_div.find('div', class_='bw-session__staff')
    if session_staff_div is None:
      global_variables.LOGGER.warning(f'Failed to get session instructor: {session_div}')
      continue

    instructor_name = ' '.join(session_staff_div.get_text().strip().lower().split())
    instructor_name = instructor_name.replace('\n', ' ')
    class_details = ClassData(
      studio=StudioType.Anarchy,
      location=StudioLocation.Robinson,
      name=session_name_div.get_text().strip(),
      instructor=instructor_name,
      time=start_datetime.strftime('%I:%M %p'),
      availability=ClassAvailability.Waitlist if 'Join Waitlist' in session_div.text else ClassAvailability.Available,
      capacity_info=CapacityInfo())

    start_date = start_datetime.date()
    if start_date not in result_dict:
      result_dict[start_date] = [copy(class_details)]
    else:
      result_dict[start_date].append(copy(class_details))

  return result_dict

def get_soup_from_response(response: requests.models.Response) -> BeautifulSoup:
  match = re.search(r'^\w+\((.*)\);?$', response.text, re.DOTALL)
  if match:
    try:
      json_str = match.group(1)
      data = json.loads(json_str)
    except Exception as e:
      global_variables.LOGGER.warning(f'Failed to parse response to json {response.text} - {e}')
      return None
  else:
    global_variables.LOGGER.warning(f'Failed to parse response {response.text}')
    return None

  try:
    cleaned_html = unescape(data['class_sessions'])
  except Exception as e:
    global_variables.LOGGER.warning(f'Failed to parse html from response {data} - {e}')
    return None

  return BeautifulSoup(cleaned_html, 'html.parser')

def get_instructorid_map_from_response_soup(soup: BeautifulSoup) -> dict[str, int]:
  session_div_list = [div for div in soup.find_all('div') if 'bw-session' in div.get('class', [])]
  instructorid_map = {}
  for session_div in session_div_list:
    session_staff_div = session_div.find('div', class_='bw-session__staff')
    if session_staff_div is None:
      global_variables.LOGGER.warning(f'Failed to get session instructor: {session_div}')
      continue

    instructor_name = ' '.join(session_staff_div.get_text().strip().lower().split())
    instructor_name = instructor_name.replace('\n', ' ')
    instructor_id = session_div.get('data-bw-widget-trainer')
    if instructor_id is None:
      global_variables.LOGGER.warning(f'Failed to get instructor id of instructor {instructor_name}: {session_div}')
      continue

    instructorid_map[instructor_name] = instructor_id

  return instructorid_map

def get_anarchy_schedule_and_instructorid_map() -> tuple[ResultData, dict[str, int]]:
  start_date = datetime.now().date()
  end_date = start_date + timedelta(weeks=3) # Anarchy schedule only shows up to 3 weeks in advance
  get_schedule_response = send_get_schedule_request(start_date=start_date, end_date=end_date)
  soup = get_soup_from_response(response=get_schedule_response)
  if soup is None:
    return ResultData(), {}

  result = ResultData()

  # Get schedule
  date_class_data_list_dict = get_schedule_from_response_soup(soup=soup)
  result.add_classes(date_class_data_list_dict)

  # Get instructor id map
  instructorid_map = get_instructorid_map_from_response_soup(soup=soup)
  if len(date_class_data_list_dict) == 0:
    # Anarchy schedule doesn't show for future dates if there are no more classes today
    start_date = start_date + timedelta(days=1)
    get_schedule_response = send_get_schedule_request(start_date=start_date, end_date=end_date)
    soup = get_soup_from_response(response=get_schedule_response)

    # Get schedule
    date_class_data_list_dict = get_schedule_from_response_soup(soup=soup)
    result.add_classes(date_class_data_list_dict)

    # Get instructor id map
    instructorid_map = get_instructorid_map_from_response_soup(soup=soup)

  return result, instructorid_map
