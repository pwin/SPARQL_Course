# -*- coding: utf-8 -*-
"""Modules 05-08: property paths, sub-queries, other query forms, named graphs."""

from querycat import q, D11, DTRIG, ALL, EDITOR, HOLOS, FUSEKI

# ===========================================================================
# 05  Property paths
# ===========================================================================

q(
    qid="q27", module="05-property-paths",
    title="Every area a shop sits inside",
    asks="For one shop, list every containing place all the way up to Great "
         "Britain.",
    how="bs:within+ follows the containment link one or more times and "
        "returns every place it can reach. Writing the same thing as a chain "
        "of patterns would need one line per level -- and you would have to "
        "know in advance how many levels there are.",
    diagram="""
    bt:shop-endpapers
          | bs:locatedIn
          v
      place-york --within--> north-yorkshire --within--> yorkshire
                                                              | within
                                                              v
                                          place-gb <--within-- england

    bs:within+  collects EVERY place on that road:

        north-yorkshire, yorkshire, england, gb        (4 rows)

    The + means "one or more hops".  The engine keeps walking until
    it runs out of edges, and it remembers where it has been.
    """,
    learn=[
        "path+ means one or more hops, and returns every node reachable that "
        "way.",
        "A path expression replaces a chain of patterns whose length you do "
        "not know.",
        "The result is a set of endpoints, not a route: SPARQL won't tell "
        "you which way it went. q32 shows what to do when you need that.",
    ],
    body="""SELECT ?areaName
WHERE {
  bt:shop-endpapers bs:locatedIn/bs:within+ ?area .
  ?area rdfs:label ?areaName .
  FILTER( LANG(?areaName) = "en" )
}""",
)

q(
    qid="q28", module="05-property-paths",
    title="Why a fixed-length chain gets the wrong answer",
    asks="Count the shops in each country, first with a fixed chain of hops "
         "and then with a path.",
    how="The place hierarchy is deliberately uneven. An English town sits "
        "inside a council area inside a region inside a country; a Scottish "
        "or Welsh one sits inside a council area inside the country, with no "
        "region in between. A pattern hard-coded to three hops finds England "
        "and misses Scotland and Wales entirely -- and reports no error while "
        "doing it.",
    diagram="""
    ENGLAND (4 levels)            SCOTLAND / WALES (3 levels)

    york                          edinburgh
      | within                      | within
    north-yorkshire               edinburgh-city
      | within                      | within
    yorkshire                     scotland
      | within                      | within
    england                       gb
      | within
    gb

    ?town bs:within/bs:within/bs:within ?country
             ---- exactly 3 hops ----
    matches York -> england          ok
    misses Edinburgh -> scotland     NO   (only 2 hops away)

    ?town bs:within+ ?country        matches both

    The wrong query returns a plausible, confident, incomplete answer.
    That is what makes it dangerous.
    """,
    learn=[
        "Real hierarchies are rarely of uniform depth, and a fixed-length "
        "chain silently drops the branches that don't match.",
        "A wrong answer that looks reasonable is worse than an error.",
        "When you mean 'contained in, at any depth', say so with +.",
    ],
    body="""SELECT ?countryName ?viaFixedChain ?viaPath
WHERE {
  ?country a bs:Country ; rdfs:label ?countryName .
  FILTER( LANG(?countryName) = "en" )

  {
    SELECT ?country (COUNT(DISTINCT ?shop) AS ?viaFixedChain)
    WHERE {
      ?shop a bs:Bookshop ; bs:locatedIn ?town .
      ?town bs:within/bs:within/bs:within ?country .
      ?country a bs:Country .
    }
    GROUP BY ?country
  }
  UNION
  {
    SELECT ?country (COUNT(DISTINCT ?shop) AS ?viaPath)
    WHERE {
      ?shop a bs:Bookshop ; bs:locatedIn ?town .
      ?town bs:within+ ?country .
      ?country a bs:Country .
    }
    GROUP BY ?country
  }
}
ORDER BY ?countryName""",
)

q(
    qid="q29", module="05-property-paths",
    title="Star and plus aren't the same",
    asks="What's the difference between bs:within* and bs:within+?",
    how="* allows zero hops, so the starting node is included in its own "
        "answer. + requires at least one hop, so it isn't. The distinction "
        "matters most when you're collecting a subtree and need to decide "
        "whether the root belongs in it.",
    diagram="""
    starting from place-york:

    bs:within+                    bs:within*
    ----------                    ----------
                                  york          <- zero hops: itself
    north-yorkshire               north-yorkshire
    yorkshire                     yorkshire
    england                       england
    gb                            gb

    4 rows                        5 rows

    Rule of thumb:
      "all my ancestors"        -> +
      "me and all my ancestors" -> *
    """,
    learn=[
        "* is zero-or-more and always includes the starting node.",
        "+ is one-or-more and never includes it, unless a cycle leads back.",
        "? is zero-or-one: the hop is allowed but not required.",
    ],
    body="""SELECT ?form ?areaName
WHERE {
  {
    bt:place-york bs:within+ ?area .
    BIND( "within+ (one or more)" AS ?form )
  }
  UNION
  {
    bt:place-york bs:within* ?area .
    BIND( "within* (zero or more)" AS ?form )
  }
  ?area rdfs:label ?areaName .
  FILTER( LANG(?areaName) = "en" )
}
ORDER BY ?form ?areaName""",
)

