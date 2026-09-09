# Module 16 · Blank nodes

The nodes with no name. They are how RDF writes lists, restrictions and anything else that is structure rather than a thing, and they behave differently from everything else in the language: they have identity inside a query and none outside it. This module is late in the sequence because it needs property paths and sub-queries, but the hazards in it turn up from module 01 onwards.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §2.4 Blank Node Identifiers in Query Results](https://www.w3.org/TR/sparql12-query/#x2-4-blank-node-identifiers-in-query-results)
- [SPARQL 1.2 Query §4.1.4 Syntax for Blank Nodes](https://www.w3.org/TR/sparql12-query/#x4-1-4-syntax-for-blank-nodes)
- [SPARQL 1.2 Query §4.2.3 RDF Collections](https://www.w3.org/TR/sparql12-query/#x4-2-3-rdf-collections)
- [SPARQL 1.2 Query §5.1.1 Blank Node Identifiers](https://www.w3.org/TR/sparql12-query/#x5-1-1-blank-node-identifiers)
- [SPARQL 1.2 Query §18.4.2 Treatment of Blank Nodes](https://www.w3.org/TR/sparql12-query/#x18-4-2-treatment-of-blank-nodes)
- [RDF 1.2 Concepts §3.5 Blank Nodes](https://www.w3.org/TR/rdf12-concepts/#x3-5-blank-nodes)
- [RDF 1.2 Concepts, Appendix B: Replacing Blank Nodes with IRIs](https://www.w3.org/TR/rdf12-concepts/#b-replacing-blank-nodes-with-iris)
- [RDF 1.2 Turtle §2.9 Collections](https://www.w3.org/TR/rdf12-turtle/#x2-9-collections)

| Query | Asks |
|---|---|
| [q109 Where the blank nodes are](q109-where-the-blank-nodes-are.rq) | This dataset has blank nodes in it. Which predicates do they carry? |
| [q110 The label in your results is not a name](q110-the-label-in-your-results-is-not-a-name.rq) | A previous query returned _:b0. What happens if you put _:b0 back into a query? |
| [q111 Walking an RDF collection](q111-walking-an-rdf-collection.rq) | Which classes are declared disjoint from one another? |
| [q112 Where in the list?](q112-where-in-the-list.rq) | An RDF collection is ordered. Which position does each member hold? |
| [q113 Telling two blank nodes apart](q113-telling-two-blank-nodes-apart.rq) | Are the two disjointness axioms really two nodes, or one node found twice? |
| [q114 Giving a blank node a name](q114-giving-a-blank-node-a-name.rq) | Mint a stable IRI for each disjointness axiom, so it can be quoted in a bug report. |
| [q115 A copy with no blank nodes left in it](q115-a-copy-with-no-blank-nodes-left-in-it.rq) | Build a graph that says the same thing about disjointness, with every blank node replaced by something nameable. |
