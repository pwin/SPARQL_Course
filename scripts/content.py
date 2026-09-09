# -*- coding: utf-8 -*-
"""Content tables for the Bookshop Trail dataset.

Places are real, with real coordinates, so distances and containment can be
checked against a map.  Everything else -- shops, people, publishers, books,
events -- is invented, so no query in this course can teach a learner a false
fact about a real person or business.
"""

COUNTRIES = [
    ("scotland", "Scotland", "Alba",  "gd"),
    ("england",  "England",  None,    None),
    ("wales",    "Wales",    "Cymru", "cy"),
]

# English regions only: Scotland and Wales go straight from council to country.
# The asymmetry is deliberate -- it is what makes `bs:within+` earn its keep.
REGIONS = [
    ("north-east-england", "North East England",       "england"),
    ("north-west-england", "North West England",       "england"),
    ("yorkshire",          "Yorkshire and the Humber", "england"),
    ("west-midlands",      "West Midlands",            "england"),
    ("east-of-england",    "East of England",          "england"),
    ("south-east-england", "South East England",       "england"),
    ("south-west-england", "South West England",       "england"),
]

# (id, label, parent)  -- parent is a region for England, a country otherwise
COUNCILS = [
    ("dumfries-galloway",  "Dumfries and Galloway", "scotland"),
    ("edinburgh-city",     "City of Edinburgh",     "scotland"),
    ("glasgow-city",       "Glasgow City",          "scotland"),
    ("fife",               "Fife",                  "scotland"),
    ("highland",           "Highland",              "scotland"),
    ("northumberland",     "Northumberland",        "north-east-england"),
    ("cumbria",            "Cumbria",               "north-west-england"),
    ("greater-manchester", "Greater Manchester",    "north-west-england"),
    ("merseyside",         "Merseyside",            "north-west-england"),
    ("north-yorkshire",    "North Yorkshire",       "yorkshire"),
    ("shropshire",         "Shropshire",            "west-midlands"),
    ("oxfordshire",        "Oxfordshire",           "south-east-england"),
    ("greater-london",     "Greater London",        "south-east-england"),
    ("cambridgeshire",     "Cambridgeshire",        "east-of-england"),
    ("norfolk",            "Norfolk",               "east-of-england"),
    ("somerset",           "Somerset",              "south-west-england"),
    ("devon",              "Devon",                 "south-west-england"),
    ("cornwall",           "Cornwall",              "south-west-england"),
    ("powys",              "Powys",                 "wales"),
    ("ceredigion",         "Ceredigion",            "wales"),
    ("city-of-cardiff",    "City of Cardiff",       "wales"),
    ("county-durham",      "County Durham",         "north-east-england"),
    ("perth-kinross",      "Perth and Kinross",     "scotland"),
]

# (id, label, lat, lon, council, population, is_book_town)
SETTLEMENTS = [
    ("wigtown",     "Wigtown",            54.8690, -4.4400, "dumfries-galloway",    1000, True),
    ("edinburgh",   "Edinburgh",          55.9533, -3.1883, "edinburgh-city",     506520, False),
    ("glasgow",     "Glasgow",            55.8642, -4.2518, "glasgow-city",       635640, False),
    ("st-andrews",  "St Andrews",         56.3398, -2.7967, "fife",                16800, False),
    ("inverness",   "Inverness",          57.4778, -4.2247, "highland",            47790, False),
    ("portree",     "Portree",            57.4125, -6.1958, "highland",             2500, False),
    ("berwick",     "Berwick-upon-Tweed", 55.7708, -2.0053, "northumberland",      12040, False),
    ("sedbergh",    "Sedbergh",           54.3200, -2.5290, "cumbria",              2800, True),
    ("kendal",      "Kendal",             54.3280, -2.7460, "cumbria",             28590, False),
    ("keswick",     "Keswick",            54.6013, -3.1347, "cumbria",              5240, False),
    ("york",        "York",               53.9600, -1.0873, "north-yorkshire",    153720, False),
    ("whitby",      "Whitby",             54.4863, -0.6133, "north-yorkshire",     13210, False),
    ("manchester",  "Manchester",         53.4808, -2.2426, "greater-manchester", 553230, False),
    ("liverpool",   "Liverpool",          53.4084, -2.9916, "merseyside",         496770, False),
    ("shrewsbury",  "Shrewsbury",         52.7069, -2.7527, "shropshire",          76780, False),
    ("ludlow",      "Ludlow",             52.3680, -2.7180, "shropshire",          10940, False),
    ("oxford",      "Oxford",             51.7520, -1.2577, "oxfordshire",        162100, False),
    ("cambridge",   "Cambridge",          52.2053,  0.1218, "cambridgeshire",     145670, False),
    ("norwich",     "Norwich",            52.6309,  1.2974, "norfolk",            144000, False),
    ("london",      "London",             51.5074, -0.1278, "greater-london",    8982000, False),
    ("bath",        "Bath",               51.3811, -2.3590, "somerset",            94090, False),
    ("exeter",      "Exeter",             50.7184, -3.5339, "devon",              130800, False),
    ("penzance",    "Penzance",           50.1186, -5.5370, "cornwall",            21200, False),
    ("hay-on-wye",  "Hay-on-Wye",         52.0760, -3.1288, "powys",                1500, True),
    ("aberystwyth", "Aberystwyth",        52.4140, -4.0810, "ceredigion",          15940, False),
    ("cardiff",     "Cardiff",            51.4816, -3.1791, "city-of-cardiff",    362310, False),
    # Four towns on the map with no bookshop of their own.  They are here so
    # that OPTIONAL, MINUS and NOT EXISTS have something real to find, and so
    # that "which town is furthest from a bookshop?" has an answer.
    ("durham",      "Durham",             54.7761, -1.5733, "county-durham",       48070, False),
    ("perth",       "Perth",              56.3950, -3.4308, "perth-kinross",       47430, False),
    ("fort-william","Fort William",       56.8198, -5.1052, "highland",            10460, False),
    ("truro",       "Truro",              50.2632, -5.0510, "cornwall",            18770, False),
]

