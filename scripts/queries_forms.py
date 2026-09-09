# -*- coding: utf-8 -*-
"""Module 12: ASK, DESCRIBE and CONSTRUCT in earnest.

Module 07 introduces the three non-SELECT forms.  This module uses them as
what they actually are: a test, a lookup, and a transformation.
"""

from querycat import q, D11, D12, DTRIG, DFULL, PROLOGUE, ALL, EDITOR, HOLOS, FUSEKI

MOD = "12-graphs-in-graphs-out"

SCHEMA_PROLOGUE = PROLOGUE + "PREFIX schema: <https://schema.org/>\n"

# ===========================================================================
# ASK -- a question with two possible answers
# ===========================================================================

q(
    qid="q75", module=MOD,
    title="Can you walk from Wigtown to London",
    asks="Is there any route along the trail from The Inkwell to Ex Libris?",
    how="A property path inside an ASK. The engine needs to find one route, "
        "not all of them, and may stop the moment it does. That makes ASK the "
        "right form for a reachability question whose answer you're going to "
        "act on rather than read.",
    diagram="""
    ASK {
      bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ bt:shop-ex-libris .
    }
                          │
                  ┌───────┴────────┐
                  ▼                ▼
                true             false
             a route exists    no route

    ──▶ true

    The same path in a SELECT returns 31 shops and has to find them
    all.  Here the engine may stop at the first success, because one
    is all the question needs.

    Compare with the negative form, which cannot stop early:

      ASK { FILTER NOT EXISTS { ...path... } }

    To prove a route does NOT exist, every possibility must be
    eliminated.  "Is there one?" is cheap; "is there none?" is not.
    """,
    learn=[
        "ASK returns one boolean and permits the engine to stop at the first "
        "solution.",
        "A positive existence question is cheap. Its negation isn't, because "
        "nothing can be concluded until the search is exhausted.",
        "Reach for ASK when a program will branch on the answer; reach for "
        "SELECT when a person will read it.",
    ],
    body="""ASK {
  bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ bt:shop-ex-libris .
}""",
)

q(
    qid="q76", module=MOD,
    title="The assertion that must come back false",
    asks="Is any bookshop missing a label?",
    how="An ASK written so that `false` is the healthy answer. Phrased this "
        "way it's a test rather than a question, and it can be run "
        "automatically: load the data, ask, and fail the build if the answer "
        "is true.",
    diagram="""
    ASK {
      ?shop a bs:Bookshop .
      FILTER NOT EXISTS { ?shop rdfs:label ?label }
    }

    ──▶ false          the data is sound

    A suite of these is a cheap integrity check, and it needs no
    SHACL processor:

      any shop with no town?           false  ✓
      any work with no author?         false  ✓
      any segment joining a shop       false  ✓
        to itself?
      any place inside itself?         false  ✓

    Turn one true and you have found a bug.  data/shapes.ttl says
    the same things in SHACL, which reports WHICH node failed;
    an ASK only reports THAT one did.  Use ASK in a script, SHACL
    when you need to fix what it finds.
    """,
    learn=[
        "An ASK whose expected answer is false is a test, and belongs in "
        "whatever runs your builds.",
        "ASK tells you that something is wrong; SHACL tells you what and "
        "where. They answer different questions and both are cheap.",
        "Writing the assertion negatively -- 'is anything broken?' -- keeps "
        "the healthy answer constant as the dataset grows.",
    ],
    body="""ASK {
  ?shop a bs:Bookshop .
  FILTER NOT EXISTS { ?shop rdfs:label ?label }
}""",
)

