# -*- coding: utf-8 -*-
"""Which query shows which feature.

At a hundred and twenty-odd queries the course needs a way in other than
reading it front to back. This scans every query for the features it uses and
builds an index: keyword or function, then the queries that demonstrate it.

It doubles as a coverage report. Anything in the catalogue below with no
queries against it is a gap, and running this is how the gaps get found:

    python scripts/features.py            # write FEATURES.md, report gaps

The patterns are matched against the query body with comments and string
literals removed, so a feature named in a comment does not count as taught.
"""

import re
from pathlib import Path

from specs import SQ, SUPD, SFED, GEOSPARQL, XPATH_FO

ROOT = Path(__file__).resolve().parent.parent

# --- the catalogue -------------------------------------------------------
#
# (group, label, pattern, spec url).  The pattern is a regular expression
# matched against the stripped query text; a plain name is turned into a
# word-boundary match, and anything containing a backslash is used as given.

_S = SQ + "#"

FEATURES = [
    ("Query forms", [
        ("SELECT", r"\bSELECT\b", _S + "x16-1-select"),
        ("SELECT expression", r"\(\s*[^)]*\bAS\s+\?", _S + "x16-1-2-select-expressions"),
        ("CONSTRUCT", r"\bCONSTRUCT\b", _S + "x16-2-construct"),
        ("ASK", r"\bASK\b", _S + "x16-3-ask"),
        ("DESCRIBE", r"\bDESCRIBE\b", _S + "x16-4-describe-informative"),
    ]),
    ("Choosing the data", [
        ("FROM", r"\bFROM\s+(?!NAMED)", _S + "x13-2-1-specifying-the-default-graph"),
        ("FROM NAMED", r"\bFROM\s+NAMED\b", _S + "x13-2-2-specifying-named-graphs"),
        ("GRAPH", r"\bGRAPH\b", _S + "x13-3-2-restricting-by-graph-iri"),
        ("SERVICE", r"\bSERVICE\b", SFED),
        ("SERVICE SILENT", r"\bSERVICE\s+SILENT\b", SFED),
    ]),
    ("Graph patterns", [
        ("OPTIONAL", r"\bOPTIONAL\b", _S + "x6-including-optional-values"),
        ("UNION", r"\bUNION\b", _S + "x7-matching-alternatives"),
        ("MINUS", r"\bMINUS\b", _S + "x8-2-removing-possible-solutions"),
        ("NOT EXISTS", r"\bNOT\s+EXISTS\b", _S + "x8-1-1-testing-for-the-absence-of-a-pattern"),
        ("EXISTS", r"(?<!NOT )\bEXISTS\b", _S + "x8-1-2-testing-for-the-presence-of-a-pattern"),
        ("FILTER", r"\bFILTER\b", _S + "x5-2-2-scope-of-filters"),
        ("BIND", r"\bBIND\b", _S + "x10-1-bind-assigning-to-variables"),
        ("VALUES", r"\bVALUES\b", _S + "x10-2-values-providing-inline-data"),
        ("UNDEF", r"\bUNDEF\b", _S + "x10-2-1-values-syntax"),
        ("Sub-query", r"\{\s*SELECT\b", _S + "x12-subqueries"),
    ]),
    ("Property paths", [
        ("sequence  /", r"[A-Za-z0-9]:[A-Za-z0-9_]+\s*/", _S + "x9-1-property-path-syntax"),
        ("inverse  ^", r"\^[A-Za-z0-9]*:", _S + "x9-1-property-path-syntax"),
        ("alternative  |", r"[A-Za-z0-9]:[A-Za-z0-9_]+\s*\|\s*\^?[A-Za-z0-9]*:", _S + "x9-1-property-path-syntax"),
        ("one or more  +", r"[A-Za-z0-9]:[A-Za-z0-9_]+\+", _S + "x9-4-arbitrary-length-path-matching"),
        ("zero or more  *", r"[A-Za-z0-9]:[A-Za-z0-9_]+\*", _S + "x9-4-arbitrary-length-path-matching"),
        ("zero or one  ?", r"[A-Za-z0-9]:[A-Za-z0-9_]+\?", _S + "x9-1-property-path-syntax"),
        ("negated  !", r"!\s*\(?\s*\^?[A-Za-z0-9]*:[A-Za-z0-9_]+", _S + "x9-1-property-path-syntax"),
    ]),
    ("Shaping the answer", [
        ("ORDER BY", r"\bORDER\s+BY\b", _S + "x15-1-order-by"),
        ("DISTINCT", r"\bDISTINCT\b", _S + "x15-3-duplicate-solutions"),
        ("REDUCED", r"\bREDUCED\b", _S + "x15-3-duplicate-solutions"),
        ("LIMIT", r"\bLIMIT\b", _S + "x15-5-limit"),
        ("OFFSET", r"\bOFFSET\b", _S + "x15-4-offset"),
        ("GROUP BY", r"\bGROUP\s+BY\b", _S + "x11-2-group-by"),
        ("HAVING", r"\bHAVING\b", _S + "x11-3-having"),
    ]),
    ("Aggregates", [
        ("COUNT", r"\bCOUNT\s*\(", _S + "x18-6-1-2-count"),
        ("SUM", r"\bSUM\s*\(", _S + "x18-6-1-3-sum"),
        ("AVG", r"\bAVG\s*\(", _S + "x18-6-1-4-avg"),
        ("MIN", r"\bMIN\s*\(", _S + "x18-6-1-5-min"),
        ("MAX", r"\bMAX\s*\(", _S + "x18-6-1-6-max"),
        ("GROUP_CONCAT", r"\bGROUP_CONCAT\s*\(", _S + "x18-6-1-7-groupconcat"),
        ("SAMPLE", r"\bSAMPLE\s*\(", _S + "x18-6-1-8-sample"),
    ]),
    ("Functional forms", [
        ("BOUND", r"\bBOUND\s*\(", _S + "x17-4-1-1-bound"),
        ("IF", r"\bIF\s*\(", _S + "x17-4-1-2-if"),
        ("COALESCE", r"\bCOALESCE\s*\(", _S + "x17-4-1-3-coalesce"),
        ("IN", r"\bIN\s*\(", _S + "x17-4-1-8-in"),
        ("NOT IN", r"\bNOT\s+IN\s*\(", _S + "x17-4-1-9-not-in"),
    ]),
    ("Functions on terms", [
        ("STR", r"\bSTR\s*\(", _S + "x17-4-2-7-str"),
        ("LANG", r"\bLANG\s*\(", _S + "x17-4-2-8-lang"),
        ("LANGDIR", r"\bLANGDIR\s*\(", _S + "x17-4-2-9-langdir"),
        ("hasLANG", r"\bhasLANG\s*\(", _S + "x17-4-2-10-haslang"),
        ("hasLANGDIR", r"\bhasLANGDIR\s*\(", _S + "x17-4-2-11-haslangdir"),
        ("DATATYPE", r"\bDATATYPE\s*\(", _S + "x17-4-2-12-datatype"),
        ("IRI", r"\bIRI\s*\(", _S + "x17-4-2-13-iri"),
        ("BNODE", r"\bBNODE\s*\(", _S + "x17-4-2-14-bnode"),
        ("STRDT", r"\bSTRDT\s*\(", _S + "x17-4-2-15-strdt"),
        ("STRLANG", r"\bSTRLANG\s*\(", _S + "x17-4-2-16-strlang"),
        ("STRLANGDIR", r"\bSTRLANGDIR\s*\(", _S + "x17-4-2-17-strlangdir"),
        ("UUID", r"\bUUID\s*\(", _S + "x17-4-2-18-uuid"),
        ("sameTerm", r"\bsameTerm\s*\(", _S + "x17-4-2-1-sameterm"),
        ("isIRI", r"\bisIRI\s*\(", _S + "x17-4-2-3-isiri"),
        ("isBLANK", r"\bisBLANK\s*\(", _S + "x17-4-2-4-isblank"),
        ("isLITERAL", r"\bisLITERAL\s*\(", _S + "x17-4-2-5-isliteral"),
        ("isNUMERIC", r"\bisNUMERIC\s*\(", _S + "x17-4-2-6-isnumeric"),
    ]),
    ("Functions on strings", [
        ("STRLEN", r"\bSTRLEN\s*\(", _S + "x17-4-3-1-strlen"),
        ("SUBSTR", r"\bSUBSTR\s*\(", _S + "x17-4-3-2-substr"),
        ("UCASE", r"\bUCASE\s*\(", _S + "x17-4-3-3-ucase"),
        ("LCASE", r"\bLCASE\s*\(", _S + "x17-4-3-4-lcase"),
        ("STRSTARTS", r"\bSTRSTARTS\s*\(", _S + "x17-4-3-5-strstarts"),
        ("STRENDS", r"\bSTRENDS\s*\(", _S + "x17-4-3-6-strends"),
        ("CONTAINS", r"\bCONTAINS\s*\(", _S + "x17-4-3-7-contains"),
        ("STRBEFORE", r"\bSTRBEFORE\s*\(", _S + "x17-4-3-8-strbefore"),
        ("STRAFTER", r"\bSTRAFTER\s*\(", _S + "x17-4-3-9-strafter"),
        ("CONCAT", r"\bCONCAT\s*\(", _S + "x17-4-3-10-concat"),
        ("langMatches", r"\blangMatches\s*\(", _S + "x17-4-3-11-langmatches"),
        ("REGEX", r"\bREGEX\s*\(", _S + "x17-4-3-12-regex"),
        ("REPLACE", r"\bREPLACE\s*\(", _S + "x17-4-3-13-replace"),
        ("ENCODE_FOR_URI", r"\bENCODE_FOR_URI\s*\(", _S + "x17-4-3-14-encode_for_uri"),
    ]),
    ("Numbers, dates and hashes", [
        ("ABS", r"\bABS\s*\(", _S + "x17-4-4-1-abs"),
        ("ROUND", r"\bROUND\s*\(", _S + "x17-4-4-2-round"),
        ("CEIL", r"\bCEIL\s*\(", _S + "x17-4-4-3-ceil"),
        ("FLOOR", r"\bFLOOR\s*\(", _S + "x17-4-4-4-floor"),
        ("RAND", r"\bRAND\s*\(", _S + "x17-4-4-5-rand"),
        ("NOW", r"\bNOW\s*\(", _S + "x17-4-5-1-now"),
        ("YEAR", r"\bYEAR\s*\(", _S + "x17-4-5-2-year"),
        ("MONTH", r"\bMONTH\s*\(", _S + "x17-4-5-3-month"),
        ("DAY", r"\bDAY\s*\(", _S + "x17-4-5-4-day"),
        ("MD5 / SHA", r"\b(MD5|SHA1|SHA256|SHA384|SHA512)\s*\(", _S + "x17-4-7-hash-functions"),
    ]),
    ("SPARQL 1.2", [
        ("TRIPLE", r"\bTRIPLE\s*\(", _S + "x17-4-6-1-triple"),
        ("SUBJECT", r"\bSUBJECT\s*\(", _S + "x17-4-6-2-subject"),
        ("PREDICATE", r"\bPREDICATE\s*\(", _S + "x17-4-6-3-predicate"),
        ("OBJECT", r"\bOBJECT\s*\(", _S + "x17-4-6-4-object"),
        ("isTRIPLE", r"\bisTRIPLE\s*\(", _S + "x17-4-6-5-istriple"),
        ("triple term  <<( )>>", r"<<\(", _S + "x4-1-rdf-term-syntax"),
        ("reifier  << ~ >>", r"<<[^(]", _S + "x4-1-rdf-term-syntax"),
        ("rdf:reifies", r"\brdf:reifies\b", _S + "x4-1-rdf-term-syntax"),
    ]),
    ("Updating", [
        ("INSERT DATA", r"\bINSERT\s+DATA\b", SUPD),
        ("DELETE DATA", r"\bDELETE\s+DATA\b", SUPD),
        ("DELETE WHERE", r"\bDELETE\s+WHERE\b", SUPD),
        ("DELETE ... INSERT", r"\bDELETE\s*\{", SUPD),
        ("INSERT ... WHERE", r"\bINSERT\s*\{", SUPD),
        ("LOAD", r"\bLOAD\b", SUPD),
        ("CLEAR", r"\bCLEAR\b", SUPD),
        ("DROP", r"\bDROP\b", SUPD),
        ("COPY", r"\bCOPY\b", SUPD),
        ("MOVE", r"\bMOVE\b", SUPD),
        ("ADD", r"\bADD\s+(GRAPH|DEFAULT|[A-Za-z0-9]*:)", SUPD),
    ]),
    ("Beyond the standard", [
        ("geo: / geof:", r"\bgeof?:[A-Za-z]", GEOSPARQL),
        ("afn:", r"\bafn:[A-Za-z]", "https://jena.apache.org/documentation/query/library-function.html"),
        ("spif:", r"\bspif:[A-Za-z]", "https://spinrdf.org/spif"),
        ("fn:", r"\bfn:[A-Za-z]", XPATH_FO),
        ("math:", r"\bmath:[A-Za-z]", XPATH_FO),
    ]),
]


