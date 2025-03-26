from common.data_types import StudioLocation

RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP = {
  "BUGIS" : StudioLocation.Bugis,
  "ORCHARD" : StudioLocation.Orchard,
  "TANJONG PAGAR" : StudioLocation.TJPG,
}

ROOM_NAME_TO_STUDIO_LOCATION_MAP = {
  "Revolution - Bugis" : StudioLocation.Bugis,
  "Revolution - Orchard" : StudioLocation.Orchard,
  "Revolution - Tanjong Pagar" : StudioLocation.TJPG,
  "TP - Nov 2024" : StudioLocation.TJPG,
  "Orchard - Nov 2024" : StudioLocation.Orchard,
}

SITE_ID_MAP = {
  "Bugis" : "amJoZkVHZTZETDY5NHExRlc0U1A4dz09",
  "Orchard" : "SUF6aklTN1BLYWVyNGtGVnBuQ2JiUT09",
  "TJPG" : "WHplM0YwQjVCUmZic3RvV3oveFFSQT09",
}