q(
    qid="q30", module="05-property-paths",
    title="Walking a link backwards",
    asks="Which shops are in Wales?",
    how="The caret reverses the direction of a link, so ^bs:locatedIn goes "
        "from a town to the shops in it. Combined with a forward path it "
        "gives the whole answer in one expression: down from Wales to its "
        "towns, then back up the locatedIn edge to the shops.",
    diagram="""
    the data points this way:

        shop --bs:locatedIn--> town --bs:within--> ... --> wales

    the question points the other way, so reverse the last two steps:

        bt:place-wales  ^bs:within+  ?town   ^bs:locatedIn  ?shop
                        -----+-----         ------+-------
                        "everything          "the shops in
                         inside Wales"        that town"

    Equivalent, and often clearer:

        ?shop bs:locatedIn/bs:within+ bt:place-wales .

    Same answer.  Choose whichever reads in the direction you think.
    """,
    learn=[
        "^p traverses p backwards. It isn't a different property, just a "
        "different direction of travel.",
        "A path can mix forward and reverse steps freely.",
        "There's usually a forwards and a backwards way to write the same "
        "question; pick the one that reads like the question.",
    ],
    body="""SELECT ?shopName ?townName
WHERE {
  bt:place-wales ^bs:within+ ?town .
  ?town ^bs:locatedIn ?shop .
  ?shop rdfs:label ?shopName .
  ?town rdfs:label ?townName .
  FILTER( LANG(?townName) = "en" )
}
ORDER BY ?townName ?shopName""",
)

q(
    qid="q31", module="05-property-paths",
    title="Walking the trail in either direction",
    asks="Which shops can be reached on foot from The Inkwell?",
    how="Trail segments are asserted once, from one shop to another, but a "
        "footpath is walkable both ways. The alternation "
        "(bs:connectsTo|^bs:connectsTo) accepts a step in either direction, "
        "and the + around it repeats that step as often as needed.",
    diagram="""
    asserted:   inkwell --connectsTo--> marginalia --> broken-spine

    but you can walk it backwards, so the step you want is:

        ( bs:connectsTo | ^bs:connectsTo )
          ----+-------    -----+--------
          forwards          backwards
                  either will do

    wrapped in + to repeat:

        ( bs:connectsTo | ^bs:connectsTo )+

    inkwell --> 31 of the 33 shops
                (the two south-western shops are on their own; q32)

    Note that inkwell reaches ITSELF: go one hop out and one back,
    and a + path has found a route home.
    """,
    learn=[
        "| is alternation: try either path expression at this step.",
        "Combining | with ^ is the standard way to treat a one-way link as "
        "two-way, without changing the data.",
        "A + path over an undirected graph makes every connected node "
        "reachable from itself. That's correct, and surprising the first "
        "time.",
    ],
    body="""SELECT ?shopName
WHERE {
  bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ ?shop .
  ?shop rdfs:label ?shopName .
}
ORDER BY ?shopName""",
)

q(
    qid="q32", module="05-property-paths",
    title="The shops you can't walk to",
    asks="Which shops are cut off from the main trail?",
    how="Reachability plus negation. NOT EXISTS asks, for each shop, whether "
        "any walkable route from The Inkwell arrives there. The two shops in "
        "the south west are joined to each other and to nothing else, so no "
        "route reaches them.",
    diagram="""
    the main network            the south-west spur

    inkwell -- ... -- ex-libris      west-quay --> penwith
       |                                 (joined to each other,
       +-- 31 shops reachable             and to nothing else)

    for each ?shop:
      NOT EXISTS { bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ ?shop }
                                                      |
                              +-----------------------+
                              v
                   no route found -> keep the row

    West Quay Books, Penwith Pages

    A path that finds nothing is not an error.  It is an answer.
    """,
    learn=[
        "Property paths and NOT EXISTS compose: 'not reachable' is just a "
        "reachability test inside a negation.",
        "Connectivity questions are the natural home of + paths.",
        "This is the query to run after adding data, to check nothing has "
        "been left stranded.",
    ],
    body="""SELECT ?shopName ?townName
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?shopName ;
        bs:locatedIn ?town .
  ?town rdfs:label   ?townName .
  FILTER( LANG(?townName) = "en" )
  FILTER NOT EXISTS {
    bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ ?shop .
  }
}
ORDER BY ?shopName""",
)

q(
    qid="q33", module="05-property-paths",
    title="Every book of fiction, however narrow the genre",
    asks="Find all fiction, including books filed under sub-genres several "
         "levels down.",
    how="The genre scheme is a SKOS tree of uneven depth: Tartan Noir is "
        "three levels below Fiction, Classics is one. skos:broader+ climbs "
        "from a book's own genre to every broader concept above it, so a book "
        "counts as fiction whichever level it was filed at.",
    diagram="""
    Literature
      +- Fiction                       <- the target
           +- Crime Fiction
           |    +- Cosy Crime          <- 3 levels down
           |    +- Tartan Noir         <- 3 levels down
           +- Speculative Fiction
           |    +- Science Fiction
           |    |    +- Hard SF        <- 4 levels down
           |    |    +- Space Opera
           |    +- Fantasy
           |         +- Folk Fantasy
           +- Classics                 <- 2 levels down

    ?book bs:genre/skos:broader* bt:genre-fiction
                   -------+----
             climb zero or more levels, so a book filed
             directly under Fiction still counts

    17 concepts sit under Fiction.  A two-hop pattern finds 5.
    """,
    learn=[
        "skos:broader+ is the standard way to query a subject hierarchy.",
        "Use * rather than + after a step that may already have arrived: "
        "here, a book filed directly as Fiction needs zero further climbs.",
        "A path can be built from several steps: bs:genre/skos:broader* is "
        "one hop then any number of hops.",
    ],
    body="""SELECT ?genreName (COUNT(?book) AS ?books)
WHERE {
  ?book a        bs:Work ;
        bs:genre ?g .
  ?g skos:broader* bt:genre-fiction .
  ?g skos:prefLabel ?genreName .
  FILTER( LANG(?genreName) = "en" )
}
GROUP BY ?genreName
ORDER BY DESC(?books) ?genreName""",
)

