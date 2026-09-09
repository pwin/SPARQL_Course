# Module 15 · Beyond the standard

Reference rather than lesson. Every engine adds functions the specification doesn't define -- ARQ's afn:, SPIN's spif:, the XPath fn: library, GeoSPARQL's geof: -- and they're genuinely useful right up until you move the query. This module measures which of them your three engines actually have, shows what each does when a function is missing, and ends with the portable rewrite.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q100 Readable names without a label](q100-readable-names-without-a-label.rq) | Show each shop's IRI as a short name, without joining to rdfs:label. |
| [q101 The square root module 09 could not have](q101-the-square-root-module-09-could-not-have.rq) | How far is each shop from York, in actual kilometres? |
| [q102 SPIN's string functions, and a silent failure](q102-spin-s-string-functions-and-a-silent-failure.rq) | Tidy up some strings with spif:, and find out what happens where spif: is not implemented. |
| [q103 The XPath library, under different names](q103-the-xpath-library-under-different-names.rq) | Do the same string work with fn: instead of the SPARQL built-ins. |
| [q104 The same query, with nothing but the standard](q104-the-same-query-with-nothing-but-the-standard.rq) | Get the local name, the namespace and a real distance using only SPARQL 1.1. |
