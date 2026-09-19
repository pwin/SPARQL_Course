# -*- coding: utf-8 -*-
"""Module 17: SPARQL Update -- changing the data.

Everything up to here reads. This module writes, and writing is a different
discipline: an update returns nothing at all, so every one of these comes in
two halves -- the update itself, and a query that shows what it did. The
checker applies each update to a throwaway copy of the dataset and then runs
the second half, which is how the numbers in these headers were arrived at:

    python scripts/check_queries.py q116 q117 q118 q119 q120 q121 q122 q123

One thing to know before starting. The Turtle Editor Viewer cannot run these.
Comunica, the library underneath it, supports SPARQL Update perfectly well --
the editor's SPARQL panel has no way to display the result of an operation
that returns nothing, so it is not wired up. The engine column in this module
says "comunica" rather than "editor" for exactly that reason. Use Fuseki or
HOLOS to follow along.
"""

from querycat import q, D11, DTRIG, COMUNICA, HOLOS, FUSEKI, ALL_UPDATE

MOD = "17-updating-the-data"

q(
    qid="q116", module=MOD,
    title="Adding facts you already know",
    asks="Add a new bookshop to the trail.",
    how="INSERT DATA takes ground triples -- no variables, no WHERE -- and puts "
        "them in the store. It is the simplest thing in SPARQL Update and the "
        "one you will use least, because most of what you want to add depends "
        "on what is already there.",
    diagram="""
    INSERT DATA {
      bt:shop-foxed-page a bs:Bookshop ; ... .
    }
             |
             '-- ground triples only. A variable here is a syntax error.

    before                    after
    ------                    -----
    2 shops in Hay-on-Wye     3
      Castle Steps Books        Castle Steps Books
      The Clock Tower           The Clock Tower
                                The Foxed Page      <- new

    Pick a subject that does not already exist. INSERT DATA on an
    IRI that is already in the store adds to it rather than
    replacing it -- which is q119's whole subject, arrived at by
    accident.

    An update returns nothing: no rows, no count, no graph. Fuseki
    answers HTTP 204 and HOLOS prints "inserted 5 deleted 0". That
    is the whole feedback, which is why the second half of every
    query in this module is a SELECT.

    INSERT DATA is also idempotent. Running it twice adds nothing
    the second time, because a graph is a set: the same triple is
    already there.
    """,
    learn=[
        "INSERT DATA adds ground triples. No variables, no WHERE clause.",
        "An update produces no result, so pair every one with a query that "
        "shows what changed. Get into the habit now.",
        "Adding a triple that is already present does nothing. RDF graphs are "
        "sets, so updates that only insert are safe to re-run.",
    ],
    body="""INSERT DATA {
  bt:shop-foxed-page
      a            bs:Bookshop ;
      rdfs:label   "The Foxed Page"@en ;
      bs:locatedIn bt:place-hay-on-wye ;
      bs:founded   "2019"^^xsd:gYear ;
      bs:hasCafe   true .
}""",
    verify="""SELECT ?name ?founded
WHERE {
  ?shop a            bs:Bookshop ;
        bs:locatedIn bt:place-hay-on-wye ;
        rdfs:label   ?name .
  OPTIONAL { ?shop bs:founded ?founded }
}
ORDER BY ?name""",
    data=D11,
    engines=ALL_UPDATE,
)

