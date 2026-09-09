# -*- coding: utf-8 -*-
"""Module 16: blank nodes.

Blank nodes turn up everywhere in RDF and are the thing beginners are most
often quietly wrong about.  The dataset has twenty-three of them, all in the
vocabulary file, and they are enough to show every important behaviour:
what a blank node is, why you cannot point at one from outside the query
that found it, how RDF collections are built out of them, and how to give
one a name when you need to.

Reproduce every number quoted here with:

    python scripts/check_queries.py q109 q110 q111 q112 q113 q114 q115
"""

from querycat import q, D11, ALL, EDITOR, HOLOS, FUSEKI

MOD = "16-blank-nodes"

q(
    qid="q109", module=MOD,
    title="Where the blank nodes are",
    asks="This dataset has blank nodes in it. Which predicates do they carry?",
    how="isBLANK is the test. Grouping the triples whose subject is blank by "
        "predicate gives a census: it says what the blank nodes are being used "
        "for without needing to name any of them.",
    diagram="""
    ?b ?p ?o .  FILTER( isBLANK(?b) )
    --                  ---------
    |                   keeps the rows whose subject has no IRI
    '-- binds to a blank node, but you can never write its name

    the census, all four thousand-odd triples in:

      rdf:first        19    the list cells that hold a member
      rdf:rest         19    the cells that point to the next one
      rdf:type          4    the two disjointness axioms
                             plus two anonymous owl:Class nodes
      owl:members       2
      owl:unionOf       2
                     ----
                       46 triples, on 23 blank nodes

    All of them are in 01-vocabulary.ttl. That is typical: blank
    nodes cluster in schema and in structures -- lists, restrictions,
    addresses, SHACL shapes -- and are rare in plain instance data,
    where things deserve names.

    isIRI, isLITERAL and isNUMERIC are the other three tests, and
    they partition every RDF term between them.
    """,
    learn=[
        "isBLANK(?x) is true when a term is a blank node -- a node with no IRI, "
        "which exists only inside the graph that contains it.",
        "A census by predicate is the quickest way to find out what the blank "
        "nodes in an unfamiliar dataset are doing.",
        "Blank nodes cluster in structure: lists, restrictions, shapes. Data "
        "about real things usually has IRIs, and should.",
    ],
    body="""SELECT ?p (COUNT(*) AS ?triples)
WHERE {
  ?b ?p ?o .
  FILTER( isBLANK(?b) )
}
GROUP BY ?p
ORDER BY DESC(?triples) ?p""",
    data=D11,
)

q(
    qid="q110", module=MOD,
    title="The label in your results is not a name",
    asks="A previous query returned _:b0. What happens if you put _:b0 back "
         "into a query?",
    how="Nothing you would want. A blank node label written in a query pattern "
        "is not a reference to anything -- it is a variable that you are not "
        "allowed to project. It matches every term in the graph, IRIs and "
        "literals included, so this query counts the whole dataset.",
    diagram="""
    SELECT (COUNT(*) AS ?triples) WHERE { _:b0 ?p ?o }

                                     4826
                                     ----
                            every triple in the file

    What you probably meant:      What SPARQL heard:

      "the node called _:b0"        "some subject, I don't care
                                     which, and don't ask me to
                                     show it to you"

    _:b0 there behaves exactly like ?anything, minus the ability
    to SELECT it. The label is scoped to the query, and it has no
    connection to the _:b0 an earlier query printed -- or to the
    _:b0 in the Turtle file, come to that.

    So the rule is:

      +--------------------------------------------------------+
      | A blank node label in query results is a local nickname |
      | the engine made up while answering. It is not stable    |
      | between queries, between engines, or between runs.      |
      | You cannot look one up. Do not store one.               |
      +--------------------------------------------------------+

    Which leaves a real problem: how do you get back to a blank
    node you have found? Two answers -- reach it by a path from
    something that does have an IRI (q111), or give it a name of
    your own (q114).
    """,
    learn=[
        "_:label in a query pattern is a variable, not a reference. It matches "
        "anything and cannot be projected.",
        "Blank node labels in results are made up by the engine per query. They "
        "are not identifiers and will not survive a second query.",
        "The way back to a blank node is a path from a named node, or a "
        "skolem IRI you mint yourself.",
    ],
    body="""SELECT (COUNT(*) AS ?triples)
WHERE {
  _:b0 ?p ?o .
}""",
    data=D11,
    notes="4826 is every triple in bookshop-trail-1.1.ttl, which is the point: "
          "_:b0 constrained nothing at all.",
)

