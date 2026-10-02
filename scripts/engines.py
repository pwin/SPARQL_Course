# -*- coding: utf-8 -*-
"""Cross-engine SPARQL runner for the Bookshop Trail course.

Runs one query against any of the three target environments and returns a
normalised result, so a query can be checked everywhere at once -- and so the
course can state precisely which engines agree.

Environment overrides:

    JENA_HOME     default C:/apache-jena-6.2.0
    HOLOS_EXE     default C:/repos/new_triplestore_sparql_engine/target/release/holos.exe
    EDITOR_HOME   a checkout of the Turtle Editor Viewer, used ONLY to borrow
                  its node_modules so Comunica can be run headless here.
                  Learners never need this: the editor itself is used online
                  at https://semantechs.co.uk/turtle-editor-viewer/ . Without
                  a checkout, run the checker with --engine holos --engine fuseki.
    NODE_EXE      any Node >= 18. The editor's engine is a WebAssembly module
                  with no dependencies; the Comunica it replaced needed Node 22.
    HOLOS_WASM_ENTRY
                  a built pkg-node/holos_wasm.js, to measure the `editor`
                  column against an engine that is not published yet. Without
                  it the editor's own installed package is used, which is what
                  that column ordinarily means.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

JENA_HOME = Path(os.environ.get("JENA_HOME", r"C:/apache-jena-6.2.0"))
HOLOS_EXE = Path(os.environ.get(
    "HOLOS_EXE", r"C:/repos/new_triplestore_sparql_engine/target/release/holos.exe"))
EDITOR_HOME = Path(os.environ.get("EDITOR_HOME", r"C:/repos/turtle-editor-viewer"))
NODE_EXE = os.environ.get("NODE_EXE") or shutil.which("node") or "node"

# GeoSPARQL for Jena.  The stock ARQ command line does not register the geof:
# functions; Fuseki's self-contained jar carries the whole implementation, so
# putting it on the classpath brings them in.  scripts/setup-geosparql.ps1
# installs the Apache SIS EPSG database that the CRS handling needs.
def _find_fuseki_jar() -> Path:
    """Locate fuseki-server.jar, whatever the install is called.

    Release and snapshot builds differ only in the directory name, and a
    machine may have both, so prefer the newest rather than insisting on one
    spelling. The jar matters because it carries Jena's GeoSPARQL
    implementation, which the ARQ command line does not load on its own.
    """
    override = os.environ.get("FUSEKI_JAR")
    if override:
        return Path(override)
    for parent in (Path("C:/"), JENA_HOME.parent):
        # Newest version first, and a release ahead of a snapshot of the same
        # version -- "6.2.0-SNAPSHOT" sorts after "6.2.0" as a plain string,
        # which is the wrong way round.
        def rank(path):
            name = path.parent.name.replace("apache-jena-fuseki-", "")
            release = not name.endswith("-SNAPSHOT")
            version = name.replace("-SNAPSHOT", "")
            parts = tuple(int(x) if x.isdigit() else 0
                          for x in version.split("."))
            return (parts, release)

        candidates = sorted(parent.glob("apache-jena-fuseki-*/fuseki-server.jar"),
                            key=rank, reverse=True)
        if candidates:
            return candidates[0]
    return Path("C:/apache-jena-fuseki-6.2.0/fuseki-server.jar")


FUSEKI_JAR = _find_fuseki_jar()
GEO_LIB = Path(os.environ.get(
    "GEO_LIB", str(Path(__file__).resolve().parent.parent / "lib" / "geosparql")))
SIS_DATA = os.environ.get(
    "SIS_DATA", str(Path(__file__).resolve().parent.parent / "build" / "sis-data"))


def _jena_classpath() -> str:
    """Jena's own bat file appends CLASSPATH with a colon, which is wrong on
    Windows, so the classpath is built here and java is invoked directly."""
    parts = [str(JENA_HOME / "lib" / "*")]
    if FUSEKI_JAR.exists():
        parts.append(str(FUSEKI_JAR))
    if GEO_LIB.exists():
        parts.append(str(GEO_LIB / "*"))
    return os.pathsep.join(parts)


def _jena_env() -> dict:
    env = {**os.environ, "JENA_HOME": str(JENA_HOME)}
    if Path(SIS_DATA).exists():
        env["SIS_DATA"] = SIS_DATA
    return env

_BNODE = re.compile(r"_:[A-Za-z0-9_.\-]+")
_HOLOS_PROGRESS = re.compile(r"^(loaded|shapes compiled|validated)")

NUMERIC = {
    "http://www.w3.org/2001/XMLSchema#integer",
    "http://www.w3.org/2001/XMLSchema#decimal",
    "http://www.w3.org/2001/XMLSchema#double",
    "http://www.w3.org/2001/XMLSchema#float",
    "http://www.w3.org/2001/XMLSchema#int",
    "http://www.w3.org/2001/XMLSchema#long",
}


def _canon_term(cell) -> str:
    """One result cell, in a form two engines can be compared on.

    Blank node labels are engine-local, so they collapse to _:b.  Numbers
    compare as numbers, so 0.90 and 0.9 are not a disagreement.  A triple
    term's value is a nested object in the SPARQL 1.2 results format, so it
    recurses into one.
    """
    kind = cell.get("type")
    if kind == "bnode":
        return "_:b"
    value = cell.get("value", "")
    if kind == "triple" and isinstance(value, dict):
        parts = (value.get("subject"), value.get("predicate"), value.get("object"))
        inner = " ".join(_canon_term(p) if isinstance(p, dict) else str(p) for p in parts)
        return f"<<( {inner} )>>"
    dt = cell.get("datatype")
    if dt in NUMERIC:
        try:
            value = f"{float(value):.6g}"
        except (TypeError, ValueError):
            pass
    if cell.get("xml:lang"):
        return f"{value}@{cell['xml:lang']}"
    if dt and dt not in NUMERIC:
        return f"{value}^^{dt}"
    return str(value)


class Result:
    """What one engine made of one query."""

    def __init__(self, engine, ok, rows=None, bindings=None, error=None, raw=""):
        self.engine = engine
        self.ok = ok
        self.rows = rows
        self.bindings = bindings or []
        self.error = error
        self.raw = raw

    def signature(self) -> str:
        """A canonical form, so two engines' answers can be compared.

        Rows are sorted, because SPARQL only guarantees an order when the
        query asks for one; numbers are compared as numbers, so that 0.90 and
        0.9 do not count as a disagreement.
        """
        canon = []
        for row in self.bindings:
            cells = [f"{var}={_canon_term(row[var])}" for var in sorted(row)]
            canon.append("|".join(cells))
        return "\n".join(sorted(canon))

    def __repr__(self):
        return f"{self.engine}: " + (f"ok rows={self.rows}" if self.ok else f"FAIL {self.error}")


def _abs(p) -> Path:
    """Absolute path.  Comunica runs with cwd set to the editor's checkout,
    so a relative path would resolve against the wrong directory."""
    return Path(p).resolve()


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=300, **kw)


_LOG_LINE = re.compile(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}[ 	]+(WARN|INFO|ERROR|DEBUG)[ 	]")


def _strip_log_noise(text: str) -> str:
    """Drop log lines Jena writes to stdout before the results.

    Without this a single SRS warning turns a valid empty result set into
    unparseable JSON, and the harness reports the log lines as rows.
    """
    lines = [l for l in (text or "").splitlines() if not _LOG_LINE.match(l.strip())]
    body = chr(10).join(lines).strip()
    if not body:
        return ""
    # A results document starts at the first brace; RDF output has no brace at
    # the start of a line, so only reposition when one is clearly present.
    first = body.find("{")
    if first > 0 and body.lstrip()[0] != "{" and not body.lstrip().startswith(
            ("PREFIX", "@prefix", "@base", "BASE", "<")):
        body = body[first:]
    return body


def _parse_results(engine, text, stderr=""):
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        # CONSTRUCT and DESCRIBE return RDF, not a result table.  Everything
        # reaching here is N-Triples: one statement per line.
        lines = [l.strip() for l in text.splitlines()
                 if l.strip() and not l.lstrip().startswith(("@", "#", "PREFIX", "BASE"))]
        lines = [_BNODE.sub("_:b", l) for l in lines]
        r = Result(engine, True, rows=len(lines), raw=stderr)
        r.bindings = [{"_stmt": {"value": l}} for l in sorted(lines)]
        return r
    if "boolean" in doc:
        return Result(engine, True, rows=1,
                      bindings=[{"_ask": {"value": str(doc["boolean"]).lower()}}], raw=stderr)
    binds = doc.get("results", {}).get("bindings", [])
    return Result(engine, True, rows=len(binds), bindings=binds, raw=stderr)


# ------------------------------------------------------------------ Jena ARQ
def jena(data_files, query_file) -> Result:
    cmd = ["java", "-cp", _jena_classpath(), "arq.sparql"]
    for d in data_files:
        cmd.append(f"--data={_abs(d).as_posix()}")
    cmd += [f"--query={_abs(query_file).as_posix()}", "--results=json"]
    env = _jena_env()
    p = _run(cmd, env=env)
    # Jena's default log4j configuration writes warnings to stdout, ahead of
    # the results, so the payload has to be found rather than assumed.
    out = _strip_log_noise(p.stdout)
    if p.returncode != 0 or not out:
        err = [l for l in (p.stderr or out).strip().splitlines() if l.strip()]
        msg = next((l for l in err if "ERROR" not in l or "Reconfiguration" not in l), "")
        return Result("fuseki", False, error=(msg or f"exit {p.returncode}")[:200], raw=p.stderr)
    if out.lstrip().startswith(("PREFIX", "@prefix", "@base", "BASE")):
        # A graph result.  riot turns it into N-Triples, which is the only
        # form all three engines can be compared in.
        tmp = Path(tempfile.gettempdir()) / "bookshop-construct.ttl"
        tmp.write_text(out, encoding="utf-8")
        r = _run(["java", "-cp", _jena_classpath(), "riotcmd.riot",
                  "--output=nt", str(tmp)], env=env)
        if r.returncode == 0 and r.stdout.strip():
            out = r.stdout.strip()
    return _parse_results("fuseki", out, p.stderr)


# -------------------------------------------------------------------- HOLOS
def holos(data_files, query_file) -> Result:
    cmd = [str(HOLOS_EXE), "query"]
    for d in data_files:
        cmd += ["--data", str(_abs(d))]
    cmd += ["--query-file", str(_abs(query_file))]
    p = _run(cmd)
    # holos prints a "loaded N quads in Xs" progress line before the result.
    # A SELECT then emits one line of JSON; a CONSTRUCT emits many lines of
    # N-Triples, so keep them all rather than only the last.
    lines = [l for l in p.stdout.strip().splitlines()
             if l.strip() and not _HOLOS_PROGRESS.match(l)]
    body = "\n".join(lines)
    if p.returncode != 0 or not body:
        err = [l for l in (p.stderr or p.stdout).strip().splitlines() if l.strip()]
        return Result("holos", False, error=(err[-1] if err else f"exit {p.returncode}")[:200],
                      raw=p.stderr)
    return _parse_results("holos", body, p.stderr)


# ------------------------------------- the editor's engine, as the editor runs it
#
# holos-wasm-node is the same WebAssembly binary the browser editor loads, with Node
# glue instead of browser glue, so what this reports is what the lab shows.  It
# replaced a Comunica runner that cannot run any more: the editor's checkout dropped
# Comunica when it moved engines, so `comunica` stopped being an engine this harness
# could reach.
_EDITOR_JS = r"""
import { readFileSync } from 'node:fs';

