# -*- coding: utf-8 -*-
"""Modules 01-04: first queries, filtering, optionality, aggregation."""

from querycat import q, D11, ALL, EDITOR, HOLOS, FUSEKI

# ===========================================================================
# 01  First queries
# ===========================================================================

q(
    qid="q01", module="01-first-queries",
    title="Every bookshop on the trail",
    asks="What bookshops are in this dataset, and what are they called?",
    how="One triple pattern finds the shops, a second fetches each one's "
        "label. Both patterns mention ?shop, so the engine keeps only the "
        "combinations where the same ?shop satisfies both -- that shared "
        "variable is the join, and it's the only join mechanism SPARQL has.",
    diagram="""
    ?shop  ──── rdf:type ────▶  bs:Bookshop      (which things are shops)
      │
      └─────── rdfs:label ───▶  ?name            (what each is called)

    Both lines constrain the SAME ?shop, so a row survives only if
    both are true of it.  33 shops in, 33 rows out.
    """,
    learn=[
        "A query is a graph pattern: you draw the shape you want and the "
        "engine finds every place the shape fits.",
        "`a` is shorthand for rdf:type. It's the one abbreviation SPARQL "
        "borrows from Turtle.",
        "Repeating a variable joins the patterns. There's no JOIN keyword "
        "because there doesn't need to be one.",
    ],
    body="""SELECT ?shop ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
}
ORDER BY ?name""",
)

q(
    qid="q02", module="01-first-queries",
    title="Everything known about one shop",
    asks="What does the dataset actually record about The Inkwell?",
    how="Fixing the subject and leaving predicate and object as variables "
        "returns every statement with that subject. It's the fastest way to "
        "find out how a strange dataset is shaped, and worth doing before "
        "writing anything more ambitious.",
    diagram="""
    bt:shop-inkwell  ──── ?p ────▶  ?o

         known                unknown
       (the subject)     (everything else)

    Turn the pattern inside out and you learn the vocabulary:
      ?p = bs:founded    ?o = 1979
      ?p = bs:locatedIn  ?o = bt:place-wigtown
      ?p = bs:hasCafe    ?o = true          ... and so on
    """,
    learn=[
        "Any position of a triple pattern can be a variable, including the "
        "predicate.",
        "This is the single most useful exploratory query there's: run it "
        "against one resource before you try to query a thousand.",
        "In the Turtle Editor Viewer you can do the same thing visually -- "
        "pick the shop in the Subjects dropdown and look at the graph.",
    ],
    body="""SELECT ?p ?o
WHERE {
  bt:shop-inkwell ?p ?o .
}
ORDER BY ?p""",
)

q(
    qid="q03", module="01-first-queries",
    title="Which town is each shop in",
    asks="Pair every shop with the name of the town it trades in.",
    how="Three patterns chained through two join variables. ?shop links the "
        "first two, ?town links the second and third. The engine is free to "
        "evaluate them in any order it likes; what matters to you is only "
        "that the shared variables line up.",
    diagram="""
    ?shop ──rdfs:label──▶ ?shopName
      │
      └──bs:locatedIn──▶ ?town ──rdfs:label──▶ ?townName

    Two joins:  ?shop  ties lines 1 and 2
                ?town  ties lines 2 and 3

    A chain like this is how you walk one hop at a time.  Module 05
    replaces the whole chain with a single path expression.
    """,
    learn=[
        "Chaining patterns walks the graph one edge at a time.",
        "Semicolon repeats the subject; a full stop starts a new one. This is "
        "Turtle syntax reused inside SPARQL.",
        "Labels live on the thing, not on the link. To show a name you almost "
        "always need one extra pattern per resource.",
    ],
    body="""SELECT ?shopName ?townName
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?shopName ;
        bs:locatedIn ?town .
  ?town rdfs:label   ?townName .
}
ORDER BY ?townName ?shopName""",
)

q(
    qid="q04", module="01-first-queries",
    title="The ten oldest shops",
    asks="Which shops have been trading longest?",
    how="ORDER BY sorts the result table after the pattern has matched, and "
        "LIMIT truncates it. Both act on the finished table, not on the "
        "matching -- so the engine still had to consider all 33 shops to know "
        "which ten come first.",
    diagram="""
    match  ─▶  33 rows  ─▶  ORDER BY ?founded  ─▶  LIMIT 10  ─▶  10 rows
                              (ascending)

    Order of evaluation, which is NOT the order you write them in:
      WHERE  ->  GROUP BY  ->  HAVING  ->  ORDER BY  ->  OFFSET/LIMIT
                                             ^
                            SELECT's projection happens around here
    """,
    learn=[
        "ORDER BY and LIMIT are applied to the result table, after matching.",
        "ORDER BY ?x is ascending; wrap it as DESC(?x) for the other "
        "direction.",
        "LIMIT without ORDER BY gives you an arbitrary ten rows, not the "
        "first ten of anything. The two belong together.",
    ],
    body="""SELECT ?name ?founded
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        bs:founded ?founded .
}
ORDER BY ?founded
LIMIT 10""",
)

