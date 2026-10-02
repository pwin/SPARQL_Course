# -*- coding: utf-8 -*-
"""Federation: SERVICE, and a real remote endpoint.

These four queries call dbpedia.org, so they need the internet and they are
skipped by the checker unless you pass --network. Everything they claim about
the three engines was measured:

    python scripts/check_queries.py --network q105 q106 q107 q108

The join works because the towns in this dataset are real. Every settlement
carries owl:sameAs to its DBpedia resource -- thirty links, all verified to
resolve -- so a federated query has something better to join on than a string
match against a label.
"""

from querycat import q, D11, DTRIG, ALL, EDITOR, HOLOS, FUSEKI

MOD = "08-named-graphs"

q(
    qid="q105", module=MOD,
    title="Bringing in DBpedia",
    asks="How many people live in each of the three book towns, according to "
         "DBpedia?",
    how="SERVICE sends part of the query to another endpoint and joins the "
        "answer back. The join key is owl:sameAs: the shops are invented but "
        "the towns are real, and each one carries a link to its DBpedia "
        "resource, so the remote side is asked about a resource rather than a "
        "name.",
    diagram="""
    here                                    dbpedia.org
    ----                                    -----------
    ?town a bs:Settlement ;
          bs:isBookTown true ;
          rdfs:label ?name ;
          owl:sameAs ?dbp  ------------->  ?dbp dbo:populationTotal ?population
                            SERVICE
              |                                        |
              '--------------- joined on ?dbp ---------'

    what comes back:

      Sedbergh    2765
      Hay-on-Wye  (DBpedia has no populationTotal for it)
      Wigtown     (nor for this one)

    So the join drops two of the three -- and that is not a bug in
    the query, it is what the remote data is like. q106 is about
    getting them back.

    owl:sameAs is what makes this work. Matching "Sedbergh" the
    string against a remote label would find the right town by luck;
    matching the IRI finds it by identity.
    """,
    learn=[
        "SERVICE evaluates a pattern at another endpoint and joins the result "
        "into the surrounding query.",
        "Federate on identifiers, not on labels. owl:sameAs is the link that "
        "makes two datasets about the same thing joinable.",
        "The remote side is someone else's data, with its own gaps. A join "
        "that drops rows is usually telling you about their coverage, not "
        "your query.",
    ],
    body="""SELECT ?name ?population
WHERE {
  ?town a          bs:Settlement ;
        bs:isBookTown true ;
        rdfs:label ?name ;
        owl:sameAs ?dbp .
  FILTER( LANG(?name) = "en" )

  SERVICE <https://dbpedia.org/sparql> {
    ?dbp dbo:populationTotal ?population .
  }
}
ORDER BY ?name""",
    extra_prefixes=("owl", "dbo"),
    engines=(EDITOR, FUSEKI),
    network=True,
    notes="One row on every engine that runs it: DBpedia holds a population for "
          "Sedbergh and not for the other two book towns." + chr(10) * 2 +
          "HOLOS refuses remote SERVICE outright -- see q108, which is about "
          "why. The browser editor runs HOLOS and *does* federate, because a "
          "browser is not a server: the request is the reader's own, from "
          "their own machine, and the editor keeps an allow-list of endpoints "
          "a shared query file may reach." + chr(10) * 2 +
          "It returned **no rows** until holos-wasm 0.20.0, and the reason is "
          "worth more than the fix. ?dbp is bound out here, but the editor "
          "sent the SERVICE pattern to DBpedia as it stood --" + chr(10) +
          "    SELECT ?dbp ?population WHERE { ?dbp dbo:populationTotal ?population }" + chr(10) +
          "-- which asks for every population in DBpedia. DBpedia caps the "
          "answer at ten thousand rows, the three book towns were not among "
          "them, and the join found nothing. Correct query, correct engine, "
          "empty answer." + chr(10) * 2 +
          "What was missing is called a bound join: sending the keys with the "
          "question, so the endpoint is asked about three resources instead "
          "of scanned for all of them. Every engine that answers this query "
          "does it; q107 is the same question written so that no engine has "
          "to. If an engine ever hands you nothing here, that is what it is "
          "not doing.",
)