// Resolved at run time, not imported by name, so an engine that is not released yet can be
// measured: point HOLOS_WASM_ENTRY at a built pkg-node/holos_wasm.js. Without it this is the
// package the editor itself has installed, which is what the `editor` column should mean.
const { Store } = await import(process.env.HOLOS_WASM_ENTRY || 'holos-wasm-node');

// The hosts the editor's allow-list permits.  Kept in step with
// src/services/federation.ts by hand: this is a checking harness, and a copy that
// can drift is better than making the course import the editor's source.
const ALLOWED_HOSTS = ['dbpedia.org', 'query.wikidata.org', 'www.wikidata.org'];
const MAX_ROUNDS = 8;

const [queryFile, ...dataFiles] = process.argv.slice(2);
const store = new Store();
for (const f of dataFiles) {
  const format = f.endsWith('.trig') ? 'trig' : f.endsWith('.nq') ? 'nquads' : 'turtle';
  store.load(readFileSync(f, 'utf8'), format, 'https://example.org/bookshop-trail/');
}
const query = readFileSync(queryFile, 'utf8');

// SERVICE: the engine has no network client, so it reports the (endpoint, query)
// pairs it wants and the host fetches them, exactly as the editor's page does.
async function fetchService(endpoint, text) {
  const url = new URL(endpoint);
  if (url.protocol !== 'https:' || !ALLOWED_HOSTS.includes(url.hostname)) {
    throw new Error(`SERVICE <${endpoint}> refused: not in the editor's allow-list`);
  }
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/sparql-query',
      Accept: 'application/sparql-results+json',
    },
    body: text,
  });
  if (!res.ok) throw new Error(`SERVICE <${endpoint}> answered HTTP ${res.status}`);
  return res.text();
}

