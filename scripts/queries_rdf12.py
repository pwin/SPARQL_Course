# -*- coding: utf-8 -*-
"""Modules 11-12: SPARQL 1.2 and RDF 1.2, then the challenges."""

from querycat import q, D11, D12, DFULL, ALL, EDITOR, HOLOS, FUSEKI

# ===========================================================================
# 11  SPARQL 1.2 and RDF 1.2
# ===========================================================================

q(
    qid="q61", module="11-sparql-1-2",
    title="Who says the shop opened when",
    asks="The founding dates are disputed. Who claims what, and how much do "
         "we trust them?",
    how="RDF 1.2 lets a statement be annotated with further statements about "
        "it. In the query, {| ... |} after a triple pattern matches those "
        "annotations, binding the variables inside. The base triple and its "
        "annotation come back in one row, with no intermediate node to invent "
        "or to remember.",
    diagram="""
    in the data:

      bt:shop-ex-libris bs:founded 1919
          {| bs:claimedBy bt:source-national-register ;
             bs:confidence 0.99 |} .
      bt:shop-ex-libris bs:founded 1921
          {| bs:claimedBy bt:source-local-paper ;
             bs:confidence 0.40 |} .

    in the query, the same shape:

      ?shop bs:founded ?year {| bs:claimedBy ?src ; bs:confidence ?c |} .
            --------+-------  -----------------+-------------------
             the statement        what is said ABOUT the statement

    +-------------+------+-------------------+------+
    | Ex Libris   | 1919 | national-register | 0.99 |
    | Ex Libris   | 1921 | local paper       | 0.40 |
    +-------------+------+-------------------+------+

    Both claims are in the graph.  Neither is privileged.  Deciding
    between them is the query's job, not the data's -- see q63.
    """,
    learn=[
        "{| ... |} in a query matches annotations on the triple pattern it "
        "follows.",
        "A dataset can hold two contradictory claims without being broken, as "
        "long as each is attributed.",
        "The syntax is symmetrical: the same {| |} that writes an annotation "
        "in Turtle reads it in SPARQL.",
    ],
    body="""SELECT ?shopName ?year ?sourceName ?confidence
WHERE {
  ?shop bs:founded ?year {| bs:claimedBy ?source ; bs:confidence ?confidence |} .
  ?shop   rdfs:label ?shopName .
  ?source rdfs:label ?sourceName .
}
ORDER BY ?shopName DESC(?confidence)""",
    data=D12,
)

q(
    qid="q62", module="11-sparql-1-2",
    title="Find the contradictions",
    asks="Which shops have two different founding dates on record?",
    how="Join the annotated pattern to itself and keep the pairs where the "
        "years differ. The self-join is on the shop; the inequality does the "
        "rest. The STR comparison on the sources keeps each disagreeing pair "
        "once rather than twice.",
    diagram="""
    ?shop bs:founded ?yearA {| bs:claimedBy ?srcA |} .
    ?shop bs:founded ?yearB {| bs:claimedBy ?srcB |} .
      ^                ^
      +-- same shop ---+ different years

    FILTER( STR(?yearA) != STR(?yearB) )   <- a genuine contradiction
    FILTER( STR(?srcA) < STR(?srcB) ) <- report each pair once

    Ex Libris     1919 vs 1921
    Endpapers     1949 vs 1946
    Candlemas   1931 vs 1928
    Castle Steps  1962 vs 1965

    Gutter and Gilt does NOT appear: two sources, same year, so
    there is no contradiction -- there is corroboration.
    """,
    learn=[
        "An annotated pattern joins to itself exactly as a plain one does.",
        "Comparing the source IRIs as strings is the standard way to emit an "
        "unordered pair once instead of twice.",
        "Recording disagreement is more useful than resolving it at load "
        "time, because the right resolution depends on the question.",
        "STR() around both years, and for the same reason as q07: comparing "
        "two xsd:gYear values directly returns nothing at all on two of the "
        "three engines. Written the obvious way, this query reports no "
        "contradictions and looks like good news.",
    ],
    body="""SELECT ?shopName ?yearA ?sourceA ?yearB ?sourceB
WHERE {
  ?shop bs:founded ?yearA {| bs:claimedBy ?srcA |} .
  ?shop bs:founded ?yearB {| bs:claimedBy ?srcB |} .
  FILTER( STR(?yearA) != STR(?yearB) )
  FILTER( STR(?srcA) < STR(?srcB) )
  ?shop rdfs:label ?shopName .
  ?srcA rdfs:label ?sourceA .
  ?srcB rdfs:label ?sourceB .
}
ORDER BY ?shopName""",
    data=D12,
)