q(
    qid="q117", module=MOD,
    title="Removing facts you can name",
    asks="The Inkwell has closed its cafe. Remove that one fact.",
    how="DELETE DATA is the mirror of INSERT DATA: ground triples, removed "
        "exactly. It will not accept a variable, which makes it safe and "
        "almost useless -- you have to already know the object you are "
        "deleting, down to its datatype.",
    diagram="""
    DELETE DATA { bt:shop-inkwell bs:hasCafe true . }

    the triple has to match EXACTLY:

      bs:hasCafe true                  matches
      bs:hasCafe "true"                does not -- a string
      bs:hasCafe "true"^^xsd:boolean   matches -- same term
      bs:hasCafe ?anything             SYNTAX ERROR

    +--------------------+--------+-------+
    |                    | before | after |
    +--------------------+--------+-------+
    | says true          |     22 |    21 |
    | says false         |     11 |    11 |
    | says nothing       |      0 |     1 |
    +--------------------+--------+-------+

    That last row is The Inkwell, and it now says NOTHING about a
    cafe -- which is not the same as saying it has none. Deleting a
    fact leaves silence, not a denial.

    Deleting a triple that is not there is not an error. It quietly
    does nothing -- so a DELETE DATA that achieves nothing looks
    exactly like one that worked.
    """,
    learn=[
        "DELETE DATA removes ground triples and takes no variables. The terms "
        "must match exactly, datatype included.",
        "Deleting a fact leaves the absence of a fact, not its negation. In "
        "RDF those are different, and q16's lesson applies here too.",
        "A DELETE that matches nothing is silent. Check with a query rather "
        "than assuming.",
    ],
    body="""DELETE DATA {
  bt:shop-inkwell bs:hasCafe true .
}""",
    verify="""SELECT ?state (COUNT(*) AS ?shops)
WHERE {
  ?shop a bs:Bookshop .
  OPTIONAL { ?shop bs:hasCafe ?cafe }
  BIND( COALESCE(STR(?cafe), "no statement") AS ?state )
}
GROUP BY ?state
ORDER BY ?state""",
    data=D11,
    engines=ALL_UPDATE,
)

q(
    qid="q118", module=MOD,
    title="Removing whatever matches",
    asks="Drop every bs:hasCafe false statement, on the grounds that they say "
         "nothing a missing statement would not.",
    how="DELETE WHERE is the shorthand that finally allows variables: the "
        "pattern is both the thing to match and the thing to remove, written "
        "once. It is the most useful deletion form and the most dangerous, "
        "because the pattern that matches too much removes too much.",
    diagram="""
    DELETE WHERE { ?shop bs:hasCafe false }
                   -----------------------
                   matched AND deleted -- the same block does both

    equivalent long form:

      DELETE { ?shop bs:hasCafe false }
      WHERE  { ?shop bs:hasCafe false }

    +--------------------+--------+-------+
    |                    | before | after |
    +--------------------+--------+-------+
    | says true          |     22 |    22 |
    | says false         |     11 |     0 |
    | says nothing       |      0 |    11 |
    +--------------------+--------+-------+

    Whether this is an improvement depends entirely on whether you
    were relying on "false" meaning "we checked, and no". Once the
    statement is gone, that shop is indistinguishable from one
    nobody has asked about.

    Now widen the pattern by one step and read it again:

        DELETE WHERE { ?s bs:hasCafe ?o }     both kinds gone
        DELETE WHERE { ?s ?p ?o }             everything gone

    q123 is about that second one.
    """,
    learn=[
        "DELETE WHERE matches and deletes with one pattern. It is the form you "
        "will reach for most.",
        "Run the pattern as a SELECT first, every time. The pattern is the "
        "whole of what makes a deletion safe.",
        "Removing a false statement is not the same as leaving it. Decide "
        "which of the two your consumers expect.",
    ],
    body="""DELETE WHERE {
  ?shop bs:hasCafe false .
}""",
    verify="""SELECT ?state (COUNT(*) AS ?shops)
WHERE {
  ?shop a bs:Bookshop .
  OPTIONAL { ?shop bs:hasCafe ?cafe }
  BIND( COALESCE(STR(?cafe), "no statement") AS ?state )
}
GROUP BY ?state
ORDER BY ?state""",
    data=D11,
    engines=ALL_UPDATE,
)

