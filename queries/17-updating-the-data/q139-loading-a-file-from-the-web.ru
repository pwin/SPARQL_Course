# ==========================================================================
#  Q139  Loading a file from the web
# ==========================================================================
#
#  ASKS
#    Fetch a graph over HTTP and put it in a named graph.
#
#  HOW IT WORKS
#    LOAD takes a URL, fetches whatever RDF is there, and adds it. It is
#    the fastest way to get a file into a store and the operation most
#    worth being careful about, because the URL comes from whoever wrote
#    the request rather than from whoever runs the server.
#
#  DIAGRAM
#        LOAD <https://raw.githubusercontent.com/.../04-bookshops.ttl>
#          INTO GRAPH bt:graph-imported
#
#        588 triples arrive in a graph that did not exist before.
#
#          LOAD <url>                    into the default graph
#          LOAD <url> INTO GRAPH <g>     into a named one
#          LOAD SILENT <url>             carry on if the fetch fails
#
#        +----------------------------------------------------------+
#        |  Same exposure as SERVICE (q108). The server makes an     |
#        |  HTTP request to an address a stranger named, from        |
#        |  inside your network:                                     |
#        |                                                           |
#        |      LOAD <http://169.254.169.254/latest/meta-data/>      |
#        |                                                           |
#        |  HOLOS refuses remote LOAD outright, for that reason.     |
#        |  Fuseki allows it, so an open update endpoint is an       |
#        |  open fetcher as well as an open writer.                  |
#        +----------------------------------------------------------+
#
#        The Graph Store Protocol does the same job over plain HTTP
#        and puts the choice of file on the client rather than in the
#        query -- see "Talking to an endpoint". For loading your own
#        data that is the better tool; LOAD is for when the request
#        itself has to say where the data comes from.
#
#        Formats: the fetched document is parsed by its content type,
#        so a server that serves Turtle as text/plain will produce a
#        parse error rather than a graph. That is the commonest reason
#        a LOAD of a working URL fails.
#
#
#  WHAT TO TAKE AWAY
#    - LOAD fetches a URL and adds the triples, optionally INTO GRAPH.
#      SILENT stops a failed fetch from failing the request.
#    - The URL is chosen by the request, not the operator. Treat an
#      update endpoint as a way to make your server fetch arbitrary
#      addresses.
#    - The Graph Store Protocol is the better route for loading your own
#      files, because the client supplies the bytes.
#
#  NOTE
#    Fuseki only, and it needs the internet. HOLOS refuses remote LOAD for
#    the reason in the diagram; the browser editor cannot run an update at
#    all.
#
#  NETWORK  calls a remote endpoint; needs the internet
#  DATA     bookshop-trail.trig
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail.trig
#  RUNS ON  fuseki
#  RETURNS  11 rows, on every engine that runs it
# ==========================================================================

PREFIX bt: <https://example.org/bookshop-trail/>

LOAD <https://raw.githubusercontent.com/pwin/SPARQL_Course/main/data/04-bookshops.ttl>
  INTO GRAPH bt:graph-imported


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