q(
    qid="q05", module="01-first-queries",
    title="What kinds of thing are in here",
    asks="Without knowing anything about the dataset, what classes does it "
         "contain?",
    how="Match every typed resource, project only the type, and ask for "
        "DISTINCT. Anything that survives is a class the data actually uses -- "
        "which isn't always the same as the classes the schema declares.",
    diagram="""
        ?s ──rdf:type──▶ ?type

     every typed thing        collapse duplicates
     (about 1,080 rows)  ──▶  DISTINCT  ──▶  ~20 classes

    Ask this first.  Then ask q06 to find out what properties each
    class carries.  Two queries and you have the map.
    """,
    learn=[
        "DISTINCT removes duplicate rows from the result table.",
        "Querying the data for its own structure beats trusting the "
        "documentation, because the data can't be out of date with itself.",
        "The classes you get back are the ones in use. A schema may declare "
        "more.",
    ],
    body="""SELECT DISTINCT ?type
WHERE {
  ?s a ?type .
}
ORDER BY ?type""",
)

q(
    qid="q06", module="01-first-queries",
    title="What can I ask about a bookshop",
    asks="Which properties do bookshops actually carry?",
    how="Restrict to subjects that are bookshops, then leave the predicate "
        "free. The result is the working vocabulary for that class -- the "
        "list of things it's worth asking a shop about.",
    diagram="""
    ?shop ──rdf:type──▶ bs:Bookshop      (restrict the subject...)
      │
      └───── ?p ──────▶ ?o               (...then free the predicate)

    Pair this with the schema itself:

      bs:founded  rdfs:comment "The year the shop opened."

    The dataset describes its own vocabulary in 01-vocabulary.ttl, so
    you can join the two and get documentation in your result table.
    """,
    learn=[
        "Constraining the subject and freeing the predicate profiles a class.",
        "This dataset carries its own schema, so a query can fetch the "
        "human-readable comment alongside the property name.",
        "OPTIONAL is used here because a property isn't guaranteed to have a "
        "comment. Module 03 explains why that matters.",
    ],
    body="""SELECT DISTINCT ?property ?comment
WHERE {
  ?shop a  bs:Bookshop ;
        ?property ?value .
  OPTIONAL { ?property rdfs:comment ?comment . }
}
ORDER BY ?property""",
)

# ===========================================================================
# 02  Filtering and expressions
# ===========================================================================

q(
    qid="q07", module="02-filtering",
    title="Shops founded before 1970",
    asks="Which shops predate 1970, and why is the obvious way to ask wrong?",
    how="FILTER drops every solution its expression doesn't judge true. The "
        "interesting part is the cast. bs:founded is an xsd:gYear, which is "
        "not a number, so it has to be converted before it can be compared "
        "with 1970 -- and the obvious conversion isn't portable. Going via "
        "STR() first works on all three engines; casting the gYear directly "
        "works on only one.",
    diagram="""
    pattern matches 33 rows
              │
              ▼
    FILTER( xsd:integer(STR(?founded)) < 1970 )
              │        ─────┬─────
              │             └── "1979"  a plain string
              │
              ├── true  ──▶ row kept
              └── false ──▶ row dropped
                              │
                              ▼
                          10 rows out

    Measured on this dataset, all three engines, same query:

      xsd:integer(?founded)            editor  0   holos  0   fuseki 10
      ?founded < "1970"^^xsd:gYear     editor  0   holos  0   fuseki 10
      xsd:integer(STR(?founded))       editor 10   holos 10   fuseki 10  ✓
      STR(?founded) < "1970"           editor 10   holos 10   fuseki 10  ✓

    The unportable versions do not error.  They return zero rows and
    look like a fact about the data.
    """,
    learn=[
        "FILTER constrains; it can't create bindings.",
        "Datatypes are real. xsd:gYear isn't a number, and engines disagree "
        "about whether they will convert one for you.",
        "STR() first, then cast. It's the portable idiom, and it's explicit "
        "about what's happening.",
        "An expression that fails inside a FILTER removes the row silently. "
        "Zero rows is the classic symptom of a datatype mistake, not "
        "evidence of an empty dataset.",
    ],
    body="""SELECT ?name ?founded
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        bs:founded ?founded .
  FILTER( xsd:integer(STR(?founded)) < 1970 )
}
ORDER BY ?founded""",
)