q(
    qid="q34", module="05-property-paths",
    title="Literary ancestry, and a cycle",
    asks="Trace every author who influenced Dilys Tremain, directly or at any "
         "remove.",
    how="bs:influencedBy+ walks the influence graph transitively. The data "
        "contains a mutual pair -- two contemporaries who cite each other -- "
        "so a naive recursive join would loop forever. A property path will "
        "not: the engine tracks which nodes it has already visited.",
    diagram="""
    dilys-tremain
        +-- cerys-lloyd -- elin-morgan -- owain-preece -- bryn-caradoc
        |                                                     |
        |                                              nesta-hywel
        |                                                     |
        |                                              iolo-vaughan
        +-- magnus-thole -+- bram-tillotson -- juno-verrall -- ...
                          +- sandy-cleghorn -- rab-fingal
                                                   |
                                            kirsty-lammond
                                                  |          <- MUTUAL
                                            tam-brodie          cycle

    bs:influencedBy+ terminates anyway.  The path evaluator keeps a
    visited set; it is looking for reachable NODES, not for routes.

    Write this as a self-join repeated by hand and the cycle hangs
    the query.
    """,
    learn=[
        "Property paths are cycle-safe. That's a guarantee of the "
        "specification, not an accident of one engine.",
        "Transitive closure over a hand-authored graph is where paths pay "
        "for themselves.",
        "The answer is a set of ancestors, with no indication of distance. "
        "If you need the number of hops, you need something else -- SPARQL "
        "has no path-length operator.",
    ],
    body="""SELECT ?ancestorName
WHERE {
  bt:author-dilys-tremain bs:influencedBy+ ?ancestor .
  ?ancestor rdfs:label ?ancestorName .
}
ORDER BY ?ancestorName""",
)

q(
    qid="q35", module="05-property-paths",
    title="Everything except the links you name",
    asks="What does a shop point at, other than its geometry and its stock?",
    how="A negated property set matches any predicate not in the list. It's "
        "the way to say 'all the other links', which is useful when "
        "exploring, and useful when you want to follow a graph outward "
        "without dragging in the bulky parts.",
    diagram="""
    !( bs:stocks | geo:hasGeometry | geo:hasDefaultGeometry )
    ^  -----------------+----------------------------------
    |                   +-- the predicates to exclude
    +-- "any predicate BUT these"

    bt:shop-colophon
        +- rdf:type            ok kept
        +- rdfs:label          ok kept
        +- bs:locatedIn        ok kept
        +- bs:stocks           NO excluded
        +- geo:hasGeometry     NO excluded

    Use ^ inside the set to exclude an incoming link:
        !( ^bs:heldAt )
    """,
    learn=[
        "!(a|b|c) matches any predicate outside the set.",
        "The negated set is the only place a path may not contain a nested "
        "expression -- it takes a plain list of predicates.",
        "Handy for exploring: follow everything except the parts you already "
        "understand.",
    ],
    body="""SELECT ?p ?o
WHERE {
  bt:shop-colophon !( bs:stocks | geo:hasGeometry | geo:hasDefaultGeometry ) ?o .
  bt:shop-colophon ?p ?o .
}
ORDER BY ?p""",
)

q(
    qid="q36", module="05-property-paths",
    title="A whole journey in one expression",
    asks="Name the country of every shop, in a single path.",
    how="The slash builds a sequence: take this step, then that one. "
        "Combining a sequence with a repetition gives an expression that "
        "reads like the sentence you would say out loud -- a shop is in a "
        "town, which is inside some area, which is a country.",
    diagram="""
    ?shop bs:locatedIn / bs:within+ / ^bs:within* ...
          -----+-----   -----+----
            one hop      any number

    the whole path:

      ?shop  --bs:locatedIn-->  town
             --bs:within+---->  any containing area
                                  |
                                  +- FILTER to keep only countries

    reads as:  "the shop is in a town, somewhere inside a country"

    A sequence with / is evaluated left to right, and the
    intermediate nodes are thrown away -- you cannot see the town.
    If you need it, use separate patterns.
    """,
    learn=[
        "/ is sequence: one step then the next.",
        "Intermediate nodes in a sequence aren't bound to anything and "
        "can't be selected. Split the path if you need them.",
        "Paths make queries shorter, not always clearer. Split a long one "
        "when the intermediate steps are part of the answer.",
    ],
    body="""SELECT ?shopName ?countryName
WHERE {
  ?shop a bs:Bookshop ;
        rdfs:label ?shopName ;
        bs:locatedIn/bs:within+ ?country .
  ?country a bs:Country ; rdfs:label ?countryName .
  FILTER( LANG(?countryName) = "en" )
}
ORDER BY ?countryName ?shopName""",
)