async function run() {
  if (!/\bSERVICE\b/i.test(query)) return store.query(query, undefined);
  for (let round = 0; round < MAX_ROUNDS; round += 1) {
    const pass = store.queryFederated(query, undefined);
    // A pass with anything pending lost rows to the unanswered clause, so it is
    // never the answer.
    if (pass.pending.length === 0) return pass.result;
    for (const p of pass.pending) {
      store.cacheService(p.endpoint, p.query, await fetchService(p.endpoint, p.query));
    }
  }
  throw new Error(`SERVICE did not settle after ${MAX_ROUNDS} rounds`);
}

const XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string';

function cell(term) {
  if (term.termType === 'Literal') {
    const out = { type: 'literal', value: term.value };
    if (term.language) out['xml:lang'] = term.language;
    else if (term.datatype && term.datatype.value !== XSD_STRING)
      out.datatype = term.datatype.value;
    return out;
  }
  if (term.termType === 'BlankNode') return { type: 'bnode', value: term.value };
  if (term.termType === 'Quad') {
    // A triple term, in the nested shape the SPARQL 1.2 results format uses --
    // which is what Jena and the HOLOS command line emit too, so the three
    // answers stay comparable.
    return {
      type: 'triple',
      value: {
        subject: cell(term.subject),
        predicate: cell(term.predicate),
        object: cell(term.object),
      },
    };
  }
  return { type: 'uri', value: term.value };
}