q(
    qid="q63", module="11-sparql-1-2",
    title="Believe the best source",
    asks="For each shop, which founding date has the strongest backing?",
    how="A sub-query finds the highest confidence attached to any founding "
        "claim about each shop; the outer query re-joins to recover the year "
        "that claim asserted. It's exactly the 'group, then join back' shape "
        "from q38, applied to annotations rather than to events.",
    diagram="""
    step 1 -- best confidence per shop
      SELECT ?shop (MAX(?c) AS ?best)
      WHERE { ?shop bs:founded ?y {| bs:confidence ?c |} }
      GROUP BY ?shop
                        |
    step 2 -- which claim had it?
      ?shop bs:founded ?year {| bs:confidence ?best |} .
                                              ----+
                              the join condition -+

    +--------------+------+------+-------------------+
    | Ex Libris    | 1919 | 0.99 | national register |
    | Endpapers    | 1949 | 0.97 | national register |
    | Candlemas  | 1931 | 0.98 | national register |
    | Castle Steps | 1962 | 0.85 | trail guide 2024  |
    +--------------+------+------+-------------------+

    The graph keeps every claim.  The query chooses.  Change the
    policy -- most recent, most sources, highest confidence -- and
    only the query changes.
    """,
    learn=[
        "Annotations turn 'which fact is true?' from a data-modelling problem "
        "into a query.",
        "Keep the conflicting claims and resolve them at query time; different "
        "questions deserve different resolutions.",
        "The aggregate-then-rejoin pattern works on annotation values exactly "
        "as it does on ordinary ones.",
    ],
    body="""SELECT ?shopName ?year ?confidence ?sourceName
WHERE {
  {
    SELECT ?shop (MAX(?c) AS ?confidence)
    WHERE { ?shop bs:founded ?y {| bs:confidence ?c |} }
    GROUP BY ?shop
  }
  ?shop bs:founded ?year {| bs:claimedBy ?source ; bs:confidence ?confidence |} .
  ?shop   rdfs:label ?shopName .
  ?source rdfs:label ?sourceName .
}
ORDER BY ?shopName""",
    data=D12,
)

q(
    qid="q64", module="11-sparql-1-2",
    title="What the annotation syntax really is",
    asks="Strip away the sugar: what triples does {| ... |} actually create?",
    how="An annotation is shorthand. Writing `s p o {| a b |}` asserts the "
        "base triple, mints a reifier, links it to a triple term with "
        "rdf:reifies, and hangs the annotation off the reifier. This query "
        "asks for the reifier directly, which is what the shorthand was "
        "hiding.",
    diagram="""
    what you write:

        bt:shop-ex-libris bs:founded 1919 {| bs:confidence 0.99 |} .

    what the parser produces -- four things, three of them triples:

        bt:shop-ex-libris bs:founded 1919 .          <- the base triple
        _:r rdf:reifies <<( bt:shop-ex-libris bs:founded 1919 )>> .
        _:r bs:confidence 0.99 .
            ^                ^
            |                +-- an ordinary triple about _:r
            +-- _:r is the "reifier": a name for the statement

        <<( s p o )>> is a TRIPLE TERM: a single RDF term whose
        value is a triple.  It may only appear as an object.

    So the annotation syntax is not a new kind of data.  It is
    ordinary triples, with a term type for talking about statements.
    """,
    learn=[
        "{| ... |} is syntactic sugar over rdf:reifies plus a triple term.",
        "A triple term <<( s p o )>> is one RDF term, legal only in object "
        "position. This is the main thing RDF 1.2 changed from the earlier "
        "RDF-star drafts.",
        "The base triple is still asserted. Annotating a statement doesn't "
        "make it hypothetical.",
        "The reifier is usually a blank node, so never sort or page on it. "
        "This query filters on the statement's subject and predicate instead, "
        "using the SPARQL 1.2 term functions from q66.",
    ],
    body="""SELECT ?statement ?p ?o
WHERE {
  ?reifier rdf:reifies ?statement ;
           ?p ?o .
  FILTER( ?p != rdf:reifies )

  # Narrow to the two rival claims about one shop, so the expansion is
  # small enough to read.  Ordering by ?reifier would not work: reifiers
  # are blank nodes, and no two engines sort those alike.
  FILTER( SUBJECT(?statement)   = bt:shop-ex-libris )
  FILTER( PREDICATE(?statement) = bs:founded )
}
ORDER BY ?p ?o""",
    data=D12,
)

