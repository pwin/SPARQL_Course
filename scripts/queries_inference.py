# -*- coding: utf-8 -*-
"""Module 18: inference, and how much of it you can write yourself.

A reasoner derives new triples from the ones you have plus the rules in the
vocabulary. That is genuinely useful and it is also, for the commonest cases,
something SPARQL can do at query time with no reasoner, no materialisation and
nothing to keep up to date.

These six run on all three engines against the asserted data. What happens
when you actually switch a reasoner on is a different subject, measured
separately in "Reasoning in the three engines" -- the short version is that
the two OWL reasoners agree with q140 exactly, and the two RDFS ones cannot
do it at all.

    python scripts/check_queries.py q140 q141 q142 q143 q144 q145
"""

from querycat import q, D11, ALL, EDITOR, HOLOS, FUSEKI

MOD = "18-inference"

q(
    qid="q140", module=MOD,
    title="The closure a reasoner would give you",
    asks="How many containment facts are there once you follow the chain?",
    how="bs:within is declared owl:TransitiveProperty, which tells a reasoner "
        "it may derive York-in-England from York-in-Yorkshire and "
        "Yorkshire-in-England. A property path computes the same set at query "
        "time. The two answers are identical, and one of them needs no "
        "reasoner, no extra storage and nothing to re-run after a write.",
    diagram="""
    asserted                        after transitivity

      York    -> Yorkshire            York -> Yorkshire
      Yorkshire -> England            York -> England       <- derived
      England -> GB                   York -> GB            <- derived
                                      Yorkshire -> England
      63 triples                      Yorkshire -> GB       <- derived
                                      England -> GB
                                      ...
                                      186 pairs

    measured, all four routes:

      +--------------------------------+-----------+
      | asserted                       |    63     |
      | Jena riotcmd.infer --rdfs      |    63     |  RDFS has no
      | HOLOS holos entail             |    63     |  transitivity rule
      | HyLAR OWL 2 RL (the editor)    |   186     |
      | Jena OWLMicro via assembler    |   186     |  two OWL reasoners,
      | ?s bs:within+ ?o               |   186     |  one path, one answer
      +--------------------------------+-----------+

    The two OWL reasoners and the property path agree exactly.
    The two RDFS reasoners cannot do it, because transitivity is
    an OWL notion and RDFS has no rule for it.

    +----------------------------------------------------------+
    |  A reasoner writes 186 pairs down and they go stale the   |
    |  moment a place moves. A path recomputes them every time  |
    |  and is never wrong. The reasoner wins when the same      |
    |  closure is queried constantly and the data barely        |
    |  changes; the path wins the rest of the time.             |
    +----------------------------------------------------------+
    """,
    learn=[
        "owl:TransitiveProperty tells a reasoner it may close a chain. p+ "
        "computes the same set at query time on any SPARQL 1.1 engine.",
        "RDFS has no transitivity rule, so an RDFS reasoner leaves a "
        "transitive property exactly as asserted. Check which profile you "
        "have before assuming.",
        "Materialised inference is a cache. Ask who invalidates it before you "
        "decide it is cheaper than a path.",
    ],
    body="""SELECT (COUNT(*) AS ?pairs)
WHERE {
  SELECT DISTINCT ?place ?container
  WHERE {
    ?place bs:within+ ?container .
  }
}""",
    data=D11,
)

