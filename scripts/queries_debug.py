# -*- coding: utf-8 -*-
"""Module 13: planning and debugging.

The diagnostic queries.  The engine-specific instructions for getting a plan
out of each of the three live in queries/13-planning-and-debugging/README.md,
because they are commands rather than queries.
"""

from querycat import q, D11, D12, DFULL, ALL, EDITOR, HOLOS, FUSEKI

MOD = "13-planning-and-debugging"

q(
    qid="q90", module=MOD,
    title="How selective is each pattern",
    asks="Before optimising anything: how many rows does each pattern in my "
         "query match on its own?",
    how="An engine joins patterns in whatever order it thinks cheapest, and "
        "it decides using estimates. When it gets that wrong, the fix is "
        "usually to know the real numbers. Counting each pattern alone tells "
        "you which one is the filter and which one is the fan-out.",
    diagram="""
    count each pattern on its own, then read the spread:

    ┌────────────────────────────────────┬────────┐
    │ ?s bs:hasCafe true                 │     22 │  ← selective
    │ ?s a bs:Bookshop                   │     33 │
    │ ?s bs:locatedIn ?o                 │     46 │
    │ ?s bs:stocks ?o                    │     95 │
    │ ?s rdfs:label ?o                   │    434 │  ← fans out
    │ ?s ?p ?o                           │  4,698 │
    └────────────────────────────────────┴────────┘

    A join costs roughly the product of what it joins, so the order
    matters:

      33 x 434   evaluated the wrong way round
      33 -> 33   evaluated the selective pattern first

    Most engines get this right unaided.  When one does not, this
    table tells you what to tell it -- and gives you the numbers to
    argue with the plan in the README.
    """,
    learn=[
        "Measure before optimising. An estimate that's wrong by a factor of "
        "a thousand is the usual cause of a slow query.",
        "The most selective pattern should be evaluated first; the engine "
        "normally arranges that, and this is how you check.",
        "`?s ?p ?o` matches the whole store. Never leave one in a query you "
        "care about the speed of.",
    ],
    body="""SELECT ?pattern ?rows
WHERE {
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s bs:hasCafe true . } }
    BIND( "?s bs:hasCafe true"  AS ?pattern ) }
  UNION
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s a bs:Bookshop . } }
    BIND( "?s a bs:Bookshop"    AS ?pattern ) }
  UNION
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s bs:locatedIn ?o . } }
    BIND( "?s bs:locatedIn ?o"  AS ?pattern ) }
  UNION
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s bs:stocks ?o . } }
    BIND( "?s bs:stocks ?o"     AS ?pattern ) }
  UNION
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s rdfs:label ?o . } }
    BIND( "?s rdfs:label ?o"    AS ?pattern ) }
  UNION
  { { SELECT (COUNT(*) AS ?rows) WHERE { ?s ?p ?o . } }
    BIND( "?s ?p ?o  (everything)" AS ?pattern ) }
}
ORDER BY ?rows""",
)

q(
    qid="q91", module=MOD,
    title="The cross product you did not mean to write",
    asks="What happens when two patterns in the same group share no variable?",
    how="Two patterns in one group are joined. If they have no variable in "
        "common there's nothing to join on, so every row of one is paired "
        "with every row of the other. No error is raised. The result is "
        "simply enormous, and every aggregate over it's wrong.",
    diagram="""
    joined -- ?town is shared:

      ?shop bs:locatedIn ?town .
      ?town rdfs:label   ?name .
             ▲       ▲
             └───────┘  the join
                          ──▶  63 rows

    crossed -- one letter changed, and nothing is shared:

      ?shop bs:locatedIn ?town .
      ?other rdfs:label  ?name .
       ─┬───
        └── a different variable, so no join at all
                          ──▶  46 x 434  =  19,964 rows

    ┌──────────────────────────────────────────────┐
    │  the symptom:  far too many rows, and every  │
    │  COUNT and SUM inflated by the same factor   │
    │                                              │
    │  the cause:    almost always a typo in a     │
    │                variable name                 │
    └──────────────────────────────────────────────┘

    Spotting it: the crossed count is EXACTLY the product of the
    two pattern sizes.  Count each pattern alone, as in q90, and
    multiply.  If the answer matches, nothing joined.

    Note that 19,964 / 63 is not a round number.  The ratio is not
    the tell -- the product is.  The joined query returns 63 rather
    than 46 because some towns carry two labels, so even the
    correct query multiplies a little.
    """,
    learn=[
        "Patterns in the same group are joined on shared variables. With none "
        "shared, you get the Cartesian product and no warning.",
        "The tell is that the row count equals the product of the pattern "
        "sizes measured separately. Count them with q90 and multiply.",
        "The cause is nearly always a mistyped variable, which is why "
        "consistent naming pays for itself.",
    ],
    body="""SELECT ?joined ?crossed ?ratio
WHERE {
  {
    SELECT (COUNT(*) AS ?joined) WHERE {
      ?shop bs:locatedIn ?town .
      ?town rdfs:label   ?name .
    }
  }
  {
    SELECT (COUNT(*) AS ?crossed) WHERE {
      ?shop  bs:locatedIn ?town .
      ?other rdfs:label   ?name .
    }
  }
  BIND( ?crossed / ?joined AS ?ratio )
}""",
)

