from common.data_types import studio_location

pilates_instructorid_map = {
  'andre w' : 2037722864135702427,
  'candice q' : 1955672703272748156,
  'janet c' : 1955670656183960814,
  'johanna m' : 2186146664434107665,
  'ruth n' : 1831629820937635529,
  'tessa t' : 2037724761823381134,
  'valerie n' : 1537574315606672790,
}

spin_instructorid_map = {
  'ally' : 1642510301125412688,
  'camille m' : 1675489003639408248,
  'cheryl o' : 2041800085439776037,
  'jamie l' : 1537577051802829896,
  'jaryl t' : 1865136743510967611,
  'jasper n' : 1537564732016297981,
  'mandy l' : 2196238173531538606,
  'marina t' : 1618656214571288130,
  'nerissa n' : 1865136868157294509,
  'rachel c' : 2203552956391884304,
  'ruth n' : 1831629820937635529,
  'samuel k' : 2041799825862689958,
  'tiffany d' : 1910049772169856114,
  'valerie n' : 1537574315606672790,
  'zachary t' : 2023749708073141918,
}

instructorid_map = {**pilates_instructorid_map, **spin_instructorid_map}

location_map = {
  studio_location.CrossStreet: 1,
}

pilates_instructor_names = list(pilates_instructorid_map)
spin_instructor_names = list(spin_instructorid_map)