q(
    qid="q65", module="11-sparql-1-2",
    title="A statement as the object of a statement",
    asks="Which claims does the National Register explicitly reject?",
    how="A triple term can be the object of an ordinary triple, which is how "
        "you point at a statement without asserting it. bs:disputes does "
        "exactly that: the disputed statement appears inside <<( ... )>> and "
        "isn't thereby claimed to be true.",
    diagram="""
    bt:source-national-register bs:disputes
        <<( bt:shop-ex-libris bs:founded "1921"^^xsd:gYear )>> .

    +---------------------------------------------------+
    |  the OBJECT of this triple is itself a triple      |
    |                                                    |
    |  and crucially, it is NOT asserted:                |
    |  saying "X disputes S" does not put S in the graph |
    +---------------------------------------------------+

    contrast with the annotation syntax, which DOES assert:

      s p o {| ... |}        asserts s p o
      ?x bs:disputes <<(s p o)>>   does not

    matching one in a query, with variables inside:

      ?source bs:disputes <<( ?shop ?prop ?value )>>

    binds ?shop, ?prop and ?value from inside the triple term.
    """,
    learn=[
        "A triple term names a statement without asserting it -- the thing "
        "reification was always trying to do.",
        "Triple terms may appear in a query pattern with variables inside, "
        "and those variables bind.",
        "Use annotation syntax when the statement is true and you want to say "
        "more about it; use a bare triple term when it may not be.",
    ],
    body="""SELECT ?sourceName ?shopName ?disputedYear
WHERE {
  ?source bs:disputes <<( ?shop bs:founded ?disputedYear )>> .
  ?source rdfs:label ?sourceName .
  ?shop   rdfs:label ?shopName .
}
ORDER BY ?shopName""",
    data=D12,
)

q(
    qid="q66", module="11-sparql-1-2",
    title="Taking a triple term apart",
    asks="Pull the subject, predicate and object out of every disputed "
         "statement.",
    how="SPARQL 1.2 adds functions over triple terms: isTRIPLE tests for one, "
        "and SUBJECT, PREDICATE and OBJECT take it apart. Together they let a "
        "query reason about statements it did not know the shape of in "
        "advance.",
    diagram="""
    ?t = <<( bt:shop-ex-libris bs:founded "1921"^^xsd:gYear )>>

        isTRIPLE(?t)     -->  true
        SUBJECT(?t)      -->  bt:shop-ex-libris
        PREDICATE(?t)    -->  bs:founded
        OBJECT(?t)       -->  "1921"^^xsd:gYear

    and in the other direction:

        TRIPLE(?s, ?p, ?o)  -->  a new triple term

    +----------------------------------------------+
    | these work on ANY triple term, whatever its  |
    | shape -- so a query can inspect statements   |
    | whose predicate it does not know             |
    +----------------------------------------------+

    Verified on all three engines: isTRIPLE, SUBJECT, PREDICATE,
    OBJECT and TRIPLE all evaluate.  VERSION() does not -- Jena has
    it, the other two do not.
    """,
    learn=[
        "isTRIPLE, SUBJECT, PREDICATE, OBJECT and TRIPLE are the SPARQL 1.2 "
        "term functions.",
        "They make generic, shape-agnostic queries over statements possible.",
        "Test with isTRIPLE before decomposing: SUBJECT of a non-triple is an "
        "error, and an error in a FILTER quietly drops the row.",
    ],
    body="""SELECT ?sourceName ?subject ?predicate ?object
WHERE {
  ?source bs:disputes ?t .
  FILTER( isTRIPLE(?t) )
  BIND( SUBJECT(?t)   AS ?subject )
  BIND( PREDICATE(?t) AS ?predicate )
  BIND( OBJECT(?t)    AS ?object )
  ?source rdfs:label ?sourceName .
}
ORDER BY ?subject""",
    data=D12,
)

