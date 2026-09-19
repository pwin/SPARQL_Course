# -*- coding: utf-8 -*-
"""What each of the three engines does when you ask it to reason.

Module 18 is about inference you can write in SPARQL, which runs everywhere.
This section is about the other kind: switching a reasoner on. All three
target engines can do it, no two of them do the same thing, and none of them
does it the way the SPARQL specification describes.

Every number here was measured on data/bookshop-trail-1.1.ttl. The commands
are the ones that produced them.
"""

from specs import SENT, SSD, OWL_PROFILES, RDFS, SEMANTICS


def _pre(text: str) -> str:
    from html import escape
    return f'<pre class="shell">{escape(text.strip(chr(10)))}</pre>'


REASONING_SECTION = f"""
<section class="module" id="reasoning">
  <div class="module-head">
    <span class="module-num">Reference</span>
    <h2>Reasoning in the three engines</h2>
    <p class="module-blurb">Module 18 derives things with property paths and
      CONSTRUCT, which runs anywhere. This is the other route: turning a
      reasoner on. All three engines can, none of them agrees with the others,
      and the differences are large enough to change what your queries
      return.</p>
    <p class="module-specs"><span>In the standards</span><a href="{SENT}"
      target="_blank" rel="noopener">SPARQL 1.2 Entailment Regimes</a> &middot;
      <a href="{OWL_PROFILES}" target="_blank" rel="noopener">OWL 2
      Profiles</a> &middot; <a href="{RDFS}" target="_blank"
      rel="noopener">RDF 1.2 Schema</a> &middot; <a href="{SEMANTICS}"
      target="_blank" rel="noopener">RDF 1.2 Semantics</a> &middot; <a
      href="{SSD}" target="_blank" rel="noopener">Service Description</a></p>
  </div>

  <div class="wrap proto-wrap">

    <div class="proto-block">
      <h3>The same dataset, four reasoners</h3>
      <p>4,826 asserted triples in, and two probes on the way out: how many
        <code>bs:within</code> triples exist afterwards, and how many things
        are typed <code>bs:Place</code>.</p>
      {_pre('''
                             distinct   usefully   bs:within  a bs:Place
                              triples        new
  asserted, no reasoning         4,826          -           63          64

  Jena  riotcmd.infer --rdfs     4,826          0          63          64
  HOLOS holos entail             5,051          0          63          64
  HyLAR OWL 2 RL (the editor)    8,777      3,952         186          64
  Jena  OWLMicro via assembler       --          --         186          64

  SPARQL  ?s bs:within+ ?o       4,826          0         186          64
                                                          ---
                                        no reasoner, same answer
''')}
      <p class="take"><b>Two things to take from that table.</b> Neither RDFS
        reasoner derives a single usable new fact on this dataset &mdash; the
        next block is why. And the last row: a property path computes the same
        transitive closure the OWL reasoners do, at query time, on every
        engine, with nothing switched on and nothing stored. Module 18 q140 is
        that query.</p>
      <p>"Usefully new" needs defining, because the raw counts flatter both
        RDFS reasoners. Jena emits 9,375 lines that reduce to 4,826 distinct
        triples &mdash; every one of them already asserted, differing only in
        blank node labels. HOLOS writes 225, of which 133 are reflexive
        axioms (<code>X rdfs:subClassOf X</code>, <code>p rdfs:subPropertyOf
        p</code>) and the remaining 92 type things as a class with no name.
        True, all of it, and not a fact you can query for.</p>
    </div>

    <div class="proto-block">
      <h3>Why RDFS adds so little here</h3>
      <p>Zero is not a bug in either engine. This dataset gives RDFS nothing
        to do: the class hierarchy is six subclass pairs in total, none more
        than one hop deep, and every instance already carries its types
        explicitly. <code>rdfs9</code>, the rule that does most of RDFS's
        work, has nothing left to derive. On a dataset where instances carry
        only their most specific type and the hierarchy is eight deep, the
        same reasoner earns its keep.</p>
      <p>What RDFS cannot do at any depth is the interesting part:
        <code>bs:within</code> is declared <code>owl:TransitiveProperty</code>
        and RDFS has no rule for transitivity, so both RDFS reasoners leave it
        at 63. Only the two OWL reasoners close it, and they agree exactly:
        186.</p>
    </div>

    <div class="proto-block">
      <h3>The browser editor &mdash; HyLAR, OWL 2 RL</h3>
      <p>Press <b>Show Facts</b>. HyLAR runs in the page, over the graph
        currently loaded, and adds what it derives to the view. It is the only
        one of the three that reasons where you can watch it happen, which
        makes it the right one to learn on.</p>
      {_pre('''
  load  data/bookshop-trail-1.1.ttl
  press Show Facts

  3,952 new triples, about 1.7 seconds
  bs:within closes from 63 to 186
  bs:author and bs:wrote fill each other in, both ways
''')}
      <p>OWL 2 RL is a rule language, so it derives new triples and never
        contradicts an existing one. Note what that means: it will happily
        derive facts from a self-contradictory ontology rather than telling
        you the ontology is broken. Consistency checking is a different job,
        and SHACL &mdash; module 12 &mdash; is the tool this course uses for
        it.</p>
    </div>

    <div class="proto-block">
      <h3>HOLOS &mdash; entail, into a graph of its own</h3>
      {_pre('''
  holos query  --data data/bookshop-trail-1.1.ttl --store run/store \\
               --query 'ASK { ?s ?p ?o }'
  holos entail --store run/store

  entailed 225 triple(s) into <https://holos.dev/ns#entailed>
    rounds  2
    store   4826 -> 5051 quads
''')}
      <p>The design decision worth copying: the derived triples go into their
        own named graph. A query sees them only if it asks for that graph, and
        <code>DROP GRAPH &lt;https://holos.dev/ns#entailed&gt;</code> undoes
        the whole thing exactly. Materialised inference goes stale the moment
        the data changes, and being able to throw it away cleanly is what
        makes it safe to have.</p>
      <p><code>--entail-budget</code> caps the closure &mdash; a reasoner on
        the wrong ontology can derive a great deal, and a budget turns a
        runaway into an error rather than a full disk.</p>
      <p class="take"><b>A finding worth reading twice.</b> 92 of those 225
        triples type every shop and publisher as a <b>blank node</b>: the
        anonymous <code>owl:unionOf</code> class that <code>bs:locatedIn</code>
        declares as its domain. Correct RDFS, and useless &mdash; you cannot
        write a query against a class with no name. Module 18 q143 finds them
        before a reasoner ever runs.</p>
    </div>

    <div class="proto-block">
      <h3>Jena &mdash; two routes, very different</h3>
      <p>The streaming inferencer is one command and does RDFS only:</p>
      {_pre('''
  java -cp "$JENA/lib/*" riotcmd.infer \\
       --rdfs=data/01-vocabulary.ttl \\
       data/bookshop-trail-1.1.ttl  >  inferred.nt
''')}
      <p class="take"><b>It streams, so it does not deduplicate.</b> That
        command emits 9,375 lines for 4,826 distinct triples &mdash; the same
        triple derived by several rules is printed once per rule. Sort and
        unique before counting anything, or you will report an inference
        closure roughly twice its real size and conclude the reasoner did
        something.</p>
      <p>For anything past RDFS, describe the model with an assembler and
        point <code>arq.sparql</code> or Fuseki at it:</p>
      {_pre('''
  # owl-micro.ttl
  @prefix ja: <http://jena.hpl.hp.com/2005/11/Assembler#> .

  <#dataset> a ja:RDFDataset ; ja:defaultGraph <#model> .
  <#model>   a ja:InfModel ;
      ja:baseModel <#base> ;
      ja:reasoner [ ja:reasonerURL
          <http://jena.hpl.hp.com/2003/OWLMicroFBRuleReasoner> ] .
  <#base>    a ja:MemoryModel ;
      ja:content [ ja:externalContent <file:///.../bookshop-trail-1.1.ttl> ] .

  java -cp "$JENA/lib/*" arq.sparql --desc=owl-micro.ttl --query=q.rq
''')}
      <p>That description ships as <code>scripts/owl-micro.ttl</code> &mdash;
        edit the one file path in it and it runs. It is what produced the 186
        in the table. Jena offers RDFS,
        OWLMicro, OWLMini and OWLFB in increasing order of what they derive
        and decreasing order of how fast they do it, plus a rule language of
        its own if none of them fits. Reasoning is applied to the model, so
        every query against that dataset sees the derived triples without
        asking &mdash; convenient, and easy to forget you switched on.</p>
    </div>

    <div class="proto-block">
      <h3>What none of them does</h3>
      <p>SPARQL has a specification for query-time entailment &mdash;
        <a href="{SENT}" target="_blank" rel="noopener">Entailment
        Regimes</a> &mdash; where the engine answers as though the entailed
        triples existed, without ever storing them, and advertises which
        regime it implements through its
        <a href="{SSD}" target="_blank" rel="noopener">service
        description</a>. None of these three does that. All three
        materialise: they compute the new triples and put them somewhere.</p>
      {_pre('''
  what the specification describes    what these engines do

  query-time entailment               materialisation
  nothing stored                      triples written
  always current                      stale as soon as data changes
  advertised in the service           you have to know
    description
''')}
      <p class="take"><b>So the practical question is never "does it
        reason".</b> It is: what does it derive, where does it put it, who
        re-runs it after a write, and can you tell derived triples from
        asserted ones afterwards? HOLOS answers the last one by construction.
        With the other two, a named graph and a discipline are on you.</p>
    </div>

  </div>
</section>"""
