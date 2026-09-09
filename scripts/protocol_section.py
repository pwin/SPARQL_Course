# -*- coding: utf-8 -*-
"""Talking to an endpoint over HTTP.

Everything else in this course hands a query to a tool. This section is about
the layer underneath: what a SPARQL request actually is on the wire, which is
what you need the moment the query has to run from a script, a notebook or
another service.

The examples run against the Fuseki that scripts/setup-fuseki.ps1 starts, so
they can be pasted and tried rather than read.
"""

from specs import SPROT, SGSP, SJSON, SCSV, SXML, SUPD

BASE = "http://localhost:3030/bookshop"


def _pre(text: str) -> str:
    from html import escape
    return f'<pre class="shell">{escape(text.strip(chr(10)))}</pre>'


PROTOCOL_SECTION = f"""
<section class="module" id="protocol">
  <div class="module-head">
    <span class="module-num">Reference</span>
    <h2>Talking to an endpoint</h2>
    <p class="module-blurb">A SPARQL endpoint is an HTTP service, and the
      protocol is small enough to learn in one sitting. Once you know it, any
      language with an HTTP client can run these queries &mdash; no library
      required. The examples below assume the Fuseki that
      <code>setup-fuseki.ps1</code> starts.</p>
    <p class="module-specs"><span>In the standards</span><a href="{SPROT}"
      target="_blank" rel="noopener">SPARQL 1.2 Protocol</a> &middot; <a
      href="{SGSP}" target="_blank" rel="noopener">Graph Store HTTP
      Protocol</a> &middot; <a href="{SJSON}" target="_blank"
      rel="noopener">Results JSON</a> &middot; <a href="{SCSV}"
      target="_blank" rel="noopener">Results CSV and TSV</a> &middot; <a
      href="{SXML}" target="_blank" rel="noopener">Results XML</a> &middot; <a
      href="{SUPD}" target="_blank" rel="noopener">SPARQL Update</a></p>
  </div>

  <div class="wrap proto-wrap">

    <div class="proto-block">
      <h3>The three endpoints</h3>
      <p>Fuseki serves a dataset at three paths, and they are deliberately
        separate: the one that can change your data is the one you do not
        expose.</p>
      {_pre(f'''
{BASE}/sparql     read      SELECT, ASK, CONSTRUCT, DESCRIBE
{BASE}/update     write     INSERT, DELETE, LOAD, DROP  (module 17)
{BASE}/data       graphs    whole graphs, by PUT / GET / DELETE
''')}
      <p class="take"><b>The update endpoint is off by default.</b> Start the
        server with <code>-Writable</code> to open it, and do that only on a
        machine you control. q123 is what an open one costs.</p>
    </div>

    <div class="proto-block">
      <h3>A query is one parameter</h3>
      <p>GET with the query in the URL is the simplest form, and it is capped
        by whatever the server allows in a request line &mdash; a few thousand
        characters. POST with
        <code>application/x-www-form-urlencoded</code> has no such limit and
        is what a client should do by default.</p>
      {_pre(f'''
# GET -- fine for short queries, and cacheable
curl -G '{BASE}/sparql' \\
     --data-urlencode 'query=SELECT (COUNT(*) AS ?n) WHERE {{ ?s ?p ?o }}'

# POST -- what to use for anything real
curl -X POST '{BASE}/sparql' \\
     -H 'Content-Type: application/sparql-query' \\
     --data-binary @queries/05-property-paths/q31-walking-the-trail-in-either-direction.rq
''')}
      <p>The second form sends the query as the request body with content type
        <code>application/sparql-query</code>, which saves the URL encoding
        entirely. Both are in the specification; servers accept both.</p>
    </div>

    <div class="proto-block">
      <h3>Asking for the format you want</h3>
      <p>The <code>Accept</code> header decides what comes back. This is the
        part most people discover by accident, and it is the part that makes
        SPARQL pleasant to use from a shell.</p>
      {_pre(f'''
# JSON -- the default for SELECT, and what most clients parse
curl -G '{BASE}/sparql' -H 'Accept: application/sparql-results+json' \\
     --data-urlencode 'query=SELECT * WHERE {{ ?s ?p ?o }} LIMIT 5'

# CSV -- straight into a spreadsheet, or into awk
curl -G '{BASE}/sparql' -H 'Accept: text/csv' \\
     --data-urlencode 'query=SELECT ?s WHERE {{ ?s a <https://example.org/bookshop-trail/schema#Bookshop> }}'

# Turtle -- for CONSTRUCT and DESCRIBE, which return a graph
curl -G '{BASE}/sparql' -H 'Accept: text/turtle' \\
     --data-urlencode 'query=DESCRIBE <https://example.org/bookshop-trail/shop-inkwell>'
''')}
      {_pre('''
SELECT / ASK          application/sparql-results+json
                      application/sparql-results+xml
                      text/csv        text/tab-separated-values

CONSTRUCT / DESCRIBE  text/turtle     application/n-triples
                      application/ld+json   application/trig
''')}
      <p class="take"><b>Ask for TSV rather than CSV</b> when a value might
        contain a comma or a newline. TSV escapes them; CSV quotes them, and
        quoting survives fewer tools than it should.</p>
    </div>

    <div class="proto-block">
      <h3>Choosing the dataset from outside the query</h3>
      <p><code>default-graph-uri</code> and <code>named-graph-uri</code> do
        what <code>FROM</code> and <code>FROM NAMED</code> do (q124, q125),
        except from the request rather than the query text. Useful when the
        query is fixed and the scope is not.</p>
      {_pre(f'''
curl -G '{BASE}/sparql' \\
     --data-urlencode 'default-graph-uri=https://example.org/bookshop-trail/graph-shops' \\
     --data-urlencode 'default-graph-uri=https://example.org/bookshop-trail/graph-places' \\
     --data-urlencode 'query=SELECT (COUNT(*) AS ?n) WHERE {{ ?s ?p ?o }}'
''')}
      <p>A query that also carries <code>FROM</code> overrides these &mdash;
        the specification says the protocol parameters are used only when the
        query has no dataset clause of its own.</p>
    </div>

    <div class="proto-block">
      <h3>Updates, and PowerShell</h3>
      <p>An update goes to the write endpoint, by POST only, and returns no
        body. Windows has <code>Invoke-RestMethod</code>, which is friendlier
        than curl for this and is what the rest of this course uses.</p>
      {_pre(f'''
# read
$q = 'SELECT (COUNT(*) AS ?n) WHERE {{ ?s ?p ?o }}'
Invoke-RestMethod -Uri '{BASE}/sparql' -Method Post -Body @{{ query = $q }} |
    ForEach-Object {{ $_.results.bindings.n.value }}

# write -- needs the server started with -Writable
$u = 'INSERT DATA {{ <urn:a> <urn:b> <urn:c> }}'
Invoke-RestMethod -Uri '{BASE}/update' -Method Post -Body @{{ update = $u }}
''')}
      <p class="take"><b>No body comes back from an update.</b> A 200 or 204
        means it was applied; anything you want to know beyond that needs a
        query, which is why every lesson in module 17 has two halves.</p>
    </div>

    <div class="proto-block">
      <h3>Whole graphs, without SPARQL</h3>
      <p>The Graph Store Protocol treats each named graph as a document:
        <code>GET</code> it, <code>PUT</code> to replace it,
        <code>POST</code> to merge into it, <code>DELETE</code> to remove it.
        For loading a file this is simpler and much faster than an
        <code>INSERT</code>.</p>
      {_pre(f'''
# replace one graph with a file
curl -X PUT '{BASE}/data?graph=https://example.org/bookshop-trail/graph-shops' \\
     -H 'Content-Type: text/turtle' \\
     --data-binary @data/04-bookshops.ttl

# read it back
curl -H 'Accept: text/turtle' \\
     '{BASE}/data?graph=https://example.org/bookshop-trail/graph-shops'

# the default graph is named with ?default rather than ?graph=...
curl -X POST '{BASE}/data?default' \\
     -H 'Content-Type: text/turtle' --data-binary @data/03-places.ttl
''')}
    </div>

    <div class="proto-block">
      <h3>What goes wrong</h3>
      {_pre('''
400  the query did not parse. The body says where.
404  wrong path -- /sparql, not /query, on this server
406  the Accept header asked for something not offered
413  the query was too long for a GET. Use POST.
500  the query parsed and then failed. Often a function the
     server does not have -- module 15, and the reason a
     column comes back empty rather than erroring.

no response at all
     a query with no LIMIT against a large store. Add one,
     then read module 13.
''')}
      <p class="take"><b>Send the same query to two engines</b> when a result
        surprises you. That is the whole method this course was built with,
        and over HTTP it costs one changed URL.</p>
    </div>

  </div>
</section>"""
