from common.data_types import studio_location

instructorid_map = {
  'albert' : 1829631370465379785,
  'aloysius' : 1061257406756947460,
  'angela' : 1061257099951998364,
  'annabelle' : 1443857916816786585,
  'becky' : 1652636794056869410,
  'cass' : 1094644926035003076,
  'cat' : 1061258331089274738,
  'celeste' : 1679384360534411233,
  'charlene' : 1061259499496539479,
  'charles' : 1846989449905308818,
  'chloe' : 1569393883983381850,
  'clarissa' : 1268581088050021515,
  'claudia' : 1550674241853064611,
  'dawn' : 1448843494620661660,
  'desmond' : 2121707513752585501,
  'endo' : 1406504389975213497,
  'gabriel' : 1463440570742474264,
  'jt lim' : 2010695410124850182,
  'jerlyn' : 1443152247969023702,
  'joanne' : 1347592168499316443,
  'jody' : 1061258619707721710,
  'joella' : 1282181370587645893,
  'krys c' : 1549833256898135461,
  'leroy' : 1738137697186219321,
  'marcus' : 1860071577723340610,
  'nickyolas' : 1842531734873179286,
  'nicole' : 1792631555521251167,
  'peixing' : 1631486896725034703,
  'sally' : 1443858935269295790,
  'semelle' : 1649766837199570375,
  'sharlyn' : 1443858692393928266,
  'shu hui' : 1312759738160645368,
  'sydney' : 2152795406222755363,
  'tanya' : 1676537740230919703,
  'val rae' : 1591317350181766876,
  'valerie' : 1247038292604486851,
  'vincent' : 2010685362199856209,
  'wei xuan' : 1380186515379849077,
  'yini' : 2041992626130912771,
  'yoppie' : 2152794507886724235,
  'yvonne' : 1738138236850537652,
  'zai' : 1562846502458492314,
  'zann' : 1562822180050306621,
  'tzer bin' : 1793200306146772455,
}

location_map = {
  studio_location.Orchard: 2,
  studio_location.TJPG: 3,
  studio_location.Bugis: 4,
  studio_location.Suntec: 5,
}

response_location_to_studio_location_map = {
  'BUGIS' : studio_location.Bugis,
  'ORCHARD' : studio_location.Orchard,
  'SUNTEC' : studio_location.Suntec,
  'TANJONG PAGAR' : studio_location.TJPG,
}

instructor_names = list(instructorid_map)
locations = list(location_map)