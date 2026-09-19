# ==========================================================================
#  Q123  The update that empties the store
# ==========================================================================
#
#  ASKS
#    What does one careless pattern cost?
#
#  HOW IT WORKS
#    Everything. DELETE WHERE with three variables matches every triple in
#    the default graph and removes all of them. There is no confirmation,
#    no transaction to roll back on most setups, and no undo. It is worth
#    running once, deliberately, on a copy -- the point lands better than a
#    warning does.
#
#  DIAGRAM
#        DELETE WHERE { ?s ?p ?o }
#
#          4826 triples  ->  0
#
#        +----------------------------------------------------------+
#        |  no prompt   no confirmation   no undo   no error         |
#        |  the operation succeeds. That is the problem with it.     |
#        +----------------------------------------------------------+
#
#        The three habits that prevent it:
#
#          1  Write the WHERE as a SELECT first and look at the rows.
#             Every deletion in this module was written that way.
#
#          2  Keep the endpoint read-only unless it needs to write.
#             Fuseki serves /query and /update separately, and most
#             deployments should never expose the second one.
#
#          3  Back up before a migration, not after noticing.
#                 holos backup --store DIR --to DIR
#                 java -cp ... tdb2.tdbbackup --loc DIR
#
#        And a fourth, for the query itself: LIMIT does nothing here.
#        There is no such thing as deleting the first ten matches.
#
#        A note on what "the default graph" means. This removes the
#        default graph only; named graphs survive, which makes the
#        damage look smaller than it is until somebody checks. DROP ALL
#        is the one that takes everything.
#
#
#  WHAT TO TAKE AWAY
#    - DELETE WHERE { ?s ?p ?o } empties the default graph, succeeds
#      quietly, and cannot be undone.
#    - Write every deletion as a SELECT first. It costs one run and it is
#      the only real safeguard.
#    - Separate read and write endpoints, and back up before migrating.
#      An update endpoint open to the internet is an open door.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  1 row, on every engine that runs it
# ==========================================================================



DELETE WHERE {
  ?s ?p ?o .
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT (COUNT(*) AS ?triplesLeft)
#  WHERE {
#    ?s ?p ?o .
#  }
