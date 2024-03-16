from common.data_types import studio_location

instructorid_map = {
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

location_map = {
  studio_location.Raffles: 1,
  studio_location.Orchard: 12,
}

response_location_to_studio_location_map = {
  'Orchard' : studio_location.Orchard,
  'Raffles Place' : studio_location.Raffles,
}

instructor_names = list(instructorid_map)
locations = list(location_map)