q(
    qid="q92", module=MOD,
    title="The join that inflates an aggregate",
    asks="Why does counting shops per council area give the wrong number when "
         "events are in the same query?",
    how="Joining shops to events multiplies the shop rows: a shop with six "
        "events appears six times. COUNT(?shop) then counts appearances "
        "rather than shops. COUNT(DISTINCT ?shop) repairs the symptom; two "
        "sub-queries repair the cause.",
    diagram="""
    one pattern, two things being counted:

      ?shop bs:locatedIn/bs:within+ ?council .
      OPTIONAL { ?event bs:heldAt ?shop }

    North Yorkshire, 3 shops, 6 events:

      Endpapers     x 3 events  ─┐
      The Bookwyrm  x 2 events  ─┼─  6 rows, not 3
      The Harbour Page x 1      ─┘

      COUNT(?shop)           =  6    wrong
      COUNT(DISTINCT ?shop)  =  3    right
      COUNT(DISTINCT ?event) =  6    right

    Greater London is starker still: 2 shops, 6 events, and
    COUNT(?shop) reports 6 -- three times the true figure.

    DISTINCT rescues COUNT.  It does not rescue SUM or AVG:
    summing floor area over those 6 rows counts Endpapers three
    times, and no SUM(DISTINCT ...) means what you want, because
    two shops may legitimately share a floor area.

    The real fix is q70's: count each thing in its own sub-query,
    and join the two summaries.
    """,
    learn=[
        "A join that multiplies rows corrupts every aggregate over them.",
        "COUNT(DISTINCT ?x) survives it. SUM and AVG don't, and can't be "
        "made to.",
        "If a query counts two unrelated things per group, it needs two "
        "aggregations -- not one join and some hope.",
    ],
    body="""SELECT ?councilName ?rows ?inflated ?correct ?events
WHERE {
  ?council a          bs:CouncilArea ;
           rdfs:label ?councilName .
  {
    SELECT ?council
           (COUNT(*)               AS ?rows)
           (COUNT(?shop)           AS ?inflated)
           (COUNT(DISTINCT ?shop)  AS ?correct)
           (COUNT(DISTINCT ?event) AS ?events)
    WHERE {
      ?shop a bs:Bookshop ; bs:locatedIn/bs:within+ ?council .
      ?council a bs:CouncilArea .
      OPTIONAL { ?event bs:heldAt ?shop . }
    }
    GROUP BY ?council
  }
  FILTER( ?inflated != ?correct )
}
ORDER BY DESC(?inflated) ?councilName""",
)

