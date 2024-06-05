from common.data_types import StudioLocation

LOCATION_MAP = {
  StudioLocation.Orchard: 2,
  StudioLocation.TJPG: 3,
  StudioLocation.Bugis: 4,
  StudioLocation.Suntec: 5,
}

RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP = {
  'BUGIS' : StudioLocation.Bugis,
  'ORCHARD' : StudioLocation.Orchard,
  'SUNTEC' : StudioLocation.Suntec,
  'TANJONG PAGAR' : StudioLocation.TJPG,
}