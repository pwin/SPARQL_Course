# Getting the plan out of each engine

A SPARQL query says *what* you want. The engine decides *how*. All three of
this course's engines will show you what they decided — and the three answers
are usefully different, because they show different layers of the same idea.

The query used throughout below is `build/plan.rq`:

```sparql
PREFIX bt:   <https://example.org/bookshop-trail/>
PREFIX bs:   <https://example.org/bookshop-trail/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?site WHERE {
  ?shop a bs:Bookshop ; rdfs:label ?name ; bs:locatedIn ?town .
  ?town bs:within+ bt:place-scotland .
  OPTIONAL { ?shop bs:website ?site }
  FILTER( STRLEN(?name) > 8 )
}
```

---

## 1 · Jena — the SPARQL algebra, before and after

Jena will print the algebra without running anything, which makes it the best
of the three for *learning* what your query means.

```powershell
$env:JENA_HOME = "C:\apache-jena-6.2.0"
& "$env:JENA_HOME\bat\qparse.bat" --print=op  --query=build\plan.rq   # as written
& "$env:JENA_HOME\bat\qparse.bat" --print=opt --query=build\plan.rq   # as optimised
```

**As written** — this is your query, translated into the algebra the
specification defines:

```
(project (?name ?site)
  (filter (> (strlen ?name) 8)
    (leftjoin
      (sequence
        (bgp
          (triple ?shop rdf:type bs:Bookshop)
          (triple ?shop rdfs:label ?name)
          (triple ?shop bs:locatedIn ?town))
        (path ?town (path+ bs:within) bt:place-scotland))
      (bgp (triple ?shop bs:website ?site)))))
```

Read it inside out. A **bgp** is a basic graph pattern — a run of triple
patterns with no filter between them. **leftjoin** is `OPTIONAL`. **filter**
sits *outside* the leftjoin, because that is where you wrote it. **project**
is the `SELECT` list.

**As optimised** — what Jena will actually run:

```
(project (?name ?site)
  (conditional
    (sequence
      (filter (> (strlen ?name) 8)
        (bgp
          (triple ?shop rdf:type bs:Bookshop)
          (triple ?shop rdfs:label ?name)))
      (bgp (triple ?shop bs:locatedIn ?town))
      (path ?town (path+ bs:within) bt:place-scotland))
    (bgp (triple ?shop bs:website ?site))))
```

Two things changed, and both are worth recognising:

- **The filter moved inwards.** It now runs directly on the two patterns that
  bind `?name`, before the `bs:locatedIn` join and before the path. Rows that
  cannot survive are discarded as early as possible. This is *filter
  pushdown*, and it is the single most valuable thing an optimiser does.
- **`leftjoin` became `conditional`.** Jena's `conditional` is a
  left-join it can evaluate in one pass because nothing in the right side can
  fail in a way that requires backtracking.

If a query is slow, compare the two forms. A filter that has *not* moved
usually cannot move — commonly because it mentions a variable the optimiser
cannot prove is bound at that point.

---

## 2 · HOLOS — the physical plan, with join algorithms

```powershell
& holos.exe query --data data\bookshop-trail-1.1.ttl --query-file build\plan.rq --explain
```

HOLOS prints JSON. Formatted, and with the IRIs shortened:

```
Project(?name, ?site)
└── LeftJoin(HashBuildRightProbeLeft, keys = ?shop, expression = true)
    ├── LeftJoin(HashBuildLeftProbeRight, keys = ?town)
    │   ├── LeftJoin(HashBuildLeftProbeRight, keys = ?shop)
    │   │   ├── LeftJoin(HashBuildLeftProbeRight, keys = ?shop)
    │   │   │   ├── QuadPattern(?shop rdf:type bs:Bookshop)
    │   │   │   └── Filter(STRLEN(?name) > 8)
    │   │   │       └── QuadPattern(?shop rdfs:label ?name)
    │   │   └── QuadPattern(?shop bs:locatedIn ?town)
    │   └── Path(?town (bs:within)+ bt:place-scotland)
    └── QuadPattern(?shop bs:website ?site)
```

Where Jena shows *what*, HOLOS shows *how*:

- **`HashBuildLeftProbeRight`** — build a hash table from the left input, then
  probe it with the right. **`HashBuildRightProbeLeft`** is the same thing the
  other way round, and choosing correctly matters: you want to build from the
  smaller side. Q90 is how you find out which side that is.