q(
    qid="q08", module="02-filtering",
    title="Large shops with a cafe",
    asks="Which shops have both a cafe and more than 150 square metres of "
         "floor?",
    how="Two conditions combined with &&. Booleans in the data are real "
        "xsd:boolean values, so ?cafe can be tested directly without "
        "comparing it to anything.",
    diagram="""
    ?shop ──bs:hasCafe───▶ ?cafe        true / false
      │
      └────bs:floorArea──▶ ?area        a decimal

    FILTER( ?cafe && ?area > 150 )
             ▲        ▲
             │        └── comparison yields a boolean
             └── already a boolean; no "= true" needed

    &&  short-circuits, and an error on the right of a false && is
    swallowed.  That is deliberate, and occasionally useful.
    """,
    learn=[
        "A boolean-valued variable can be used as a condition directly.",
        "&& and || combine conditions; ! negates one.",
        "Writing `?cafe = true` works but reads worse, and tells the reader "
        "you weren't sure it was a boolean.",
    ],
    body="""SELECT ?name ?area
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?name ;
        bs:hasCafe   ?cafe ;
        bs:floorArea ?area .
  FILTER( ?cafe && ?area > 150 )
}
ORDER BY DESC(?area)""",
)

q(
    qid="q09", module="02-filtering",
    title="Sort books into price bands",
    asks="Group the books into cheap, mid and dear without changing the data.",
    how="BIND computes a value and binds it to a new variable, which can then "
        "be selected, sorted or grouped like any other. Nested IF builds the "
        "band. Unlike FILTER, BIND adds a column rather than removing rows.",
    diagram="""
    ?book ──bs:rrp──▶ ?price

              BIND( IF(?price < 12, "cheap",
                    IF(?price < 18, "mid", "dear")) AS ?band )
                                    │
                                    ▼
    ┌────────┬───────┬────────┐
    │ ?book  │ ?price│ ?band  │   <- a new column, computed
    ├────────┼───────┼────────┤
    │ ...    │  9.99 │ cheap  │
    │ ...    │ 15.50 │ mid    │
    │ ...    │ 21.00 │ dear   │
    └────────┴───────┴────────┘

    BIND sees only variables bound EARLIER in the group.  Move it to
    the top and ?price is unbound, so ?band comes out unbound too.
    """,
    learn=[
        "BIND adds a computed column; FILTER removes rows. They are the two "
        "halves of expression handling.",
        "IF(condition, then, else) nests, and is the closest SPARQL gets to a "
        "CASE statement.",
        "Position matters: BIND can only use what's already bound above it.",
    ],
    body="""SELECT ?title ?price ?band
WHERE {
  ?book a          bs:Work ;
        rdfs:label ?title ;
        bs:rrp     ?price .
  BIND( IF(?price < 12.00, "cheap",
        IF(?price < 18.00, "mid", "dear")) AS ?band )
}
ORDER BY ?price""",
)

q(
    qid="q10", module="02-filtering",
    title="Titles containing a word",
    asks="Which books have 'sea' or 'water' somewhere in the title?",
    how="REGEX matches a regular expression against a string. The third "
        "argument 'i' makes it case-insensitive. Because REGEX has to look "
        "inside every title, it can't use an index -- fine on 74 books, "
        "something to think about on 74 million.",
    diagram="""
    ?work ──rdfs:label──▶ ?title      74 titles

    FILTER( REGEX(?title, "sea|water", "i") )
                          ───┬─────  ─┬─
                             │        └── flags: i = ignore case
                             └── alternation: either word

           "The Dark Sea"   ✓        "High Water"  ✓
           "Cold Harbour"   ✗        "Scree"       ✗

    CONTAINS(?title, "Sea") is cheaper when you do not need a pattern.
    """,
    learn=[
        "REGEX(text, pattern, flags) is the general string test; CONTAINS, "
        "STRSTARTS and STRENDS are the cheap specific ones.",
        "REGEX works on the lexical form, so a language-tagged literal and a "
        "plain one behave the same way here.",
        "Regular expressions defeat text indexes. Prefer the specific "
        "functions when they will do.",
    ],
    body="""SELECT ?title
WHERE {
  ?work a          bs:Work ;
        rdfs:label ?title .
  FILTER( REGEX(?title, "sea|water", "i") )
}
ORDER BY ?title""",
)

q(
    qid="q11", module="02-filtering",
    title="Place names in Welsh and Gaelic",
    asks="Which places carry a name in a language other than English?",
    how="A language-tagged literal carries its tag as part of the value. "
        "LANG() extracts it; comparing it to '' finds the untagged ones. Here "
        "we keep everything that's tagged but not English.",
    diagram="""
    bt:place-cardiff rdfs:label "Cardiff"@en
                     rdfs:label "Caerdydd"@cy
                                 ───────  ──
                                  value   tag

    LANG(?label)  ──▶  "en"   or  "cy"   or  ""  (no tag at all)

    FILTER( LANG(?label) != "en" && LANG(?label) != "" )

    langMatches(LANG(?l), "cy") is the proper test: it also matches
    "cy-GB", which a plain = would miss.
    """,
    learn=[
        "A language tag is part of the literal, not a separate property.",
        "LANG() returns the empty string for a literal with no tag, so a bare "
        "!= \"en\" would let untagged strings through.",
        "langMatches handles subtags such as cy-GB properly; use it when the "
        "data may contain them.",
    ],
    body="""SELECT ?place ?label ?language
WHERE {
  ?place a          bs:Place ;
         rdfs:label ?label .
  BIND( LANG(?label) AS ?language )
  FILTER( ?language != "en" && ?language != "" )
}
ORDER BY ?language ?label""",
)

