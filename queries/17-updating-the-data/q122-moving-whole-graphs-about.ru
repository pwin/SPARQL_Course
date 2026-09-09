# ==========================================================================
#  Q122  Moving whole graphs about
# ==========================================================================
#
#  ASKS
#    Copy one named graph, then drop another, without touching a single
#    triple pattern.
#
#  HOW IT WORKS
#    Graph management is its own small language: LOAD, CLEAR, DROP, COPY,
#    MOVE and ADD work on whole graphs at a time. They are far faster than
#    the equivalent INSERT/DELETE, and they are how a staging graph gets
#    promoted to a live one.
#
#  DIAGRAM
#        COPY  <a> TO <b>     b is emptied, then a's contents put in it
#        MOVE  <a> TO <b>     the same, and then a is dropped
#        ADD   <a> TO <b>     a's contents added; b keeps what it had
#        DROP  GRAPH <a>      the graph and its name, gone
#        CLEAR GRAPH <a>      emptied, but the name remains
#
#        the difference that catches people:
#
#          COPY  destination emptied first     ADD  destination kept
#
#        the trail dataset, in graphs:
#
#          bt:graph-places     places, councils, regions, countries
#          bt:graph-shops      the bookshops
#          bt:graph-people     authors and publishers
#          bt:graph-events     readings, launches, fairs
#          ... and six more
#
#        after COPY bt:graph-shops TO bt:graph-shops-backup
#          and DROP GRAPH bt:graph-events :
#
#          shops-backup holds exactly what shops holds
#          events is gone -- not empty, gone
#
#        LOAD <http://somewhere/data.ttl> INTO GRAPH <g> fetches over
#        the network, and it is the same exposure as SERVICE in q108:
#        a URL chosen by whoever wrote the request, fetched by your
#        server. HOLOS refuses remote LOAD for that reason.
#
#
#  WHAT TO TAKE AWAY
#    - COPY, MOVE, ADD, DROP and CLEAR act on whole graphs and are much
#      cheaper than the pattern-based equivalent.
#    - COPY and MOVE empty the destination first; ADD does not. DROP
#      removes the graph, CLEAR only empties it.
#    - LOAD fetches a URL of the requester's choosing. Treat it like
#      SERVICE, and expect a careful engine to refuse it.
#
#  NOTE
#    Fuseki and HOLOS. Comunica's update handling of whole-graph operations
#    over an in-memory store is not something this course relies on, and
#    the editor cannot run an update at all.
#
#  DATA     bookshop-trail.trig
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail.trig
#  RUNS ON  holos, fuseki
#  RETURNS  10 rows, on every engine that runs it
# ==========================================================================

PREFIX bt: <https://example.org/bookshop-trail/>

COPY bt:graph-shops TO bt:graph-shops-backup ;

DROP GRAPH bt:graph-events


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?graph (COUNT(*) AS ?triples)
#  WHERE {
#    GRAPH ?graph { ?s ?p ?o }
#  }
#  GROUP BY ?graph
#  ORDER BY ?graph