# ===========================================================================
# 06  Sub-queries
# ===========================================================================

q(
    qid="q37", module="06-subqueries",
    title="Books priced above average",
    asks="Which books cost more than the average book?",
    how="A single query can't compare a row against a summary of all rows, "
        "because by the time the aggregate exists the rows are gone. The "
        "sub-query computes the average first and yields one row with one "
        "column; the outer query then joins every book against that single "
        "row and filters.",
    diagram="""
    +- inner query ----------------------------+
    |  SELECT (AVG(?p) AS ?avgPrice)           |
    |  WHERE { ?b bs:rrp ?p }                  |
    |                                          |
    |  result:  +----------+                   |
    |           | 15.87    |   ONE row         |
    |           +----------+                   |
    +-------------------+----------------------+
                        | joined to every outer row
                        v
    +- outer query ----------------------------+
    |  ?book bs:rrp ?price                     |
    |  FILTER( ?price > ?avgPrice )            |
    +------------------------------------------+

    Inner runs FIRST.  It cannot see ?book, ?price or anything else
    from the outer query -- only what it computes itself.
    """,
    learn=[
        "A sub-query runs first and independently; the outer query joins "
        "against its result.",
        "This is the only way to compare a value with an aggregate over the "
        "same data.",
        "Variables don't leak inwards. A sub-query can't see the outer "
        "query's bindings, which is exactly why it can be evaluated once.",
    ],
    body="""SELECT ?title ?price ?avgPrice
WHERE {
  ?book a          bs:Work ;
        rdfs:label ?title ;
        bs:rrp     ?price .
  {
    SELECT (ROUND(AVG(?p) * 100) / 100 AS ?avgPrice)
    WHERE { ?b a bs:Work ; bs:rrp ?p . }
  }
  FILTER( ?price > ?avgPrice )
}
ORDER BY DESC(?price)
LIMIT 15""",
)

q(
    qid="q38", module="06-subqueries",
    title="The best-attended event at every shop",
    asks="For each shop, which single event drew the biggest crowd?",
    how="Two passes. The inner query finds the maximum attendance per shop, "
        "collapsing the events away. The outer query then re-joins that "
        "maximum against the events to recover which event it was -- the "
        "detail the aggregate had to throw away.",
    diagram="""
    step 1: what is the maximum, per shop?

      SELECT ?shop (MAX(?a) AS ?best)
      GROUP BY ?shop
                    +----------+-----+
                    | ex-libris| 320 |
                    | endpapers| 210 |
                    +----------+-----+
                          |
    step 2: join back to find WHICH event that was

      ?event bs:heldAt ?shop ; bs:attendance ?best
                                             ----+
                       the join condition -------+

                    +----------+-----+------------------+
                    | ex-libris| 320 | Launch with Ines |
                    +----------+-----+------------------+

    "Group, then join back" is the standard shape for top-N-per-group.
    A tie produces two rows, which is usually what you want.
    """,
    learn=[
        "Aggregating discards the detail. Joining the aggregate back recovers "
        "it.",
        "This shape -- group to find an extreme, re-join to identify it -- is "
        "one of the most reusable in SPARQL.",
        "Ties give several rows. If you need exactly one, you must say how "
        "to break the tie.",
    ],
    body="""SELECT ?shopName ?eventLabel ?attendance
WHERE {
  {
    SELECT ?shop (MAX(?a) AS ?attendance)
    WHERE { ?e bs:heldAt ?shop ; bs:attendance ?a . }
    GROUP BY ?shop
  }
  ?event bs:heldAt     ?shop ;
         bs:attendance ?attendance ;
         rdfs:label    ?eventLabel .
  ?shop  rdfs:label    ?shopName .
}
ORDER BY DESC(?attendance)
LIMIT 15""",
)

q(
    qid="q39", module="06-subqueries",
    title="An aggregate over an aggregate",
    asks="On average, how many books does each of a publisher's authors "
         "write?",
    how="Counting books per author is one aggregation; averaging those counts "
        "per publisher is a second, over the results of the first. SPARQL "
        "can't nest aggregates in one expression, so the inner grouping has "
        "to happen in a sub-query and the outer one over its output.",
    diagram="""
    level 1 -- count books per author per publisher
      GROUP BY ?publisher ?author
        +-----------+----------------+---+
        | northwind | rhona-blackwood| 2 |
        | northwind | fenella-drew   | 2 |
        | northwind | kirsty-lammond | 2 |
        +-----------+----------------+---+
                          |
    level 2 -- average those counts per publisher
      GROUP BY ?publisher
        +-----------+------+---------+
        | northwind |  4   |  2.0    |
        |           |auth. | mean    |
        +-----------+------+---------+

    AVG(COUNT(?x)) is not legal SPARQL.  The nesting has to be
    expressed as a sub-query, which is the whole reason they exist.
    """,
    learn=[
        "Aggregates don't nest inside one expression; nest the queries "
        "instead.",
        "The inner query's grouping keys become ordinary columns to the outer "
        "query.",
        "Reading these from the inside out is the only way they make sense.",
    ],
    body="""SELECT ?publisherName (COUNT(?author) AS ?authors)
       (ROUND(AVG(?bookCount) * 10) / 10 AS ?meanBooksPerAuthor)
WHERE {
  {
    SELECT ?publisher ?author (COUNT(?book) AS ?bookCount)
    WHERE {
      ?book bs:publishedBy ?publisher ;
            bs:author      ?author .
    }
    GROUP BY ?publisher ?author
  }
  ?publisher rdfs:label ?publisherName .
}
GROUP BY ?publisher ?publisherName
ORDER BY DESC(?meanBooksPerAuthor) ?publisherName""",
)

