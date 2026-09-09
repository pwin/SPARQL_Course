# ==========================================================================
#  Q137  Emptying, moving and merging graphs
# ==========================================================================
#
#  ASKS
#    Empty one graph, move a second into a third, and merge a fourth into
#    it.
#
#  HOW IT WORKS
#    q122 covered COPY and DROP. These are the other three, and the
#    distinctions between them are the whole of the vocabulary: CLEAR
#    empties but keeps the name, MOVE is a copy that removes the source,
#    and ADD merges without emptying the destination first.
#
#  DIAGRAM
#        CLEAR GRAPH <a>     a is empty. The name still exists.
#        DROP  GRAPH <a>     a is gone. Asking for it is an error.
#
#        MOVE <a> TO <b>     b emptied, a's contents moved in, a dropped
#        COPY <a> TO <b>     b emptied, a's contents copied in, a kept
#        ADD  <a> TO <b>     b KEPT, a's contents added, a kept
#
#        applied to the trail dataset:
#
#          CLEAR GRAPH bt:graph-claims       243 triples -> 0, name kept
#          MOVE bt:graph-trail TO bt:graph-archive
#                                            trail gone, archive has 429
#          ADD bt:graph-people TO bt:graph-books
#                                            books 918 + people 301 = 1219
#
#        +----------------------------------------------------------+
#        |  ADD is the one to reach for when merging, and the one    |
#        |  people reach for COPY instead of. COPY silently empties  |
#        |  the destination first, so a merge written with COPY      |
#        |  destroys whatever was already there.                     |
#        +----------------------------------------------------------+
#
#        LOAD <url> INTO GRAPH <g> is the sixth of these, and it
#        fetches over the network. That makes it the same exposure as
#        SERVICE (q108): a URL the requester chose, fetched by your
#        server, from inside your network. HOLOS refuses remote LOAD
#        for that reason, and an endpoint that allows it should have an
#        allow-list in front of it.
#
#        All six are also SILENT-able: CLEAR SILENT GRAPH <a> succeeds
#        rather than failing when there is no such graph.
#
#
#  WHAT TO TAKE AWAY
#    - CLEAR empties a graph and keeps its name; DROP removes both.
#    - MOVE, COPY and ADD differ in two ways: whether the destination is
#      emptied first, and whether the source survives. ADD is the merge.
#    - LOAD fetches a URL of the requester's choosing, which is why a
#      careful engine refuses it or puts an allow-list in front.
#
#  NOTE
#    Fuseki and HOLOS, for the same reason as q122. Note that bt:graph-
#    claims survives as a name with nothing in it, so it disappears from a
#    result grouped by GRAPH -- an empty graph has no triples to group.
#
#  DATA     bookshop-trail.trig
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail.trig
#  RUNS ON  holos, fuseki
#  RETURNS  9 rows, on every engine that runs it
# ==========================================================================

PREFIX bt: <https://example.org/bookshop-trail/>

CLEAR GRAPH bt:graph-claims ;

MOVE bt:graph-trail TO bt:graph-archive ;

ADD bt:graph-people TO bt:graph-books


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