const out = await run();
if (typeof out === 'boolean') {
  console.log(JSON.stringify({ boolean: out }));
} else if (out.length > 0 && typeof out[0] === 'string') {
  // CONSTRUCT and DESCRIBE come back as N-Triples with no trailing separator.
  console.log('#NTRIPLES');
  for (const line of out) console.log(`${line} .`);
} else {
  // `variables` is the projection as the engine parsed it, so a column unbound in
  // every row is still named -- which the rows cannot show.
  const vars = out.variables ?? [];
  const bindings = out.map((row) => {
    const encoded = {};
    for (const v of vars) if (row[v]) encoded[v] = cell(row[v]);
    return encoded;
  });
  console.log(JSON.stringify({ head: { vars }, results: { bindings } }));
}
"""


def editor(data_files, query_file) -> Result:
    """The engine the browser editor runs, driven headlessly."""
    runner = EDITOR_HOME / ".course-runner.mjs"
    try:
        runner.write_text(_EDITOR_JS, encoding="utf-8")
        cmd = [NODE_EXE, str(runner), str(_abs(query_file))] + [str(_abs(d)) for d in data_files]
        p = _run(cmd, cwd=str(EDITOR_HOME))
        out = (p.stdout or "").strip().splitlines()
        if p.returncode != 0 or not out:
            err = [l for l in (p.stderr or "").strip().splitlines() if l.strip()]
            msg = next((l for l in err if not l.startswith((" ", "\t"))), f"exit {p.returncode}")
            return Result("editor", False, error=msg[:200], raw=p.stderr)
        if out[0].startswith("#NTRIPLES"):
            return _parse_results("editor", chr(10).join(out[1:]), p.stderr)
        return _parse_results("editor", out[-1], p.stderr)
    finally:
        runner.unlink(missing_ok=True)


# --------------------------------------------------------------- SPARQL Update
#
# An update has no result to compare, so a course query in module 17 comes in
# two halves: the update itself, and a SELECT that shows what it did.  Each
# runner applies the update to a throwaway copy of the data and then answers
# the second half against the result, which makes an update checkable in
# exactly the same way as everything else.

def jena_update(data_files, update_file, verify_file) -> Result:
    """arq.update applies the request and dumps the whole store; arq.sparql
    then answers the verification query against the dump."""
    env = _jena_env()
    cmd = ["java", "-cp", _jena_classpath(), "arq.update"]
    for d in data_files:
        cmd.append(f"--data={_abs(d).as_posix()}")
    cmd += [f"--update={_abs(update_file).as_posix()}", "--dump"]
    p = _run(cmd, env=env)
    dumped = _strip_log_noise(p.stdout)
    if p.returncode != 0 or not dumped:
        err = [l for l in (p.stderr or dumped).strip().splitlines() if l.strip()]
        return Result("fuseki", False,
                      error=(err[-1] if err else f"exit {p.returncode}")[:200],
                      raw=p.stderr)
    with tempfile.TemporaryDirectory(prefix="bookshop-upd-") as tmp:
        # .trig, because the dump carries named graphs when the update
        # touched one and Turtle would lose them without complaining.
        out = Path(tmp) / "after.trig"
        out.write_text(dumped, encoding="utf-8")
        return jena([out], verify_file)


def holos_update(data_files, update_file, verify_file) -> Result:
    """holos update needs a persistent store, so the data is loaded into a
    throwaway RocksDB directory first and thrown away afterwards."""
    with tempfile.TemporaryDirectory(prefix="bookshop-upd-") as tmp:
        store = Path(tmp) / "store"
        load = [str(HOLOS_EXE), "query", "--store", str(store)]
        for d in data_files:
            load += ["--data", str(_abs(d))]
        load += ["--query", "ASK { ?s ?p ?o }"]
        p = _run(load)
        if p.returncode != 0:
            return Result("holos", False, error=f"load failed: {p.stderr[:180]}",
                          raw=p.stderr)

        p = _run([str(HOLOS_EXE), "update", "--store", str(store),
                  "--update-file", str(_abs(update_file))])
        if p.returncode != 0:
            err = [l for l in (p.stderr or p.stdout).strip().splitlines() if l.strip()]
            return Result("holos", False,
                          error=(err[-1] if err else f"exit {p.returncode}")[:200],
                          raw=p.stderr)

        p = _run([str(HOLOS_EXE), "query", "--store", str(store),
                  "--query-file", str(_abs(verify_file))])
        lines = [l for l in p.stdout.strip().splitlines()
                 if l.strip() and not _HOLOS_PROGRESS.match(l)]
        body = chr(10).join(lines)
        if p.returncode != 0 or not body:
            err = [l for l in (p.stderr or p.stdout).strip().splitlines() if l.strip()]
            return Result("holos", False,
                          error=(err[-1] if err else f"exit {p.returncode}")[:200],
                          raw=p.stderr)
        return _parse_results("holos", body, p.stderr)


_EDITOR_UPDATE_JS = r"""
import { readFileSync } from 'node:fs';