# Real Welsh and Gaelic place names: they give the language-tag lessons
# something real to work on.
PLACE_ALT_NAMES = {
    "cardiff":     [("Caerdydd", "cy")],
    "hay-on-wye":  [("Y Gelli Gandryll", "cy")],
    "aberystwyth": [("Aberystwyth", "cy")],
    "edinburgh":   [("Dun Eideann", "gd")],
    "glasgow":     [("Glaschu", "gd")],
    "inverness":   [("Inbhir Nis", "gd")],
    "portree":     [("Port Righ", "gd")],
    "wigtown":     [("Baile na h-Uige", "gd")],
}


# DBpedia resources for the same real places.  The shops, people and books are
# invented; the towns are not, and owl:sameAs is how a dataset says so.  These
# links are what makes the federation module possible: they give a SERVICE
# call something to join on that is not a string match on a label.
# Verified: all thirty resolve on dbpedia.org.
DBPEDIA = {
    "wigtown":      "Wigtown",
    "edinburgh":    "Edinburgh",
    "glasgow":      "Glasgow",
    "st-andrews":   "St_Andrews",
    "inverness":    "Inverness",
    "portree":      "Portree",
    "berwick":      "Berwick-upon-Tweed",
    "sedbergh":     "Sedbergh",
    "kendal":       "Kendal",
    "keswick":      "Keswick,_Cumbria",
    "york":         "York",
    "whitby":       "Whitby",
    "manchester":   "Manchester",
    "liverpool":    "Liverpool",
    "shrewsbury":   "Shrewsbury",
    "ludlow":       "Ludlow",
    "oxford":       "Oxford",
    "cambridge":    "Cambridge",
    "norwich":      "Norwich",
    "london":       "London",
    "bath":         "Bath,_Somerset",
    "exeter":       "Exeter",
    "penzance":     "Penzance",
    "hay-on-wye":   "Hay-on-Wye",
    "aberystwyth":  "Aberystwyth",
    "cardiff":      "Cardiff",
    "durham":       "Durham,_England",
    "perth":        "Perth,_Scotland",
    "fort-william": "Fort_William,_Highland",
    "truro":        "Truro",
}