q(
    qid="q119", module=MOD,
    title="Correcting a value",
    asks="Ex Libris was founded in 1921, not 1919. Change it.",
    how="DELETE and INSERT in one operation, sharing a WHERE clause. The "
        "WHERE runs once, its bindings feed both templates, and the DELETE "
        "half is applied before the INSERT half. Leaving the DELETE out is "
        "the commonest mistake in SPARQL Update, and it does not look like a "
        "mistake: the new value appears, and so does the old one.",
    diagram="""
    DELETE { ?shop bs:founded ?old }        <- the old triple, by variable
    INSERT { ?shop bs:founded "1921" }      <- the new one
    WHERE  { ?shop bs:founded ?old .        <- binds ?old, once
             FILTER( ?shop = bt:shop-ex-libris ) }

    with the DELETE:          without it:

      bs:founded 1921           bs:founded 1919
                                bs:founded 1921
                                ---------------
                                Two founding years, no error, and
                                a query that asks for one now
                                returns two rows.

    A property being single-valued is a claim your data makes, not
    a rule the store enforces. Nothing stops a second value
    arriving, which is what owl:FunctionalProperty is for -- it
    says what a reasoner may conclude, and still does not stop the
    insert.

    +----------------------------------------------------------+
    |  Order inside one operation: DELETE first, then INSERT.   |
    |  So a value can be replaced by one computed from itself.  |
    +----------------------------------------------------------+
    """,
    learn=[
        "DELETE/INSERT/WHERE is the workhorse. One WHERE, two templates, "
        "delete applied before insert.",
        "An INSERT with no matching DELETE leaves both values in place. "
        "Nothing warns you; the property simply has two.",
        "Bind the old value to a variable in the WHERE and delete it by "
        "variable, rather than naming what you think it is.",
    ],
    body="""DELETE { ?shop bs:founded ?old }
INSERT { ?shop bs:founded "1921"^^xsd:gYear }
WHERE  {
  ?shop      a          bs:Bookshop ;
             bs:founded ?old .
  FILTER( ?shop = bt:shop-ex-libris )
}""",
    verify="""SELECT ?name ?founded
WHERE {
  bt:shop-ex-libris rdfs:label ?name ;
                    bs:founded ?founded .
}
ORDER BY ?founded""",
    data=D11,
    engines=ALL_UPDATE,
)

q(
    qid="q120", module=MOD,
    title="Materialising what a path already knows",
    asks="Every shop is in a country by way of two or three bs:within hops. "
         "Write that down as one triple per shop.",
    how="INSERT ... WHERE is CONSTRUCT that keeps its output. The WHERE walks "
        "the path from module 05; the template records the answer. Afterwards "
        "the same question is a single triple pattern, which is faster to "
        "answer and easier for anything downstream to consume.",
    diagram="""
    what the path costs, every time it is asked:

      ?shop bs:locatedIn ?town .
      ?town bs:within+ ?country .            <- two or three hops,
      ?country a bs:Country .                   evaluated per shop

    what the update leaves behind:

      ?shop bs:inCountry ?country .          <- one hop

    +-------------+--------+
    | England     |     20 |
    | Scotland    |      9 |
    | Wales       |      4 |
    +-------------+--------+
                     33 shops, each in exactly one country

    This is materialisation, and it is a trade rather than a win:

      faster to query        the derived triples are now data,
      simpler downstream     and nothing keeps them true. Move a
                             shop to another town and bs:inCountry
                             still says the old country.

    So either re-run it after every change, or do not store it and
    pay the path cost at query time. What you must not do is store
    it and forget which of the two you chose.

    bs:inCountry is not in the vocabulary file. Derived shortcuts
    usually are not, which is another reason to keep them clearly
    separable -- a named graph is the usual answer, and module 08
    has the mechanism.
    """,
    learn=[
        "INSERT ... WHERE is a CONSTRUCT whose output is kept. Anything you "
        "can construct, you can materialise.",
        "Materialised triples are stale the moment the facts they came from "
        "change. Decide who re-runs them, and when.",
        "Keep derived triples separable from asserted ones -- a named graph is "
        "the cheapest way -- so they can be dropped and rebuilt.",
    ],
    body="""INSERT { ?shop bs:inCountry ?country }
WHERE {
  ?shop    a            bs:Bookshop ;
           bs:locatedIn ?town .
  ?town    bs:within+   ?country .
  ?country a            bs:Country .
}""",
    verify="""SELECT ?country (COUNT(?shop) AS ?shops)
WHERE {
  ?shop    bs:inCountry ?country .
  ?country rdfs:label   ?name .
  FILTER( LANG(?name) = "en" )
}
GROUP BY ?country
ORDER BY DESC(?shops) ?country""",
    data=D11,
    engines=ALL_UPDATE,
)