// See the query runner: resolved at run time so an unreleased build can be measured.
const { Store } = await import(process.env.HOLOS_WASM_ENTRY || 'holos-wasm-node');

const [updateFile, verifyFile, ...dataFiles] = process.argv.slice(2);
const store = new Store();
for (const f of dataFiles) {
  const format = f.endsWith('.trig') ? 'trig' : f.endsWith('.nq') ? 'nquads' : 'turtle';
  store.load(readFileSync(f, 'utf8'), format, 'https://example.org/bookshop-trail/');
}
store.update(readFileSync(updateFile, 'utf8'), undefined);
const out = store.query(readFileSync(verifyFile, 'utf8'), undefined);

const XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string';

function cell(term) {
  if (term.termType === 'Literal') {
    const out = { type: 'literal', value: term.value };
    if (term.language) out['xml:lang'] = term.language;
    else if (term.datatype && term.datatype.value !== XSD_STRING)
      out.datatype = term.datatype.value;
    return out;
  }
  if (term.termType === 'BlankNode') return { type: 'bnode', value: term.value };
  if (term.termType === 'Quad') {
    return {
      type: 'triple',
      value: {
        subject: cell(term.subject),
        predicate: cell(term.predicate),
        object: cell(term.object),
      },
    };
  }
  return { type: 'uri', value: term.value };
}

