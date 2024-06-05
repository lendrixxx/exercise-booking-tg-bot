from common.data_types import StudioLocation

LOCATION_MAP = {
  StudioLocation.Centrepoint: 1,
  StudioLocation.StarVista: 2,
  StudioLocation.MilleniaWalk: 3,
  StudioLocation.i12: 5,
  StudioLocation.GreatWorld: 6,
  StudioLocation.Raffles: 8,
}

LOCATION_STR_MAP = {
  'The Centrepoint (CTP)' : StudioLocation.Centrepoint,
  'The Star Vista (STV)' : StudioLocation.StarVista,
  'Millenia Walk (MW)' : StudioLocation.MilleniaWalk,
  'i12 Katong (KTG)' : StudioLocation.i12,
  'Great World (GW)' : StudioLocation.GreatWorld,
  'Raffles Place (RP)' : StudioLocation.Raffles,
}