q(
    qid="q40", module="06-subqueries",
    title="Shops that punch above their weight",
    asks="Which shops draw a bigger total audience than the average shop "
         "does?",
    how="Three levels. The innermost totals attendance per shop; the middle "
        "one averages those totals into a single number; the outer query "
        "compares each shop against it. Each level is a plain query -- the "
        "difficulty is only in seeing which order they run in.",
    diagram="""
    innermost:  total per shop
        ex-libris 829, endpapers 520, cotton-quarto 443, ...
                          |
    middle:  average of those totals   -->  231.4   (one row)
                          |
    outer:  keep shops whose total exceeds it
                          v
        +---------------+-------+--------+
        | Ex Libris     |  829  | 231.4  |
        | Endpapers     |  520  | 231.4  |
        | Cotton Quarto |  443  | 231.4  |
        +---------------+-------+--------+

    Note the middle query aggregates over the INNER query's rows,
    not over the events.  Averaging attendance directly would answer
    a different question: the average event, not the average shop.
    """,
    learn=[
        "Sub-queries nest as deeply as the question needs.",
        "'Average per shop' and 'average per event' are different numbers. "
        "Which one you get depends on what you grouped before averaging.",
        "Build these from the inside out, and run each level on its own "
        "first.",
    ],
    body="""SELECT ?shopName ?total ?averageShop
WHERE {
  {
    SELECT ?shop (SUM(?a) AS ?total)
    WHERE { ?e bs:heldAt ?shop ; bs:attendance ?a . }
    GROUP BY ?shop
  }
  {
    SELECT (ROUND(AVG(?t) * 10) / 10 AS ?averageShop)
    WHERE {
      SELECT ?s (SUM(?a) AS ?t)
      WHERE { ?e bs:heldAt ?s ; bs:attendance ?a . }
      GROUP BY ?s
    }
  }
  ?shop rdfs:label ?shopName .
  FILTER( ?total > ?averageShop )
}
ORDER BY DESC(?total)""",
)

q(
    qid="q41", module="06-subqueries",
    title="Limiting the inner query, not the outer one",
    asks="Show every book by the three most prolific authors.",
    how="Putting LIMIT in the outer query would cut off books. Putting it in "
        "the sub-query picks three authors and then lets the outer query "
        "fetch all of their books. The sub-query decides who; the outer "
        "query decides what to show.",
    diagram="""
    WRONG                          RIGHT
    ?author ...                    { SELECT ?author
    ?book bs:author ?author          WHERE {...}
    LIMIT 3                          ORDER BY DESC(?n)
                                     LIMIT 3 }
    --> 3 BOOKS                    ?book bs:author ?author

                                   --> 3 AUTHORS,
                                       all their books

    The sub-query is a filter on WHICH authors, evaluated once.
    LIMIT inside it limits authors; LIMIT outside limits rows.

    ORDER BY inside a sub-query is meaningful precisely because
    LIMIT is there to use it.
    """,
    learn=[
        "LIMIT inside a sub-query restricts what the outer query joins "
        "against, which is a completely different operation from truncating "
        "the output.",
        "ORDER BY plus LIMIT inside a sub-query is the idiom for 'the top N "
        "of something, then everything about them'.",
        "Ordering an outer query doesn't order its sub-queries, and vice "
        "versa.",
        "Add a tie-break. Six authors have three books; without ?author as a "
        "second sort key, which three come back is up to the engine, and the "
        "three engines really do choose differently.",
    ],
    body="""SELECT ?authorName ?title ?year
WHERE {
  {
    SELECT ?author (COUNT(?b) AS ?books)
    WHERE { ?b a bs:Work ; bs:author ?author . }
    GROUP BY ?author
    ORDER BY DESC(?books) ?author
    LIMIT 3
  }
  ?book  bs:author          ?author ;
         rdfs:label         ?title ;
         bs:publicationYear ?year .
  ?author rdfs:label        ?authorName .
}
ORDER BY ?authorName ?year""",
)

q(
    qid="q42", module="06-subqueries",
    title="Authors more prolific than the person who inspired them",
    asks="Which authors wrote more books than the author who influenced "
         "them?",
    how="Two independent counts, joined on the influence link. Each sub-query "
        "produces a table of author-to-count; the outer pattern joins them "
        "through bs:influencedBy so the two counts land in the same row and "
        "can be compared.",
    diagram="""
    +- count per author -+        +- count per author -+
    | dilys-tremain   2  |        | cerys-lloyd     2  |
    | magnus-thole    2  |        | magnus-thole    2  |
    +---------+----------+        +---------+----------+
              |                             |
              |   ?author bs:influencedBy ?mentor
              +--------------+--------------+
                             v
              FILTER( ?ownBooks > ?mentorBooks )

    The same sub-query appears twice with different variable names.
    That is the SPARQL way of aliasing a table -- there is no AS for
    a whole sub-query.
    """,
    learn=[
        "The same sub-query can be used twice with different variables, which "
        "is how you compare a thing with a related thing.",
        "The join between the two copies is an ordinary triple pattern in the "
        "outer query.",
        "SPARQL has no table aliases; repeating the sub-query is the "
        "substitute, and engines are generally clever enough not to compute "
        "it twice.",
    ],
    body="""SELECT ?authorName ?ownBooks ?mentorName ?mentorBooks
WHERE {
  ?author bs:influencedBy ?mentor .
  {
    SELECT ?author (COUNT(?b) AS ?ownBooks)
    WHERE { ?b a bs:Work ; bs:author ?author . }
    GROUP BY ?author
  }
  {
    SELECT ?mentor (COUNT(?b2) AS ?mentorBooks)
    WHERE { ?b2 a bs:Work ; bs:author ?mentor . }
    GROUP BY ?mentor
  }
  ?author rdfs:label ?authorName .
  ?mentor rdfs:label ?mentorName .
  FILTER( ?ownBooks > ?mentorBooks )
}
ORDER BY DESC(?ownBooks) ?authorName""",
)

