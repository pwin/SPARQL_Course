# Module 08 · Named graphs and federation

The dataset also ships as TriG, with each subject area in its own named graph. GRAPH lets you ask where a fact came from, which is the cheapest form of provenance there's. The second half of the module takes the same idea across the network: SERVICE puts the other graph on somebody else's machine, and the last four queries join this dataset to DBpedia.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query §13 RDF Dataset](https://www.w3.org/TR/sparql12-query/#x13-rdf-dataset)
- [SPARQL 1.2 Query §13.2 Specifying RDF Datasets](https://www.w3.org/TR/sparql12-query/#x13-2-specifying-rdf-datasets)
- [SPARQL 1.2 Query §13.3 Querying the Dataset](https://www.w3.org/TR/sparql12-query/#x13-3-querying-the-dataset)
- [SPARQL 1.2 Query §14 Basic Federated Query](https://www.w3.org/TR/sparql12-query/#x14-basic-federated-query)
- [SPARQL 1.2 Federated Query](https://www.w3.org/TR/sparql12-federated-query/)
- [SPARQL 1.2 Query, Security Considerations](https://www.w3.org/TR/sparql12-query/#c-security-considerations)
- [RDF 1.2 TriG](https://www.w3.org/TR/rdf12-trig/)

| Query | Asks |
|---|---|
| [q48 What graphs are in this dataset](q48-what-graphs-are-in-this-dataset.rq) | The TriG file splits the data by subject matter. What are the parts called, and how big is each? |
| [q49 Where did this fact come from](q49-where-did-this-fact-come-from.rq) | Which part of the dataset asserts each thing known about The Inkwell? |
| [q50 Querying one graph, then all of them](q50-querying-one-graph-then-all-of-them.rq) | Count the shops using only the shops graph, and then across the whole dataset. |
| [q51 Joining across two graphs](q51-joining-across-two-graphs.rq) | Pair each shop with its town's name, when the shops and the places live in different graphs. |
| [q124 Choosing the dataset in the query](q124-choosing-the-dataset-in-the-query.rq) | Answer a question against two of the ten graphs and ignore the rest. |
| [q125 Keeping the graphs apart](q125-keeping-the-graphs-apart.rq) | Count the triples in two named graphs, and say which is which. |
| [q105 Bringing in DBpedia](q105-bringing-in-dbpedia.rq) | How many people live in each of the three book towns, according to DBpedia? |
| [q106 Keeping the rows the remote side cannot answer](q106-keeping-the-rows-the-remote-side-cannot-answer.rq) | List all three book towns, with the population where DBpedia has one. |
| [q107 Sending the list with the question](q107-sending-the-list-with-the-question.rq) | Ask DBpedia about a batch of towns in one round trip, in a way both engines answer. |
| [q108 When the other end is not there](q108-when-the-other-end-is-not-there.rq) | What happens when the remote endpoint is unreachable, and why does HOLOS refuse to call one at all? |