q(
    qid="q106", module=MOD,
    title="Keeping the rows the remote side cannot answer",
    asks="List all three book towns, with the population where DBpedia has "
         "one.",
    how="The obvious fix for q105 dropping rows is to wrap the SERVICE in an "
        "OPTIONAL, and that is exactly right: a town DBpedia has no population "
        "for keeps its row, with the column empty. What the OPTIONAL cannot do "
        "is make the remote call selective -- so on an engine that sends the "
        "clause unbound, as the browser editor did before holos-wasm 0.20.0, "
        "all three rows survive with all three columns empty, and nothing "
        "looks wrong.",
    diagram="""
    OPTIONAL {
      SERVICE <https://dbpedia.org/sparql> {
        ?dbp dbo:populationTotal ?population
      }
    }

    measured, this dataset, this endpoint:

      +---------+-------+---------------------------------------+
      | Fuseki  | 3 rows| Sedbergh 2765, the other two blank  ok |
      | editor  | 3 rows| Sedbergh 2765, the other two blank  ok |
      | HOLOS   |   --  | refuses remote SERVICE entirely       |
      +---------+-------+---------------------------------------+

    Before holos-wasm 0.20.0 the editor returned those same three rows
    with the population empty in all of them -- the right row count and
    the wrong data, which is the hardest kind of difference to notice.
    The OPTIONAL was never what was wrong: take it away and you have
    q105, where the same unbound clause returned no rows at all.

    q107 is the shape that never depended on the engine.
    """,
    learn=[
        "OPTIONAL around SERVICE is the usual way to keep rows the remote side "
        "cannot answer, and it is not portable.",
        "Check a federated query on the engine you will actually run it on. "
        "The row count agreeing proves nothing.",
        "When it does not work, push the values in explicitly instead -- q107.",
    ],
    body="""SELECT ?name ?population
WHERE {
  ?town a          bs:Settlement ;
        bs:isBookTown true ;
        rdfs:label ?name ;
        owl:sameAs ?dbp .
  FILTER( LANG(?name) = "en" )

  OPTIONAL {
    SERVICE <https://dbpedia.org/sparql> {
      ?dbp dbo:populationTotal ?population .
    }
  }
}
ORDER BY ?name""",
    extra_prefixes=("owl", "dbo"),
    engines=(EDITOR, FUSEKI),
    network=True,
    notes="Three rows, two of them with an empty population, because DBpedia "
          "has one for Sedbergh and not for Hay-on-Wye or Wigtown. That is "
          "the OPTIONAL doing its job: without it those two towns would "
          "disappear rather than appear incomplete." + chr(10) * 2 +
          "Worth knowing what this used to show. Until holos-wasm 0.20.0 the "
          "browser editor returned all three rows with *every* population "
          "empty, because it sent the SERVICE pattern to DBpedia unbound -- "
          "see q105. Same three rows, same shape of answer, one real value "
          "missing from it. A federated query that returns the row count you "
          "expected has told you nothing about whether it worked.",
)

q(
    qid="q107", module=MOD,
    title="Sending the list with the question",
    asks="Ask DBpedia about a batch of towns in one round trip, in a way both "
         "engines answer.",
    how="Rather than relying on the engine to push bindings across, put them "
        "in the SERVICE block yourself with VALUES. The remote endpoint gets "
        "one self-contained query naming exactly the resources you care "
        "about, and there is nothing for an engine to get wrong.",
    diagram="""
    SERVICE <https://dbpedia.org/sparql> {
      VALUES ?dbp {
        <http://dbpedia.org/resource/York>
        <http://dbpedia.org/resource/Bath,_Somerset>
        ...
      }
      ?dbp dbo:populationTotal ?population .
    }

    five IRIs go out, four answers come back:

      +-------------------------+------------+
      | York                    |    141,685 |
      | Bath, Somerset          |     94,092 |
      | Penzance                |     20,734 |
      | Sedbergh                |      2,765 |
      | Norwich                 |  -- no dbo:populationTotal --
      +-------------------------+------------+

    Norwich drops out for the same reason Hay-on-Wye did in q105.
    Asking for five things and getting four is normal when the data
    is somebody else's.

    why this is the shape to reach for:

      - both engines answer it identically
      - one round trip rather than one per row
      - the remote endpoint sees a query it can plan properly
      - you can paste the SERVICE block straight into DBpedia's own
        form to see what it does on its own

    The cost is that the list is fixed. Generate the VALUES block
    from a first, local query when it needs to vary.
    """,
    learn=[
        "VALUES inside a SERVICE block sends the keys with the question, which "
        "is the most portable way to federate.",
        "One round trip for n resources beats n round trips. Federation is "
        "dominated by latency, not by matching.",
        "A self-contained SERVICE block can be tested directly against the "
        "remote endpoint, which is how you tell whose fault an empty result "
        "is.",
        "And it is the version that runs everywhere. q105 asks the same "
        "question and depends on the engine pushing the keys in for you; this "
        "one asks nothing of the engine, so Fuseki, Comunica and the browser "
        "editor all return the same four rows. Portability here is not a "
        "nicety -- it is the difference between a query that works and one "
        "that works on your engine.",
    ],
    body="""SELECT ?dbp ?population
WHERE {
  SERVICE <https://dbpedia.org/sparql> {
    VALUES ?dbp {
      <http://dbpedia.org/resource/York>
      <http://dbpedia.org/resource/Bath,_Somerset>
      <http://dbpedia.org/resource/Penzance>
      <http://dbpedia.org/resource/Sedbergh>
      <http://dbpedia.org/resource/Norwich>
    }
    ?dbp dbo:populationTotal ?population .
  }
}
ORDER BY DESC(?population)""",
    extra_prefixes=("dbo",),
    engines=(EDITOR, FUSEKI),
    network=True,
)