q(
    qid="q77", module=MOD,
    title="One boolean per row, not one per query",
    asks="For every shop, does it stock any translated fiction?",
    how="ASK answers once for the whole query, which is no use when the "
        "question is really about each row. EXISTS is the row-wise form of "
        "the same test: it evaluates a pattern against the current bindings "
        "and yields a boolean you can bind, filter or select.",
    diagram="""
    ASK { ... }              one boolean, for the whole query
    EXISTS { ... }           one boolean, for the current row

    BIND( EXISTS { ?shop bs:stocks/bs:genre bt:genre-translated-fiction }
          AS ?stocksTranslated )
          ──┬───                            ▲
            │                               └── ?shop is bound from
            └── evaluated once per row          the surrounding row

    ┌──────────────────────┬───────────────────┐
    │ Verso and Recto      │ true              │
    │ Turn the Page        │ true              │
    │ The Inkwell          │ false             │
    └──────────────────────┴───────────────────┘

    FILTER EXISTS is the same test used to drop rows.  BIND EXISTS
    keeps every row and records the answer, which is usually what a
    report wants.
    """,
    learn=[
        "EXISTS is the per-row version of ASK, and it can be bound to a "
        "variable rather than only used to filter.",
        "BIND(EXISTS{...} AS ?flag) keeps every row and labels it. FILTER "
        "EXISTS removes rows. Choose by whether the absence is worth "
        "reporting.",
        "The inner pattern sees the outer bindings, which is what makes it a "
        "test about this row rather than about the dataset.",
    ],
    body="""SELECT ?name ?stocksTranslated
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  BIND( EXISTS { ?shop bs:stocks/bs:genre bt:genre-translated-fiction }
        AS ?stocksTranslated )
}
ORDER BY DESC(?stocksTranslated) ?name""",
)

q(
    qid="q78", module=MOD,
    title="Asking a question about a total",
    asks="Does any single town have three or more bookshops?",
    how="ASK takes a whole group pattern, so it can contain a sub-query with "
        "grouping and HAVING. The sub-query produces a row only for towns that "
        "pass, and ASK then reports whether any row survived.",
    diagram="""
    ASK {
      { SELECT ?town (COUNT(?shop) AS ?n)
        WHERE  { ?shop a bs:Bookshop ; bs:locatedIn ?town }
        GROUP BY ?town
        HAVING ( COUNT(?shop) >= 3 ) }
    }
                    │
      the sub-query yields zero rows
                    │
                    ▼
                  false

    Seven towns have two shops -- Wigtown, Edinburgh, Glasgow,
    Sedbergh, York, London and Hay-on-Wye.  None has three.  Change
    the 3 to a 2 and the answer becomes true.

    An aggregate cannot appear at the top level of an ASK, because
    there is nothing to group.  Put it in a sub-query and the
    question becomes "did that produce anything?"
    """,
    learn=[
        "ASK accepts any group pattern, sub-queries included, so any question "
        "you can express as 'are there any rows?' can be asked.",
        "The sub-query does the counting; ASK only reports whether anything "
        "survived HAVING.",
        "This is the cheap way to check a threshold without reading a table "
        "to find out.",
    ],
    body="""ASK {
  {
    SELECT ?town (COUNT(?shop) AS ?shops)
    WHERE {
      ?shop a            bs:Bookshop ;
            bs:locatedIn ?town .
    }
    GROUP BY ?town
    HAVING ( COUNT(?shop) >= 3 )
  }
}""",
)

q(
    qid="q79", module=MOD,
    title="Asking inside one named graph",
    asks="Does the stock graph say anything at all about The Sea Margin?",
    how="An ASK wrapped in GRAPH asks about one part of the dataset rather "
        "than the whole of it. That turns it into a question about where a "
        "fact is filed, which is exactly what you want before joining across "
        "graphs that may not both be loaded.",
    diagram="""
    ASK { GRAPH bt:graph-stock { bt:shop-sea-margin bs:stocks ?anything } }
                └──────┬──────┘
                  only this graph

    ──▶ true

    Useful before a bigger query:

      ASK { GRAPH bt:graph-stock  { ?s ?p ?o } }   is it loaded?
      ASK { GRAPH bt:graph-claims { ?s ?p ?o } }   is the 1.2 layer here?

    An endpoint you did not load yourself may hold any subset of
    what you expect.  Two ASKs tell you which, in less time than
    reading the documentation.
    """,
    learn=[
        "GRAPH inside ASK scopes the question to one named graph.",
        "A pair of ASKs is the quickest way to find out what an unfamiliar "
        "endpoint actually has loaded.",
        "Remember module 08: a pattern outside GRAPH sees only the default "
        "graph, which in this TriG file is nearly empty.",
    ],
    body="""ASK {
  GRAPH bt:graph-stock {
    bt:shop-sea-margin bs:stocks ?anything .
  }
}""",
    data=DTRIG,
)

# ===========================================================================
# DESCRIBE -- and the CONSTRUCT that should usually replace it
# ===========================================================================