q(
    qid="q67", module="11-sparql-1-2",
    title="Text that knows which way it runs",
    asks="Which labels are written right to left?",
    how="RDF 1.2 adds a base direction to language-tagged strings, written "
        "@ar--rtl. LANGDIR returns it, hasLANGDIR tests for it, and STRLANGDIR "
        "constructs one. Without the direction, a renderer has to guess where "
        "to put a trailing bracket -- and it guesses wrong often enough to "
        "matter.",
    diagram="""
    "البحر المظلم"@ar--rtl
     ------+-----  -+- -+-
           |        |   +-- base direction: rtl
           |        +------ language: Arabic
           +--------------- the text

    LANGDIR(?l)      -->  "rtl"
    hasLANGDIR(?l)   -->  true   (false for plain @ar)
    LANG(?l)         -->  "ar"   (unchanged from 1.1)
    STRLANGDIR("hi","en","ltr")  -->  "hi"@en--ltr

    why it matters:

      title (2019)      with direction, the bracket is placed
      (2019) title      without it, the renderer may guess wrongly

    A language tag says how to pronounce it.  A direction says how
    to lay it out.  They are different questions.
    """,
    learn=[
        "@lang--dir attaches a base direction to a literal; LANGDIR reads it.",
        "hasLANGDIR distinguishes a directional literal from a plain "
        "language-tagged one, which matters because most data has neither.",
        "Direction is a rendering fact, not a linguistic one, and RDF 1.1 had "
        "nowhere to put it.",
    ],
    body="""SELECT ?label ?language ?direction
WHERE {
  ?thing rdfs:label ?label .
  FILTER( isLITERAL(?label) && hasLANGDIR(?label) )
  BIND( LANG(?label)    AS ?language )
  BIND( LANGDIR(?label) AS ?direction )
}
ORDER BY ?language ?label""",
    data=D12,
)

q(
    qid="q68", module="11-sparql-1-2",
    title="The same fact, modelled twice",
    asks="Stock levels are in this dataset twice over -- once the RDF 1.1 way "
         "and once the 1.2 way. Compare them.",
    how="The 1.1 model invents a bs:StockRecord node to carry copies and "
        "price. The 1.2 model annotates the bs:stocks link directly. Both "
        "answer the question; the query shows what each costs to write, and "
        "confirms they agree.",
    diagram="""
    RDF 1.1 -- invent a node                RDF 1.2 -- annotate the link

    bt:stock-inkwell--the-book-town         bt:shop-inkwell
      a bs:StockRecord ;                        bs:stocks bt:book-the-book-town
      bs:atShop     bt:shop-inkwell ;           {| bs:copies 12 ;
      bs:ofWork     bt:book-... ;                  bs:shelfPrice 9.99 |} .
      bs:copies     12 ;
      bs:shelfPrice 9.99 .

    5 triples, 1 invented IRI                3 triples, 1 blank reifier
    the link is implicit                     the link is a real triple
    every query goes via the record          simple queries stay simple

    querying them:

      ?r bs:atShop ?shop ;                   ?shop bs:stocks ?work
         bs:ofWork ?work ;                       {| bs:copies ?n |} .
         bs:copies ?n .

    Neither is wrong.  The 1.1 form is better when the relationship
    has its own identity and lifecycle; the 1.2 form is better when
    you just want to say a bit more about a link that already exists.
    """,
    learn=[
        "The n-ary relation pattern -- invent a node -- is how RDF 1.1 says "
        "anything about a relationship, and it works.",
        "RDF 1.2 annotations remove the invented node, keeping the "
        "relationship queryable as a plain triple.",
        "Model with an intermediate node when the relationship is a thing in "
        "its own right; annotate when it's only a link you want to qualify.",
    ],
    body="""SELECT ?shopName ?title ?copiesVia11 ?copiesVia12
WHERE {
  ?record a         bs:StockRecord ;
          bs:atShop ?shop ;
          bs:ofWork ?work ;
          bs:copies ?copiesVia11 .
  ?shop bs:stocks ?work {| bs:copies ?copiesVia12 |} .
  ?shop rdfs:label ?shopName .
  ?work rdfs:label ?title .
}
ORDER BY ?shopName ?title""",
    data=D12,
)