q(
    qid="q93", module=MOD,
    title="Why is my result empty",
    asks="A query returns nothing. Which line is responsible?",
    how="Bisect it. Each branch tests a longer prefix of the query with "
        "EXISTS, so the answer flips from true to false at exactly the line "
        "that kills it. It beats commenting lines out by hand, and it runs in "
        "one go.",
    diagram="""
    build the query up one line at a time, and ask EXISTS at each:

    ┌───────────────────────────────────────────┬───────┐
    │ 1  any bs:Bookshop at all                 │ true  │
    │ 2  ...with a bs:founded                   │ true  │
    │ 3  ...founded before 1970, cast directly  │  ???  │  ← flips here
    │ 4  ...founded before 1970, via STR()      │ true  │
    └───────────────────────────────────────────┴───────┘

    Step 3 is the q07 trap: xsd:integer() applied straight to an
    xsd:gYear.  On Fuseki it is true; on the browser editor and on
    HOLOS it is false, and no error is raised on any of them.

    Run this on YOUR engine.  Whichever line flips is the one to
    rewrite -- and if none of them flips, the problem is in a part
    of the query this ladder does not reach.

    The empty-result checklist, in the order that pays off:

      1  a datatype comparison            (q07, q62, q60)
      2  a language tag on a literal      (q95)
      3  a mistyped prefix or IRI         (q96)
      4  a FILTER that escaped an OPTIONAL (q19)
      5  MINUS with no shared variable    (q17)
    """,
    learn=[
        "Bisect with EXISTS rather than by commenting lines out. One run "
        "tells you where it breaks.",
        "An empty result is far more often a datatype or language-tag "
        "mismatch than a genuine absence of data.",
        "Nothing here errors. Silence is the normal failure mode in SPARQL, "
        "which is why a ladder like this is worth keeping to hand.",
    ],
    body="""SELECT ?step ?matches
WHERE {
  { BIND( "1  any bs:Bookshop at all"                AS ?step )
    BIND( EXISTS { ?s a bs:Bookshop . }              AS ?matches ) }
  UNION
  { BIND( "2  ...with a bs:founded"                  AS ?step )
    BIND( EXISTS { ?s a bs:Bookshop ; bs:founded ?y . } AS ?matches ) }
  UNION
  { BIND( "3  ...founded before 1970, cast directly" AS ?step )
    BIND( EXISTS { ?s a bs:Bookshop ; bs:founded ?y .
                   FILTER( xsd:integer(?y) < 1970 ) } AS ?matches ) }
  UNION
  { BIND( "4  ...founded before 1970, via STR()"     AS ?step )
    BIND( EXISTS { ?s a bs:Bookshop ; bs:founded ?y .
                   FILTER( xsd:integer(STR(?y)) < 1970 ) } AS ?matches ) }
}
ORDER BY ?step""",
    notes="engines-differ: step 3 is the point. Fuseki reports true, the "
          "browser editor and HOLOS report false, and none of them raises an "
          "error. That's what the query is for -- run it on the engine you "
          "actually use, and believe that column rather than this note.",
)

q(
    qid="q94", module=MOD,
    title="Pin one case while you work on it",
    asks="How do I run a complicated query against a single known resource?",
    how="VALUES binds a variable to a fixed list before anything else runs, "
        "which turns a query over the whole dataset into a query over one row "
        "of it. Delete the line and the query is the real one again -- no "
        "other edits, so there's nothing to forget to undo.",
    diagram="""
    VALUES ?shop { bt:shop-cliff-road }
    ?shop a bs:Bookshop ; rdfs:label ?shopName ; bs:locatedIn ?town .
    ?town  rdfs:label ?townName .
    ?town  bs:within+ ?country .
    ?country a bs:Country ; rdfs:label ?countryName .

    with the VALUES line     1 shop,  easy to read
    without it              33 shops, the real query

    Add rows to widen the net without losing the focus:

      VALUES ?shop { bt:shop-cliff-road
                     bt:shop-sea-margin
                     bt:shop-west-quay }

    and several variables at once, when the interesting case is a
    combination:

      VALUES (?shop ?genre) {
        (bt:shop-verso bt:genre-translated-fiction)
        (bt:shop-quire bt:genre-graphic-novels)
      }

    Better than a FILTER for this: VALUES restricts before the join
    rather than after it, so the debugging run is fast even when
    the real query is not.
    """,
    learn=[
        "VALUES injects a fixed table of bindings, and is the cleanest way to "
        "pin a query to one case while you work on it.",
        "It restricts before the join, so a clamped query stays fast however "
        "slow the unclamped one is.",
        "One line in, one line out. Nothing else about the query changes, "
        "which is what makes it safe.",
    ],
    body="""SELECT ?shopName ?townName ?countryName
WHERE {
  # Delete this one line to run the query for real.
  VALUES ?shop { bt:shop-cliff-road bt:shop-sea-margin }

  ?shop    a          bs:Bookshop ;
           rdfs:label ?shopName ;
           bs:locatedIn ?town .
  ?town    rdfs:label ?townName .
  ?town    bs:within+ ?country .
  ?country a          bs:Country ;
           rdfs:label ?countryName .
  FILTER( LANG(?townName) = "en" && LANG(?countryName) = "en" )
}
ORDER BY ?shopName""",
)