q(
    qid="q108", module=MOD,
    title="When the other end is not there",
    asks="What happens when the remote endpoint is unreachable, and why does "
         "HOLOS refuse to call one at all?",
    how="SERVICE SILENT tells the engine to carry on with no bindings rather "
        "than fail when a remote call goes wrong. Fuseki honours it. HOLOS "
        "declines to make the request at all, and its reason is worth "
        "understanding. The browser editor, which now runs HOLOS, refuses "
        "this endpoint too -- it is not on the editor's allow-list -- and "
        "then raises rather than shrugging, for a reason that is about the "
        "protocol between the engine and the page and not about SILENT.",
    diagram="""
    SERVICE SILENT <https://endpoint.invalid/sparql> { ... }

    measured against a host that does not exist:

      +---------+------------------+--------------------------+
      |         | SERVICE          | SERVICE SILENT           |
      +---------+------------------+--------------------------+
      | Fuseki  | error            | 3 rows, no bindings   ok |
      | editor  | error            | error                    |
      | HOLOS   | refuses          | refuses                  |
      +---------+------------------+--------------------------+

    WHY HOLOS REFUSES

    A SERVICE IRI is a URL chosen by whoever wrote the query. An
    engine that follows it will make its server issue a request to
    that address -- from inside your network:

        SERVICE <http://169.254.169.254/latest/meta-data/>
        SERVICE <http://localhost:9200/>
        SERVICE <http://admin.internal/>

    That is server-side request forgery, and the query language is
    the attack surface. HOLOS evaluates SERVICE only against
    endpoints registered in the process, and refuses remote HTTP
    outright; it refuses remote LOAD for the same reason. Enabling
    it safely needs an allow-list, which is a policy decision rather
    than a default.

    Not a bug, then, but a position. Worth knowing which position
    your own endpoint takes before you expose it.
    """,
    learn=[
        "SERVICE SILENT continues with no bindings instead of failing. Fuseki "
        "honours it. The browser editor refuses the remote call and then "
        "raises, so SILENT buys you nothing there -- measured, not assumed; "
        "the NOTE says why that is the protocol's doing.",
        "A public endpoint that follows arbitrary SERVICE IRIs will make "
        "requests to any address a stranger names, including ones only it can "
        "reach. That is SSRF, and it is why HOLOS refuses.",
        "Federation is a network operation wearing the clothes of a join: it "
        "can be slow, it can fail, and it can be a security question.",
    ],
    body="""SELECT ?name ?remote
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .

  # The host does not exist. SILENT is what decides whether that
  # ends the query or is simply shrugged off.
  SERVICE SILENT <https://endpoint.invalid/sparql> {
    ?shop bs:somethingRemote ?remote .
  }
}
ORDER BY ?name
LIMIT 5""",
    engines=(FUSEKI,),
    network=True,
    notes="Fuseki is the one that actually calls out and shrugs the failure "
          "off: five rows, no population column, which is SILENT doing "
          "exactly what it says." + chr(10) * 2 +
          "The browser editor runs HOLOS in WebAssembly, which has no network "
          "client, so federation there is a conversation: the engine reports "
          "the endpoint and query it wants, the page fetches, and the query "
          "is run again. What the engine reports is the endpoint and the "
          "query -- and not whether the clause was written SILENT. So when "
          "the page declines endpoint.invalid, as it declines anything not on "
          "its allow-list, it cannot tell \"could not call, and the query said "
          "carry on\" apart from \"could not call, and the answer would be "
          "wrong without it\", and it raises. Refusing the call is the "
          "position; raising is the cost of a protocol that does not carry "
          "the one word that would settle it." + chr(10) * 2 +
          "Native HOLOS refuses remote SERVICE outright, SILENT or not, which "
          "is why this query claims only Fuseki.",
)


# --- the dataset clauses -------------------------------------------------
#
# These two belong with q48-q51 rather than with federation, and `place`
# puts them there: query ids are permanent, reading order is not.