# ===========================================================================
# 12  Challenges
# ===========================================================================

q(
    qid="q69", module="14-challenges",
    title="Whose influence reaches furthest",
    asks="Which author has the largest number of literary descendants?",
    how="Reachability plus aggregation. The inverse path ^bs:influencedBy+ "
        "runs down the influence graph from an author to everyone who "
        "inherits from them at any remove; counting the distinct endpoints "
        "ranks the authors. The two-cycle in the data means some authors "
        "appear among their own descendants, which is correct and worth "
        "noticing.",
    diagram="""
    influence points BACKWARDS -- from the later author to the earlier:

        dilys-tremain  --bs:influencedBy-->  cerys-lloyd

    so "who did X influence?" reverses it:

        ?ancestor  ^bs:influencedBy+  ?descendant
                   ---------+-------
                   one or more hops, downstream

    +----------------+-------------+
    | rhona-blackwood| many        |   the roots of the graph
    | maud-ellery    | many        |   reach almost everyone
    | ...            |             |
    | dilys-tremain  | 0           |   the leaves reach nobody
    +----------------+-------------+

    Watch for the mutual pair: tam-brodie and kirsty-lammond each
    influenced the other, so each is among their own descendants.
    COUNT(DISTINCT ?d) still terminates -- paths are cycle-safe.
    """,
    learn=[
        "Aggregating over a path result is how you measure a graph rather than "
        "just traverse it.",
        "Reversing the path direction turns 'my ancestors' into 'my "
        "descendants' without touching the data.",
        "COUNT(DISTINCT ...) matters here: several routes may reach the same "
        "descendant, and you want people, not paths.",
    ],
    body="""SELECT ?authorName (COUNT(DISTINCT ?descendant) AS ?reach)
WHERE {
  ?author a bs:Author ; rdfs:label ?authorName .
  OPTIONAL { ?author ^bs:influencedBy+ ?descendant . }
}
GROUP BY ?author ?authorName
ORDER BY DESC(?reach) ?authorName
LIMIT 15""",
)