# ===========================================================================
# 07  Other query forms
# ===========================================================================

q(
    qid="q43", module="07-construct-ask-describe",
    title="Build a simpler graph",
    asks="Produce a small graph of shops and the names of their towns, ready "
         "to paste back into the editor.",
    how="CONSTRUCT returns RDF instead of a table. The template between the "
        "braces is filled in once per solution, so the output is a graph "
        "whose shape you chose rather than the one the data happens to have.",
    diagram="""
    WHERE  finds solutions          CONSTRUCT  builds triples

    ?shop = bt:shop-inkwell         bt:shop-inkwell
    ?name = "The Inkwell"    -->        rdfs:label "The Inkwell" ;
    ?town = "Wigtown"                   bs:townName "Wigtown" .

    one solution  ------------->  two triples

    The template may invent predicates that appear nowhere in the
    source: bs:townName is created here, purely for the output.

    In the Turtle Editor Viewer the result comes back as Turtle --
    paste it into the editor pane and the graph view will draw it.
    """,
    learn=[
        "CONSTRUCT returns a graph. Its template is instantiated once per "
        "solution.",
        "It's the standard way to reshape data for another tool, or to "
        "simplify before visualising.",
        "A graph is a set, so duplicate triples collapse once the result is "
        "loaded somewhere. The result stream itself is another matter -- see "
        "q44, where the three engines disagree about exactly that.",
    ],
    body="""CONSTRUCT {
  ?shop rdfs:label  ?shopName ;
        bs:townName ?townName .
}
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?shopName ;
        bs:locatedIn ?town .
  ?town rdfs:label   ?townName .
  FILTER( LANG(?townName) = "en" )
}""",
)

q(
    qid="q44", module="07-construct-ask-describe",
    title="Materialise the links that aren't there",
    asks="The data records bs:imprintOf but never bs:hasImprint. Create it.",
    how="CONSTRUCT can assert the inverse of an existing link, turning a "
        "query into a small inference step. The result is a graph you can "
        "load alongside the original -- which is what an OWL reasoner would "
        "do for you, more slowly and with more ceremony.",
    diagram="""
    in the data:

        pub-saltmarsh --bs:imprintOf--> pub-northwind

    CONSTRUCT { ?parent bs:hasImprint ?child }
    WHERE     { ?child bs:imprintOf ?parent }

    produces:

        pub-northwind --bs:hasImprint--> pub-saltmarsh

    The vocabulary already declares
        bs:hasImprint owl:inverseOf bs:imprintOf
    so a reasoner would infer this.  CONSTRUCT does the same job in
    one query, with no reasoner and no surprises.

    In the editor, 'Show Facts' runs the HyLAR reasoner and infers
    it from the OWL declaration instead.  Compare the two.
    """,
    learn=[
        "CONSTRUCT is the cheapest form of inference: you state the rule as a "
        "query.",
        "The output is a graph, so it can be loaded back and queried "
        "alongside the source.",
        "^bs:imprintOf answers the same question without materialising "
        "anything. Materialise only when many queries will need it.",
        "Count what comes back before you trust it. This template emits three "
        "triples per solution, and several solutions share a parent, so the "
        "same label triple is built more than once.",
    ],
    notes="engines-differ: 27 triples from the browser editor, 22 from HOLOS "
          "and Fuseki. The template is instantiated nine times, giving 27 "
          "triples of which 22 are distinct. HOLOS and Fuseki return the set; "
          "Comunica returns the stream, duplicates and all. Both are "
          "defensible -- a graph is a set, but a result stream need not be -- "
          "and it matters the moment you count rows instead of loading them.",
    body="""CONSTRUCT {
  ?parent bs:hasImprint ?child .
  ?parent rdfs:label    ?parentName .
  ?child  rdfs:label    ?childName .
}
WHERE {
  ?child  bs:imprintOf ?parent ;
          rdfs:label   ?childName .
  ?parent rdfs:label   ?parentName .
}""",
)