q(
    qid="q141", module=MOD,
    title="Filling in the other direction",
    asks="Every work has an author; how many author-to-work links are there "
         "if you count both properties?",
    how="bs:wrote is declared owl:inverseOf bs:author, so a reasoner would "
        "make each complete from the other. The data does not have them "
        "complete: 74 works name an author, and only 68 authors name a work. "
        "Reading the property backwards with ^ recovers all 74 without "
        "deriving anything.",
    diagram="""
    bs:wrote  owl:inverseOf  bs:author .

    asserted                     what a reasoner would add

      ?a bs:wrote  ?w    68        6 more bs:wrote
      ?w bs:author ?a    74        6 more... no: none. 74 already.

    +----------------------------+-------+
    | ?a bs:wrote ?w             |    68 |
    | ?w bs:author ?a  (flipped) |    74 |
    | either of the two          |    74 |   <- this query
    +----------------------------+-------+

    So bs:wrote is missing six links that bs:author has. A
    reasoner would fix that by deriving them. So does this:

      { ?author bs:wrote ?work } UNION { ?work bs:author ?author }

    and so does the shorter form, which is the one to remember:

      ?work ^bs:wrote|bs:author ?author

    ^ reads a predicate backwards (module 05, q32). An inverse
    declaration in the vocabulary is a promise about what a
    reasoner may do; ^ is the same journey with no promise
    required.

    Worth noticing which way round the gap is. Nothing warns you
    that one direction of an inverse pair is less complete than
    the other -- the data simply answers differently depending on
    which way you ask, and that is a thing to check for rather
    than to discover.
    """,
    learn=[
        "owl:inverseOf lets a reasoner complete each direction from the "
        "other. ^ reads a predicate backwards and needs no reasoner.",
        "Data with an inverse pair is rarely complete in both directions. Ask "
        "both ways and compare before trusting either.",
        "UNION of the two directions and ^p|q are the same query. The second "
        "is shorter and the engine can plan it as one path.",
    ],
    body="""SELECT (COUNT(*) AS ?links)
WHERE {
  SELECT DISTINCT ?author ?work
  WHERE {
    ?work ^bs:wrote|bs:author ?author .
  }
}""",
    data=D11,
)

q(
    qid="q142", module=MOD,
    title="What RDFS would actually add here",
    asks="How deep is the class hierarchy a reasoner would have to walk?",
    how="RDFS's most useful rule says that something in a class is also in "
        "every superclass of it. How much that gives you depends entirely on "
        "how deep the hierarchy is and how completely the data is typed. "
        "Here: six subclass pairs, and every instance already carries its "
        "types. Which is why switching RDFS on adds so little.",
    diagram="""
    the whole class hierarchy of this vocabulary:

      bs:Settlement    rdfs:subClassOf  bs:Place
      bs:CouncilArea   rdfs:subClassOf  bs:Place
      bs:Region        rdfs:subClassOf  bs:Place
      bs:Country       rdfs:subClassOf  bs:Place
      bs:Author        rdfs:subClassOf  bs:Person
      bs:Translation   rdfs:subClassOf  bs:Work

      6 pairs. Nothing is more than one hop deep.

    and so, measured:

      +--------------------------------+---------+----------+
      |                                | triples | usefully |
      |                                |         |      new |
      +--------------------------------+---------+----------+
      | asserted                       |   4,826 |        — |
      | Jena riotcmd.infer --rdfs      |   4,826 |        0 |
      | HOLOS holos entail             |   5,051 |        0 |
      | HyLAR OWL 2 RL                 |   8,777 |    3,952 |
      +--------------------------------+---------+----------+

    Neither RDFS reasoner derives a usable new fact here. HOLOS
    writes 225 triples, of which 133 are reflexive -- X is a
    subclass of X -- and 92 type things as a class with no name
    (q143). Jena writes none at all.

    That is not a failing of either. It is what RDFS is for
    meeting a dataset that has no deep hierarchy and is already
    fully typed. On data where instances carry only their most
    specific type and the hierarchy is eight deep, the same
    reasoner earns its keep.

    rdfs:subClassOf+ walks it without one, and gives the six pairs
    directly -- which is also how you check a hierarchy for the
    cycle that would make a reasoner loop.

    +----------------------------------------------------------+
    |  Measure the hierarchy before you switch a reasoner on.   |
    |  This query is that measurement, it takes a second, and   |
    |  it will sometimes tell you not to bother.                |
    +----------------------------------------------------------+
    """,
    learn=[
        "RDFS earns its keep on deep hierarchies and partially typed data. "
        "This dataset has neither, so it adds 140 triples.",
        "rdfs:subClassOf+ walks the hierarchy with no reasoner, and shows you "
        "how much one would have to do.",
        "The size of an inference closure is a property of your data, not of "
        "the engine. Measure before choosing.",
    ],
    body="""SELECT ?subclass ?superclass
WHERE {
  ?subclass rdfs:subClassOf+ ?superclass .
  FILTER( ?subclass != ?superclass )
}
ORDER BY ?superclass ?subclass""",
    data=D11,
    extra_prefixes=("rdfs",),
)