# (id, label, settlement, founded, floor_m2, staff, specialism, second_hand, cafe)
SHOPS = [
    ("inkwell",       "The Inkwell",           "wigtown",     1979, 140,  4, "crime-fiction",      True,  True),
    ("marginalia",    "Marginalia",            "wigtown",     1994,  85,  2, "poetry",             True,  False),
    ("colophon",      "Colophon Books",        "edinburgh",   1963, 320, 11, "literary-fiction",   False, True),
    ("broken-spine",  "The Broken Spine",      "edinburgh",   2008,  95,  3, "tartan-noir",        True,  False),
    ("quire",         "The Quire",             "glasgow",     1987, 260,  9, "graphic-novels",     False, True),
    ("verso",         "Verso and Recto",       "glasgow",     2015, 110,  4, "translated-fiction", False, True),
    ("gutter-gilt",   "Gutter and Gilt",       "st-andrews",  1955, 130,  5, "history",            True,  False),
    ("northern-light","Northern Light Books",  "inverness",   1998, 175,  6, "nature-writing",     False, True),
    ("sea-margin",    "The Sea Margin",        "portree",     2011,  60,  2, "folk-fantasy",       False, True),
    ("borderprint",   "Borderprint",           "berwick",     1972, 105,  3, "maritime-history",   True,  False),
    ("dales-folio",   "The Dales Folio",       "sedbergh",    1968, 150,  4, "nature-writing",     True,  True),
    ("errata",        "Errata",                "sedbergh",    2001,  70,  2, "science-fiction",    True,  False),
    ("pressmark",     "Pressmark",             "kendal",      1983, 190,  6, "travel-writing",     False, True),
    ("bookbarrow",    "Bookbarrow",            "keswick",     1990,  80,  3, "mountaineering",     True,  False),
    ("endpapers",     "Endpapers",             "york",        1949, 400, 14, "history",            True,  True),
    ("bookwyrm",      "The Bookwyrm",          "york",        2013, 120,  5, "fantasy",            False, True),
    ("harbour-page",  "The Harbour Page",      "whitby",      1996,  90,  3, "maritime-history",   True,  False),
    ("cotton-quarto", "Cotton Quarto",         "manchester",  1974, 380, 15, "industrial-history", False, True),
    ("signature",     "Signature Books",       "liverpool",   2004, 210,  8, "poetry",             False, True),
    ("severn-leaf",   "Severn Leaf",           "shrewsbury",  1966, 160,  5, "geology",            True,  False),
    ("dog-eared",     "The Dog-Eared",         "ludlow",      1988,  75,  2, "cosy-crime",         True,  True),
    ("candlemas",   "Candlemas Books",     "oxford",      1931, 290, 12, "classics",           True,  True),
    ("chapter-verse", "Chapter and Verse",     "cambridge",   1958, 240, 10, "science-fiction",    False, True),
    ("broads-bindery","The Broads Bindery",    "norwich",     1992, 115,  4, "nature-writing",     True,  False),
    ("ex-libris",     "Ex Libris",             "london",      1919, 520, 22, "literary-fiction",   True,  True),
    ("turn-the-page", "Turn the Page",         "london",      2018, 130,  6, "translated-fiction", False, True),
    ("crescent",      "The Crescent Bookroom", "bath",        1961, 200,  7, "historical-fiction", True,  True),
    ("west-quay",     "West Quay Books",       "exeter",      1985, 145,  5, "travel-writing",     False, False),
    ("penwith",       "Penwith Pages",         "penzance",    2006,  65,  2, "folk-fantasy",       True,  True),
    ("castle-steps",  "Castle Steps Books",    "hay-on-wye",  1962, 230,  8, "history",            True,  True),
    ("clock-tower",   "The Clock Tower",       "hay-on-wye",  1977, 180,  6, "cosy-crime",         True,  False),
    ("cliff-road",    "Cliff Road Books",      "aberystwyth", 2000,  95,  3, "poetry",             False, True),
    ("taff-margin",   "Taff Margin",           "cardiff",     1994, 210,  9, "graphic-novels",     False, True),
]