q(
    qid="q80", module=MOD,
    title="Describe everything that matches",
    asks="Give me a description of every bookshop in Wales.",
    how="DESCRIBE takes a WHERE clause. The pattern selects the resources, "
        "and the engine then describes each one. It's the quickest way to "
        "pull a subgraph out of an endpoint when you don't yet know what the "
        "resources look like.",
    diagram="""
    DESCRIBE ?shop
    WHERE {
      ?shop a bs:Bookshop ;
            bs:locatedIn/bs:within+ bt:place-wales .
    }

    step 1   the WHERE clause finds 4 shops
    step 2   the engine describes each of them
    step 3   the descriptions are merged into ONE graph

             ┌──────────────┐
             │ Cliff Road   │──┐
             ├──────────────┤  │
             │ Taff Margin  │──┤   one graph,
             ├──────────────┤  ├─▶ not four
             │ Castle Steps │──┤
             ├──────────────┤  │
             │ Clock Tower  │──┘
             └──────────────┘

    The result is a graph, so the shops are not separable in it
    afterwards except by querying it again.
    """,
    learn=[
        "DESCRIBE accepts a WHERE clause, and describes every resource the "
        "pattern binds.",
        "The descriptions merge into a single graph; there's no boundary "
        "between them in the result.",
        "Good for grabbing a subgraph to look at. Still engine-defined, so "
        "still not for a pipeline -- q82 shows the replacement.",
    ],
    body="""DESCRIBE ?shop
WHERE {
  ?shop a            bs:Bookshop ;
        bs:locatedIn/bs:within+ bt:place-wales .
}""",
)

q(
    qid="q81", module=MOD,
    title="Describe several things at once",
    asks="Describe a shop, the town it's in, and an author who lives there.",
    how="DESCRIBE takes a list of IRIs with no WHERE clause at all. The three "
        "descriptions come back merged, which is convenient when you want the "
        "neighbourhood of a few known resources and don't care where one "
        "ends and the next begins.",
    diagram="""
    DESCRIBE bt:shop-inkwell bt:place-wigtown bt:author-rab-fingal

    no WHERE clause: the resources are named directly

        shop-inkwell   ──┐
        place-wigtown  ──┼──▶  one merged graph
        author-rab-fingal ┘

    Note what is NOT here.  Nothing links the three in the result
    unless the data already linked them -- DESCRIBE does not invent
    connections, and it does not follow them either.

    bt:shop-inkwell bs:locatedIn bt:place-wigtown   is in the graph
    because the shop's own description contains it.  The reverse
    direction is not, unless your engine chooses to include
    incoming statements.  Most do not.
    """,
    learn=[
        "DESCRIBE takes a bare list of IRIs, which is the shortest useful "
        "query in SPARQL.",
        "It describes each resource independently and merges the results.",
        "Incoming statements are usually absent. If you need 'what points at "
        "this?', ask for it explicitly with ^ or a second pattern.",
    ],
    body="""DESCRIBE bt:shop-inkwell bt:place-wigtown bt:author-rab-fingal""",
)

q(
    qid="q82", module=MOD,
    title="The CONSTRUCT that replaces DESCRIBE",
    asks="Get a description of The Quire that every engine will produce "
         "identically -- and that's actually readable.",
    how="DESCRIBE leaves the choice of what to include to the engine. Writing "
        "the same thing as CONSTRUCT pins it down, and lets you add what a "
        "bare description always lacks: the labels of the things it points "
        "at, so the result reads without a second query.",
    diagram="""
    DESCRIBE bt:shop-quire        engine decides.  Not reproducible.

    CONSTRUCT {                   you decide.  Reproducible.
      bt:shop-quire ?p ?o .
      ?o rdfs:label ?oLabel .     <- the useful addition
    }
    WHERE {
      bt:shop-quire ?p ?o .
      OPTIONAL { ?o rdfs:label ?oLabel }
    }

    without the labels:            with them:

      bs:locatedIn                   bs:locatedIn
        bt:place-glasgow               bt:place-glasgow
                                     bt:place-glasgow rdfs:label
                                       "Glasgow"@en

    The OPTIONAL matters: ?o is often a literal or a geometry node
    with no label, and without it those statements vanish from the
    output along with the rest of the row.
    """,
    learn=[
        "Anything DESCRIBE does, CONSTRUCT does explicitly and identically on "
        "every engine.",
        "Pulling in the labels of referenced resources is what makes a "
        "description legible; DESCRIBE won't do it for you.",
        "OPTIONAL around the label is required, or objects without one take "
        "their whole row with them.",
        "Glasgow has a label in English and another in Gaelic, so the row for "
        "bs:locatedIn is produced twice and the base triple with it. Q44 "
        "explains why that changes the triple count on one engine and not the "
        "other two.",
    ],
    notes="engines-differ: 26 triples from the browser editor, 25 from HOLOS "
          "and Fuseki, for the reason set out in q44 -- the template is "
          "instantiated once per solution, and bt:place-glasgow has two "
          "labels, so `bt:shop-quire bs:locatedIn bt:place-glasgow` is built "
          "twice. Comunica returns the stream; the other two return the set. "
          "Load either into a graph and they are identical.",
    body="""CONSTRUCT {
  bt:shop-quire ?p ?o .
  ?o rdfs:label ?oLabel .
}
WHERE {
  bt:shop-quire ?p ?o .
  OPTIONAL { ?o rdfs:label ?oLabel . }
}""",
)

