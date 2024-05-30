from common.data_types import studio_location

pilates_instructorid_map = {
  'arlene' : 2160875872725238935,
  'audrey' : 1996994498550302066,
  'birdie' : 1180807733788542506,
  'cass' : 1357866602611082454,
  'celia' : 1925180746985637520,
  'chris' : 831536396748457337,
  'christina' : 1101053328256664706,
  'daniella' : 2033233873118168303,
  'darryl' : 2163761010370938383,
  'deborah' : 2041986242735769080,
  'dominic' : 2072210158787757325,
  'jaline' : 1565057901930743754,
  'janina' : 1845513974624290437,
  'jean' : 830351642418218848,
  'jolene' : 2057115525326047109,
  'kai' : 831527925596554758,
  'louise' : 1949842029760481231,
  'marta' : 1851348768838911538,
  'nadia' : 2004850802815928297,
  'natalie' : 2062259724987926022,
  'nicole y' : 1506318891066852495,
  'rissa' : 1200624397262522298,
  'shauna' : 2038340722679088310,
  'si ling' : 831526543095235711,
  'tara' : 1822365229946767326,
  'vanie' : 1641234695419070373,
  'vnex' : 1656299566300923754,
  'wesley' : 831521921425212645,
  'zul' : 1656300400749315316,
}

spin_instructorid_map = {
  'adli' : 1645448892432516382,
  'aminah' : 1260133520399926445,
  'belle' : 1667940767512921923,
  'birdie' : 1180807733788542506,
  'brian' : 1168576278962373813,
  'charmian' : 1007644182870754845,
  'chin' : 1380209966429767189,
  'christina' : 1101053328256664706,
  'danial' : 1512190772407960669,
  'darren' : 1392508419851682974,
  'doro' : 1671536910410974685,
  'je' : 830350906779239658,
  'jy' : 1395485866276685236,
  'janani' : 1650450857231124160,
  'jean' : 830351642418218848,
  'jelina' : 1022257696251839524,
  'jocelyn' : 2099803114801465164,
  'jojo' : 1379359863418651956,
  'justin t' : 2077478890380461382,
  'kenji' : 1646157782874851024,
  'lydia' : 830352466917721680,
  'nat' : 1099739124576814651,
  'rat' : 1412163505716463360,
  'ria' : 1036620094051976840,
  'rianda' : 997646247982531896,
  'ru' : 2087677733806016437,
  'shana' : 830351728074295225,
  'shaun' : 1383894950298519223,
  'si ling' : 831526543095235711,
  'tanzo' : 1656526894608155770,
  'terence' : 1117212584303396493,
  'tricia' : 2097765867042374967,
  'triscilla' : 1659323167006524630,
  'una' : 1485215787596646394,
  'vanessa' : 1004056440844846141,
  'vnex' : 1656299566300923754,
  'zoe' : 1219377436370666792,
  'zul' : 1656300400749315316,
}

location_map = {
  studio_location.Centrepoint: 1,
  studio_location.StarVista: 2,
  studio_location.MilleniaWalk: 3,
  studio_location.i12: 5,
  studio_location.GreatWorld: 6,
  studio_location.Raffles: 8,
}

location_str_map = {
  'The Centrepoint (CTP)' : studio_location.Centrepoint,
  'The Star Vista (STV)' : studio_location.StarVista,
  'Millenia Walk (MW)' : studio_location.MilleniaWalk,
  'i12 Katong (KTG)' : studio_location.i12,
  'Great World (GW)' : studio_location.GreatWorld,
  'Raffles Place (RP)' : studio_location.Raffles,
}

pilates_instructor_names = list(pilates_instructorid_map)
spin_instructor_names = list(spin_instructorid_map)
pilates_locations = list(location_map)
pilates_locations.remove('Millenia Walk')
spin_locations = list(location_map)
spin_locations.remove('Great World')