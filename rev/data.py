from common.data_types import StudioLocation

RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP = {
  'BUGIS' : StudioLocation.Bugis,
  'ORCHARD' : StudioLocation.Orchard,
  'SUNTEC' : StudioLocation.Suntec,
  'TANJONG PAGAR' : StudioLocation.TJPG,
}

ROOM_NAME_TO_STUDIO_LOCATION_MAP = {
  'Revolution - Bugis' : StudioLocation.Bugis,
  'Revolution - Orchard' : StudioLocation.Orchard,
  'Revolution - Suntec' : StudioLocation.Suntec,
  'Revolution - Tanjong Pagar' : StudioLocation.TJPG,
}

SITE_ID_MAP = {
  'Bugis' : 'amJoZkVHZTZETDY5NHExRlc0U1A4dz09',
  'Orchard' : 'SUF6aklTN1BLYWVyNGtGVnBuQ2JiUT09',
  'Suntec' : 'WE5rWUdOLzhIVjNLc2k0cTd4dWRQdz09',
  'TJPG' : 'WHplM0YwQjVCUmZic3RvV3oveFFSQT09',
}