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

from querycat import q, D11, ALL, EDITOR, HOLOS, FUSEKI

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
    notes="HOLOS refuses remote SERVICE outright -- see q108, which is about "
          "why. On the other two this returns one row, because DBpedia holds "
          "a population for Sedbergh and not for the other two book towns.",
)

q(
    qid="q106", module=MOD,
    title="Keeping the rows the remote side cannot answer",
    asks="List all three book towns, with the population where DBpedia has "
         "one.",
    how="The obvious fix for q105 dropping rows is to wrap the SERVICE in an "
        "OPTIONAL, and on Jena that is exactly right. In the browser editor it "
        "returns all three rows and no populations at all: Comunica does not "
        "push the outer binding into a SERVICE nested inside an OPTIONAL. Same "
        "query, same endpoint, different answer.",
    diagram="""
    OPTIONAL {
      SERVICE <https://dbpedia.org/sparql> {
        ?dbp dbo:populationTotal ?population
      }
    }

    measured, this dataset, this endpoint:

      +---------+-------+---------------------------------------+
      | Fuseki  | 3 rows| Sedbergh 2765, the other two blank  ok |
      | editor  | 3 rows| ALL THREE blank                       |
      | HOLOS   |   --  | refuses remote SERVICE entirely       |
      +---------+-------+---------------------------------------+

    Comunica gets the row count right and the data wrong, which is
    the hardest kind of difference to notice.

    Without the OPTIONAL (q105) both engines agree, because then the
    binding goes in as part of an ordinary join. The disagreement is
    specifically about OPTIONAL wrapping SERVICE.

    q107 is the shape that works on both.
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
    notes="engines-differ: and the difference is the lesson. Fuseki fills in "
          "Sedbergh's population; the browser editor returns the same three "
          "rows with the column empty, because Comunica does not carry the "
          "outer binding into a SERVICE inside an OPTIONAL.",
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
        "than fail when a remote call goes wrong. Fuseki honours it. The "
        "browser editor raises anyway. HOLOS declines to make the request in "
        "the first place, and its reason is worth understanding.",
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
        "honours it; Comunica raises anyway, so do not rely on it in the "
        "browser.",
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
    notes="Fuseki only. The browser editor raises rather than honouring "
          "SILENT, and HOLOS refuses remote SERVICE altogether -- which is "
          "the point of the query rather than a limitation of it.",
)