q(
    qid="q83", module=MOD,
    title="Following one hop further",
    asks="Describe The Sea Margin including its geometry, which lives on a "
         "separate node.",
    how="GeoSPARQL puts the coordinates on a geometry node, so a one-hop "
        "description of a shop contains a pointer and no numbers. The two "
        "halves are gathered with UNION rather than by nesting one inside the "
        "other -- and the reason why is worth more than the query.",
    diagram="""
    a one-hop description stops at a pointer:

      bt:shop-sea-margin
          geo:hasDefaultGeometry  bt:geom-shop-sea-margin   <- a pointer
          wgs84:lat               57.41...

    the coordinates are on the node it points to:

      bt:geom-shop-sea-margin
          geo:asWKT  "<...CRS84> POINT(-6.19 57.41)"

    THE WRONG WAY -- nest them in one solution:

      ?shop ?p ?o .
      OPTIONAL { ?shop geo:hasDefaultGeometry ?geom . ?geom ?gp ?go }

      17 shop statements x 2 geometry statements = 34 solutions,
      each firing a two-triple template.  The distinct triples are
      still only 20, but the engine built 68 of them to get there --
      and on an engine that does not deduplicate its CONSTRUCT
      stream, all 68 come back.

    THE RIGHT WAY -- keep the halves independent:

      { VALUES ?s { bt:shop-sea-margin }  ?s ?p ?o }
      UNION
      { bt:shop-sea-margin geo:hasDefaultGeometry ?s . ?s ?p ?o }

      17 + 3 solutions.  20 triples.  No multiplication anywhere.

    Two patterns that share no variable but sit in the same group
    multiply.  UNION concatenates instead.  When you are gathering
    unrelated facts about different subjects, that is the one you
    want.
    """,
    learn=[
        "A resource's useful description rarely stops at one hop: geometry, "
        "addresses and n-ary nodes all sit one further out.",
        "Nesting two independent patterns in one group multiplies the "
        "solutions. UNION gathers them without a cross product.",
        "Decide the depth deliberately. Unbounded following turns a "
        "description into a copy of the dataset.",
    ],
    body="""CONSTRUCT {
  ?s ?p ?o .
}
WHERE {
  # The shop's own statements...
  { VALUES ?s { bt:shop-sea-margin }
    ?s ?p ?o . }
  UNION
  # ...and, separately, the statements of the node its geometry points to.
  { bt:shop-sea-margin geo:hasDefaultGeometry ?s .
    ?s ?p ?o . }
}""",
)

# ===========================================================================
# CONSTRUCT -- SPARQL as a transformation language
# ===========================================================================

q(
    qid="q84", module=MOD,
    title="CONSTRUCT WHERE, the short form",
    asks="Extract the shops with their names and founding years, unchanged.",
    how="When the template you want is exactly the pattern you matched, the "
        "template can be omitted. `CONSTRUCT WHERE { ... }` uses the pattern "
        "as its own template. It's the standard way to cut a subgraph out of "
        "a larger one without retyping it.",
    diagram="""
    the long way:

      CONSTRUCT { ?shop a bs:Bookshop ; rdfs:label ?n ; bs:founded ?y }
      WHERE     { ?shop a bs:Bookshop ; rdfs:label ?n ; bs:founded ?y }
                  ─────────────── identical ───────────────

    the short way:

      CONSTRUCT WHERE { ?shop a bs:Bookshop ; rdfs:label ?n ; bs:founded ?y }

    99 triples out: three per shop.

    Restrictions, and the reason they exist -- the pattern IS the
    template, so it must be something a template could contain:

      no FILTER, no OPTIONAL, no UNION, no sub-query
      just a basic graph pattern

    Need any of those?  Write the template out.  That is q85.
    """,
    learn=[
        "CONSTRUCT WHERE { ... } reuses the pattern as the template, and is "
        "the idiomatic way to extract a subgraph unchanged.",
        "It accepts only a basic graph pattern: no FILTER, OPTIONAL, UNION or "
        "sub-query.",
        "The moment you need to reshape anything, write the template out in "
        "full.",
    ],
    body="""CONSTRUCT WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        bs:founded ?year .
}""",
)