q(
    qid="q45", module="07-construct-ask-describe",
    title="A yes or no question",
    asks="Is there a bookshop in Wales with a cafe?",
    how="ASK returns a single boolean. The engine may stop at the first match, "
        "so it's the cheapest way to test for existence -- and much better "
        "than running a SELECT and counting the rows yourself.",
    diagram="""
    ASK {
      ?shop bs:locatedIn/bs:within+ bt:place-wales ;
            bs:hasCafe true .
    }

              +-------------+
              |  any match? |
              +------+------+
                     |
            +--------+--------+
            v                 v
          true              false

    One value comes back, not a table.  The engine is allowed to
    stop looking the moment it finds one solution.

    In the editor the result appears as a single true/false rather
    than a results grid.
    """,
    learn=[
        "ASK answers existence questions and returns one boolean.",
        "It's cheaper than SELECT because the engine can stop at the first "
        "solution.",
        "Use it for tests -- in a script, or in a validation step -- not for "
        "fetching data.",
    ],
    body="""ASK {
  ?shop bs:locatedIn/bs:within+ bt:place-wales ;
        bs:hasCafe             true .
}""",
)

q(
    qid="q46", module="07-construct-ask-describe",
    title="Describe a resource",
    asks="Give me everything that describes The Quire.",
    how="DESCRIBE hands back a graph the engine thinks describes the "
        "resource. What counts as a description is up to the engine, which "
        "makes DESCRIBE convenient for exploring and unwise to rely on in "
        "code that must behave identically everywhere.",
    diagram="""
    DESCRIBE bt:shop-quire

    most engines return the "concise bounded description":

        bt:shop-quire ?p ?o           <- all outgoing statements
              plus, for any ?o that is a blank node,
              that node's statements too, recursively

    what you get is NOT specified:
      Jena              outgoing statements
      HOLOS             outgoing statements
      Comunica          outgoing statements
      another engine    might include incoming ones too

    For anything reproducible, write the CONSTRUCT you actually
    mean.  DESCRIBE is for looking around.
    """,
    learn=[
        "DESCRIBE returns a graph chosen by the engine, and the specification "
        "deliberately leaves the choice open.",
        "It's excellent for exploring an unfamiliar endpoint.",
        "Never build a pipeline on it: write the CONSTRUCT you mean instead.",
    ],
    notes="engines-differ: and that's the lesson. Measured on this dataset, "
          "the three engines return different graphs for the same DESCRIBE. "
          "Nothing is broken -- the specification leaves the choice to the "
          "engine. This is the only query in the course whose answer is "
          "allowed to vary, and the only one where that's the point.",
    body="""DESCRIBE bt:shop-quire""",
)

q(
    qid="q47", module="07-construct-ask-describe",
    title="A summary graph worth keeping",
    asks="Build a compact profile of every shop: name, town, country, "
         "specialism and event count.",
    how="CONSTRUCT with aggregation. The sub-query counts events per shop; "
        "the template then assembles one tidy node per shop. The output is "
        "small enough to paste into the editor and see whole, which the "
        "source data isn't.",
    diagram="""
    5,000-triple dataset            ~165-triple summary
    +--------------------+          +--------------------+
    | shops, towns,      |  -->     | bt:shop-quire      |
    | councils, regions, |          |   rdfs:label ...   |
    | countries, events, |          |   bs:townName ...  |
    | geometry, stock... |          |   bs:countryName ..|
    +--------------------+          |   bs:eventCount 2  |
                                    +--------------------+

    This is the query to run before visualising.  The editor's graph
    view draws 10 subjects at a time; a summary makes those 10
    subjects worth looking at.
    """,
    learn=[
        "CONSTRUCT and aggregation combine: compute in the WHERE, assemble in "
        "the template.",
        "Producing a small summary graph is the practical answer to 'this "
        "dataset is too big to visualise'.",
        "The output is valid Turtle. Save it, load it, query it again.",
    ],
    body="""CONSTRUCT {
  ?shop rdfs:label     ?shopName ;
        bs:townName    ?townName ;
        bs:countryName ?countryName ;
        bs:specialism  ?genreName ;
        bs:eventCount  ?events .
}
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?shopName ;
        bs:locatedIn ?town ;
        bs:specialises ?genre .
  ?town  rdfs:label  ?townName .
  ?genre skos:prefLabel ?genreName .
  ?town  bs:within+  ?country .
  ?country a bs:Country ; rdfs:label ?countryName .
  FILTER( LANG(?townName) = "en" && LANG(?countryName) = "en"
          && LANG(?genreName) = "en" )
  {
    SELECT ?shop (COUNT(?e) AS ?events)
    WHERE { ?e bs:heldAt ?shop . }
    GROUP BY ?shop
  }
}""",
)

# ===========================================================================
# 08  Named graphs
# ===========================================================================

q(
    qid="q48", module="08-named-graphs",
    title="What graphs are in this dataset",
    asks="The TriG file splits the data by subject matter. What are the "
         "parts called, and how big is each?",
    how="GRAPH ?g binds the name of the graph a pattern matched in. With the "
        "pattern left completely open, the result is an inventory of the "
        "dataset -- the first thing worth asking of an endpoint you haven't "
        "seen before.",
    diagram="""
    a dataset is a default graph plus zero or more named graphs:

    + default graph --------------------------+
    |  bt:dataset rdfs:label "The Bookshop..."|
    +-----------------------------------------+
    + bt:graph-places -+ + bt:graph-books -+
    | 30 settlements   | | 74 works        |
    | 23 councils ...  | | ...             |
    +------------------+ +-----------------+

    GRAPH ?g { ?s ?p ?o }
          |
          +-- binds to the NAME of whichever graph matched

    Triples in the default graph are NOT visible to GRAPH ?g.
    That catches people out: the dataset description in the default
    graph does not appear in this count.
    """,
    learn=[
        "GRAPH ?g { ... } binds ?g to the name of the graph the pattern "
        "matched in.",
        "The default graph isn't one of the named graphs and won't be "
        "found this way.",
        "Counting triples per graph is the fastest way to understand an "
        "unfamiliar dataset's layout.",
    ],
    body="""SELECT ?g (COUNT(*) AS ?triples)
WHERE {
  GRAPH ?g { ?s ?p ?o }
}
GROUP BY ?g
ORDER BY DESC(?triples)""",
    data=DTRIG,
)