q(
    qid="q111", module=MOD,
    title="Walking an RDF collection",
    asks="Which classes are declared disjoint from one another?",
    how="An RDF collection -- the ( a b c ) in Turtle -- is not a list "
        "structure the query language knows about. It is a chain of blank "
        "nodes, each carrying rdf:first for its item and rdf:rest for the rest "
        "of the chain. rdf:rest*/rdf:first is the path that walks it, and it "
        "is the reason property paths and blank nodes belong in the same "
        "lesson.",
    diagram="""
    what the file says:

      [] a owl:AllDisjointClasses ;
         owl:members ( bs:Settlement bs:CouncilArea bs:Region bs:Country ) .

    what is actually stored:

      _:axiom --owl:members--> _:c1 --rdf:first--> bs:Settlement
                                |
                            rdf:rest
                                v
                               _:c2 --rdf:first--> bs:CouncilArea
                                |
                            rdf:rest
                                v
                               _:c3 --rdf:first--> bs:Region
                                |
                            rdf:rest
                                v
                               _:c4 --rdf:first--> bs:Country
                                |
                            rdf:rest
                                v
                             rdf:nil        <- the end of the list

    the path that gets the members out:

      owl:members / rdf:rest* / rdf:first
      -----------   ---------   ---------
       one hop to    zero or     the item
       the first     more hops   in this
       cell          along the   cell
                     chain

    Note rdf:rest* and not rdf:rest+ : the zero-length case is what
    lets the first member out. With + you would silently lose it.

    Fifteen classes come back, from the two axioms in the file.
    """,
    learn=[
        "An RDF collection is a chain of blank nodes with rdf:first and "
        "rdf:rest. Nothing in SPARQL treats it as a list.",
        "rdf:rest*/rdf:first is the idiom for reading one out. The star, not "
        "the plus -- the plus drops the first member.",
        "This is also why you can reach a blank node without naming it: start "
        "from something with an IRI and walk.",
    ],
    body="""SELECT ?member
WHERE {
  ?axiom a           owl:AllDisjointClasses ;
         owl:members/rdf:rest*/rdf:first ?member .
}
ORDER BY ?member""",
    data=D11,
    extra_prefixes=("owl", "rdf"),
)

q(
    qid="q112", module=MOD,
    title="Where in the list?",
    asks="An RDF collection is ordered. Which position does each member hold?",
    how="The order is in the chain, not in any property, so it has to be "
        "counted. Every cell from the head to this one is one hop of "
        "rdf:rest*, so counting those cells gives the position. It is an "
        "aggregate over a path, which is a shape worth having in your hands.",
    diagram="""
    head --> c1 --> c2 --> c3 --> c4 --> nil

    for c3, how many cells lie between the head and it, inclusive?

      head rdf:rest* ?between .      <- c1, c2, c3, c4  (and head=c1)
      ?between rdf:rest* c3 .        <- keeps c1, c2, c3
                                        -------------
                                        COUNT = 3

    so ?position falls out of a GROUP BY on the cell:

      +--------------------+----------+
      | bs:Settlement      |        1 |
      | bs:CouncilArea     |        2 |
      | bs:Region          |        3 |
      | bs:Country         |        4 |
      +--------------------+----------+

    GROUP BY ?cell groups on a blank node, which is fine: within
    one query the engine knows perfectly well which node is which.
    It is only outside the query that the identity evaporates.

    The FILTER on bs:Country picks the four-member axiom out of the
    two in the file, using a member as the handle -- again, reaching
    a blank node through something named.
    """,
    learn=[
        "RDF collections are ordered, and the order lives in the chain. "
        "Counting rdf:rest* hops is how you recover it.",
        "GROUP BY on a blank node works and is deterministic within a single "
        "query. Sorting or paging on one is not -- see the note on q64.",
        "Counting along a path is a general trick: depth in a hierarchy is the "
        "same query with a different predicate.",
    ],
    body="""SELECT ?member (COUNT(?between) AS ?position)
WHERE {
  ?axiom   a owl:AllDisjointClasses ;
           owl:members ?head .
  ?head    rdf:rest*/rdf:first bs:Country .

  ?head    rdf:rest* ?between .
  ?between rdf:rest* ?cell .
  ?cell    rdf:first ?member .
}
GROUP BY ?cell ?member
ORDER BY ?position""",
    data=D11,
    extra_prefixes=("owl", "rdf"),
)