q(
    qid="q85", module=MOD,
    title="Republish it in someone else's vocabulary",
    asks="Turn the shops into schema.org, so a search engine could read them.",
    how="A template may use any vocabulary, not just the one the data is in. "
        "This is the everyday use of CONSTRUCT: your data stays in the model "
        "that suits you, and a query publishes it in the model your consumer "
        "expects. The blank node in the template builds structure that does "
        "not exist in the source at all.",
    diagram="""
    source model                    published model

    bs:Bookshop                     schema:BookStore
    rdfs:label                      schema:name
    bs:founded                      schema:foundingDate
    bs:locatedIn ─▶ place ─▶ label  schema:address ─▶ [ a PostalAddress ;
                                                        addressLocality ]
    wgs84:lat / long                schema:latitude / longitude

    the blank node:

      schema:address [ a schema:PostalAddress ;
                       schema:addressLocality ?town ]
                     ▲
                     └── a FRESH blank node per solution, invented
                         by the template; nothing like it exists in
                         the source data

    Each solution gets its own.  Two shops never share one, which
    is what you want here and is worth knowing when it is not.
    """,
    learn=[
        "A CONSTRUCT template can use any vocabulary. Storing in one model "
        "and publishing in another is a query, not a migration.",
        "Blank nodes in a template are minted fresh for each solution, so "
        "structure can be invented that the source doesn't have.",
        "This is how you serve schema.org, or DCAT, or anything else, from "
        "data you did not model that way.",
    ],
    body="""CONSTRUCT {
  ?shop a                    schema:BookStore ;
        schema:name          ?name ;
        schema:foundingDate  ?year ;
        schema:latitude      ?lat ;
        schema:longitude     ?long ;
        schema:address       [ a schema:PostalAddress ;
                               schema:addressLocality ?town ] .
}
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?name ;
        bs:founded   ?year ;
        wgs84:lat    ?lat ;
        wgs84:long   ?long ;
        bs:locatedIn ?place .
  ?place rdfs:label  ?town .
  FILTER( LANG(?town) = "en" )
}""",
    prefixes=SCHEMA_PROLOGUE,
)

q(
    qid="q86", module=MOD,
    title="Upgrade RDF 1.1 data to RDF 1.2",
    asks="Turn the 95 StockRecord nodes into RDF 1.2 annotations, "
         "automatically.",
    how="This is the migration module 11 argues for, written as one query. "
        "TRIPLE() builds a triple term from three variables; IRI() mints a "
        "stable reifier from the record's own name; and the template emits "
        "the base triple, the rdf:reifies link and the annotations. Run it "
        "against the 1.1 file and the output is the 1.2 file's stock section.",
    diagram="""
    in  (RDF 1.1, an invented node)      out  (RDF 1.2)

    bt:stock-inkwell--the-book-town      bt:shop-inkwell bs:stocks
        a bs:StockRecord ;                   bt:book-the-book-town .
        bs:atShop     ?shop ;
        bs:ofWork     ?work ;            bt:reifier-inkwell--the-book-town
        bs:copies     12 ;                   rdf:reifies <<( ?shop bs:stocks
        bs:shelfPrice 9.99 .                                  ?work )>> ;
                                             bs:copies     12 ;
                                             bs:shelfPrice 9.99 .

    the two functions that make it work:

      BIND( TRIPLE(?shop, bs:stocks, ?work) AS ?statement )
            ──────┬─────                         builds a triple term
                  └── SPARQL 1.2

      BIND( IRI(CONCAT("...reifier-", ?suffix)) AS ?reifier )
            ─┬─                                    a stable name, so
             └── re-running gives the same IRIs     the output is idempotent

    A blank node would work too, and would produce a different
    graph every run.  For a migration you want the same one.
    """,
    learn=[
        "TRIPLE(s, p, o) constructs a triple term in an expression, which is "
        "how you get one into a CONSTRUCT template -- templates can't call "
        "functions themselves.",
        "IRI(CONCAT(...)) mints names from data. Deriving them from something "
        "stable makes the transformation repeatable.",
        "A whole modelling migration can be one query. Run it, check the "
        "output, load it, drop the old nodes.",
    ],
    body="""CONSTRUCT {
  ?shop    bs:stocks     ?work .
  ?reifier rdf:reifies   ?statement ;
           bs:copies     ?copies ;
           bs:shelfPrice ?price .
}
WHERE {
  ?record a             bs:StockRecord ;
          bs:atShop     ?shop ;
          bs:ofWork     ?work ;
          bs:copies     ?copies ;
          bs:shelfPrice ?price .

  BIND( TRIPLE(?shop, bs:stocks, ?work) AS ?statement )
  BIND( IRI(CONCAT("https://example.org/bookshop-trail/reifier-",
                   STRAFTER(STR(?record),
                            "https://example.org/bookshop-trail/stock-")))
        AS ?reifier )
}""",
    notes="Reads the RDF 1.1 file and writes RDF 1.2, so it needs a SPARQL "
          "1.2 engine to run even though its input is 1.1. All three qualify.",
)