q(
    qid="q143", module=MOD,
    title="The inference nobody wanted",
    asks="Which properties would a reasoner use to type things as a class "
         "with no name?",
    how="rdfs:domain does not constrain anything. It licenses an inference: "
        "if ?s has this property then ?s is in this class. When the domain is "
        "an anonymous union class -- written [ owl:unionOf ( A B ) ] because "
        "the property applies to two kinds of thing -- a reasoner dutifully "
        "types every subject as a blank node. True, and unusable.",
    diagram="""
    the vocabulary says:

      bs:locatedIn rdfs:domain [ a owl:Class ;
                                 owl:unionOf ( bs:Bookshop bs:Publisher ) ] .

    RDFS rule rdfs2 therefore derives, for all 46 subjects:

      bt:shop-inkwell  rdf:type  _:b0 .
                                 ---
                       a class with no name. You cannot write a
                       query against it, cannot report it, cannot
                       link to it. It is 92 of the 225 triples
                       HOLOS entails.

    +------------------+---------------+
    | bs:founded       |            46 |   33 shops + 13 publishers
    | bs:locatedIn     |            46 |   the same 46
    +------------------+---------------+

    Both properties apply to a shop or a publisher, so both
    declare the same anonymous union as their domain, and both
    make the reasoner type the same 46 things as the same
    nameless class.

    Two lessons, and the second is the bigger one:

      1  rdfs:domain is not a constraint. It never says "this is
         wrong"; it says "therefore this is also true". A shop
         with a bs:locatedIn is not checked against anything --
         it is typed. Use SHACL (module 12) when you want the
         checking meaning.

      2  A reasoner produces everything its rules permit, not
         what you were hoping for. Some of that is noise, and
         noise you have to store and search past.

    Blank nodes as classes are module 16's subject arriving from
    an unexpected direction, and q109's census is what finds them.
    """,
    learn=[
        "rdfs:domain licenses an inference; it does not constrain. It cannot "
        "make anything invalid, only make more things true.",
        "An anonymous union class as a domain makes a reasoner type every "
        "subject as a blank node -- correct, and impossible to query.",
        "A closure contains everything the rules permit. Look at what a "
        "reasoner derived before deciding to keep it.",
    ],
    body="""SELECT ?property (COUNT(DISTINCT ?s) AS ?wouldBeTyped)
WHERE {
  ?property rdfs:domain ?anonymousClass .
  FILTER( isBLANK(?anonymousClass) )
  ?s ?property ?o .
}
GROUP BY ?property
ORDER BY ?property""",
    data=D11,
    extra_prefixes=("rdfs",),
)