q(
    qid="q12", module="02-filtering",
    title="Build a one-line description of each shop",
    asks="Produce a single human-readable string per shop.",
    how="String functions compose. CONCAT joins, UCASE and SUBSTR reshape, "
        "STR strips a literal down to its lexical form so that a typed value "
        "can be glued to a plain one without a datatype clash.",
    diagram="""
    "The Inkwell"  +  "Wigtown"  +  1979
           │              │           │
           │              │           └─ STR() -> "1979"
           │              │                (drop the xsd:gYear)
           ▼              ▼              ▼
    CONCAT(?name, " of ", ?town, ", est. ", STR(?founded))
                             │
                             ▼
          "The Inkwell of Wigtown, est. 1979"

    Without STR() around the gYear, CONCAT is given a typed literal
    and an engine may refuse the whole expression.
    """,
    learn=[
        "STR() is the workhorse: it turns any literal or IRI into a plain "
        "string so the string functions will accept it.",
        "CONCAT with a typed literal is a common source of silently empty "
        "results.",
        "Everything computed with BIND can be selected, ordered and grouped "
        "like stored data.",
    ],
    body="""SELECT ?description
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?name ;
        bs:founded   ?founded ;
        bs:locatedIn ?place .
  ?place rdfs:label  ?town .
  FILTER( LANG(?town) = "en" )
  BIND( CONCAT(?name, " of ", ?town, ", est. ", STR(?founded)) AS ?description )
}
ORDER BY ?description""",
)

q(
    qid="q13", module="02-filtering",
    title="How old is each shop today",
    asks="How many years has each shop been trading?",
    how="NOW() gives the current dateTime, YEAR() pulls the year out of it, "
        "and subtracting the founding year gives an age that changes as the "
        "calendar does. The result is computed at query time and stored "
        "nowhere.",
    diagram="""
        NOW()  ──▶  2026-09-09T...  ──YEAR()──▶  2026
                                                   │
      bs:founded "1979"^^xsd:gYear                 │
              │                                    │
              └─ xsd:integer(STR()) ──▶ 1979       │
                                     │             │
                                     └──── - ──────┘
                                           │
                                           ▼
                                         ?age = 47

    Derived, not stored.  Run it next year and every number moves.
    """,
    learn=[
        "NOW() is evaluated once per query, so every row sees the same "
        "instant.",
        "The same gYear trap as q07, and here it's worse: a failed cast "
        "inside BIND leaves ?age unbound and keeps the row, so the query "
        "returns the right number of rows with an empty column.",
        "YEAR, MONTH, DAY, HOURS, MINUTES and SECONDS take apart a dateTime.",
        "Deriving values at query time is usually better than storing them, "
        "because stored ages go stale.",
    ],
    body="""SELECT ?name ?founded ?age
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        bs:founded ?founded .
  BIND( YEAR(NOW()) - xsd:integer(STR(?founded)) AS ?age )
}
ORDER BY DESC(?age) ?name
LIMIT 12""",
)

# ===========================================================================
# 03  Optional data, alternatives and negation
# ===========================================================================

q(
    qid="q14", module="03-optional-and-negation",
    title="Shops, with a website if there's one",
    asks="List every shop, showing its website where one is recorded.",
    how="Without OPTIONAL, the pattern would silently drop the shops that "
        "have no website. OPTIONAL tries the inner pattern and, when it does "
        "not match, keeps the row anyway with ?site left unbound.",
    diagram="""
    required                     optional
    ┌────────────────────┐      ┌──────────────────────┐
    │ ?shop a bs:Bookshop│─────▶│ ?shop bs:website ?site│
    │ ?shop rdfs:label ? │      └──────────────────────┘
    └────────────────────┘                │
             33 rows            ┌─────────┴──────────┐
                                ▼                    ▼
                         matched: ?site bound   no match:
                                                ?site UNBOUND
                                                row still kept
                                     │
                                     ▼
                                  33 rows

    Drop the OPTIONAL and you get fewer rows -- and no warning.
    """,
    learn=[
        "OPTIONAL is a left join. The left side is kept whatever happens on "
        "the right.",
        "An unbound variable isn't an empty string and not zero. It's "
        "absent, and BOUND() is how you test for it.",
        "The commonest bug in SPARQL is a missing OPTIONAL quietly shrinking "
        "the answer.",
    ],
    body="""SELECT ?name ?site
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  OPTIONAL { ?shop bs:website ?site . }
}
ORDER BY ?name""",
)

