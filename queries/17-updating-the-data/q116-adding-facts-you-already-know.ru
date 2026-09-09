# ==========================================================================
#  Q116  Adding facts you already know
# ==========================================================================
#
#  ASKS
#    Add a new bookshop to the trail.
#
#  HOW IT WORKS
#    INSERT DATA takes ground triples — no variables, no WHERE — and puts
#    them in the store. It is the simplest thing in SPARQL Update and the
#    one you will use least, because most of what you want to add depends
#    on what is already there.
#
#  DIAGRAM
#        INSERT DATA {
#          bt:shop-foxed-page a bs:Bookshop ; ... .
#        }
#                 |
#                 '-- ground triples only. A variable here is a syntax error.
#
#        before                    after
#        ------                    -----
#        2 shops in Hay-on-Wye     3
#          Castle Steps Books        Castle Steps Books
#          The Clock Tower           The Clock Tower
#                                    The Foxed Page      <- new
#
#        Pick a subject that does not already exist. INSERT DATA on an
#        IRI that is already in the store adds to it rather than
#        replacing it -- which is q119's whole subject, arrived at by
#        accident.
#
#        An update returns nothing: no rows, no count, no graph. Fuseki
#        answers HTTP 204 and HOLOS prints "inserted 5 deleted 0". That
#        is the whole feedback, which is why the second half of every
#        query in this module is a SELECT.
#
#        INSERT DATA is also idempotent. Running it twice adds nothing
#        the second time, because a graph is a set: the same triple is
#        already there.
#
#
#  WHAT TO TAKE AWAY
#    - INSERT DATA adds ground triples. No variables, no WHERE clause.
#    - An update produces no result, so pair every one with a query that
#      shows what changed. Get into the habit now.
#    - Adding a triple that is already present does nothing. RDF graphs
#      are sets, so updates that only insert are safe to re-run.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  3 rows, on every engine that runs it
# ==========================================================================

PREFIX bt:   <https://example.org/bookshop-trail/>
PREFIX bs:   <https://example.org/bookshop-trail/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
  bt:shop-foxed-page
      a            bs:Bookshop ;
      rdfs:label   "The Foxed Page"@en ;
      bs:locatedIn bt:place-hay-on-wye ;
      bs:founded   "2019"^^xsd:gYear ;
      bs:hasCafe   true .
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?name ?founded
#  WHERE {
#    ?shop a            bs:Bookshop ;
#          bs:locatedIn bt:place-hay-on-wye ;
#          rdfs:label   ?name .
#    OPTIONAL { ?shop bs:founded ?founded }
#  }
#  ORDER BY ?name