q(
    qid="q144", module=MOD,
    title="A reasoner you can read",
    asks="Materialise the containment closure as a graph, with the derived "
         "triples marked as derived.",
    how="A CONSTRUCT is a single inference rule you can read, test and change. "
        "This one does what an OWL reasoner does for transitivity, and adds "
        "the thing a reasoner does not: it says which triples it made up, so "
        "they can be told apart afterwards and dropped when they go stale.",
    diagram="""
    the rule, in one query:

      ?place bs:within+ ?container            IF
        ->  ?place bs:withinTransitive ?container    THEN

    186 triples out, on a different predicate from the 63 that
    were asserted. That separation is deliberate:

      bs:within             asserted, 63.   Untouched.
      bs:withinTransitive   derived, 186.   Droppable.

    +----------------------------------------------------------+
    |  A reasoner that writes into the same predicate leaves    |
    |  you unable to answer "who said this?". Load derived      |
    |  triples into their own graph, or onto their own          |
    |  predicate, or both -- HOLOS uses a graph, this uses a    |
    |  predicate, and either beats mixing them.                 |
    +----------------------------------------------------------+

    What CONSTRUCT gives you that a reasoner does not:

      you can read the rule            it is one query
      you can test it                  q140 counts what it makes
      you can change it                without changing the data
      it stops where you say           no unwanted closure (q143)
      it runs on every engine          no profile to negotiate

    What a reasoner gives you that this does not: all the other
    rules at once, and consistency you did not have to think
    about. Module 17 q120 is this pattern written as an INSERT,
    which is materialisation proper.
    """,
    learn=[
        "A CONSTRUCT is one inference rule, written where you can read it. "
        "That is most of what a reasoner does, minus the surprises.",
        "Put derived triples on their own predicate or in their own graph. "
        "Mixing them with asserted ones destroys provenance and cannot be "
        "undone.",
        "q120 turns this into an INSERT. The difference between deriving and "
        "storing is who has to remember to re-run it.",
    ],
    body="""CONSTRUCT {
  ?place bs:withinTransitive ?container .
}
WHERE {
  ?place bs:within+ ?container .
}""",
    data=D11,
)

q(
    qid="q145", module=MOD,
    title="What entailment cannot do",
    asks="The vocabulary says a Place and a Bookshop can never be the same "
         "thing. What happens if one is?",
    how="Nothing, as far as any query is concerned. Entailment only ever adds "
        "triples; it has no way to remove one or to answer no. A disjointness "
        "axiom makes an ontology inconsistent rather than making a query "
        "empty, and a rule reasoner will usually carry on regardless. "
        "Checking is a separate job with separate tools.",
    diagram="""
    the vocabulary asserts:

      [] a owl:AllDisjointClasses ;
         owl:members ( bs:Place bs:Bookshop bs:Person ... ) .

    if something were both a Place and a Bookshop:

      OWL DL      the ontology is INCONSISTENT. Everything
                  follows from it, so every answer is
                  meaningless -- which a DL reasoner reports
                  and a rule reasoner mostly does not.

      OWL 2 RL    derives owl:Nothing or a clash flag, or
                  simply carries on. Rule reasoners are built
                  to add, not to object.

      your query  returns the row. Nothing checked anything.

    +----------------------------------------------------------+
    |  Entailment is monotonic: adding data never withdraws a   |
    |  conclusion. So it can never say "this is wrong", only    |
    |  "and therefore this as well". Every validation question  |
    |  you have is outside it.                                  |
    +----------------------------------------------------------+

    Which is what SHACL is for, and module 12 uses it in earnest.
    This query is the SPARQL version of the same check: find
    anything that is in two classes declared disjoint. It returns
    nothing on this dataset, and returning nothing is the answer
    you want.

      disjointness declared, in pairs      15 classes, 2 axioms
      things violating it                   0

    A test that passes silently is worth writing down: q76 is the
    ASK form of the same idea, and the reason to prefer it is
    that a boolean false is harder to overlook than an empty
    table.
    """,
    learn=[
        "Entailment is monotonic. It adds; it cannot retract, contradict or "
        "report. No amount of reasoning will tell you your data is wrong.",
        "A disjointness axiom makes the ontology inconsistent, not the query "
        "empty. Most rule reasoners will not even mention it.",
        "Validation is a separate tool: SHACL, or a query like this one run "
        "as a test. Module 12 does both.",
    ],
    body="""SELECT ?thing ?classA ?classB
WHERE {
  ?axiom a           owl:AllDisjointClasses ;
         owl:members/rdf:rest*/rdf:first ?classA ,
                                         ?classB .
  FILTER( STR(?classA) < STR(?classB) )

  ?thing a ?classA , ?classB .
}
ORDER BY ?thing ?classA ?classB""",
    data=D11,
    extra_prefixes=("owl", "rdf"),
    expect="no rows, which is the answer you want",
)