q(
    qid="q15", module="03-optional-and-negation",
    title="Which books have no ISBN",
    asks="Find the books with no ISBN recorded, and say why.",
    how="OPTIONAL brings the ISBN in when there's one; !BOUND(?isbn) then "
        "keeps only the rows where it did not arrive. This 'optional then "
        "test for unbound' shape is the classic way to express absence, and "
        "still the clearest when you also want a value from the row.",
    diagram="""
    ?work rdfs:label ?title            74 works
                │
                ▼
    OPTIONAL { ?work bs:isbn ?isbn }
                │
        ┌───────┴────────┐
        ▼                ▼
    ?isbn bound      ?isbn UNBOUND
        │                │
        │                ▼
        │       FILTER(!BOUND(?isbn))  ✓ kept
        ▼
      dropped

    Every book published before 1970 lands on the right-hand branch,
    because ISBNs did not exist yet.
    """,
    learn=[
        "OPTIONAL + !BOUND is the 'anti-join': rows where the optional part "
        "failed.",
        "NOT EXISTS says the same thing more directly when you don't need "
        "anything from inside the optional block.",
        "Absence in the data usually means something. Here it means the book "
        "is older than the ISBN system.",
    ],
    body="""SELECT ?title ?year
WHERE {
  ?work a                  bs:Work ;
        rdfs:label         ?title ;
        bs:publicationYear ?year .
  OPTIONAL { ?work bs:isbn ?isbn . }
  FILTER( !BOUND(?isbn) )
}
ORDER BY ?year""",
)

q(
    qid="q16", module="03-optional-and-negation",
    title="Towns with no bookshop",
    asks="Which settlements on the map have no bookshop at all?",
    how="NOT EXISTS tests whether a pattern has any match, using the current "
        "row's bindings. It binds nothing itself -- it's a pure test -- so "
        "?shop inside the braces is invisible outside them.",
    diagram="""
    for each ?town:
    ┌──────────────────────────────────────────┐
    │  does ANY ?shop have bs:locatedIn ?town? │
    └──────────────────────────────────────────┘
              │                     │
             yes                    no
              │                     │
           dropped              ✓ kept

    Durham, Perth, Fort William, Truro

    NOT EXISTS is evaluated per row, with ?town already bound.  That
    is what makes it a correlated test rather than a set difference.
    """,
    learn=[
        "NOT EXISTS asks 'is there any match?' and contributes no bindings.",
        "It's correlated: variables bound outside are visible inside.",
        "Prefer it to OPTIONAL + !BOUND when you want nothing from the inner "
        "pattern -- it says what you mean.",
    ],
    body="""SELECT ?townName
WHERE {
  ?town a          bs:Settlement ;
        rdfs:label ?townName .
  FILTER( LANG(?townName) = "en" )
  FILTER NOT EXISTS { ?shop bs:locatedIn ?town . }
}
ORDER BY ?townName""",
)

q(
    qid="q17", module="03-optional-and-negation",
    title="MINUS and NOT EXISTS aren't the same",
    asks="Show the case where swapping MINUS for NOT EXISTS changes the "
         "answer.",
    how="NOT EXISTS evaluates its pattern with the outer bindings in place. "
        "MINUS removes rows by comparing whole solutions, and a MINUS whose "
        "pattern shares no variable with the outer query can remove nothing "
        "at all. This query runs both side by side so the difference is "
        "visible rather than theoretical.",
    diagram="""
    NOT EXISTS { ?shop bs:hasCafe true }
        ?shop is BOUND inside -> a real per-row test
        ──▶ removes the shops that do have a cafe

    MINUS { ?other bs:hasCafe true }
        no shared variable -> nothing to compare on
        ──▶ removes NOTHING

    ┌──────────────┬───────────┬────────────┐
    │              │ shares a  │ removes    │
    │              │ variable? │            │
    ├──────────────┼───────────┼────────────┤
    │ NOT EXISTS   │ n/a       │ correctly  │
    │ MINUS (same) │ yes       │ correctly  │
    │ MINUS (diff) │ no        │ nothing    │
    └──────────────┴───────────┴────────────┘
    """,
    learn=[
        "NOT EXISTS is a test on the current row. MINUS is a set operation on "
        "whole solutions.",
        "MINUS with no shared variable is a silent no-op -- it won't "
        "error, it will just fail to filter.",
        "When in doubt use NOT EXISTS: its correlation behaviour is the one "
        "people expect.",
    ],
    body="""SELECT ?viaNotExists ?viaMinusShared ?viaMinusUnrelated
WHERE {
  # Shops with no cafe, asked three ways.  Only two of them work.
  {
    SELECT (COUNT(*) AS ?viaNotExists) WHERE {
      ?s a bs:Bookshop .
      FILTER NOT EXISTS { ?s bs:hasCafe true . }
    }
  }
  {
    SELECT (COUNT(*) AS ?viaMinusShared) WHERE {
      ?s a bs:Bookshop .
      MINUS { ?s bs:hasCafe true . }
    }
  }
  {
    SELECT (COUNT(*) AS ?viaMinusUnrelated) WHERE {
      ?s a bs:Bookshop .
      MINUS { ?other bs:hasCafe true . }
    }
  }
}""",
)