q(
    qid="q124", module=MOD, place=51.7,
    title="Choosing the dataset in the query",
    asks="Answer a question against two of the ten graphs and ignore the "
         "rest.",
    how="FROM names the graphs to merge into the default graph for this query "
        "only. Nothing is copied and nothing is changed: the engine builds a "
        "dataset for the duration of the query, and the ordinary triple "
        "patterns see exactly that. It is the cheapest way to scope a "
        "question.",
    diagram="""
    the store                         this query's dataset
    ---------                         --------------------
    bt:graph-vocabulary
    bt:graph-genres
    bt:graph-places      ------\
    bt:graph-shops       ---\   \
    bt:graph-people          \   '--> default graph
    bt:graph-books            '-----> (places + shops merged)
    bt:graph-events
    bt:graph-trail                    everything else: invisible
    bt:graph-stock
    bt:graph-claims

    FROM bt:graph-shops
    FROM bt:graph-places

    Two clauses, one default graph. FROM does not give you two
    graphs you can tell apart -- for that you want FROM NAMED and
    GRAPH, which is q125.

    +----------------------------------------------------------+
    |  no FROM at all   the service decides what the default    |
    |                   graph is, and services disagree. On     |
    |                   this TriG file the default graph holds  |
    |                   only the descriptions of the graphs,    |
    |                   so ?s a bs:Bookshop finds nothing.      |
    |                   That is q50's surprise.                 |
    +----------------------------------------------------------+

    A caution worth carrying: FROM takes an IRI, and an engine
    that does not hold that graph may go and fetch it over HTTP.
    Same exposure as SERVICE and LOAD.
    """,
    learn=[
        "FROM builds this query's default graph by merging the graphs it "
        "names. It reads; it does not copy or change anything.",
        "Several FROM clauses merge into one graph. Use FROM NAMED when you "
        "need to know which graph a fact came from.",
        "Without a dataset clause you get whatever the service calls the "
        "default graph, and that is not standardised.",
    ],
    body="""SELECT ?name ?town
FROM bt:graph-shops
FROM bt:graph-places
WHERE {
  ?shop a            bs:Bookshop ;
        rdfs:label   ?name ;
        bs:locatedIn ?place .
  ?place rdfs:label  ?town .
  FILTER( LANG(?town) = "en" )
}
ORDER BY ?name
LIMIT 8""",
    data=DTRIG,
)

q(
    qid="q125", module=MOD, place=51.8,
    title="Keeping the graphs apart",
    asks="Count the triples in two named graphs, and say which is which.",
    how="FROM NAMED adds a graph to the dataset without merging it, so GRAPH "
        "can still name it. This is the pairing that gives you provenance: "
        "FROM for the facts you want to treat as one body, FROM NAMED for the "
        "ones whose origin matters.",
    diagram="""
    FROM        merges into the default graph -- origin lost
    FROM NAMED  keeps the graph addressable   -- origin kept

    FROM NAMED bt:graph-shops
    FROM NAMED bt:graph-places
    WHERE { GRAPH ?g { ?s ?p ?o } }

      +-------------------------+-------+
      | bt:graph-places         |   794 |
      | bt:graph-shops          |   588 |
      +-------------------------+-------+

    and the eight other graphs contribute nothing, because they
    are not in this query's dataset at all.

    measured:

      FROM         editor  yes    holos  yes    fuseki  yes
      FROM NAMED   editor  yes    holos  yes    fuseki  yes

    Both work in the browser since the editor moved to the HOLOS
    engine -- two rows, measured. The Comunica build before it raised
    rather than answering: over an in-memory store it had no actor for
    the pattern a FROM NAMED dataset produces, so the advice used to be
    to scope with FROM and keep FROM NAMED for a real endpoint.
    """,
    learn=[
        "FROM NAMED puts a graph in the dataset without merging it, so GRAPH "
        "can still ask which graph a fact is in.",
        "FROM and FROM NAMED are independent. A query can have both, and a "
        "graph named only by FROM NAMED is not in the default graph.",
        "The browser editor supports FROM NAMED as of its move to the HOLOS "
        "engine; the Comunica build it used before did not, and errored "
        "rather than ignoring the clause. Still check the dataset clauses on "
        "the engine you will deploy against: support is not universal.",
    ],
    body="""SELECT ?graph (COUNT(*) AS ?triples)
FROM NAMED bt:graph-shops
FROM NAMED bt:graph-places
WHERE {
  GRAPH ?graph { ?s ?p ?o }
}
GROUP BY ?graph
ORDER BY ?graph""",
    data=DTRIG,
    engines=ALL,
    notes="Fuseki and HOLOS. Comunica raises \"none of the configured actors "
          "were able to handle the operation type pattern\" for FROM NAMED "
          "over an in-memory store; FROM on its own (q124) works there.",
)
