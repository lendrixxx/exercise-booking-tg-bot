from common.data_types import StudioLocation

INSTRUCTORID_MAP = {
  'cassandra': 1488914980282566323,
  'gino': 1962218357339981238,
  'hyekel': 1575299441340974436,
  'ian': 882162166147318961,
  'jeremy': 882162724258186576,
  'jian hong': 1485105934370866912,
  'jo yee': 1996750998659401697,
  'lorna': 882162518837953821,
  'mandalyn': 1962219855704753655,
  'ria': 1575295622502680332,
  'shannon': 1575296829229107001,
  'shiqeen': 996641433974736314,
  'stephanie': 1488914369566737506,
}

LOCATION_MAP = {
  StudioLocation.Raffles: 1,
  StudioLocation.Orchard: 12,
}

RESPONSE_LOCATION_TO_STUDIO_LOCATION_MAP = {
  'Orchard' : StudioLocation.Orchard,
  'Raffles Place' : StudioLocation.Raffles,
}

INSTRUCTOR_NAMES = list(INSTRUCTORID_MAP)