# ---------------------------------------------------------------------------
# Genre taxonomy (SKOS).  Depth varies from 2 to 4 so that `skos:broader+`
# and `skos:broader*` behave visibly differently from a fixed-length pattern.
# (id, prefLabel, broader-or-None, altLabels, scopeNote-or-None)
# ---------------------------------------------------------------------------
GENRES = [
    ("literature",         "Literature",          None,                 [], "The top concept: everything in the scheme is narrower than this."),
    ("fiction",            "Fiction",             "literature",         [], None),
    ("non-fiction",        "Non-fiction",         "literature",         ["Nonfiction"], None),
    ("poetry",             "Poetry",              "literature",         ["Verse"], None),

    ("crime-fiction",      "Crime Fiction",       "fiction",            ["Mystery"], None),
    ("cosy-crime",         "Cosy Crime",          "crime-fiction",      ["Cozy Mystery"], "Low-jeopardy crime, usually with an amateur detective."),
    ("tartan-noir",        "Tartan Noir",         "crime-fiction",      [], "Scottish hard-boiled crime writing."),
    ("police-procedural",  "Police Procedural",   "crime-fiction",      [], None),

    ("speculative-fiction","Speculative Fiction", "fiction",            ["SF and Fantasy"], None),
    ("science-fiction",    "Science Fiction",     "speculative-fiction",["SF", "Sci-Fi"], None),
    ("hard-sf",            "Hard Science Fiction","science-fiction",    ["Hard SF"], None),
    ("space-opera",        "Space Opera",         "science-fiction",    [], None),
    ("climate-fiction",    "Climate Fiction",     "science-fiction",    ["Cli-Fi"], None),
    ("fantasy",            "Fantasy",             "speculative-fiction",[], None),
    ("folk-fantasy",       "Folk Fantasy",        "fantasy",            ["Folkloric Fantasy"], "Fantasy drawing on local folklore and landscape."),
    ("portal-fantasy",     "Portal Fantasy",      "fantasy",            [], None),

    ("historical-fiction", "Historical Fiction",  "fiction",            [], None),
    ("literary-fiction",   "Literary Fiction",    "fiction",            [], None),
    ("translated-fiction", "Translated Fiction",  "fiction",            [], "Fiction read in translation; the original language is recorded on the work."),
    ("graphic-novels",     "Graphic Novels",      "fiction",            ["Comics"], None),
    ("classics",           "Classics",            "fiction",            [], None),

    ("nature-writing",     "Nature Writing",      "non-fiction",        [], None),
    ("ornithology",        "Ornithology",         "nature-writing",     ["Birdwatching"], None),
    ("geology",            "Geology",             "nature-writing",     ["Earth Science"], None),
    ("mountaineering",     "Mountaineering",      "nature-writing",     ["Hillwalking"], None),

    ("history",            "History",             "non-fiction",        [], None),
    ("maritime-history",   "Maritime History",    "history",            ["Naval History"], None),
    ("industrial-history", "Industrial History",  "history",            [], None),
    ("local-history",      "Local History",       "history",            [], None),

    ("travel-writing",     "Travel Writing",      "non-fiction",        [], None),
    ("biography",          "Biography",           "non-fiction",        ["Life Writing"], None),
]

# Welsh / Gaelic labels on a few concepts, for the language-tag module.
GENRE_ALT_LANG = {
    "poetry":        [("Barddoniaeth", "cy"), ("Bardachd", "gd")],
    "history":       [("Hanes", "cy")],
    "fiction":       [("Ffuglen", "cy")],
    "nature-writing":[("Ysgrifennu Natur", "cy")],
}

# ---------------------------------------------------------------------------
# Publishers.  `bs:imprintOf` chains are three deep in places, which is what
# makes an inverse path (`^bs:imprintOf*`) worth teaching.
# (id, label, parent-or-None, founded, town)
# ---------------------------------------------------------------------------
PUBLISHERS = [
    ("lodestone-group", "Lodestone Group",      None,               1988, "london"),
    ("northwind",       "Northwind Press",      "lodestone-group",  1971, "edinburgh"),
    ("saltmarsh",       "Saltmarsh Books",      "northwind",        1996, "norwich"),
    ("bell-rock",       "Bell Rock Editions",   "northwind",        2003, "st-andrews"),
    ("cairn",           "Cairn Publishing",     "lodestone-group",  1979, "inverness"),
    ("drovers-road",    "Drovers Road Press",   "cairn",            2009, "hay-on-wye"),

    ("thornfield",      "Thornfield House",     None,               1934, "oxford"),
    ("pica",            "Pica Books",           "thornfield",       1990, "cambridge"),
    ("wrenline",        "Wrenline",             "pica",             2012, "bath"),

    ("greenslate",      "Greenslate",           None,               2001, "cardiff"),
    ("cwm-press",       "Cwm Press",            "greenslate",       2014, "aberystwyth"),

    ("harbourmaster",   "Harbourmaster Books",  None,               1962, "whitby"),
    ("tide-and-tiller", "Tide and Tiller",      "harbourmaster",    1998, "penzance"),
]