q(
    qid="q121", module=MOD,
    title="The migration, done in place",
    asks="Turn the 95 StockRecord nodes into RDF 1.2 annotations, and remove "
         "the old ones.",
    how="q86 built this graph with CONSTRUCT and left you holding it. Here the "
        "same transformation is applied to the store, and then a second "
        "operation removes what it replaced -- the half CONSTRUCT cannot do. "
        "Two operations separated by a semicolon, applied in order.",
    diagram="""
    operation 1     read the old shape, write the new one
    operation 2     delete the old shape

      INSERT { ... } WHERE { ?record a bs:StockRecord ; ... } ;
      DELETE WHERE   { ?record a bs:StockRecord ; ?p ?o }
                   ^
                   the semicolon. Operations run in order, and the
                   second sees what the first did -- which is why
                   the delete must come second, and why writing it
                   first quietly produces nothing at all.

    before                          after
    ------                          -----
    95 bs:StockRecord nodes         0
    0 bs:stocks triples             95
    0 reifiers                      95, each with copies and price

    Idempotence is what makes this survivable. The reifier IRI is
    derived from the record's own name, so a migration interrupted
    half way can simply be run again: the triples it already wrote
    are written again to no effect.

    +----------------------------------------------------------+
    |  Take a backup first. There is no transaction spanning    |
    |  the two operations on every engine, no undo, and no      |
    |  prompt. `holos backup` and Fuseki's tdb2.tdbbackup are   |
    |  the two this course uses.                                |
    +----------------------------------------------------------+
    """,
    learn=[
        "Several operations in one request, separated by ';', run in order, "
        "and each sees the effect of the last.",
        "Migrate then delete, in that order. The reverse loses the data the "
        "migration needed.",
        "Derive new IRIs from stable existing ones and the whole request "
        "becomes safe to re-run. That is worth more than it sounds at 3am.",
    ],
    body="""INSERT {
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
  BIND( IRI( REPLACE( STR(?record),
                      "/stock-", "/reifier-" ) ) AS ?reifier )
} ;

DELETE WHERE {
  ?record a  bs:StockRecord ;
          ?p ?o .
}""",
    verify="""SELECT ?shape (COUNT(*) AS ?n)
WHERE {
  { ?s a bs:StockRecord .          BIND( "old: StockRecord" AS ?shape ) }
  UNION
  { ?s bs:stocks ?w .              BIND( "new: bs:stocks"  AS ?shape ) }
  UNION
  { ?s rdf:reifies ?t .            BIND( "new: reifier"    AS ?shape ) }
}
GROUP BY ?shape
ORDER BY ?shape""",
    data=D11,
    engines=ALL_UPDATE,
    extra_prefixes=("rdf",),
)