q(
    qid="q113", module=MOD,
    title="Telling two blank nodes apart",
    asks="Are the two disjointness axioms really two nodes, or one node found "
         "twice?",
    how="Blank nodes have identity inside a query even though they have no "
        "name outside it. sameTerm compares two bindings and answers "
        "truthfully, so a self-join with a not-same filter counts the "
        "distinct pairs.",
    diagram="""
    ?a a owl:AllDisjointClasses .
    ?b a owl:AllDisjointClasses .
    FILTER( !sameTerm(?a, ?b) )

    with two axioms in the file:

      (a1,a1) (a1,a2)        the filter removes the diagonal
      (a2,a1) (a2,a2)        and 2 ordered pairs survive

    +--------------------------------------------------------+
    | inside one query   blank nodes have identity. They      |
    |                    join, compare and group correctly.   |
    |                                                         |
    | outside the query  they have none. The label you saw    |
    |                    means nothing to the next query.     |
    +--------------------------------------------------------+

    A note on the anonymous form: writing

        [] a owl:AllDisjointClasses ; owl:members ?head .

    means exactly what ?axiom meant in q111 -- one node, matched
    once, just not projectable. Two separate [] in the same query
    are two separate variables, and nothing stops them matching the
    same node.

    Use != rather than !sameTerm and most engines will still do the
    right thing on blank nodes, but sameTerm is the operator that is
    actually defined for them, and it does not raise on terms that
    cannot be compared by value.
    """,
    learn=[
        "sameTerm compares RDF terms by identity, and it is the right test for "
        "blank nodes.",
        "Identity is real within a query and gone outside it. That is the whole "
        "of what makes blank nodes awkward.",
        "[] is an unnamed variable used once. Two [] in one query are two "
        "different variables, not the same node.",
    ],
    body="""SELECT (COUNT(*) AS ?orderedPairs)
WHERE {
  ?a a owl:AllDisjointClasses .
  ?b a owl:AllDisjointClasses .
  FILTER( !sameTerm(?a, ?b) )
}""",
    data=D11,
    extra_prefixes=("owl",),
)