q(
    qid="q18", module="03-optional-and-negation",
    title="Everyone who worked on a book",
    asks="List every person credited on a work, whether as author or "
         "translator.",
    how="UNION evaluates both branches independently and concatenates the "
        "results. The two branches need not bind the same variables; here "
        "they deliberately bind ?role differently so the output says which "
        "branch a row came from.",
    diagram="""
         ┌──────────────────────────┐
         │ ?work bs:author ?person  │  ──▶ ?role = "author"
         │                          │
         └──────────────────────────┘
                     UNION                    both result sets
         ┌──────────────────────────┐         concatenated
         │ ?work bs:translatedBy ?p │  ──▶ ?role = "translator"
         └──────────────────────────┘

    UNION does NOT deduplicate.  Add DISTINCT if you need that.
    A person appearing in both branches gets two rows, which here
    is exactly right: they did two different jobs.
    """,
    learn=[
        "UNION concatenates; it doesn't merge or deduplicate.",
        "Branches may bind different variables. Anything a branch doesn't "
        "bind comes out unbound for its rows.",
        "Binding a constant per branch is the standard trick for labelling "
        "which alternative matched.",
    ],
    body="""SELECT DISTINCT ?personName ?role
WHERE {
  {
    ?work bs:author ?person .
    BIND( "author" AS ?role )
  }
  UNION
  {
    ?work bs:translatedBy ?person .
    BIND( "translator" AS ?role )
  }
  ?person rdfs:label ?personName .
}
ORDER BY ?personName ?role""",
)

q(
    qid="q19", module="03-optional-and-negation",
    title="Why a FILTER inside OPTIONAL behaves oddly",
    asks="Compare filtering inside an OPTIONAL with filtering after it.",
    how="A FILTER inside OPTIONAL decides whether the optional part matches. "
        "A FILTER after it decides whether the whole row survives. The first "
        "keeps every shop and blanks out the small ones; the second throws "
        "the small ones away entirely.",
    diagram="""
    INSIDE                          AFTER
    OPTIONAL {                      OPTIONAL {
      ?shop bs:floorArea ?a           ?shop bs:floorArea ?a
      FILTER(?a > 250)              }
    }                               FILTER(?a > 250)

    33 rows out                     8 rows out
    small shops kept,               small shops REMOVED --
    ?a unbound                      because an unbound ?a
                                    fails the comparison

    Same words, different place, different answer.  This one catches
    everybody at least once.
    """,
    learn=[
        "A FILTER inside OPTIONAL constrains the optional match. Outside, it "
        "constrains the row.",
        "A comparison on an unbound variable is an error, and an error in a "
        "FILTER means 'drop the row'.",
        "If your OPTIONAL suddenly stops being optional, look for a FILTER "
        "that escaped from its braces.",
    ],
    body="""SELECT ?name ?areaInside
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  OPTIONAL {
    ?shop bs:floorArea ?areaInside .
    FILTER( ?areaInside > 250 )
  }
}
ORDER BY ?name""",
)

# ===========================================================================
# 04  Aggregation
# ===========================================================================

q(
    qid="q20", module="04-aggregation",
    title="How many shops in each town",
    asks="Count the bookshops town by town.",
    how="GROUP BY collapses the matching rows into one row per distinct "
        "?townName, and COUNT reports how many went into each. Every "
        "expression in SELECT must then be either a grouping key or an "
        "aggregate -- there's nowhere else for a value to come from.",
    diagram="""
    rows after matching          after GROUP BY ?townName
    ┌──────────┬──────────┐      ┌──────────┬───────┐
    │ Wigtown  │ Inkwell  │      │ Wigtown  │   2   │
    │ Wigtown  │Marginalia│  ──▶ │ Edinburgh│   2   │
    │ Edinburgh│ Colophon │      │ Hay-on-W │   2   │
    │ Edinburgh│ Broken S │      │ York     │   2   │
    │ York     │ Endpapers│      │ ...      │  ...  │
    │ ...      │ ...      │      └──────────┴───────┘
    └──────────┴──────────┘        one row per group

    SELECT may name ?townName (the key) and COUNT(...) (an aggregate).
    Naming ?shop would be a syntax error: which of the two?
    """,
    learn=[
        "GROUP BY turns many rows into one row per key.",
        "Anything in SELECT must be a grouping key or wrapped in an "
        "aggregate.",
        "COUNT(?x) counts rows where ?x is bound; COUNT(*) counts rows.",
    ],
    body="""SELECT ?townName (COUNT(?shop) AS ?shops)
WHERE {
  ?shop a            bs:Bookshop ;
        bs:locatedIn ?town .
  ?town rdfs:label   ?townName .
  FILTER( LANG(?townName) = "en" )
}
GROUP BY ?townName
ORDER BY DESC(?shops) ?townName""",
)