q(
    qid="q95", module=MOD,
    title="The language tag that stops a match",
    asks="Why does comparing a label to a string find nothing?",
    how="A literal with a language tag isn't equal to the same characters "
        "without one. They are different RDF terms. Nearly every label in "
        "this dataset is tagged, so the obvious comparison silently matches "
        "nothing at all.",
    diagram="""
    in the data:      "Cardiff"@en        tagged
    in the query:     "Cardiff"           untagged

                      "Cardiff"@en  =  "Cardiff"   ──▶  false

    three ways to write the comparison:

    ┌──────────────────────────┬──────┬────────────────────────┐
    │ ?label = "Cardiff"       │  0   │ different terms        │
    │ ?label = "Cardiff"@en    │  1   │ exact, but brittle     │
    │ STR(?label) = "Cardiff"  │  1   │ drops the tag: robust  │
    └──────────────────────────┴──────┴────────────────────────┘

    STR() is the general answer, and the same tool that fixes the
    datatype traps in q07 and q62.  It strips a literal to its
    characters, whatever was attached.

    Watch for this in ORDER BY too: sorting on a tagged literal is
    not the same as sorting on its text, and engines differ on the
    result (q25 found exactly that).
    """,
    learn=[
        "A language-tagged literal is a different term from the plain string, "
        "and equality between them is false.",
        "STR() strips the tag and is the portable way to compare text.",
        "langMatches(LANG(?l), \"en\") is the right test when you want a "
        "language rather than a value, and it handles subtags such as en-GB.",
    ],
    body="""SELECT ?comparison ?matches
WHERE {
  { { SELECT (COUNT(*) AS ?matches) WHERE {
        ?p a bs:Settlement ; rdfs:label ?label .
        FILTER( ?label = "Cardiff" ) } }
    BIND( "?label = Cardiff          (untagged)" AS ?comparison ) }
  UNION
  { { SELECT (COUNT(*) AS ?matches) WHERE {
        ?p a bs:Settlement ; rdfs:label ?label .
        FILTER( ?label = "Cardiff"@en ) } }
    BIND( "?label = Cardiff@en       (tagged)"   AS ?comparison ) }
  UNION
  { { SELECT (COUNT(*) AS ?matches) WHERE {
        ?p a bs:Settlement ; rdfs:label ?label .
        FILTER( STR(?label) = "Cardiff" ) } }
    BIND( "STR(?label) = Cardiff     (tag dropped)" AS ?comparison ) }
}
ORDER BY ?comparison""",
)

