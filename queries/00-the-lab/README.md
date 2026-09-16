# Module 00 · The lab

Before the first query, learn the room. The **Turtle Editor Viewer** is the
environment this course is built around, and it does four things no plain
SPARQL endpoint does: it *draws* the graph you are querying, it *reasons* over
it, it *converts* it between formats, and it *validates* it against SHACL —
all in the browser, with nothing installed.

These are not SPARQL exercises. They take about twenty minutes and they will
make every query afterwards easier to picture.

The editor is **used online**. There is nothing to install:

**<https://semantechs.co.uk/turtle-editor-viewer/>**

---

## 1 · Load something small and look at it

Open `data/04-bookshops.ttl` with **Choose File**.

The editor parses as you type, finds the subjects, and draws the first ten of
them. Ten is the default cap, and it is the reason this course ships eleven
small module files instead of one large one — the combined
`bookshop-trail-1.1.ttl` is perfectly good to *query*, and almost useless to
*look at*.

Try, in the Graph pane:

| Control | What to notice |
|---|---|
| **Subjects** dropdown | Pick `bt:shop-inkwell` alone. That single node with its dozen edges is exactly what query **q02** returns as a table. |
| **Engine**: `dot` → `neato` → `circo` | `dot` ranks the hierarchy; `neato` shows clusters; `circo` shows the ring structure. Same graph, three different questions answered. |
| **Hide Types** | Removes the `rdf:type` edges. The shape of the *data* appears once the class edges stop dominating. |
| **Hide Annotations** | Removes labels and comments. What is left is the skeleton the property-path module walks. |
| **Get All** | Re-reads the editor pane and rebuilds the graph from *everything* in it. This is the one to remember: it also **reloads the internal triplestore the SPARQL panel queries**. Edit the Turtle, press Get All, and only then will your query see the change. |

> **Do this one properly.** Load `data/03-places.ttl`, hide types and
> annotations, and choose the `dot` engine. You are looking at the containment
> hierarchy that module 05 spends ten queries on. Notice that the English
> branch is one level deeper than the Scottish and Welsh ones — that asymmetry
> is the entire point of **q28**, and it is visible here before you write a
> single line of SPARQL.

---

## 2 · Run your first query in the SPARQL panel

With `04-bookshops.ttl` loaded, press **Add Prefixes** in the SPARQL panel. It
reads the prefixes out of the data in the editor and prepends them, so you do
not have to type the `PREFIX` block by hand.

Then:

```sparql
SELECT ?shop ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
}
ORDER BY ?name
```

Thirty-three rows. That's **q01**, and module 01 starts there.

> **If you edit the data, press Get All first.** The SPARQL panel runs against
> a store built from the parsed editor content, not against the text in front
> of you. Changing a triple and re-running the query without pressing Get All
> gives you the old answer, and it looks exactly like the query being wrong.
> It's the first thing to check when an edit appears to have had no effect.

The panel runs `SELECT`, `ASK`, `CONSTRUCT` and `DESCRIBE`. A `CONSTRUCT`
returns Turtle — copy it back into the editor pane and the graph view will
draw *that* instead. **q47**, **q82** and **q87** are written to be used
exactly this way: reshape a large dataset into a small graph, then look at it.

---

## 3 · Watch a reasoner do what a property path does

Click **Show Facts** in the Graph toolbar. The editor runs HyLAR, a
client-side OWL 2 RL reasoner, and opens a window with two lists: **explicit
triples**, which you wrote, and **implicit triples**, which it worked out.

The vocabulary in `data/01-vocabulary.ttl` is written to give it something
real to do:

```turtle
bs:within       a owl:TransitiveProperty .
bs:connectsTo   a owl:SymmetricProperty .
bs:hasImprint   owl:inverseOf bs:imprintOf .
```

Load `data/03-places.ttl` and press **Show Facts**. Because `bs:within` is
transitive, the reasoner materialises every ancestor link — York to Yorkshire,
York to England, York to Great Britain — as real triples you can then query
with a plain one-hop pattern.

**This is the same answer that `bs:within+` computes**, arrived at from the
other end:

|  | Reasoner | Property path |
|---|---|---|
| When the work happens | Once, up front | Every time you ask |
| What it costs | Storage, and a re-run after every change | Nothing until asked |
| What you query | `?town bs:within ?area` | `?town bs:within+ ?area` |
| Portability | Needs a reasoner | Any SPARQL 1.1 engine |

Neither is the right answer in general. Knowing that they are two routes to
the same place is the point — and it is worth seeing before module 05, so that
the paths feel like a choice rather than the only option.

Try the same on `data/05-people.ttl`: `bs:hasImprint` is asserted **nowhere**
in the data, and the reasoner will produce it from `owl:inverseOf`. Query
**q44** builds the identical triples with `CONSTRUCT` instead.

---

## 4 · Convert between formats

**To JSON-LD** and **To Turtle** in the Graph toolbar round-trip the data.

Worth doing once with `data/10-annotations-1.2.ttl` open: RDF 1.2 triple terms
and the `{| ... |}` annotation syntax have no settled JSON-LD form, so the
conversion is where you find out what your toolchain actually supports. Better
to discover that here than in a pipeline.

---

## 5 · Validate the data

The panel at the bottom right of the editor validates as well as queries.
Open the shapes in a second tab — the **+** on the tab strip, then **Load
URL** — choose that tab in the **Shapes** dropdown, switch back to the data
tab and press **Validate**. Or let the link do it:

```
https://semantechs.co.uk/turtle-editor-viewer/?dot=<data url>&shapes=<shapes url>
```

On the untouched data `shapes.ttl` reports **eight violations**, all from one
shape: `sh:lessThan bs:died` on `bs:born`, where both values are `xsd:gYear`.
SPARQL's `<` is not defined for gYear, and the editor's engine treats a
comparison it cannot make as a failure. The HOLOS command line compares the
years anyway and reports clean:

```powershell
holos validate --data data/bookshop-trail-1.1.ttl --shapes data/shapes.ttl
```

Two engines, the same shape, two verdicts, and both defensible — q07 is the
same gYear fact seen from a query. Anything else the editor reports is real.

Now break it on purpose. In the editor, change a shop's `bs:staffCount` to
`0`, or delete an author's `bs:born`, and validate again: one more violation,
pointing at that shop. The shape files are
commented with what each constraint is for, and two of them carry notes about
mistakes that were made writing them — `sh:lessThan` is easy to point the
wrong way, and `sh:datatype xsd:string` quietly rejects every
language-tagged label.

---

## 6 · Load by URL

The Graph toolbar takes a URL, and the app accepts `?dot=<url>`, so a link can
carry a dataset with it. The course's own files are on GitHub and send the CORS
header the editor needs:

```
https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2F04-bookshops.ttl
```

Add `&shapes=<url>` and a shapes file opens in its own tab, already selected
for validation, with the data tab left in front.

`./scripts/open-editor.ps1 04-bookshops` builds that and opens it;
`-Shapes shapes` adds the shapes; `-List` shows every file it can open. Every
query in the course document has its own link, so you never have to assemble
one by hand.

Useful for setting an exercise: send the link, and the other person lands in
the editor with the data already there.

---

## What you should be able to do now

- Load a module file and read its shape in the graph view
- Choose a layout engine that answers the question you are asking
- Prepend the prefixes without typing them
- Run a `SELECT` and a `CONSTRUCT`, and feed the `CONSTRUCT` back into the view
- Explain the difference between inferring a fact and computing it on demand
- Validate the data and read a SHACL violation

Then start on [module 01](../01-first-queries/).
