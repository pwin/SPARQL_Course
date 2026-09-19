# Module 17 · Updating the data

Everything before this reads. SPARQL Update writes: INSERT, DELETE, the two together, whole-graph operations, and a migration applied in place rather than handed back. An update returns nothing, so every query here comes with a second one that shows what it did. The editor's SPARQL panel cannot run these -- use Fuseki or HOLOS.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q116 Adding facts you already know](q116-adding-facts-you-already-know.ru) | Add a new bookshop to the trail. |
| [q117 Removing facts you can name](q117-removing-facts-you-can-name.ru) | The Inkwell has closed its cafe. Remove that one fact. |
| [q118 Removing whatever matches](q118-removing-whatever-matches.ru) | Drop every bs:hasCafe false statement, on the grounds that they say nothing a missing statement would not. |
| [q119 Correcting a value](q119-correcting-a-value.ru) | Ex Libris was founded in 1921, not 1919. Change it. |
| [q120 Materialising what a path already knows](q120-materialising-what-a-path-already-knows.ru) | Every shop is in a country by way of two or three bs:within hops. Write that down as one triple per shop. |
| [q121 The migration, done in place](q121-the-migration-done-in-place.ru) | Turn the 95 StockRecord nodes into RDF 1.2 annotations, and remove the old ones. |
| [q122 Moving whole graphs about](q122-moving-whole-graphs-about.ru) | Copy one named graph, then drop another, without touching a single triple pattern. |
| [q137 Emptying, moving and merging graphs](q137-emptying-moving-and-merging-graphs.ru) | Empty one graph, move a second into a third, and merge a fourth into it. |
| [q139 Loading a file from the web](q139-loading-a-file-from-the-web.ru) | Fetch a graph over HTTP and put it in a named graph. |
| [q123 The update that empties the store](q123-the-update-that-empties-the-store.ru) | What does one careless pattern cost? |