q(
    qid="q87", module=MOD,
    title="A profile of the genre scheme",
    asks="Build a graph that records, for each genre, how many shops "
         "specialise in it and how many works are filed under it.",
    how="Aggregation happens in sub-queries; the template assembles the "
        "results. Because `skos:broader*` climbs the tree, a shop "
        "specialising in Tartan Noir counts towards Crime Fiction and Fiction "
        "as well -- so the output is a rolled-up profile, not a flat tally.",
    diagram="""
    two sub-queries, one template:

      ┌ shops per genre, rolled up the tree ──────┐
      │ ?shop bs:specialises/skos:broader* ?genre │
      └───────────────────┬───────────────────────┘
                          │
      ┌ works per genre, rolled up ───────────────┐
      │ ?work bs:genre/skos:broader* ?genre       │
      └───────────────────┬───────────────────────┘
                          ▼
      CONSTRUCT { ?genre bs:shopCount ?shops ;
                         bs:workCount ?works ;
                         skos:prefLabel ?label }

    the rolling up, in one branch:

      Cosy Crime       2 shops    ─┐
      Tartan Noir      1 shop     ─┼─▶ Crime Fiction  4 shops
      Crime Fiction    1 shop     ─┘        └──────▶ Fiction  17
                                                        └──▶ Literature  33

    A flat count would put 1 against Crime Fiction and lose the
    other three.  The * is what makes the number mean what a reader
    will assume it means -- and Literature, the top concept, ends up
    with all 33 shops, which is the correct answer to "how many
    shops specialise in some kind of literature?"
    """,
    learn=[
        "CONSTRUCT plus aggregation produces derived graphs -- summaries you "
        "can store, publish or query again.",
        "Rolling a count up a SKOS tree is one path expression, and it's "
        "almost always what the reader expects a category total to mean.",
        "The output is small. Load it back into the editor and the whole "
        "profile fits in the graph view.",
    ],
    body="""CONSTRUCT {
  ?genre skos:prefLabel ?label ;
         bs:shopCount   ?shops ;
         bs:workCount   ?works .
}
WHERE {
  ?genre skos:prefLabel ?label .
  FILTER( LANG(?label) = "en" )
  {
    SELECT ?genre (COUNT(DISTINCT ?shop) AS ?shops)
    WHERE { ?shop bs:specialises/skos:broader* ?genre . }
    GROUP BY ?genre
  }
  {
    SELECT ?genre (COUNT(DISTINCT ?work) AS ?works)
    WHERE { ?work bs:genre/skos:broader* ?genre . }
    GROUP BY ?genre
  }
}""",
)