q(
    qid="q70", module="14-challenges",
    title="A weekend in one county",
    asks="For every council area, what's there to do: how many shops, how "
         "many events, and what do the shops specialise in?",
    how="Four techniques in one query. A property path climbs from shop to "
        "council area whatever the depth; a sub-query counts events without "
        "multiplying the shop count; GROUP_CONCAT lists the specialisms; and "
        "OPTIONAL keeps the council areas that have no shops at all.",
    diagram="""
    the trap this query avoids:

      joining shops AND events in one pattern multiplies them --
      a council with 3 shops and 8 events yields 24 rows, and
      COUNT(DISTINCT ?shop) is then the only thing that still works

    so events are counted in their own sub-query, per council:

    + outer ------------------------------------+
    |  ?shop bs:locatedIn/bs:within+ ?council   |
    |  GROUP BY ?council                        |
    |      COUNT(DISTINCT ?shop)                |
    |      GROUP_CONCAT(?specialism)            |
    |                                           |
    |  + inner: events per council -----------+ |
    |  | ?e bs:heldAt ?s .                    | |
    |  | ?s bs:locatedIn/bs:within+ ?council  | |
    |  | GROUP BY ?council                    | |
    |  +--------------------------------------+ |
    +-------------------------------------------+

    Counting two different things per group almost always means two
    sub-queries.  One join cannot serve both.
    """,
    learn=[
        "Counting two unrelated things per group needs two aggregations, not "
        "one join.",
        "A join that multiplies rows corrupts every aggregate over it except "
        "COUNT(DISTINCT).",
        "Build queries like this one piece at a time, checking the row count "
        "after each addition.",
    ],
    notes="engines-differ: the order of the specialisms inside each "
          "GROUP_CONCAT is unspecified, and the three engines order them "
          "differently. The counts and the membership agree exactly. Same "
          "caveat as q24.",
    body="""SELECT ?councilName ?shops ?events ?specialisms
WHERE {
  {
    SELECT ?council (COUNT(DISTINCT ?shop) AS ?shops)
           (GROUP_CONCAT(DISTINCT ?genreName; SEPARATOR=", ") AS ?specialisms)
    WHERE {
      ?shop a bs:Bookshop ;
            bs:locatedIn/bs:within+ ?council ;
            bs:specialises ?genre .
      ?council a bs:CouncilArea .
      ?genre skos:prefLabel ?genreName .
      FILTER( LANG(?genreName) = "en" )
    }
    GROUP BY ?council
  }
  OPTIONAL {
    SELECT ?council (COUNT(?e) AS ?events)
    WHERE {
      ?e bs:heldAt ?s .
      ?s bs:locatedIn/bs:within+ ?council .
      ?council a bs:CouncilArea .
    }
    GROUP BY ?council
  }
  ?council rdfs:label ?councilName .
}
ORDER BY DESC(?shops) ?councilName""",
)

q(
    qid="q71", module="14-challenges",
    title="The gaps in the catalogue",
    asks="Which genres does the trail specialise in but barely stock, and "
         "which does it stock without anyone specialising?",
    how="Two sets, compared. One sub-query counts the shops that name each "
        "genre as their specialism; another counts the works filed under it "
        "or anything narrower. A full outer comparison isn't available in "
        "SPARQL, so a UNION of the genres from both sides gives the key set, "
        "and OPTIONAL fills in whichever side is missing.",
    diagram="""
    SPARQL has no FULL OUTER JOIN.  Build one:

    step 1 -- every genre that appears on either side
        { ?g ^bs:specialises ?anyShop }      shops' specialisms
        UNION
        { ?w bs:genre/skos:broader* ?g }     genres of works

    step 2 -- OPTIONAL sub-query for each count

        ?g --+-- OPTIONAL { shops specialising  } --> ?shops
             +-- OPTIONAL { works in this genre } --> ?works

    step 3 -- COALESCE turns "no match" into zero

        COALESCE(?shops, 0)

    +-------------------+-------+-------+
    | genre             | shops | works |
    +-------------------+-------+-------+
    | mountaineering    |   1   |   2   |   thin
    | climate-fiction   |   0   |   3   |   stocked, nobody's speciality
    | classics          |   1   |   0   |   claimed, nothing filed
    +-------------------+-------+-------+

    COALESCE is the tool for turning absence into a usable value.
    """,
    learn=[
        "SPARQL has no full outer join; UNION for the keys plus OPTIONAL for "
        "the values is how you build one.",
        "COALESCE(?x, 0) converts an unbound value into something arithmetic "
        "and ORDER BY can use.",
        "skos:broader* on the works side means a book filed under Tartan Noir "
        "counts towards Crime Fiction too.",
    ],
    body="""SELECT ?genreName (COALESCE(?shops, 0) AS ?specialists)
       (COALESCE(?works, 0) AS ?titles)
WHERE {
  { ?g ^bs:specialises ?someShop . }
  UNION
  { ?someWork bs:genre ?g . }
  ?g skos:prefLabel ?genreName .
  FILTER( LANG(?genreName) = "en" )

  OPTIONAL {
    SELECT ?g (COUNT(DISTINCT ?shop) AS ?shops)
    WHERE { ?shop bs:specialises ?g . }
    GROUP BY ?g
  }
  OPTIONAL {
    SELECT ?g (COUNT(DISTINCT ?work) AS ?works)
    WHERE { ?work bs:genre/skos:broader* ?g . }
    GROUP BY ?g
  }
}
ORDER BY ?specialists DESC(?titles) ?genreName""",
)