q(
    qid="q96", module=MOD,
    title="Find the mistyped IRI",
    asks="A pattern matches nothing and the vocabulary looks right. How do I "
         "check?",
    how="Take a census of the predicate namespaces actually in use. A "
        "mistyped prefix produces an IRI in a namespace that appears nowhere "
        "else, or doesn't appear at all -- and either is obvious the moment "
        "the real namespaces are listed next to their counts.",
    diagram="""
    strip each predicate back to its namespace and count:

      REPLACE( STR(?p), "[^#/]*$", "" )

      <...bookshop-trail/schema#founded>  ──▶  <...schema#>

    ┌─────────────────────────────────────────────┬───────┐
    │ https://example.org/bookshop-trail/schema#  │ 2,248 │
    │ http://www.w3.org/1999/02/22-rdf-syntax-ns# │ 1,088 │
    │ http://www.w3.org/2000/01/rdf-schema#       │   620 │
    │ http://www.opengis.net/ont/geosparql#       │   387 │
    │ http://www.w3.org/2004/02/skos/core#        │   152 │
    │ http://www.w3.org/2003/01/geo/wgs84_pos#    │   126 │
    │ http://purl.org/dc/terms/                   │    74 │
    │ http://www.w3.org/2002/07/owl#              │     3 │
    └─────────────────────────────────────────────┴───────┘

    Eight namespaces, and the counts are a sanity check in
    themselves: owl# appears three times, because the vocabulary
    declares exactly three OWL characteristics.

    Now compare with what your query is asking for.  The two
    mistakes this catches:

      schema:  vs  schema#     one character, no match, no error
      https:   vs  http:       the same, and easier to miss

    This dataset uses https://example.org/... and http://www.w3.org/...
    -- both schemes, deliberately, because real data does.

    The same census on rdf:type objects tells you the classes:
        SELECT ?class (COUNT(*) AS ?n)
        WHERE { ?s a ?class } GROUP BY ?class
    """,
    learn=[
        "Listing the namespaces actually in use finds a mistyped prefix in "
        "one query.",
        "A wrong IRI isn't an error in SPARQL. It's a pattern that matches "
        "nothing, which looks exactly like an empty dataset.",
        "http versus https, and # versus /, are the two that catch everyone. "
        "Copy IRIs from the data; don't retype them.",
    ],
    body="""SELECT ?namespace (COUNT(*) AS ?uses)
WHERE {
  ?s ?p ?o .
  BIND( REPLACE(STR(?p), "[^#/]*$", "") AS ?namespace )
}
GROUP BY ?namespace
ORDER BY DESC(?uses)""",
)

q(
    qid="q97", module=MOD,
    title="Three spellings, one answer, three plans",
    asks="Do these three ways of asking 'which shops are in Scotland' give "
         "the same result?",
    how="They do, and the engines build visibly different algebra for each. "
        "That's the point: a query is a description of what you want, not "
        "instructions for getting it, and the shape you write isn't "
        "necessarily the shape that runs. Run this, then read the plans in "
        "the module README.",
    diagram="""
    A  two patterns, path in the second

         ?shop bs:locatedIn ?town .
         ?town bs:within+ bt:place-scotland .

    B  one pattern, path chained on

         ?shop bs:locatedIn/bs:within+ bt:place-scotland .

    C  the same journey, walked backwards

         bt:place-scotland ^bs:within+/^bs:locatedIn ?shop .

    all three ──▶ 9 shops

    but the algebra differs.  Jena, for A:

      (sequence (bgp (triple ?shop bs:locatedIn ?town))
                (path ?town (path+ bs:within) bt:place-scotland))

    and for B it folds the join away entirely:

      (path ?shop (seq bs:locatedIn (path+ bs:within)) bt:place-scotland)

    Which is faster depends on the store, the data and the
    direction the index favours.  Measure; do not assume.  What is
    reliable is that all three mean the same thing -- so write the
    one that reads best, and only reach for another when a
    measurement tells you to.
    """,
    learn=[
        "Several spellings of one question are common, and they are genuinely "
        "equivalent.",
        "The engine rewrites what you wrote. Reading the plan is how you find "
        "out into what.",
        "Write for the reader first. Rewrite for the optimiser only when you "
        "have measured a reason to.",
    ],
    body="""SELECT ?spelling ?shops
WHERE {
  { { SELECT (COUNT(DISTINCT ?shop) AS ?shops) WHERE {
        ?shop a bs:Bookshop ; bs:locatedIn ?town .
        ?town bs:within+ bt:place-scotland . } }
    BIND( "A  two patterns, path in the second" AS ?spelling ) }
  UNION
  { { SELECT (COUNT(DISTINCT ?shop) AS ?shops) WHERE {
        ?shop a bs:Bookshop ; bs:locatedIn/bs:within+ bt:place-scotland . } }
    BIND( "B  one pattern, path chained on"     AS ?spelling ) }
  UNION
  { { SELECT (COUNT(DISTINCT ?shop) AS ?shops) WHERE {
        bt:place-scotland ^bs:within+/^bs:locatedIn ?shop .
        ?shop a bs:Bookshop . } }
    BIND( "C  the same journey, backwards"      AS ?spelling ) }
}
ORDER BY ?spelling""",
)