_IRI = re.compile(r"<[^>\s]*>")
_STR = re.compile(r"\"\"\".*?\"\"\"|\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'", re.S)
_COMMENT = re.compile("#[^" + chr(10) + "]*")


def _strip(text: str) -> str:
    """Query text with comments and string literals removed.

    Order matters. An IRI usually contains a #, so stripping comments first
    would eat the rest of every line that mentions one -- which silently hides
    most of the function calls in the course. Literals go first, then IRIs
    collapse to <>, and only then are comments removed. The empty <> keeps the
    << of a triple term and a reifier detectable, which is the one place the
    angle brackets themselves are the feature.
    """
    text = _STR.sub(' ""', text)
    text = _IRI.sub("<>", text)
    return _COMMENT.sub(" ", text)


def scan(catalogue) -> dict:
    """feature label -> [query, ...], in reading order."""
    found: dict[str, list] = {}
    ordered = sorted(catalogue, key=lambda i: (i.module, i.sort_key))
    for group, entries in FEATURES:
        for label, pattern, _url in entries:
            rx = re.compile(pattern)
            hits = []
            for item in ordered:
                text = _strip(item.body + chr(10) + (item.verify or ""))
                if rx.search(text):
                    hits.append(item)
            found[label] = hits
    return found


def gaps(found: dict) -> list:
    return [label for label, hits in found.items() if not hits]


