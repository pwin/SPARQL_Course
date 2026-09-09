# -*- coding: utf-8 -*-
"""Module 00 of the course document: the editor itself.

Prose rather than queries, so it's written here by hand instead of coming
from the query catalogue.  Kept in its own file because build_docs.py is
already long enough.
"""

LAB_SECTION = """
<section class="module" id="m00">
  <div class="module-head">
    <span class="module-num">Module 00</span>
    <h2>The lab</h2>
    <p class="module-blurb">Before the first query, learn the room. The Turtle
      Editor Viewer does four things a plain SPARQL endpoint doesn't: it draws
      the graph you're querying, reasons over it, converts it between formats
      and validates it against SHACL &mdash; all in the browser, with nothing
      installed. These aren't SPARQL exercises. They take twenty minutes and
      they make every query afterwards easier to picture.</p>
  </div>

  <article class="query">
    <header class="qhead"><span class="qid">00.1</span>
      <h3>Load something small and look at it</h3></header>
    <p class="asks">Open <code>data/04-bookshops.ttl</code> with Choose File,
      and spend five minutes in the graph pane before writing anything.</p>
    <div class="mech">
      <div class="mech-prose">
        <h4>How it works</h4>
        <p>The editor parses as you type, finds the subjects and draws the
          first ten of them. Ten is the cap, and it's exactly why this course
          ships eleven small module files rather than one large one: the
          combined dataset is perfectly good to <em>query</em> and almost
          useless to <em>look at</em>.</p>
        <h4>What to take away</h4>
        <ul class="learn">
          <li><b>Subjects</b> dropdown &mdash; pick <code>bt:shop-inkwell</code>
            on its own. That node and its dozen edges are precisely what Q02
            returns as a table.</li>
          <li><b>Engine</b>: dot, then neato, then circo. The same graph, three
            different questions answered &mdash; hierarchy, clustering, ring
            structure.</li>
          <li><b>Hide Types</b> and <b>Hide Annotations</b> strip the class and
            label edges, leaving the skeleton that module 05 walks.</li>
          <li><b>Get All</b> re-reads the pane and redraws from everything in
            it &mdash; and, importantly, <b>reloads the internal triplestore
            the SPARQL panel queries</b>. Edit the Turtle, press Get All, and
            only then does your query see the change.</li>
        </ul>
      </div>
      <figure class="diagram"><pre>Do this one properly:

  load    data/03-places.ttl
  set     Hide Types, Hide Annotations
  engine  dot

You are now looking at the containment hierarchy that
module 05 spends ten queries on.  Notice that the
English branch runs one level deeper than the Scottish
and Welsh ones:

  york      -> north-yorkshire -> yorkshire -> england
  edinburgh -> edinburgh-city  -> scotland

That asymmetry is the entire point of Q28, and it is
visible here before you write a line of SPARQL.</pre></figure>
    </div>
  </article>

  <article class="query">
    <header class="qhead"><span class="qid">00.2</span>
      <h3>Watch a reasoner do what a property path does</h3></header>
    <p class="asks">Click Show Facts. HyLAR, an OWL 2 RL reasoner, runs in the
      browser and shows you what it worked out.</p>
    <div class="mech">
      <div class="mech-prose">
        <h4>How it works</h4>
        <p>The vocabulary is written to give it real work:
          <code>bs:within</code> is declared an
          <code>owl:TransitiveProperty</code>, <code>bs:connectsTo</code> an
          <code>owl:SymmetricProperty</code>, and <code>bs:hasImprint</code> is
          the <code>owl:inverseOf bs:imprintOf</code> &mdash; a property
          asserted nowhere in the data at all.</p>
        <p>Load <code>data/03-places.ttl</code> and press Show Facts. Because
          containment is transitive, the reasoner materialises York to
          Yorkshire, York to England and York to Great Britain as real triples,
          which you can then match with a plain one-hop pattern.</p>
        <h4>What to take away</h4>
        <ul class="learn">
          <li>That's the same answer <code>bs:within+</code> computes, reached
            from the opposite end.</li>
          <li>Neither is right in general. Seeing both before module 05 is what
            makes property paths feel like a choice rather than the only
            option.</li>
          <li>Try it on <code>data/05-people.ttl</code> as well: Q44 builds the
            identical inverse triples with CONSTRUCT instead.</li>
        </ul>
      </div>
      <figure class="diagram"><pre>                reasoner           property path
                --------           -------------
work happens    once, up front     every time you ask
costs           storage, and a     nothing until asked
                re-run on change
you then write  ?t bs:within ?a    ?t bs:within+ ?a
portability     needs a reasoner   any SPARQL 1.1 engine

Two routes to the same set of triples.  This course
takes the second, because it travels.</pre></figure>
    </div>
  </article>

  <article class="query">
    <header class="qhead"><span class="qid">00.3</span>
      <h3>Convert, validate, and share by URL</h3></header>
    <p class="asks">The remaining editor features worth knowing before you
      start on the queries.</p>
    <div class="mech">
      <div class="mech-prose">
        <h4>What to take away</h4>
        <ul class="learn">
          <li><b>Add Prefixes</b> reads the prefixes out of the loaded data and
            prepends them to your query. The course's queries already carry
            the few they need, so this is for when you write your own.</li>
          <li><b>Get All, again.</b> Worth saying twice: an edit you have not
            pressed Get All after is invisible to the SPARQL panel, and the
            stale answer looks exactly like a wrong query. First thing to
            check when a change appears to do nothing.</li>
          <li><b>To JSON-LD / To Turtle</b> round-trip the data. Worth doing
            once with <code>data/10-annotations-1.2.ttl</code> open: RDF 1.2
            triple terms have no settled JSON-LD form, so the conversion is
            where you discover what your toolchain actually supports. Better
            here than in a pipeline.</li>
          <li><b>SHACL.</b> The editor bundles rdf-validate-shacl, and the
            course ships <code>data/shapes.ttl</code>. It reports clean. Break
            something on purpose &mdash; set a staff count to zero &mdash; and
            run it again.</li>
          <li><b>Load by URL.</b> The toolbar takes a URL, and the app accepts
            <code>?dot=&lt;url&gt;</code>, so a link can carry a dataset with
            it. The easy way to hand someone an exercise.</li>
        </ul>
      </div>
      <figure class="diagram"><pre>A CONSTRUCT is the loop back to the picture:

   the full dataset
        |
        |  Q47, a summary CONSTRUCT
        v
   ~165 triples of Turtle
        |
        |  copy out of the results pane
        v
   paste into the editor pane
        |
        v
   the graph view draws that instead

The editor's ten-subject cap stops being a limit the
moment you get to choose which ten.</pre></figure>
    </div>
  </article>
</section>
"""
