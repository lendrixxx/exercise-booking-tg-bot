from common.data_types import StudioLocation

LOCATION_MAP = {
  StudioLocation.Raffles: 1,
  StudioLocation.Orchard: 12,
}

RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP = {
  "Orchard" : StudioLocation.Orchard,
  "Raffles Place" : StudioLocation.Raffles,
}