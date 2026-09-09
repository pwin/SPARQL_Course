# ==========================================================================
#  Q118  Removing whatever matches
# ==========================================================================
#
#  ASKS
#    Drop every bs:hasCafe false statement, on the grounds that they say
#    nothing a missing statement would not.
#
#  HOW IT WORKS
#    DELETE WHERE is the shorthand that finally allows variables: the
#    pattern is both the thing to match and the thing to remove, written
#    once. It is the most useful deletion form and the most dangerous,
#    because the pattern that matches too much removes too much.
#
#  DIAGRAM
#        DELETE WHERE { ?shop bs:hasCafe false }
#                       -----------------------
#                       matched AND deleted -- the same block does both
#
#        equivalent long form:
#
#          DELETE { ?shop bs:hasCafe false }
#          WHERE  { ?shop bs:hasCafe false }
#
#        +--------------------+--------+-------+
#        |                    | before | after |
#        +--------------------+--------+-------+
#        | says true          |     22 |    22 |
#        | says false         |     11 |     0 |
#        | says nothing       |      0 |    11 |
#        +--------------------+--------+-------+
#
#        Whether this is an improvement depends entirely on whether you
#        were relying on "false" meaning "we checked, and no". Once the
#        statement is gone, that shop is indistinguishable from one
#        nobody has asked about.
#
#        Now widen the pattern by one step and read it again:
#
#            DELETE WHERE { ?s bs:hasCafe ?o }     both kinds gone
#            DELETE WHERE { ?s ?p ?o }             everything gone
#
#        q123 is about that second one.
#
#
#  WHAT TO TAKE AWAY
#    - DELETE WHERE matches and deletes with one pattern. It is the form
#      you will reach for most.
#    - Run the pattern as a SELECT first, every time. The pattern is the
#      whole of what makes a deletion safe.
#    - Removing a false statement is not the same as leaving it. Decide
#      which of the two your consumers expect.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  2 rows, on every engine that runs it
# ==========================================================================

PREFIX bs: <https://example.org/bookshop-trail/schema#>

DELETE WHERE {
  ?shop bs:hasCafe false .
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