if (typeof out === 'boolean') {
  console.log(JSON.stringify({ boolean: out }));
} else if (out.length > 0 && typeof out[0] === 'string') {
  console.log('#NTRIPLES');
  for (const line of out) console.log(`${line} .`);
} else {
  const vars = out.variables ?? [];
  const bindings = out.map((row) => {
    const encoded = {};
    for (const v of vars) if (row[v]) encoded[v] = cell(row[v]);
    return encoded;
  });
  console.log(JSON.stringify({ head: { vars }, results: { bindings } }));
}
"""


def editor_update(data_files, update_file, verify_file) -> Result:
    """The editor's engine does support update.  The editor's SPARQL panel has no
    way to display the result of an operation that returns nothing, which is a
    different thing and is why module 17 claims `holos-wasm` rather than
    `editor`."""
    runner = EDITOR_HOME / ".course-update-runner.mjs"
    try:
        runner.write_text(_EDITOR_UPDATE_JS, encoding="utf-8")
        cmd = ([NODE_EXE, str(runner), str(_abs(update_file)),
                str(_abs(verify_file))] + [str(_abs(d)) for d in data_files])
        p = _run(cmd, cwd=str(EDITOR_HOME))
        out = (p.stdout or "").strip().splitlines()
        if p.returncode != 0 or not out:
            err = [l for l in (p.stderr or "").strip().splitlines() if l.strip()]
            msg = next((l for l in err if not l.startswith((" ", "	"))),
                       f"exit {p.returncode}")
            return Result("holos-wasm", False, error=msg[:200], raw=p.stderr)
        if out[0].startswith("#NTRIPLES"):
            return _parse_results("holos-wasm", chr(10).join(out[1:]), p.stderr)
        return _parse_results("holos-wasm", out[-1], p.stderr)
    finally:
        runner.unlink(missing_ok=True)


UPDATE_ENGINES = {
    "holos-wasm": editor_update,
    "editor": editor_update,
    "holos": holos_update,
    "fuseki": jena_update,
    "jena": jena_update,
}


def run_all_updates(data_files, update_file, verify_file,
                    engines=("holos-wasm", "holos", "fuseki")):
    """Apply one update on several engines and compare what it did."""
    return {e: UPDATE_ENGINES[e](data_files, update_file, verify_file)
            for e in engines}


ENGINES = {
    "editor": editor,
    "holos": holos,
    "fuseki": jena,
    # The editor's engine under its own name, for when it is the engine rather
    # than the hosted tool that matters -- module 17, where the panel cannot
    # display what the engine can perfectly well do.
    "holos-wasm": editor,
    "jena": jena,
}


def run_all(data_files, query_file, engines=("editor", "holos", "fuseki")):
    """Run one query on several engines.  Keys come back exactly as given."""
    return {e: ENGINES[e](data_files, query_file) for e in engines}