q(
    qid="q122", module=MOD,
    title="Moving whole graphs about",
    asks="Copy one named graph, then drop another, without touching a single "
         "triple pattern.",
    how="Graph management is its own small language: LOAD, CLEAR, DROP, COPY, "
        "MOVE and ADD work on whole graphs at a time. They are far faster "
        "than the equivalent INSERT/DELETE, and they are how a staging graph "
        "gets promoted to a live one.",
    diagram="""
    COPY  <a> TO <b>     b is emptied, then a's contents put in it
    MOVE  <a> TO <b>     the same, and then a is dropped
    ADD   <a> TO <b>     a's contents added; b keeps what it had
    DROP  GRAPH <a>      the graph and its name, gone
    CLEAR GRAPH <a>      emptied, but the name remains

    the difference that catches people:

      COPY  destination emptied first     ADD  destination kept

    the trail dataset, in graphs:

      bt:graph-places     places, councils, regions, countries
      bt:graph-shops      the bookshops
      bt:graph-people     authors and publishers
      bt:graph-events     readings, launches, fairs
      ... and six more

    after COPY bt:graph-shops TO bt:graph-shops-backup
      and DROP GRAPH bt:graph-events :

      shops-backup holds exactly what shops holds
      events is gone -- not empty, gone

    LOAD <http://somewhere/data.ttl> INTO GRAPH <g> fetches over
    the network, and it is the same exposure as SERVICE in q108:
    a URL chosen by whoever wrote the request, fetched by your
    server. HOLOS refuses remote LOAD for that reason.
    """,
    learn=[
        "COPY, MOVE, ADD, DROP and CLEAR act on whole graphs and are much "
        "cheaper than the pattern-based equivalent.",
        "COPY and MOVE empty the destination first; ADD does not. DROP removes "
        "the graph, CLEAR only empties it.",
        "LOAD fetches a URL of the requester's choosing. Treat it like "
        "SERVICE, and expect a careful engine to refuse it.",
    ],
    body="""COPY bt:graph-shops TO bt:graph-shops-backup ;

DROP GRAPH bt:graph-events""",
    verify="""SELECT ?graph (COUNT(*) AS ?triples)
WHERE {
  GRAPH ?graph { ?s ?p ?o }
}
GROUP BY ?graph
ORDER BY ?graph""",
    data=DTRIG,
    engines=(HOLOS, FUSEKI),
    notes="Fuseki and HOLOS. Comunica's update handling of whole-graph "
          "operations over an in-memory store is not something this course "
          "relies on, and the editor cannot run an update at all.",
)

q(
    qid="q123", module=MOD,
    title="The update that empties the store",
    asks="What does one careless pattern cost?",
    how="Everything. DELETE WHERE with three variables matches every triple "
        "in the default graph and removes all of them. There is no "
        "confirmation, no transaction to roll back on most setups, and no "
        "undo. It is worth running once, deliberately, on a copy -- the point "
        "lands better than a warning does.",
    diagram="""
    DELETE WHERE { ?s ?p ?o }

      4826 triples  ->  0

    +----------------------------------------------------------+
    |  no prompt   no confirmation   no undo   no error         |
    |  the operation succeeds. That is the problem with it.     |
    +----------------------------------------------------------+

    The three habits that prevent it:

      1  Write the WHERE as a SELECT first and look at the rows.
         Every deletion in this module was written that way.

      2  Keep the endpoint read-only unless it needs to write.
         Fuseki serves /query and /update separately, and most
         deployments should never expose the second one.

      3  Back up before a migration, not after noticing.
             holos backup --store DIR --to DIR
             java -cp ... tdb2.tdbbackup --loc DIR

    And a fourth, for the query itself: LIMIT does nothing here.
    There is no such thing as deleting the first ten matches.

    A note on what "the default graph" means. This removes the
    default graph only; named graphs survive, which makes the
    damage look smaller than it is until somebody checks. DROP ALL
    is the one that takes everything.
    """,
    learn=[
        "DELETE WHERE { ?s ?p ?o } empties the default graph, succeeds "
        "quietly, and cannot be undone.",
        "Write every deletion as a SELECT first. It costs one run and it is "
        "the only real safeguard.",
        "Separate read and write endpoints, and back up before migrating. An "
        "update endpoint open to the internet is an open door.",
    ],
    body="""DELETE WHERE {
  ?s ?p ?o .
}""",
    verify="""SELECT (COUNT(*) AS ?triplesLeft)
WHERE {
  ?s ?p ?o .
}""",
    data=D11,
    engines=ALL_UPDATE,
)
