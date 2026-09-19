# Module 11 · SPARQL 1.2 and RDF 1.2

How to say something about a statement, and how to ask about it afterwards. Triple terms, the annotation syntax, and language strings that know which way they are written.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query 17.4.6 Functions on Triple Terms](https://www.w3.org/TR/sparql12-query/#x17-4-6-functions-on-triple-terms)
- [SPARQL 1.2 Query 17.4.2.9 LANGDIR](https://www.w3.org/TR/sparql12-query/#x17-4-2-9-langdir)
- [SPARQL 1.2 Query 17.4.2.17 STRLANGDIR](https://www.w3.org/TR/sparql12-query/#x17-4-2-17-strlangdir)
- [SPARQL 1.2 Query, Appendix A: changes since SPARQL 1.1](https://www.w3.org/TR/sparql12-query/#a-changes-between-sparql-1-1-query-language-and-sparql-1-2-query-language)
- [RDF 1.2 Concepts 3.6 Triple Terms](https://www.w3.org/TR/rdf12-concepts/#x3-6-triple-terms)
- [RDF 1.2 Concepts 3.4.3 Initial Text Direction](https://www.w3.org/TR/rdf12-concepts/#x3-4-3-initial-text-direction)
- [RDF 1.2 Turtle 2.11 Reifying Triples](https://www.w3.org/TR/rdf12-turtle/#x2-11-reifying-triples)

| Query | Asks |
|---|---|
| [q61 Who says the shop opened when](q61-who-says-the-shop-opened-when.rq) | The founding dates are disputed. Who claims what, and how much do we trust them? |
| [q62 Find the contradictions](q62-find-the-contradictions.rq) | Which shops have two different founding dates on record? |
| [q63 Believe the best source](q63-believe-the-best-source.rq) | For each shop, which founding date has the strongest backing? |
| [q134 Naming a statement in the query itself](q134-naming-a-statement-in-the-query-itself.rq) | Find the shop whose founding year somebody disputes, using the reifier syntax rather than a variable. |
| [q64 What the annotation syntax really is](q64-what-the-annotation-syntax-really-is.rq) | Strip away the sugar: what triples does {| ... |} actually create? |
| [q65 A statement as the object of a statement](q65-a-statement-as-the-object-of-a-statement.rq) | Which claims does the National Register explicitly reject? |
| [q66 Taking a triple term apart](q66-taking-a-triple-term-apart.rq) | Pull the subject, predicate and object out of every disputed statement. |
| [q67 Text that knows which way it runs](q67-text-that-knows-which-way-it-runs.rq) | Which labels are written right to left? |
| [q138 Building and matching language tags](q138-building-and-matching-language-tags.rq) | Which labels carry a language tag, which of them are English, and how do you add a tag to a string that has none? |
| [q68 The same fact, modelled twice](q68-the-same-fact-modelled-twice.rq) | Stock levels are in this dataset twice over -- once the RDF 1.1 way and once the 1.2 way. Compare them. |
