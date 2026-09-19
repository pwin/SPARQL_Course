# ==========================================================================
#  Q117  Removing facts you can name
# ==========================================================================
#
#  ASKS
#    The Inkwell has closed its cafe. Remove that one fact.
#
#  HOW IT WORKS
#    DELETE DATA is the mirror of INSERT DATA: ground triples, removed
#    exactly. It will not accept a variable, which makes it safe and almost
#    useless -- you have to already know the object you are deleting, down
#    to its datatype.
#
#  DIAGRAM
#        DELETE DATA { bt:shop-inkwell bs:hasCafe true . }
#
#        the triple has to match EXACTLY:
#
#          bs:hasCafe true                  matches
#          bs:hasCafe "true"                does not -- a string
#          bs:hasCafe "true"^^xsd:boolean   matches -- same term
#          bs:hasCafe ?anything             SYNTAX ERROR
#
#        +--------------------+--------+-------+
#        |                    | before | after |
#        +--------------------+--------+-------+
#        | says true          |     22 |    21 |
#        | says false         |     11 |    11 |
#        | says nothing       |      0 |     1 |
#        +--------------------+--------+-------+
#
#        That last row is The Inkwell, and it now says NOTHING about a
#        cafe -- which is not the same as saying it has none. Deleting a
#        fact leaves silence, not a denial.
#
#        Deleting a triple that is not there is not an error. It quietly
#        does nothing -- so a DELETE DATA that achieves nothing looks
#        exactly like one that worked.
#
#
#  WHAT TO TAKE AWAY
#    - DELETE DATA removes ground triples and takes no variables. The
#      terms must match exactly, datatype included.
#    - Deleting a fact leaves the absence of a fact, not its negation. In
#      RDF those are different, and q16's lesson applies here too.
#    - A DELETE that matches nothing is silent. Check with a query rather
#      than assuming.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  3 rows, on every engine that runs it
# ==========================================================================

PREFIX bt: <https://example.org/bookshop-trail/>
PREFIX bs: <https://example.org/bookshop-trail/schema#>

DELETE DATA {
  bt:shop-inkwell bs:hasCafe true .
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?state (COUNT(*) AS ?shops)
#  WHERE {
#    ?shop a bs:Bookshop .
#    OPTIONAL { ?shop bs:hasCafe ?cafe }
#    BIND( COALESCE(STR(?cafe), "no statement") AS ?state )
#  }
#  GROUP BY ?state
#  ORDER BY ?state
