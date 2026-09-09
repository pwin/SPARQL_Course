# ==========================================================================
#  Q119  Correcting a value
# ==========================================================================
#
#  ASKS
#    Ex Libris was founded in 1921, not 1919. Change it.
#
#  HOW IT WORKS
#    DELETE and INSERT in one operation, sharing a WHERE clause. The WHERE
#    runs once, its bindings feed both templates, and the DELETE half is
#    applied before the INSERT half. Leaving the DELETE out is the
#    commonest mistake in SPARQL Update, and it does not look like a
#    mistake: the new value appears, and so does the old one.
#
#  DIAGRAM
#        DELETE { ?shop bs:founded ?old }        <- the old triple, by variable
#        INSERT { ?shop bs:founded "1921" }      <- the new one
#        WHERE  { ?shop bs:founded ?old .        <- binds ?old, once
#                 FILTER( ?shop = bt:shop-ex-libris ) }
#
#        with the DELETE:          without it:
#
#          bs:founded 1921           bs:founded 1919
#                                    bs:founded 1921
#                                    ---------------
#                                    Two founding years, no error, and
#                                    a query that asks for one now
#                                    returns two rows.
#
#        A property being single-valued is a claim your data makes, not
#        a rule the store enforces. Nothing stops a second value
#        arriving, which is what owl:FunctionalProperty is for -- it
#        says what a reasoner may conclude, and still does not stop the
#        insert.
#
#        +----------------------------------------------------------+
#        |  Order inside one operation: DELETE first, then INSERT.   |
#        |  So a value can be replaced by one computed from itself.  |
#        +----------------------------------------------------------+
#
#
#  WHAT TO TAKE AWAY
#    - DELETE/INSERT/WHERE is the workhorse. One WHERE, two templates,
#      delete applied before insert.
#    - An INSERT with no matching DELETE leaves both values in place.
#      Nothing warns you; the property simply has two.
#    - Bind the old value to a variable in the WHERE and delete it by
#      variable, rather than naming what you think it is.
#
#  DATA     bookshop-trail-1.1.ttl
#  LOAD IT  https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2Fbookshop-trail-1.1.ttl
#  RUNS ON  comunica, holos, fuseki
#  RETURNS  1 row, on every engine that runs it
# ==========================================================================

PREFIX bt:   <https://example.org/bookshop-trail/>
PREFIX bs:   <https://example.org/bookshop-trail/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

DELETE { ?shop bs:founded ?old }
INSERT { ?shop bs:founded "1921"^^xsd:gYear }
WHERE  {
  ?shop      a          bs:Bookshop ;
             bs:founded ?old .
  FILTER( ?shop = bt:shop-ex-libris )
}


# ------------------------------------------------------------------------
#  CHECK IT WORKED.  Run this afterwards, against the
#  updated store.  An update returns nothing, so this
#  is the only way to see what it did.
# ------------------------------------------------------------------------
#
#  SELECT ?name ?founded
#  WHERE {
#    bt:shop-ex-libris rdfs:label ?name ;
#                      bs:founded ?founded .
#  }
#  ORDER BY ?founded