q(
    qid="q88", module=MOD,
    title="A validation report, as RDF",
    asks="Produce a graph listing everything questionable in the dataset.",
    how="Three checks in a UNION, each binding a message, and a template that "
        "mints a fresh blank node per finding. The result is a report you can "
        "query, diff against last week's, or hand to another tool -- which a "
        "printed table isn't.",
    diagram="""
    ┌ works with no ISBN ───────────┐
    │ FILTER NOT EXISTS {?w bs:isbn}│─┐
    ├ shops with no website ────────┤ │
    │ FILTER NOT EXISTS {?s website}│─┼─ UNION ─▶ CONSTRUCT
    ├ shops off the trail ──────────┤ │             │
    │ FILTER NOT EXISTS {path}      │─┘             │
    └───────────────────────────────┘               ▼

      []  a          bs:DataIssue ;
          bs:about   ?thing ;
          bs:message ?message .
      ▲
      └── a fresh blank node for every finding

    ┌──────────────────────┬────────────────────────────────┐
    │ bt:book-cold-harbour │ Work has no ISBN               │
    │ bt:shop-marginalia   │ Shop publishes no website      │
    │ bt:shop-west-quay    │ Not reachable on foot from the │
    │                      │ start of the trail             │
    └──────────────────────┴────────────────────────────────┘

    19 findings, 57 triples -- three per finding:

      11  works published before 1970, so no ISBN existed
       6  shops that publish no website
       2  the south-western pair, joined to each other and
          to nothing else

    Every one is expected in this dataset.  A report of
    known-acceptable findings is still worth generating: what you
    watch is the diff against last time.
    """,
    learn=[
        "A report that's RDF can be queried, diffed and stored. A report "
        "that's a printed table can only be read.",
        "[] in a template mints a fresh blank node per solution -- the right "
        "choice when the finding has no identity of its own.",
        "UNION with a bound message is how you run several unrelated checks "
        "in one pass.",
    ],
    body="""CONSTRUCT {
  []  a          bs:DataIssue ;
      bs:about   ?thing ;
      bs:message ?message .
}
WHERE {
  {
    ?thing a bs:Work .
    FILTER NOT EXISTS { ?thing bs:isbn ?isbn }
    BIND( "Work has no ISBN. Expected for titles published before 1970." AS ?message )
  }
  UNION
  {
    ?thing a bs:Bookshop .
    FILTER NOT EXISTS { ?thing bs:website ?site }
    BIND( "Shop publishes no website." AS ?message )
  }
  UNION
  {
    ?thing a bs:Bookshop .
    FILTER NOT EXISTS {
      bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ ?thing .
    }
    BIND( "Shop is not reachable on foot from the start of the trail." AS ?message )
  }
}""",
)

q(
    qid="q89", module=MOD,
    title="Invent a relationship the data doesn't have",
    asks="Link every pair of shops that share a town.",
    how="Nothing in the data says two shops are neighbours; it says only "
        "which town each is in. The relationship is implied by the join, and "
        "CONSTRUCT is what turns an implication into a triple you can then "
        "traverse with a property path like any other.",
    diagram="""
    what the data says:

      shop-inkwell    bs:locatedIn  place-wigtown
      shop-marginalia bs:locatedIn  place-wigtown

    what it implies, and does not state:

      shop-inkwell  bs:sameTownAs  shop-marginalia

    the join that finds it:

      ?a bs:locatedIn ?town .
      ?b bs:locatedIn ?town .        <- same ?town: that IS the relationship
      FILTER( STR(?a) < STR(?b) )    <- each pair once, not twice

    7 pairs, one per two-shop town: Wigtown, Edinburgh, Glasgow,
    Sedbergh, York, London and Hay-on-Wye.  14 triples, because the
    template asserts the link in both directions.

    Load the result alongside the source and bs:sameTownAs is now
    an ordinary predicate -- paths, counts and all.  This is how a
    graph grows a shortcut it uses often.
    """,
    learn=[
        "A relationship implied by a shared value becomes a real edge the "
        "moment you CONSTRUCT it.",
        "STR(?a) < STR(?b) is the standard guard for emitting an unordered "
        "pair once rather than twice, and it also stops a thing pairing with "
        "itself.",
        "Materialising a frequently-walked shortcut is a legitimate "
        "optimisation. Just be sure you can rebuild it when the source "
        "changes.",
    ],
    body="""CONSTRUCT {
  ?a bs:sameTownAs ?b .
  ?b bs:sameTownAs ?a .
}
WHERE {
  ?a a bs:Bookshop ; bs:locatedIn ?town .
  ?b a bs:Bookshop ; bs:locatedIn ?town .
  FILTER( STR(?a) < STR(?b) )
}""",
)