q(
    qid="q21", module="04-aggregation",
    title="What each shop's stock is worth",
    asks="Total the shelf value of every shop's stock.",
    how="The value of a stock line is copies times price, so the aggregate "
        "has to multiply before it sums. SUM accepts an expression, not just "
        "a variable, which saves a BIND -- though a BIND would be clearer if "
        "the expression got any longer.",
    diagram="""
    each bs:StockRecord:   copies × shelfPrice
                              12   ×   9.99   =  119.88
                               8   ×  10.99   =   87.92
                               5   ×   8.99   =   44.95
                                              ─────────
              SUM per shop, after GROUP BY ?shop   252.75

    SELECT ?name (SUM(?copies * ?price) AS ?value)
                      ─────────┬───────
                        expression, evaluated per row,
                        THEN summed per group
    """,
    learn=[
        "Aggregates take expressions, so arithmetic can happen before the "
        "sum.",
        "ROUND, FLOOR, CEIL and ABS are available for tidying the result.",
        "Grouping by ?shop and selecting ?name works because each shop has "
        "exactly one label -- if it had two, you would need SAMPLE or a "
        "second grouping key.",
    ],
    body="""SELECT ?name (ROUND(SUM(?copies * ?price) * 100) / 100 AS ?stockValue)
WHERE {
  ?record a             bs:StockRecord ;
          bs:atShop     ?shop ;
          bs:copies     ?copies ;
          bs:shelfPrice ?price .
  ?shop   rdfs:label    ?name .
}
GROUP BY ?shop ?name
ORDER BY DESC(?stockValue)
LIMIT 12""",
)

q(
    qid="q22", module="04-aggregation",
    title="Average attendance by kind of event",
    asks="Which kinds of event draw the biggest crowds?",
    how="One row per event goes in; one row per event kind comes out, "
        "carrying the mean, the extremes and the count. Reporting the count "
        "alongside the average is a habit worth forming: an average over two "
        "events means much less than one over twenty.",
    diagram="""
    59 events
       │
       ├─ Launch    ──┐
       ├─ Reading   ──┤   GROUP BY ?kind
       ├─ Panel     ──┤        │
       ├─ Workshop  ──┤        ▼
       └─ ...       ──┘   ┌─────────┬─────┬─────┬─────┬─────┐
                          │ kind    │  n  │ avg │ min │ max │
                          ├─────────┼─────┼─────┼─────┼─────┤
                          │ Launch  │  8  │ 190 │ 102 │ 320 │
                          │ Workshop│  8  │  21 │  14 │  28 │
                          └─────────┴─────┴─────┴─────┴─────┘

    Several aggregates over the same grouping cost one pass.
    """,
    learn=[
        "COUNT, SUM, AVG, MIN, MAX and SAMPLE can all appear in one SELECT "
        "over the same grouping.",
        "Always show the group size next to an average.",
        "MIN and MAX work on any ordered type, including dates and strings.",
    ],
    body="""SELECT ?kind
       (COUNT(?event) AS ?events)
       (ROUND(AVG(?attendance)) AS ?meanAttendance)
       (MIN(?attendance) AS ?smallest)
       (MAX(?attendance) AS ?largest)
WHERE {
  ?event a             bs:Event ;
         bs:eventKind  ?kind ;
         bs:attendance ?attendance .
}
GROUP BY ?kind
ORDER BY DESC(?meanAttendance)""",
)

q(
    qid="q23", module="04-aggregation",
    title="Only the busy shops",
    asks="Which shops held three or more events, and how many people came in "
         "total?",
    how="HAVING filters groups, after aggregation. FILTER can't do this job: "
        "it runs before the grouping, when the aggregate doesn't exist yet. "
        "The two aren't interchangeable and the error message when you "
        "confuse them is rarely helpful.",
    diagram="""
    WHERE   ─▶  filter individual rows      (FILTER lives here)
       │
       ▼
    GROUP BY ─▶ collapse into groups
       │
       ▼
    HAVING  ─▶  filter whole groups         (HAVING lives here)
       │
       ▼
    ORDER BY ─▶ sort what survived

    HAVING( COUNT(?event) >= 3 )
              ────────┬──────
              an aggregate -- only legal after grouping
    """,
    learn=[
        "FILTER runs before GROUP BY; HAVING runs after it.",
        "An aggregate in a FILTER is an error. Aggregates don't exist until "
        "the grouping has happened.",
        "HAVING may use an aggregate you did not select.",
    ],
    body="""SELECT ?name (COUNT(?event) AS ?events) (SUM(?attendance) AS ?totalAudience)
WHERE {
  ?event a             bs:Event ;
         bs:heldAt     ?shop ;
         bs:attendance ?attendance .
  ?shop  rdfs:label    ?name .
}
GROUP BY ?shop ?name
HAVING( COUNT(?event) >= 3 )
ORDER BY DESC(?totalAudience)""",
)