q(
    qid="q114", module=MOD,
    title="Giving a blank node a name",
    asks="Mint a stable IRI for each disjointness axiom, so it can be quoted "
         "in a bug report.",
    how="Skolemising means replacing a blank node with an IRI. The IRI has to "
        "come from the node's content, never from its label, because the label "
        "changes between runs. Here the content is the size of the axiom and "
        "its alphabetically first member, computed in a sub-query and turned "
        "into an IRI with CONCAT and IRI().",
    diagram="""
      a blank node                    an IRI you can send to somebody
      ------------                    ------------------------------
        _:b0        --skolemise-->    bt:axiom-bookshop-11
        _:b1                          bt:axiom-councilarea-4

    the key must come from the CONTENT:

      MIN(?local)  ->  "Bookshop"       stable across runs
      COUNT(?m)    ->  11               stable across engines
      STR(?axiom)  ->  "b0"             CHANGES. Never use it.

    +--------------------------------------------------------+
    | RDF has a convention for this: IRIs under               |
    | .../.well-known/genid/ are understood to be             |
    | skolem IRIs -- IRIs standing in for blank nodes.        |
    | A readable name works just as well when the graph is    |
    | yours; the convention matters when you publish.         |
    +--------------------------------------------------------+

    Going the other way, BNODE() mints a fresh blank node -- one
    per solution, so it is the tool for building structure in a
    CONSTRUCT template rather than for identifying anything.

    Skolemising is not free. You have asserted that these two
    axioms are distinct, findable things, and if the file changes
    so that a third axiom also starts with Bookshop and has eleven
    members, two of them collide. Pick a key that cannot.
    """,
    learn=[
        "Skolemising replaces a blank node with an IRI so it can be referred "
        "to from outside. Derive the IRI from content, never from the label.",
        "IRI(CONCAT(...)) builds an IRI at query time; the .well-known/genid/ "
        "prefix is the published convention for skolem IRIs.",
        "BNODE() is the opposite operation, and it mints a fresh node per "
        "solution -- useful for structure, useless for identity.",
    ],
    body="""SELECT ?id ?size ?firstMember
WHERE {
  {
    SELECT ?axiom (COUNT(?m) AS ?size) (MIN(?local) AS ?firstMember)
    WHERE {
      ?axiom a           owl:AllDisjointClasses ;
             owl:members/rdf:rest*/rdf:first ?m .
      BIND( REPLACE(STR(?m), "^.*[/#]", "") AS ?local )
    }
    GROUP BY ?axiom
  }
  BIND( IRI(CONCAT("https://example.org/bookshop-trail/axiom-",
                   LCASE(?firstMember), "-", STR(?size))) AS ?id )
}
ORDER BY ?id""",
    data=D11,
    extra_prefixes=("owl", "rdf"),
)

q(
    qid="q115", module=MOD,
    title="A copy with no blank nodes left in it",
    asks="Build a graph that says the same thing about disjointness, with "
         "every blank node replaced by something nameable.",
    how="CONSTRUCT with a skolem IRI in the subject position. The list "
        "structure disappears: instead of a chain of cells, each axiom gets a "
        "flat set of bs:disjointMember triples. The result loads into any "
        "engine, survives a round trip through a file, and can be diffed.",
    diagram="""
    before -- 23 blank nodes, 46 triples of plumbing:

      _:a --owl:members--> _:c1 --rdf:rest--> _:c2 --rdf:rest--> ...
                             |                  |
                        rdf:first          rdf:first
                             v                  v
                       bs:Settlement    bs:CouncilArea

    after -- no blank nodes, no plumbing:

      bt:axiom-bookshop-11    bs:disjointMember  bs:Bookshop ;
                              bs:disjointMember  bs:Person ;
                              ...
      bt:axiom-councilarea-4  bs:disjointMember  bs:Settlement ;
                              ...

    15 triples out, one per member, and every subject has a name.

    What was lost: the order of the list, and the fact that OWL
    reads it as one axiom rather than a bag of memberships. That is
    the trade -- flattening is easier to query and no longer means
    quite the same thing. Do it for reporting and for diffing, not
    as a replacement for the original.

    Sending the result somewhere: press Get All in the editor after
    running a CONSTRUCT and the constructed triples come back as
    Turtle you can save.
    """,
    learn=[
        "CONSTRUCT plus a skolem IRI is how you hand a blank-node structure to "
        "something that cannot cope with blank nodes.",
        "Flattening a collection loses its order and its meaning as a single "
        "axiom. Know what you are giving up.",
        "A graph with no blank nodes can be diffed, merged and quoted. That is "
        "worth a lot when the data is under review.",
    ],
    body="""CONSTRUCT {
  ?id bs:disjointMember ?member .
}
WHERE {
  {
    SELECT ?axiom (COUNT(?m) AS ?size) (MIN(?local) AS ?firstMember)
    WHERE {
      ?axiom a           owl:AllDisjointClasses ;
             owl:members/rdf:rest*/rdf:first ?m .
      BIND( REPLACE(STR(?m), "^.*[/#]", "") AS ?local )
    }
    GROUP BY ?axiom
  }
  ?axiom owl:members/rdf:rest*/rdf:first ?member .
  BIND( IRI(CONCAT("https://example.org/bookshop-trail/axiom-",
                   LCASE(?firstMember), "-", STR(?size))) AS ?id )
}""",
    data=D11,
    extra_prefixes=("owl", "rdf"),
)