- **`keys = ?shop`** — the join variable. If you ever see a join with no keys,
  you have written the cross product of Q91.
- The **`Filter` has been pushed down** onto the `rdfs:label` pattern, exactly
  as Jena did. Two independently written optimisers agreeing is a good sign
  that the rewrite is the right one.

HOLOS also offers `--reorder`, which builds cardinality statistics and orders
each basic graph pattern by estimated selectivity before evaluating:

```powershell
& holos.exe query --data data\bookshop-trail-1.1.ttl --query-file build\plan.rq --reorder --explain
```

That is Q90's table, computed by the engine and applied automatically.

---

## 3 · The browser editor — Comunica's plans

Comunica exposes `explain` through its API, in three modes:

```js
const engine = new QueryEngine();
const r = await engine.explain(query, { sources: [store] }, 'physical');
console.log(JSON.stringify(r.data, null, 2));
```

- `'parsed'` — the query as an algebra tree, straight from the parser
- `'logical'` — after Comunica's own rewriting
- `'physical'` — the operators it actually ran, with the actor that handled
  each one

The physical plan is the interesting one: Comunica is built out of actors that
bid for work, so its plan tells you *which implementation* handled each step —
which is a different and useful kind of detail from the other two.

The SPARQL panel in the editor does not surface this, so it is a Node
exercise rather than a browser one. `scripts/engines.py` contains a working
Comunica harness you can adapt in about five lines.

---

## 4 · Reading any plan: the vocabulary

| In a plan | Written in SPARQL as | Watch for |
|---|---|---|
| `bgp` / `QuadPattern` | a run of triple patterns | how many rows each one matches on its own (Q90) |
| `join` / `sequence` | two patterns sharing a variable | a join with no key is a cross product (Q91) |
| `leftjoin` / `conditional` | `OPTIONAL` | a `filter` that ended up inside it (Q19) |
| `filter` | `FILTER` | how far *down* it was pushed; further is better |
| `path` | `+ * ? ^ /` | these are rarely reordered — put a selective pattern before one |
| `project` | the `SELECT` list | — |
| `group` / `extend` | `GROUP BY`, `BIND`, `AS` | aggregation happens after the join, so a multiplied join is already wrong by here (Q92) |
| `distinct` / `reduced` | `DISTINCT` | `DISTINCT` over a large intermediate result is often the real cost |
| `slice` | `LIMIT` / `OFFSET` | it is applied *last*, so it rarely saves any work unless the engine can push it |

---

## 5 · The debugging playbook

**The result is empty.** In the order that pays off:

1. A datatype comparison — `xsd:gYear`, `xsd:date`, `geo:wktLiteral`. Go via
   `STR()`. (Q07, Q62, Q60)
2. A language tag — `"Cardiff"` never equals `"Cardiff"@en`. (Q95)
3. A mistyped prefix or IRI — `http` vs `https`, `#` vs `/`. (Q96)
4. A `FILTER` that escaped its `OPTIONAL`. (Q19)
5. `MINUS` with no shared variable, which removes nothing. (Q17)

Then bisect with Q93's EXISTS ladder to find the exact line.

**There are far too many rows.**

1. Count each pattern alone and multiply. If the product matches your row
   count, nothing joined. (Q90, Q91)
2. Look for a mistyped variable — `?other` where you meant `?town`.
3. Check whether a legitimate join is simply one-to-many: two labels per
   place will double a row count without anything being wrong.

**The numbers are wrong but the rows look right.**

1. Something in the join multiplied before the aggregate. `COUNT(DISTINCT ?x)`
   will tell you: if it differs from `COUNT(?x)`, that is your answer. (Q92)
2. `SUM` and `AVG` cannot be repaired with `DISTINCT`. Split into sub-queries.
   (Q70)
3. Check for zero-count groups that vanished entirely — you need `OPTIONAL`
   plus `COUNT(?x)`, not `COUNT(*)`. (Q25)

**It is slow.**

1. Get the plan. Check the filter was pushed down.
2. Run Q90 against your own predicates and see whether the engine's join order
   matches the selectivity.
3. Look for `?s ?p ?o`, an unbound predicate, or a path starting from an
   unbound variable — each of these scans everything.
4. Add a bounding box or another cheap selective pattern *first*, so the
   expensive test runs on fewer candidates. (Q52)
5. Only then start rewriting. Q97 is the reminder that three spellings of one
   question are equivalent, so rewriting is a legitimate tool — but measure
   before and after, because the fastest spelling depends on the store.