q(
    qid="q49", module="08-named-graphs",
    title="Where did this fact come from",
    asks="Which part of the dataset asserts each thing known about The "
         "Inkwell?",
    how="The same pattern as an ordinary query, wrapped in GRAPH ?g. Every "
        "solution now carries the name of the graph that supplied it, which "
        "is provenance at its cheapest -- no extra vocabulary, no annotation, "
        "just the filing system.",
    diagram="""
    bt:shop-inkwell ?p ?o

    without GRAPH:  where did that come from?  no idea

    GRAPH ?g { bt:shop-inkwell ?p ?o }

      ?g = bt:graph-shops   ?p = bs:founded    ?o = 1979
      ?g = bt:graph-shops   ?p = bs:hasCafe    ?o = true
      ?g = bt:graph-stock   ?p = bs:stocks     ?o = bt:book-...
      ?g = bt:graph-trail   ?p = bs:connectsTo ?o = bt:shop-...
                 |
                 +-- the same subject, facts from three graphs

    Named graphs give you per-triple provenance for free, as long as
    "which file it came from" is the granularity you need.  For finer
    grain -- who said it, when, how sure -- see module 11.
    """,
    learn=[
        "Wrapping a pattern in GRAPH ?g adds the source to every row.",
        "This is the cheapest provenance mechanism there's, and often "
        "enough.",
        "It records where a fact is filed, not who asserted it. RDF 1.2 "
        "annotations answer the second question.",
    ],
    body="""SELECT ?g ?p ?o
WHERE {
  GRAPH ?g { bt:shop-inkwell ?p ?o }
}
ORDER BY ?g ?p""",
    data=DTRIG,
)

q(
    qid="q50", module="08-named-graphs",
    title="Querying one graph, then all of them",
    asks="Count the shops using only the shops graph, and then across the "
         "whole dataset.",
    how="A pattern inside GRAPH sees only that graph. The same pattern "
        "outside GRAPH sees the default graph, which in this TriG file holds "
        "nothing but the dataset description -- so it finds nothing at all. "
        "That surprise is the lesson.",
    diagram="""
    GRAPH bt:graph-shops { ?s a bs:Bookshop }     -->  33

    { ?s a bs:Bookshop }        (no GRAPH)        -->   0
                                                       ^
        because the default graph of this TriG file    |
        contains only the dataset description ---------+

    Compare with the Turtle files, where everything IS the default
    graph and the second pattern finds all 33.

    Same triples, different filing, different answers.  Know which
    kind of file you loaded.
    """,
    learn=[
        "A pattern not inside GRAPH matches the default graph only.",
        "Loading TriG instead of Turtle can silently change what your query "
        "returns.",
        "Many endpoints put everything in the default graph as well. Never "
        "assume; run this query and find out.",
    ],
    body="""SELECT ?scope (COUNT(?s) AS ?shops)
WHERE {
  {
    GRAPH bt:graph-shops { ?s a bs:Bookshop }
    BIND( "inside GRAPH bt:graph-shops" AS ?scope )
  }
  UNION
  {
    ?s a bs:Bookshop .
    BIND( "default graph, no GRAPH keyword" AS ?scope )
  }
  UNION
  {
    GRAPH ?any { ?s a bs:Bookshop }
    BIND( "any named graph" AS ?scope )
  }
}
GROUP BY ?scope
ORDER BY ?scope""",
    data=DTRIG,
)

q(
    qid="q51", module="08-named-graphs",
    title="Joining across two graphs",
    asks="Pair each shop with its town's name, when the shops and the places "
         "live in different graphs.",
    how="One GRAPH block per source, joined on the shared variable exactly as "
        "ordinary patterns are. Nothing about the join changes because the "
        "data is filed separately -- which is the point of named graphs.",
    diagram="""
    + bt:graph-shops ------------+
    | ?shop bs:locatedIn ?town   |--+
    +----------------------------+  |  joined on ?town
    + bt:graph-places -----------+  |
    | ?town rdfs:label ?townName |<-+
    +----------------------------+

    The join is the shared variable, as always.  Graph boundaries do
    not obstruct it.

    This is how federated queries work too: SERVICE replaces GRAPH,
    and the other side is a different server rather than a different
    graph.
    """,
    learn=[
        "Patterns in different GRAPH blocks join on shared variables like any "
        "others.",
        "Named graphs partition storage; they don't partition querying.",
        "The same shape scales up to SERVICE, where the other graph is on "
        "another machine.",
    ],
    body="""SELECT ?shopName ?townName
WHERE {
  GRAPH bt:graph-shops {
    ?shop a          bs:Bookshop ;
          rdfs:label ?shopName ;
          bs:locatedIn ?town .
  }
  GRAPH bt:graph-places {
    ?town rdfs:label ?townName .
  }
  FILTER( LANG(?townName) = "en" )
}
ORDER BY ?townName ?shopName
LIMIT 20""",
    data=DTRIG,
)
