import json
import os
import pytz
import requests
from common.data_types import CapacityInfo, ClassData, RESPONSE_AVAILABILITY_MAP, ResultData, StudioLocation, StudioType
from copy import copy
from datetime import datetime, timedelta
from studios.rev.data import ROOM_NAME_TO_STUDIO_LOCATION_MAP, SITE_ID_MAP

SECURITY_TOKEN = os.environ.get("BOOKING_BOT_REV_SECURITY_TOKEN")

def send_get_schedule_request(location: StudioLocation, start_date: datetime.date, end_date: datetime) -> requests.models.Response:
  start_date_str = datetime.strftime(start_date,"%Y-%m-%d")
  end_date_str = datetime.strftime(end_date,"%Y-%m-%d")
  url = "https://widgetapi.hapana.com/v2/wAPI/site/sessions?sessionCategory=classes"
  params = {"siteID": SITE_ID_MAP[location], "startDate": start_date_str, "endDate": end_date_str}
  headers = {
    "Content-Type": "application/json",
    "Securitytoken": SECURITY_TOKEN,
  }
  return requests.get(url=url, params=params, headers=headers)


def parse_get_schedule_response(logger: "logging.Logger", response: requests.models.Response) -> dict[datetime.date, list[ClassData]]:
  if response.status_code != 200:
    logger.warning(f"Failed to get schedule - API callback error {response.status_code}")
    return {}

  result_dict = {}
  try:
    response_json = json.loads(response.text)
    if "success" not in response_json:
      logger.warning(f"Failed to get schedule - API callback failed: {response_json}")
      return {}
  except Exception as e:
    logger.warning(f"Failed to get schedule - {e}: {response.text}")
    return {}

  for data in response_json["data"]:
    try:
      if data["sessionStatus"] == "complete":
        continue

      class_date = datetime.strptime(data["sessionDate"], "%Y-%m-%d").date()
      instructors = []
      for instructorData in data["instructorData"]:
        instructors.append(instructorData["instructorName"])
      instructor_str = " / ".join(instructors)

      class_name = data["sessionName"]
      class_name_location_split_pos = class_name.find(" @ ")
      class_name = class_name[:class_name_location_split_pos]
      class_time = datetime.strptime(data["startTime"], "%H:%M:%S")

      if data["roomName"] in ROOM_NAME_TO_STUDIO_LOCATION_MAP:
        location = ROOM_NAME_TO_STUDIO_LOCATION_MAP[data["roomName"]]
      else:
        location = StudioLocation.Null
        class_name += " @ " + data["roomName"]

      class_details = ClassData(
        studio=StudioType.Rev,
        location=location,
        name=class_name,
        instructor=instructor_str,
        time=datetime.strftime(class_time, "%I:%M %p").lstrip("0"),
        availability=RESPONSE_AVAILABILITY_MAP[data["sessionStatus"]],
        capacity_info=CapacityInfo(
          has_info=True,
          capacity=data["capacity"],
          remaining=data["remaining"],
          waitlist_capacity=data["waitlistCapacity"],
          waitlist_reserved=data["waitlistReserved"]))

      if class_date not in result_dict:
        result_dict[class_date] = [copy(class_details)]
      else:
        result_dict[class_date].append(copy(class_details))

    except Exception as e:
      logger.warning(f"Failed to get details of class - {e}. Data: {data}")

  return result_dict

def get_rev_schedule(logger: "logging.Logger") -> ResultData:
  result = ResultData()
  start_date = datetime.now(pytz.timezone("Asia/Singapore"))
  end_date = start_date + timedelta(weeks=4) # Rev schedule only shows up to 4 weeks in advance

  # REST API can only select one location at a time
  for location in ["Bugis", "Orchard", "TJPG"]:
    get_schedule_response = send_get_schedule_request(location=location, start_date=start_date, end_date=end_date)
    date_class_data_list_dict = parse_get_schedule_response(logger=logger, response=get_schedule_response)
    result.add_classes(date_class_data_list_dict)

  return result

def get_instructorid_map(logger: "logging.Logger") -> dict[str, int]:
  url = "https://widgetapi.hapana.com/v2/wAPI/site/instructor?siteID=WHplM0YwQjVCUmZic3RvV3oveFFSQT09"
  headers = {
    "Content-Type": "application/json",
    "Securitytoken": SECURITY_TOKEN,
  }
  response = requests.get(url=url, headers=headers)
  if response.status_code != 200:
    logger.warning(f"Failed to get list of instructors - API callback error {response.status_code}")
    return {}

  try:
    response_json = json.loads(response.text)
    instructorid_map = {}
    if response_json["success"] == False:
      logger.warning(f"Failed to get list of instructors - API callback failed")
      return {}

    for data in response_json["data"]:
      instructorid_map[data["instructorName"].lower()] = data["instructorID"]

  except Exception as e:
    logger.warning(f"Failed to get list of instructors - {e}")
    return {}

  return instructorid_map

def get_rev_schedule_and_instructorid_map(logger: "logging.Logger") -> tuple[ResultData, dict[str, int]]:
  return get_rev_schedule(logger=logger), get_instructorid_map(logger=logger)