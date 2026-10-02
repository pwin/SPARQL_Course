# -*- coding: utf-8 -*-
"""The prose half of module 13: how to get a plan out of each engine.

Commands rather than queries, so it's written by hand here and inserted at
the head of module 13.  The same material is in
queries/13-planning-and-debugging/PLANS.md.
"""

PLANS_PREAMBLE = """
<article class="query">
  <header class="qhead"><span class="qid">13.0</span>
    <h3>Getting the plan out of each engine</h3></header>
  <p class="asks">A query says <em>what</em> you want; the engine decides
    <em>how</em>. Jena and HOLOS each show you what they decided, and the two
    answers are usefully different because they show different layers of the
    same idea: the algebra the specification defines, and the physical plan with
    its join algorithms and the row count each operator actually produced.</p>

  <div class="code-wrap"><pre class="code"><code><span class="t-comment"># the query used throughout this section</span>
<span class="t-kw">SELECT</span> <span class="t-var">?name</span> <span class="t-var">?site</span> <span class="t-kw">WHERE</span> {
  <span class="t-var">?shop</span> <span class="t-kw">a</span> <span class="t-pname">bs:Bookshop</span> ; <span class="t-pname">rdfs:label</span> <span class="t-var">?name</span> ; <span class="t-pname">bs:locatedIn</span> <span class="t-var">?town</span> .
  <span class="t-var">?town</span> <span class="t-pname">bs:within</span>+ <span class="t-pname">bt:place-scotland</span> .
  <span class="t-kw">OPTIONAL</span> { <span class="t-var">?shop</span> <span class="t-pname">bs:website</span> <span class="t-var">?site</span> }
  <span class="t-kw">FILTER</span>( <span class="t-fn">STRLEN</span>(<span class="t-var">?name</span>) &gt; 8 )
}</code></pre></div>

  <div class="mech">
    <div class="mech-prose">
      <h4>Jena &mdash; the algebra, before and after</h4>
      <p><code>qparse --print=op</code> shows your query as the algebra the
        specification defines; <code>--print=opt</code> shows what Jena will
        actually run. Neither executes anything, which makes Jena the best of
        the three for learning what a query <em>means</em>.</p>
      <h4>HOLOS &mdash; the physical plan, with the counts</h4>
      <p><code>--explain</code> prints the operator tree with the join
        algorithm and the join keys on every node, and the number of rows that
        node produced. Where Jena shows what, HOLOS shows how: which side of
        each join is built into a hash table and which side probes it, and how
        far each step narrowed the answer. <code>--reorder</code> builds
        cardinality statistics first and orders each basic graph pattern by
        estimated selectivity.</p>
      <h4>The browser editor &mdash; the same plan</h4>
      <p>The editor runs HOLOS as WebAssembly, and
        <code>store.explain(query)</code> returns the same tree with the same
        counts. The SPARQL panel doesn't surface it yet, so this is a script
        rather than a click &mdash; but it is the same engine, so nothing about
        the plan you read on the command line stops being true in a tab.
        Comunica, which the editor used to run, names the <em>actor</em> that
        handled each operator rather than only the operation; that is a third
        shape worth seeing, and the course no longer runs it.</p>
    </div>
    <figure class="diagram"><pre>JENA, as written -- the filter is where you put it

  (project (?name ?site)
    (filter (&gt; (strlen ?name) 8)
      (leftjoin
        (sequence
          (bgp (triple ?shop rdf:type bs:Bookshop)
               (triple ?shop rdfs:label ?name)
               (triple ?shop bs:locatedIn ?town))
          (path ?town (path+ bs:within) bt:place-scotland))
        (bgp (triple ?shop bs:website ?site)))))

JENA, optimised -- the filter has MOVED INWARDS

  (project (?name ?site)
    (conditional
      (sequence
        (filter (&gt; (strlen ?name) 8)
          (bgp (triple ?shop rdf:type bs:Bookshop)
               (triple ?shop rdfs:label ?name)))
        (bgp (triple ?shop bs:locatedIn ?town))
        (path ?town (path+ bs:within) bt:place-scotland))
      (bgp (triple ?shop bs:website ?site))))

HOLOS -- the same pushdown, plus the join algorithms
and what each operator actually produced

  Project(?name, ?site)                              9 rows
  +- LeftJoin(HashBuildRightProbeLeft, keys = ?shop)  9
     +- LeftJoin(HashBuildLeftProbeRight, ?town)      9
     |  +- LeftJoin(HashBuildLeftProbeRight, ?shop)  32
     |  |  +- QuadPattern(?shop rdf:type bs:Bookshop)
     |  |  |                                         33
     |  |  +- Filter(STRLEN(?name) &gt; 8)           355
     |  |     +- QuadPattern(?shop rdfs:label ?name)
     |  |                                            444
     |  +- QuadPattern(?shop bs:locatedIn ?town)     46
     |  +- Path(?town (bs:within)+ bt:place-scotland)
     |                                               14
     +- QuadPattern(?shop bs:website ?site)          27

Read the counts upwards and you have the funnel: 444
labels, 355 long enough, 32 after the join to a shop,
9 once the town must be Scottish.

Two independently written optimisers pushing the same
filter to the same place is a good sign the rewrite is
the right one.</pre></figure>
  </div>

  <div class="callout callout-note"><b>Filter pushdown is the one to
    recognise.</b> In both plans the <code>FILTER</code> ends up directly on
    the pattern that binds <code>?name</code>, before the join and before the
    path, so rows that can't survive are discarded as early as possible. If a
    query is slow, compare the two forms: a filter that has <em>not</em> moved
    usually can't, commonly because it mentions a variable the optimiser
    can't prove is bound at that point.</div>
</article>

<article class="query">
  <header class="qhead"><span class="qid">13.0b</span>
    <h3>Reading any plan, and the debugging playbook</h3></header>
  <p class="asks">The operator names are shared across engines. So are the
    failure modes.</p>
  <div class="mech">
    <div class="mech-prose">
      <h4>What the operators mean</h4>
      <ul class="learn">
        <li><b>bgp</b> / <b>QuadPattern</b> &mdash; a run of triple patterns. Ask how
          many rows each matches alone (Q90).</li>
        <li><b>join</b> / <b>sequence</b> &mdash; two patterns sharing a variable. A
          join with no key is the cross product of Q91.</li>
        <li><b>leftjoin</b> / <b>conditional</b> &mdash; <code>OPTIONAL</code>. Look
          for a filter that ended up inside it (Q19).</li>
        <li><b>filter</b> &mdash; check how far down it was pushed. Further is
          better.</li>
        <li><b>path</b> &mdash; rarely reordered, so put a selective pattern before
          one.</li>
        <li><b>group</b> / <b>extend</b> &mdash; aggregation happens after the join,
          so a multiplied join is already wrong by the time it runs (Q92).</li>
        <li><b>slice</b> &mdash; <code>LIMIT</code>, applied last, so it seldom saves
          work unless the engine can push it.</li>
      </ul>
    </div>
    <figure class="diagram"><pre>THE RESULT IS EMPTY -- in payoff order

  1  a datatype comparison        Q07, Q62, Q60
       gYear, date, wktLiteral -- go via STR()
  2  a language tag               Q95
       "Cardiff" never equals "Cardiff"@en
  3  a mistyped prefix or IRI     Q96
       http vs https, # vs /
  4  a FILTER that escaped an OPTIONAL   Q19
  5  MINUS with no shared variable       Q17

  then bisect with Q93's EXISTS ladder.

FAR TOO MANY ROWS

  1  count each pattern alone and MULTIPLY   Q90, Q91
       product matches your row count? nothing joined
  2  look for a mistyped variable
  3  or a legitimate one-to-many: two labels
     per place doubles a count with nothing wrong

THE NUMBERS ARE WRONG, THE ROWS LOOK RIGHT

  1  COUNT(DISTINCT ?x) != COUNT(?x)?  something
     multiplied before the aggregate    Q92
  2  SUM and AVG cannot be repaired with DISTINCT.
     Split into sub-queries             Q70
  3  zero-count groups vanish entirely unless you
     use OPTIONAL and COUNT(?x)         Q25

IT IS SLOW

  1  get the plan; check the filter was pushed down
  2  run Q90 on your own predicates; does the join
     order match the selectivity?
  3  hunt for ?s ?p ?o, an unbound predicate, or a
     path starting from an unbound variable
  4  add a cheap selective pattern FIRST      Q52
  5  only then rewrite -- and measure, because the
     fastest spelling depends on the store    Q97</pre></figure>
  </div>
</article>
"""
