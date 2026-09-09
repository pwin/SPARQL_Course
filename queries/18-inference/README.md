# Module 18 · Inference

A reasoner derives new triples from the ones you have plus the rules in the vocabulary. For the commonest cases -- transitivity, inverse properties, class hierarchies -- SPARQL does the same job at query time, on every engine, with nothing stored and nothing to keep up to date. This module writes those inferences as queries; the reference section on reasoning measures what happens when you switch a real reasoner on instead, and no two of the three engines agree.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q140 The closure a reasoner would give you](q140-the-closure-a-reasoner-would-give-you.rq) | How many containment facts are there once you follow the chain? |
| [q141 Filling in the other direction](q141-filling-in-the-other-direction.rq) | Every work has an author; how many author-to-work links are there if you count both properties? |
| [q142 What RDFS would actually add here](q142-what-rdfs-would-actually-add-here.rq) | How deep is the class hierarchy a reasoner would have to walk? |
| [q143 The inference nobody wanted](q143-the-inference-nobody-wanted.rq) | Which properties would a reasoner use to type things as a class with no name? |
| [q144 A reasoner you can read](q144-a-reasoner-you-can-read.rq) | Materialise the containment closure as a graph, with the derived triples marked as derived. |
| [q145 What entailment cannot do](q145-what-entailment-cannot-do.rq) | The vocabulary says a Place and a Bookshop can never be the same thing. What happens if one is? |