q(
    qid="q72", module="14-challenges",
    title="Where should the next shop go",
    asks="Rank the shopless towns by how underserved they are: population, "
         "and distance to the nearest existing shop.",
    how="Negation finds the towns without a shop; a sub-query finds each "
        "one's distance to the nearest shop on the National Grid; and a "
        "computed score combines the two. Nothing here's new -- it's q16, "
        "q54 and a BIND, assembled.",
    diagram="""
    + towns with no shop -------------+   q16
    |  FILTER NOT EXISTS {            |
    |    ?s bs:locatedIn ?town }      |
    +------------+--------------------+
                 |
    + nearest shop, squared metres ---+   q54
    |  MIN( (dx)^2 + (dy)^2 )         |
    +------------+--------------------+
                 |
    + combine ------------------------+
    |  score = population x km        |
    |          ---+----    -+-        |
    |        demand     distance      |
    +---------------------------------+

    A bigger town further from any shop scores higher.  The formula
    is a judgement, not a fact -- which is exactly why it belongs in
    the query and not in the data.
    """,
    learn=[
        "Complex questions are assemblies of simple ones. Write and test the "
        "parts separately.",
        "Scoring formulas belong in queries: they encode a policy, and "
        "policies change more often than facts.",
        "State the units. A score mixing people and kilometres is meaningful "
        "only for ranking, and should never be reported as a quantity.",
    ],
    body="""SELECT ?townName ?population ?nearestKm ?score
WHERE {
  ?town a bs:Settlement ;
        rdfs:label ?townName ;
        bs:population ?population ;
        bs:easting ?te ; bs:northing ?tn .
  FILTER( LANG(?townName) = "en" )
  FILTER NOT EXISTS { ?anyShop bs:locatedIn ?town . }
  {
    SELECT ?town (MIN(?d2) AS ?closest)
    WHERE {
      ?town a bs:Settlement ; bs:easting ?e1 ; bs:northing ?n1 .
      ?shop a bs:Bookshop  ; bs:easting ?e2 ; bs:northing ?n2 .
      BIND( (?e2 - ?e1) * (?e2 - ?e1) + (?n2 - ?n1) * (?n2 - ?n1) AS ?d2 )
    }
    GROUP BY ?town
  }
  BIND( ROUND(?closest / 100000) / 10 AS ?nearestKm )
  BIND( ROUND(?population * ?nearestKm / 1000) AS ?score )
}
ORDER BY DESC(?score)""",
    data=DFULL,
)

q(
    qid="q73", module="14-challenges",
    title="A reading list from one shop",
    asks="Starting at The Sea Margin, build a reading list: everything it "
         "stocks, plus everything by the authors who influenced those books' "
         "authors.",
    how="Two hops of a different kind, joined. From the shop to its stock is "
        "one link; from a book to its author's influences is a path; from "
        "those authors back to their works is an inverse. UNION keeps the "
        "shop's own stock and the wider recommendations in one list, labelled "
        "by where each came from.",
    diagram="""
    branch 1 -- what the shop actually has

      bt:shop-sea-margin --bs:stocks--> ?work

    branch 2 -- what its authors were reading

      bt:shop-sea-margin --bs:stocks--> ?stocked
                                          | bs:author
                                          v
                                       ?author
                                          | bs:influencedBy+
                                          v
                                       ?ancestor
                                          | ^bs:author
                                          v
                                        ?work

    +--------------------+------------------+
    | The Selkie Ledger  | in stock         |
    | An Lochan          | in stock         |
    | The Shieling       | recommended      |
    | Cold Harbour       | recommended      |
    +--------------------+------------------+

    A recommendation engine in fourteen lines, and no machine
    learning anywhere near it.
    """,
    learn=[
        "Chaining a forward link, a transitive path and an inverse link is the "
        "shape of most graph recommendations.",
        "UNION with a labelling BIND keeps provenance in the result: the "
        "reader can see why each row is there.",
        "This is what a graph database is for. The equivalent in SQL needs a "
        "recursive CTE and a good deal more typing.",
    ],
    body="""SELECT DISTINCT ?title ?authorName ?why
WHERE {
  {
    bt:shop-sea-margin bs:stocks ?work .
    BIND( "in stock" AS ?why )
  }
  UNION
  {
    bt:shop-sea-margin bs:stocks ?stocked .
    ?stocked bs:author ?author .
    ?author bs:influencedBy+ ?ancestor .
    ?work bs:author ?ancestor .
    BIND( "recommended: an influence on this shop's authors" AS ?why )
  }
  ?work   rdfs:label ?title .
  ?work   bs:author  ?writer .
  ?writer rdfs:label ?authorName .
}
ORDER BY ?why ?authorName ?title""",
)

