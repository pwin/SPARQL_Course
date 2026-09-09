# Module 08 · Named graphs

The dataset also ships as TriG, with each subject area in its own named graph. GRAPH lets you ask where a fact came from, which is the cheapest form of provenance there's.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q48 What graphs are in this dataset](q48-what-graphs-are-in-this-dataset.rq) | The TriG file splits the data by subject matter. What are the parts called, and how big is each? |
| [q49 Where did this fact come from](q49-where-did-this-fact-come-from.rq) | Which part of the dataset asserts each thing known about The Inkwell? |
| [q50 Querying one graph, then all of them](q50-querying-one-graph-then-all-of-them.rq) | Count the shops using only the shops graph, and then across the whole dataset. |
| [q51 Joining across two graphs](q51-joining-across-two-graphs.rq) | Pair each shop with its town's name, when the shops and the places live in different graphs. |
