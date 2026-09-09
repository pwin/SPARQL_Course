# Module 12 · Graphs in, graphs out

Module 07 introduced ASK, CONSTRUCT and DESCRIBE. This one uses them in earnest. The shift is in what SPARQL is for: not answering a question and printing a table, but testing a condition, or taking a graph in and handing a different graph back. Every query here returns a boolean or RDF -- not one of them returns a table.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §16.2 CONSTRUCT](https://www.w3.org/TR/sparql12-query/#x16-2-construct)
- [SPARQL 1.2 Query §16.2.1 Templates with Blank Nodes](https://www.w3.org/TR/sparql12-query/#x16-2-1-templates-with-blank-nodes)
- [SPARQL 1.2 Query §16.4 DESCRIBE](https://www.w3.org/TR/sparql12-query/#x16-4-describe-informative)
- [SPARQL 1.2 Update](https://www.w3.org/TR/sparql12-update/)
- [SHACL](https://www.w3.org/TR/shacl/)

| Query | Asks |
|---|---|
| [q75 Can you walk from Wigtown to London](q75-can-you-walk-from-wigtown-to-london.rq) | Is there any route along the trail from The Inkwell to Ex Libris? |
| [q76 The assertion that must come back false](q76-the-assertion-that-must-come-back-false.rq) | Is any bookshop missing a label? |
| [q77 One boolean per row, not one per query](q77-one-boolean-per-row-not-one-per-query.rq) | For every shop, does it stock any translated fiction? |
| [q78 Asking a question about a total](q78-asking-a-question-about-a-total.rq) | Does any single town have three or more bookshops? |
| [q79 Asking inside one named graph](q79-asking-inside-one-named-graph.rq) | Does the stock graph say anything at all about The Sea Margin? |
| [q80 Describe everything that matches](q80-describe-everything-that-matches.rq) | Give me a description of every bookshop in Wales. |
| [q81 Describe several things at once](q81-describe-several-things-at-once.rq) | Describe a shop, the town it's in, and an author who lives there. |
| [q82 The CONSTRUCT that replaces DESCRIBE](q82-the-construct-that-replaces-describe.rq) | Get a description of The Quire that every engine will produce identically -- and that's actually readable. |
| [q83 Following one hop further](q83-following-one-hop-further.rq) | Describe The Sea Margin including its geometry, which lives on a separate node. |
| [q84 CONSTRUCT WHERE, the short form](q84-construct-where-the-short-form.rq) | Extract the shops with their names and founding years, unchanged. |
| [q85 Republish it in someone else's vocabulary](q85-republish-it-in-someone-else-s-vocabulary.rq) | Turn the shops into schema.org, so a search engine could read them. |
| [q86 Upgrade RDF 1.1 data to RDF 1.2](q86-upgrade-rdf-1.1-data-to-rdf-1.2.rq) | Turn the 95 StockRecord nodes into RDF 1.2 annotations, automatically. |
| [q87 A profile of the genre scheme](q87-a-profile-of-the-genre-scheme.rq) | Build a graph that records, for each genre, how many shops specialise in it and how many works are filed under it. |
| [q88 A validation report, as RDF](q88-a-validation-report-as-rdf.rq) | Produce a graph listing everything questionable in the dataset. |
| [q89 Invent a relationship the data doesn't have](q89-invent-a-relationship-the-data-doesn-t-have.rq) | Link every pair of shops that share a town. |