def markdown(found: dict) -> str:
    total = sum(1 for hits in found.values() if hits)
    counted = sum(len(e) for _g, e in FEATURES)
    out = [
        "# Find a feature",
        "",
        "Every SPARQL keyword and function this course demonstrates, and where. "
        + (f"All {counted} features in the catalogue have at least one query "
           "against them." if total == counted else
           f"{total} of {counted} features in the catalogue have at least one "
           "query against them; the rest are listed at the end as gaps."),
        "",
        "Generated by `python scripts/features.py` &mdash; it reads the query "
        "bodies, so it cannot disagree with them.",
        "",
    ]
    for group, entries in FEATURES:
        out += [f"## {group}", "", "| Feature | Queries | Spec |", "|---|---|---|"]
        for label, _pattern, url in entries:
            hits = found[label]
            if not hits:
                out.append(f"| `{label}` | — | [§]({url}) |")
                continue
            if len(hits) > 20:
                # Listing sixty links for SELECT helps nobody.
                links = f"used throughout — {len(hits)} queries"
            else:
                links = ", ".join(
                    f"[{i.qid}](queries/{i.module}/{i.filename})" for i in hits)
            out.append(f"| `{label}` | {links} | [§]({url}) |")
        out.append("")
    missing = gaps(found)
    if missing:
        out += ["## Not covered", "",
                "Features in the catalogue with no query against them:", "",
                "".join(f"`{m}` " for m in missing), ""]
    return "\n".join(out)


