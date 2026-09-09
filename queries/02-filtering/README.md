# Module 02 · Filtering and expressions

A pattern says which shape to match; a FILTER says which of the matches to keep. This module is also where the built-in functions live, and where the difference between a value and its lexical form starts to matter.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §3 RDF Term Constraints](https://www.w3.org/TR/sparql12-query/#x3-rdf-term-constraints-informative)
- [SPARQL 1.2 Query §10.1 BIND](https://www.w3.org/TR/sparql12-query/#x10-1-bind-assigning-to-variables)
- [SPARQL 1.2 Query §17.2.3 Effective Boolean Value](https://www.w3.org/TR/sparql12-query/#x17-2-3-effective-boolean-value-ebv)
- [SPARQL 1.2 Query §17.4.3 Functions on Strings](https://www.w3.org/TR/sparql12-query/#x17-4-3-functions-on-strings)
- [SPARQL 1.2 Query §17.4.5 Functions on Dates and Times](https://www.w3.org/TR/sparql12-query/#x17-4-5-functions-on-dates-and-times)

| Query | Asks |
|---|---|
| [q07 Shops founded before 1970](q07-shops-founded-before-1970.rq) | Which shops predate 1970, and why is the obvious way to ask wrong? |
| [q08 Large shops with a cafe](q08-large-shops-with-a-cafe.rq) | Which shops have both a cafe and more than 150 square metres of floor? |
| [q09 Sort books into price bands](q09-sort-books-into-price-bands.rq) | Group the books into cheap, mid and dear without changing the data. |
| [q10 Titles containing a word](q10-titles-containing-a-word.rq) | Which books have 'sea' or 'water' somewhere in the title? |
| [q127 Taking a string apart](q127-taking-a-string-apart.rq) | Build a short sortable code for each shop from its name. |
| [q11 Place names in Welsh and Gaelic](q11-place-names-in-welsh-and-gaelic.rq) | Which places carry a name in a language other than English? |
| [q12 Build a one-line description of each shop](q12-build-a-one-line-description-of-each-shop.rq) | Produce a single human-readable string per shop. |
| [q13 How old is each shop today](q13-how-old-is-each-shop-today.rq) | How many years has each shop been trading? |
| [q128 Asking a value what it is](q128-asking-a-value-what-it-is.rq) | For one shop, report the kind and datatype of everything said about it. |
| [q129 Four ways to lose the decimals](q129-four-ways-to-lose-the-decimals.rq) | Round the shelf price of every book, four different ways, and see where they differ. |
| [q130 Pulling a date apart](q130-pulling-a-date-apart.rq) | Break every event date into its parts. |