# ---------------------------------------------------------------------------
# Authors.  `bs:influencedBy` is a directed graph with long chains, a
# diamond, and one deliberate two-cycle -- because learners must find out
# that `+` copes with cycles and a hand-written recursive join does not.
# (id, name, born, died-or-None, based_in, writes_in, influenced_by[])
# ---------------------------------------------------------------------------
AUTHORS = [
    ("rhona-blackwood",  "Rhona Blackwood",   1901, 1978, "edinburgh",   "en", []),
    ("iolo-vaughan",     "Iolo Vaughan",      1908, 1981, "aberystwyth", "cy", []),
    ("gerard-tyne",      "Gerard Tyne",       1912, 1990, "berwick",     "en", []),
    ("maud-ellery",      "Maud Ellery",       1918, 1994, "oxford",      "en", ["rhona-blackwood"]),
    ("callum-strachan",  "Callum Strachan",   1922, 2001, "inverness",   "gd", ["rhona-blackwood"]),
    ("perrin-oakes",     "Perrin Oakes",      1925, 2004, "ludlow",      "en", ["gerard-tyne"]),
    ("nesta-hywel",      "Nesta Hywel",       1930, 2011, "hay-on-wye",  "cy", ["iolo-vaughan"]),
    ("dermot-lisle",     "Dermot Lisle",      1933, 2016, "liverpool",   "en", ["maud-ellery", "gerard-tyne"]),
    ("agnes-varden",     "Agnes Varden",      1937, None, "york",        "en", ["maud-ellery"]),
    ("torin-mackay",     "Torin MacKay",      1940, None, "portree",     "gd", ["callum-strachan"]),
    ("bryn-caradoc",     "Bryn Caradoc",      1944, None, "cardiff",     "cy", ["nesta-hywel"]),
    ("selina-frayne",    "Selina Frayne",     1947, None, "bath",        "en", ["perrin-oakes", "maud-ellery"]),
    ("hal-morrow",       "Hal Morrow",        1951, None, "manchester",  "en", ["dermot-lisle"]),
    ("ines-calloway",    "Ines Calloway",     1954, None, "london",      "en", ["agnes-varden", "dermot-lisle"]),
    ("fenella-drew",     "Fenella Drew",      1958, None, "sedbergh",    "en", ["agnes-varden"]),
    ("owain-preece",     "Owain Preece",      1960, None, "shrewsbury",  "cy", ["bryn-caradoc"]),
    ("kirsty-lammond",   "Kirsty Lammond",    1962, None, "glasgow",     "en", ["torin-mackay", "hal-morrow"]),
    ("marek-oyelaran",   "Marek Oyelaran",    1965, None, "london",      "en", ["ines-calloway"]),
    ("delia-stannard",   "Delia Stannard",    1967, None, "cambridge",   "en", ["selina-frayne"]),
    ("rab-fingal",       "Rab Fingal",        1969, None, "wigtown",     "en", ["kirsty-lammond"]),
    ("juno-verrall",     "Juno Verrall",      1971, None, "whitby",      "en", ["fenella-drew", "ines-calloway"]),
    ("elin-morgan",      "Elin Morgan",       1974, None, "aberystwyth", "cy", ["owain-preece"]),
    ("sandy-cleghorn",   "Sandy Cleghorn",    1976, None, "st-andrews",  "en", ["rab-fingal"]),
    ("priya-nandakumar", "Priya Nandakumar",  1978, None, "norwich",     "en", ["marek-oyelaran", "delia-stannard"]),
    ("tam-brodie",       "Tam Brodie",        1980, None, "edinburgh",   "en", ["kirsty-lammond", "rab-fingal"]),
    ("cerys-lloyd",      "Cerys Lloyd",       1982, None, "hay-on-wye",  "cy", ["elin-morgan"]),
    ("noor-haddad",      "Noor Haddad",       1984, None, "london",      "ar", ["marek-oyelaran"]),
    ("bram-tillotson",   "Bram Tillotson",    1986, None, "keswick",     "en", ["juno-verrall"]),
    ("orla-finnerty",    "Orla Finnerty",     1988, None, "penzance",    "en", ["priya-nandakumar"]),
    ("magnus-thole",     "Magnus Thole",      1990, None, "kendal",      "en", ["bram-tillotson", "sandy-cleghorn"]),
    ("yara-tesfaye",     "Yara Tesfaye",      1992, None, "manchester",  "en", ["noor-haddad", "orla-finnerty"]),
    ("dilys-tremain",    "Dilys Tremain",     1995, None, "exeter",      "en", ["cerys-lloyd", "magnus-thole"]),
]

# A deliberate mutual influence: two contemporaries who cite each other.
# `bs:influencedBy+` must still terminate.
MUTUAL_INFLUENCE = [("tam-brodie", "kirsty-lammond")]

# Authors who never influenced anyone and were never influenced: useful for
# teaching the difference between `*` (includes self) and `+`.
