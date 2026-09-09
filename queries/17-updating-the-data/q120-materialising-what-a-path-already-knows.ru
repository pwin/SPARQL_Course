# ==========================================================================
#  Q120  Materialising what a path already knows
# ==========================================================================
#
#  ASKS
#    Every shop is in a country by way of two or three bs:within hops.
#    Write that down as one triple per shop.
#
#  HOW IT WORKS
#    INSERT ... WHERE is CONSTRUCT that keeps its output. The WHERE walks
#    the path from module 05; the template records the answer. Afterwards
#    the same question is a single triple pattern, which is faster to
#    answer and easier for anything downstream to consume.
#
#  DIAGRAM
#        what the path costs, every time it is asked:
#
#          ?shop bs:locatedIn ?town .
#          ?town bs:within+ ?country .            <- two or three hops,
#          ?country a bs:Country .                   evaluated per shop
#
#        what the update leaves behind:
#
#          ?shop bs:inCountry ?country .          <- one hop
#
#        +-------------+--------+
#        | England     |     20 |
#        | Scotland    |      9 |
#        | Wales       |      4 |
#        +-------------+--------+
#                         33 shops, each in exactly one country
#
#        This is materialisation, and it is a trade rather than a win:
#
#          faster to query        the derived triples are now data,
#          simpler downstream     and nothing keeps them true. Move a
#                                 shop to another town and bs:inCountry
#                                 still says the old country.
#
#        So either re-run it after every change, or do not store it and
#        pay the path cost at query time. What you must not do is store
#        it and forget which of the two you chose.
#
#        bs:inCountry is not in the vocabulary file. Derived shortcuts
#        usually are not, which is another reason to keep them clearly
#        separable -- a named graph is the usual answer, and module 08
#        has the mechanism.
#
#
#  WHAT TO TAKE AWAY
#    - INSERT ... WHERE is a CONSTRUCT whose output is kept. Anything you
#      can construct, you can materialise.
#    - Materialised triples are stale the moment the facts they came from
#      change. Decide who re-runs them, and when.
#    - Keep derived triples separable from asserted ones — a named graph
#      is the cheapest way — so they can be dropped and rebuilt.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  3 rows, on every engine that runs it
# ==========================================================================

PREFIX bs:   <https://example.org/bookshop-trail/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

INSERT { ?shop bs:inCountry ?country }
WHERE {
  ?shop    a            bs:Bookshop ;
           bs:locatedIn ?town .
  ?town    bs:within+   ?country .
  ?country a            bs:Country .
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?country (COUNT(?shop) AS ?shops)
#  WHERE {
#    ?shop    bs:inCountry ?country .
#    ?country rdfs:label   ?name .
#    FILTER( LANG(?name) = "en" )
#  }
#  GROUP BY ?country
#  ORDER BY DESC(?shops) ?country