def html(found: dict) -> str:
    """The same index as a section of the course document, linking to the
    query cards on the page rather than to the files."""
    from html import escape
    groups = []
    for group, entries in FEATURES:
        rows = []
        for label, _pattern, url in entries:
            hits = found[label]
            if len(hits) > 20:
                links = (f'<span class="more">used throughout — '
                         f'{len(hits)} queries</span>')
            else:
                links = " ".join(
                    f'<a href="#{i.qid}">{i.qid}</a>' for i in hits)
            rows.append(
                f'<tr><th><a href="{url}" target="_blank" rel="noopener">'
                f'{escape(label)}</a></th><td>{links or "&mdash;"}</td></tr>')
        groups.append(f'<div class="feat-group"><h3>{escape(group)}</h3>'
                      f'<table class="feat"><tbody>{"".join(rows)}</tbody>'
                      f'</table></div>')
    covered = sum(1 for hits in found.values() if hits)
    total = sum(len(e) for _g, e in FEATURES)
    return f"""
<section class="module" id="features">
  <div class="module-head">
    <span class="module-num">Reference</span>
    <h2>Find a feature</h2>
    <p class="module-blurb">Every SPARQL keyword and function this course
      demonstrates, and which queries demonstrate it &mdash; {covered} of
      {total} in the catalogue. Built by scanning the query bodies, so it
      cannot drift from them; the feature name links to the section of the
      specification that defines it.</p>
  </div>
  <div class="wrap feat-wrap">{"".join(groups)}</div>
</section>"""


def main() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from querycat import CATALOGUE
    import queries_core          # noqa: F401
    for mod in ("queries_paths", "queries_geo", "queries_rdf12", "queries_forms",
                "queries_debug", "queries_extensions", "queries_federation",
                "queries_blanknodes", "queries_update", "queries_toolkit", "queries_inference"):
        try:
            __import__(mod)
        except ModuleNotFoundError:
            pass

    found = scan(CATALOGUE)
    (ROOT / "FEATURES.md").write_text(markdown(found) + "\n", encoding="utf-8")
    counted = sum(len(e) for _g, e in FEATURES)
    covered = sum(1 for hits in found.values() if hits)
    print(f"  FEATURES.md: {covered} of {counted} features have a query")
    missing = gaps(found)
    if missing:
        print(f"  {len(missing)} with none: " + ", ".join(missing))


if __name__ == "__main__":
    main()