q(
    qid="q24", module="04-aggregation",
    title="List each author's books on one line",
    asks="For each author, put all their titles into a single cell.",
    how="GROUP_CONCAT folds the values of a group into one string with a "
        "separator. It's the aggregate you reach for when the consumer of "
        "the result wants a summary rather than a row per item.",
    diagram="""
    Agnes Varden ─┬─ "Minster Yard"
                  ├─ "The Chapter House"
                  └─ "A Cold Coming"
                        │
       GROUP_CONCAT(?title; SEPARATOR=" / ")
                        │
                        ▼
    "Minster Yard / The Chapter House / A Cold Coming"

    The separator is a keyword argument after a semicolon -- the one
    place in SPARQL where that syntax appears.
    """,
    learn=[
        "GROUP_CONCAT(?x; SEPARATOR=\", \") flattens a group into one string.",
        "The order inside the concatenation isn't guaranteed unless you sort "
        "in a sub-query first.",
        "COUNT alongside it tells the reader how many items were folded in.",
    ],
    notes="engines-differ: the ORDER of the titles inside the concatenated "
          "string isn't specified, and the three engines really do differ. "
          "The set of titles is identical; only the sequence varies. If order "
          "matters, sort in a sub-query first -- and even then, not every "
          "engine promises to honour it.",
    body="""SELECT ?author (COUNT(?book) AS ?titles)
       (GROUP_CONCAT(?title; SEPARATOR=" / ") AS ?works)
WHERE {
  ?book a          bs:Work ;
        rdfs:label ?title ;
        bs:author  ?person .
  ?person rdfs:label ?author .
}
GROUP BY ?person ?author
ORDER BY DESC(?titles) ?author
LIMIT 12""",
)

q(
    qid="q25", module="04-aggregation",
    title="Counting things that aren't there",
    asks="Count events per shop, including the shops that held none.",
    how="A plain GROUP BY over the events can only see shops that appear in "
        "an event, so a shop with none is simply absent. Bringing the shops "
        "in first and making the events OPTIONAL keeps every shop, and "
        "COUNT(?event) then correctly reports zero -- because COUNT ignores "
        "unbound values.",
    diagram="""
    WRONG                          RIGHT
    ?e bs:heldAt ?shop             ?shop a bs:Bookshop
    GROUP BY ?shop                 OPTIONAL { ?e bs:heldAt ?shop }
                                   GROUP BY ?shop

    shops with 0 events            every shop appears
    vanish entirely                     │
                                        ▼
                              COUNT(?event) = 0
                              because COUNT skips unbound

    COUNT(?event)  counts bound values     -> 0 for an empty shop
    COUNT(*)       counts rows             -> 1  ... which is wrong
    """,
    learn=[
        "Aggregating over a join can only see what the join produced. Zeroes "
        "have to be arranged for.",
        "COUNT(?x) ignores unbound ?x; COUNT(*) counts the row regardless. "
        "Here that distinction is the whole answer.",
        "In this dataset every shop has held at least one event, so the two "
        "forms agree -- run it against a shop you've just added and they "
        "won't.",
    ],
    body="""SELECT ?name (COUNT(?event) AS ?events)
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  OPTIONAL { ?event bs:heldAt ?shop . }
}
GROUP BY ?shop ?name
ORDER BY ?events ?name""",
)

q(
    qid="q26", module="04-aggregation",
    title="One number for the whole dataset",
    asks="How many shops, books, authors and events are there altogether?",
    how="An aggregate with no GROUP BY treats the entire result as a single "
        "group, giving exactly one row. Four UNION branches each count one "
        "class, so the answer arrives as a small summary table rather than as "
        "four separate queries.",
    diagram="""
    ┌────────────────────────────┐
    │ ?s a bs:Bookshop  -> "shop"│──┐
    ├────────────────────────────┤  │
    │ ?s a bs:Work      -> "work"│──┤  UNION
    ├────────────────────────────┤  ├──────▶ GROUP BY ?class
    │ ?s a bs:Author  -> "author"│──┤             │
    ├────────────────────────────┤  │             ▼
    │ ?s a bs:Event    -> "event"│──┘      ┌────────┬─────┐
    └────────────────────────────┘         │ author │  32 │
                                           │ event  │  59 │
                                           │ shop   │  33 │
                                           │ work   │  74 │
                                           └────────┴─────┘
    """,
    learn=[
        "An aggregate with no GROUP BY produces exactly one row.",
        "UNION plus a bound constant is the idiom for a summary table.",
        "COUNT(DISTINCT ?x) is what you want whenever the pattern could match "
        "the same resource twice.",
    ],
    body="""SELECT ?class (COUNT(DISTINCT ?s) AS ?count)
WHERE {
  { ?s a bs:Bookshop . BIND( "bookshops" AS ?class ) }
  UNION
  { ?s a bs:Work .     BIND( "works"     AS ?class ) }
  UNION
  { ?s a bs:Author .   BIND( "authors"   AS ?class ) }
  UNION
  { ?s a bs:Event .    BIND( "events"    AS ?class ) }
}
GROUP BY ?class
ORDER BY ?class""",
)
