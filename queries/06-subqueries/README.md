# Module 06 · Sub-queries

A SELECT inside a WHERE clause. It runs first, produces a small table, and the outer query joins against it. This is how you say 'above average', 'the top three in each group', and 'the one with the most'. A VALUES block is the same shape with the table written by hand instead of computed.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §12 Subqueries](https://www.w3.org/TR/sparql12-query/#x12-subqueries)
- [SPARQL 1.2 Query §15 Solution Sequences and Modifiers](https://www.w3.org/TR/sparql12-query/#x15-solution-sequences-and-modifiers)
- [SPARQL 1.2 Query §18.3.1 Variable Scope](https://www.w3.org/TR/sparql12-query/#x18-3-1-variable-scope)
- [SPARQL 1.2 Query §10.2 VALUES](https://www.w3.org/TR/sparql12-query/#x10-2-values-providing-inline-data)

| Query | Asks |
|---|---|
| [q37 Books priced above average](q37-books-priced-above-average.rq) | Which books cost more than the average book? |
| [q38 The best-attended event at every shop](q38-the-best-attended-event-at-every-shop.rq) | For each shop, which single event drew the biggest crowd? |
| [q39 An aggregate over an aggregate](q39-an-aggregate-over-an-aggregate.rq) | On average, how many books does each of a publisher's authors write? |
| [q40 Shops that punch above their weight](q40-shops-that-punch-above-their-weight.rq) | Which shops draw a bigger total audience than the average shop does? |
| [q41 Limiting the inner query, not the outer one](q41-limiting-the-inner-query-not-the-outer-one.rq) | Show every book by the three most prolific authors. |
| [q42 Authors more prolific than the person who inspired them](q42-authors-more-prolific-than-the-person-who-inspired-them.rq) | Which authors wrote more books than the author who influenced them? |
| [q99 A lookup table written into the query](q99-a-lookup-table-written-into-the-query.rq) | Check three shops against the specialism you expected each to have, with one deliberately left blank. |
