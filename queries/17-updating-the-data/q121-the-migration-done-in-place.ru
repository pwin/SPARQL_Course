# ==========================================================================
#  Q121  The migration, done in place
# ==========================================================================
#
#  ASKS
#    Turn the 95 StockRecord nodes into RDF 1.2 annotations, and remove the
#    old ones.
#
#  HOW IT WORKS
#    q86 built this graph with CONSTRUCT and left you holding it. Here the
#    same transformation is applied to the store, and then a second
#    operation removes what it replaced -- the half CONSTRUCT cannot do.
#    Two operations separated by a semicolon, applied in order.
#
#  DIAGRAM
#        operation 1     read the old shape, write the new one
#        operation 2     delete the old shape
#
#          INSERT { ... } WHERE { ?record a bs:StockRecord ; ... } ;
#          DELETE WHERE   { ?record a bs:StockRecord ; ?p ?o }
#                       ^
#                       the semicolon. Operations run in order, and the
#                       second sees what the first did -- which is why
#                       the delete must come second, and why writing it
#                       first quietly produces nothing at all.
#
#        before                          after
#        ------                          -----
#        95 bs:StockRecord nodes         0
#        0 bs:stocks triples             95
#        0 reifiers                      95, each with copies and price
#
#        Idempotence is what makes this survivable. The reifier IRI is
#        derived from the record's own name, so a migration interrupted
#        half way can simply be run again: the triples it already wrote
#        are written again to no effect.
#
#        +----------------------------------------------------------+
#        |  Take a backup first. There is no transaction spanning    |
#        |  the two operations on every engine, no undo, and no      |
#        |  prompt. `holos backup` and Fuseki's tdb2.tdbbackup are   |
#        |  the two this course uses.                                |
#        +----------------------------------------------------------+
#
#
#  WHAT TO TAKE AWAY
#    - Several operations in one request, separated by ';', run in order,
#      and each sees the effect of the last.
#    - Migrate then delete, in that order. The reverse loses the data the
#      migration needed.
#    - Derive new IRIs from stable existing ones and the whole request
#      becomes safe to re-run. That is worth more than it sounds at 3am.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  2 rows, on every engine that runs it
# ==========================================================================

PREFIX bs:  <https://example.org/bookshop-trail/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT {
  ?shop    bs:stocks     ?work .
  ?reifier rdf:reifies   ?statement ;
           bs:copies     ?copies ;
           bs:shelfPrice ?price .
}
WHERE {
  ?record a             bs:StockRecord ;
          bs:atShop     ?shop ;
          bs:ofWork     ?work ;
          bs:copies     ?copies ;
          bs:shelfPrice ?price .
  BIND( TRIPLE(?shop, bs:stocks, ?work) AS ?statement )
  BIND( IRI( REPLACE( STR(?record),
                      "/stock-", "/reifier-" ) ) AS ?reifier )
} ;

DELETE WHERE {
  ?record a  bs:StockRecord ;
          ?p ?o .
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?shape (COUNT(*) AS ?n)
#  WHERE {
#    { ?s a bs:StockRecord .          BIND( "old: StockRecord" AS ?shape ) }
#    UNION
#    { ?s bs:stocks ?w .              BIND( "new: bs:stocks"  AS ?shape ) }
#    UNION
#    { ?s rdf:reifies ?t .            BIND( "new: reifier"    AS ?shape ) }
#  }
#  GROUP BY ?shape
#  ORDER BY ?shape
