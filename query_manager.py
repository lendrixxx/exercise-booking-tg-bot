from common.data_types import QueryData

class QueryManager:
  def __init__(self):
    self.user_query_data = {}

  def reset_query(self, user_id, chat_id):
    self.user_query_data[(user_id, chat_id)] = QueryData(studios={}, current_studio=StudioType.Null, weeks=0, days=[])

  def update_query_data_current_studio(self, user_id, chat_id, current_studio):
    self.user_query_data[(user_id, chat_id)].current_studio = current_studio

  def update_query_data_studios(self, user_id, chat_id, studios):
    self.user_query_data[(user_id, chat_id)].studios = studios

  def update_query_data_days(self, user_id, chat_id, days):
    self.user_query_data[(user_id, chat_id)].days = days

  def get_query_data(self, user_id, chat_id):
    return self.user_query_data[(user_id, chat_id)]