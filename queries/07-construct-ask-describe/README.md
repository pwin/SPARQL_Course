# Module 07 · Other query forms

SELECT isn't the only answer shape. CONSTRUCT builds a new graph, ASK returns a boolean, DESCRIBE hands back whatever the engine thinks describes a resource. This module introduces the three; module 12 uses them in earnest, and is worth reaching for as soon as these five make sense.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q43 Build a simpler graph](q43-build-a-simpler-graph.rq) | Produce a small graph of shops and the names of their towns, ready to paste back into the editor. |
| [q44 Materialise the links that aren't there](q44-materialise-the-links-that-aren-t-there.rq) | The data records bs:imprintOf but never bs:hasImprint. Create it. |
| [q45 A yes or no question](q45-a-yes-or-no-question.rq) | Is there a bookshop in Wales with a cafe? |
| [q46 Describe a resource](q46-describe-a-resource.rq) | Give me everything that describes The Quire. |
| [q47 A summary graph worth keeping](q47-a-summary-graph-worth-keeping.rq) | Build a compact profile of every shop: name, town, country, specialism and event count. |