q(
    qid="q74", module="14-challenges",
    title="A trust report",
    asks="Produce a report of every disputed fact in the dataset, the rival "
         "claims, and which source the evidence favours.",
    how="The capstone. Annotations supply the claims, a sub-query finds the "
        "best-supported one, GROUP_CONCAT lists the rivals, and the result is "
        "a single table a human could act on. It uses most of the course at "
        "once, which is the point.",
    diagram="""
    for every shop with more than one founding claim:

      + all claims ----------------------------+
      | ?shop bs:founded ?y {| claimedBy ?s ;  |
      |                        confidence ?c |}|
      +------------+---------------------------+
                   |
      + best per shop ---------+  + list them all ----------+
      | MAX(?c) -> ?best       |  | GROUP_CONCAT(?y)        |
      +------------+-----------+  +------------+------------+
                   +-----------+---------------+
                               v
    +--------------+----------+----------+-------------------+
    | shop         | claims   | accepted | on the word of    |
    +--------------+----------+----------+-------------------+
    | Ex Libris    |1919,1921 |   1919   | national register |
    | Endpapers    |1946,1949 |   1949   | national register |
    | Candlemas  |1928,1931 |   1931   | national register |
    | Castle Steps |1962,1965 |   1962   | trail guide 2024  |
    +--------------+----------+----------+-------------------+

    HAVING(COUNT(DISTINCT ?y) > 1) keeps only the genuine
    disagreements: shops whose sources agree are not news.
    """,
    learn=[
        "RDF 1.2 annotations plus ordinary SPARQL aggregation produce real "
        "provenance reporting, with no special machinery.",
        "HAVING on a count is how you keep only the interesting groups.",
        "The dataset stores what was claimed; the query decides what to "
        "believe. Keeping those separate is the whole argument for "
        "statement-level annotation.",
    ],
    notes="engines-differ: the years inside the GROUP_CONCAT come out in "
          "different orders on the three engines, and SAMPLE is explicitly "
          "allowed to pick any value from its group. The shops listed and the "
          "year accepted for each are identical everywhere.",
    body="""SELECT ?shopName
       (GROUP_CONCAT(DISTINCT STR(?year); SEPARATOR=", ") AS ?claimedYears)
       (SAMPLE(?accepted) AS ?accept)
       (SAMPLE(?acceptedSource) AS ?onTheWordOf)
WHERE {
  ?shop bs:founded ?year {| bs:confidence ?c |} .
  ?shop rdfs:label ?shopName .
  {
    SELECT ?shop (MAX(?c2) AS ?bestConfidence)
    WHERE { ?shop bs:founded ?y2 {| bs:confidence ?c2 |} }
    GROUP BY ?shop
  }
  ?shop bs:founded ?accepted
        {| bs:confidence ?bestConfidence ; bs:claimedBy ?src |} .
  ?src rdfs:label ?acceptedSource .
}
GROUP BY ?shop ?shopName
HAVING( COUNT(DISTINCT ?year) > 1 )
ORDER BY ?shopName""",
    data=D12,
)
