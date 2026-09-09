# Module 05 · Property paths

The feature that turns SPARQL from a table language into a graph language. A path expression walks an arbitrary number of hops, in either direction, and it terminates even when the data has cycles.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §9 Property Paths](https://www.w3.org/TR/sparql12-query/#x9-property-paths)
- [SPARQL 1.2 Query §9.1 Property Path Syntax](https://www.w3.org/TR/sparql12-query/#x9-1-property-path-syntax)
- [SPARQL 1.2 Query §9.4 Arbitrary Length Path Matching](https://www.w3.org/TR/sparql12-query/#x9-4-arbitrary-length-path-matching)
- [SPARQL 1.2 Query §18.5 Property Path Patterns](https://www.w3.org/TR/sparql12-query/#x18-5-property-path-patterns)

| Query | Asks |
|---|---|
| [q27 Every area a shop sits inside](q27-every-area-a-shop-sits-inside.rq) | For one shop, list every containing place all the way up to Great Britain. |
| [q28 Why a fixed-length chain gets the wrong answer](q28-why-a-fixed-length-chain-gets-the-wrong-answer.rq) | Count the shops in each country, first with a fixed chain of hops and then with a path. |
| [q29 Star and plus aren't the same](q29-star-and-plus-aren-t-the-same.rq) | What's the difference between bs:within* and bs:within+? |
| [q30 Walking a link backwards](q30-walking-a-link-backwards.rq) | Which shops are in Wales? |
| [q133 A hop that may not be there](q133-a-hop-that-may-not-be-there.rq) | List every place with its council area, falling back to the place itself where there is no council above it. |
| [q31 Walking the trail in either direction](q31-walking-the-trail-in-either-direction.rq) | Which shops can be reached on foot from The Inkwell? |
| [q32 The shops you can't walk to](q32-the-shops-you-can-t-walk-to.rq) | Which shops are cut off from the main trail? |
| [q33 Every book of fiction, however narrow the genre](q33-every-book-of-fiction-however-narrow-the-genre.rq) | Find all fiction, including books filed under sub-genres several levels down. |
| [q34 Literary ancestry, and a cycle](q34-literary-ancestry-and-a-cycle.rq) | Trace every author who influenced Dilys Tremain, directly or at any remove. |
| [q35 Everything except the links you name](q35-everything-except-the-links-you-name.rq) | What does a shop point at, other than its geometry and its stock? |
| [q36 A whole journey in one expression](q36-a-whole-journey-in-one-expression.rq) | Name the country of every shop, in a single path. |
