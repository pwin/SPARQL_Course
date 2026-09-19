# -*- coding: utf-8 -*-
"""Pointers into the standards.

Everything this course teaches is defined somewhere, usually in one short
section of one W3C document, and the fastest way to settle an argument about
SPARQL is to read that section. This file holds the links: the documents
themselves, and a per-module list of the sections that module is about.

The section anchors were taken from the published documents rather than
typed from memory, so they land on the right heading. Check them with:

    python scripts/check_links.py
"""

# --- the documents -------------------------------------------------------

SQ = "https://www.w3.org/TR/sparql12-query/"
SFED = "https://www.w3.org/TR/sparql12-federated-query/"
SUPD = "https://www.w3.org/TR/sparql12-update/"
SPROT = "https://www.w3.org/TR/sparql12-protocol/"
SJSON = "https://www.w3.org/TR/sparql12-results-json/"
SCSV = "https://www.w3.org/TR/sparql12-results-csv-tsv/"
SXML = "https://www.w3.org/TR/sparql12-results-xml/"
SSD = "https://www.w3.org/TR/sparql12-service-description/"
SENT = "https://www.w3.org/TR/sparql12-entailment/"
SGSP = "https://www.w3.org/TR/sparql12-graph-store-protocol/"

SQ11 = "https://www.w3.org/TR/sparql11-query/"
SFED11 = "https://www.w3.org/TR/sparql11-federated-query/"
SUPD11 = "https://www.w3.org/TR/sparql11-update/"

CONCEPTS = "https://www.w3.org/TR/rdf12-concepts/"
TURTLE = "https://www.w3.org/TR/rdf12-turtle/"
TRIG = "https://www.w3.org/TR/rdf12-trig/"
NTRIPLES = "https://www.w3.org/TR/rdf12-n-triples/"
SEMANTICS = "https://www.w3.org/TR/rdf12-semantics/"
RDFS = "https://www.w3.org/TR/rdf12-schema/"

SHACL = "https://www.w3.org/TR/shacl/"
SHACL12 = "https://www.w3.org/TR/shacl12-core/"
OWL_SYNTAX = "https://www.w3.org/TR/owl2-syntax/"
OWL_PRIMER = "https://www.w3.org/TR/owl2-primer/"
OWL_PROFILES = "https://www.w3.org/TR/owl2-profiles/"
SKOS = "https://www.w3.org/TR/skos-reference/"
PROV = "https://www.w3.org/TR/prov-o/"
XPATH_FO = "https://www.w3.org/TR/xpath-functions-31/"
GEOSPARQL = "https://docs.ogc.org/is/22-047r1/22-047r1.html"


# The reading list, grouped the way a learner would want it.  The note says
# why this course cares about the document, not what the document is.
STANDARDS = [
    ("The query language", [
        ("SPARQL 1.2 Query Language", SQ,
         "The one to bookmark. Everything in modules 01 to 09 and 11 to 16 is "
         "defined here, and section 17.4 is the function reference you will "
         "open most often."),
        ("SPARQL 1.2 Update", SUPD,
         "INSERT, DELETE and LOAD. The course reads rather than writes, so "
         "this appears only in module 12."),
        ("SPARQL 1.2 Federated Query", SFED,
         "SERVICE, in its own short document. Module 08."),
        ("SPARQL 1.1 Query Language", SQ11,
         "The previous edition, still what most engines implement in full. "
         "Worth having open beside the 1.2 document when an engine disagrees "
         "with you."),
    ]),
    ("The data model and its syntaxes", [
        ("RDF 1.2 Concepts and Abstract Syntax", CONCEPTS,
         "What a triple, a literal, a blank node and a triple term actually "
         "are. Appendix B is the one on replacing blank nodes with IRIs."),
        ("RDF 1.2 Turtle", TURTLE,
         "The syntax every data file in this course is written in."),
        ("RDF 1.2 TriG", TRIG,
         "Turtle plus named graphs, which is what bookshop-trail.trig uses."),
        ("RDF 1.2 N-Triples", NTRIPLES,
         "One triple per line, no abbreviations. The format to fall back on "
         "when a parser disagrees with you about Turtle."),
        ("RDF 1.2 Schema", RDFS,
         "rdfs:label, rdfs:subClassOf, rdfs:domain and rdfs:range."),
        ("RDF 1.2 Semantics", SEMANTICS,
         "What entailment means. Only needed if you start asking what a "
         "reasoner is allowed to conclude."),
    ]),
    ("Vocabularies the dataset uses", [
        ("OWL 2 Structural Specification", OWL_SYNTAX,
         "The normative one. The vocabulary file is OWL 2 DL, and this is the "
         "document that says what that requires."),
        ("OWL 2 Primer", OWL_PRIMER,
         "The readable one. Start here."),
        ("OWL 2 Profiles", OWL_PROFILES,
         "What DL, EL, QL and RL are, and why the datatype map matters."),
        ("SKOS Reference", SKOS,
         "The genre scheme is a SKOS concept scheme: broader, narrower, "
         "prefLabel, altLabel."),
        ("PROV-O", PROV,
         "Where the provenance terms in the annotations come from."),
        ("SHACL", SHACL,
         "Validating the shape of the data, used in module 12. SHACL 1.2 "
         "Core is at " + SHACL12 + "."),
        ("OGC GeoSPARQL 1.1", GEOSPARQL,
         "geo:asWKT, geof:sfWithin, geof:distance and the rest of module 10. "
         "An OGC standard, not a W3C one."),
    ]),
    ("Results, protocol and functions", [
        ("SPARQL 1.2 Query Results JSON Format", SJSON,
         "What comes back over HTTP, and what the checking harness in this "
         "repository compares."),
        ("SPARQL 1.2 Query Results CSV and TSV Formats", SCSV,
         "The formats to ask for when the answer is going into a spreadsheet."),
        ("SPARQL 1.2 Query Results XML Format", SXML,
         "The oldest of the three, still widely produced."),
        ("SPARQL 1.2 Protocol", SPROT,
         "How a query gets to an endpoint over HTTP: the query parameter, "
         "default-graph-uri, and which verbs are allowed."),
        ("SPARQL 1.2 Graph Store HTTP Protocol", SGSP,
         "Managing whole graphs with PUT and DELETE rather than with SPARQL "
         "Update."),
        ("SPARQL 1.2 Service Description", SSD,
         "How an endpoint advertises what it supports -- including which "
         "extension functions, which module 15 is about."),
        ("SPARQL 1.2 Entailment Regimes", SENT,
         "What it means to query with a reasoner switched on."),
        ("XPath and XQuery Functions and Operators 3.1", XPATH_FO,
         "SPARQL borrows its function semantics from here, and module 15 "
         "meets the fn: library directly."),
    ]),
]


# --- what each module is defined by --------------------------------------
#
# Three to six sections per module: the ones worth reading before or after
# the queries, not everything the module touches.

MODULE_SPECS = {
    "01-first-queries": [
        ("SPARQL 1.2 Query 2. Making Simple Queries",
         SQ + "#x2-making-simple-queries-informative"),
        ("SPARQL 1.2 Query 4. SPARQL Syntax", SQ + "#x4-sparql-syntax"),
        ("SPARQL 1.2 Query 5. Graph Patterns", SQ + "#x5-graph-patterns"),
        ("SPARQL 1.2 Query 16.1 SELECT", SQ + "#x16-1-select"),
        ("RDF 1.2 Turtle", TURTLE),
    ],
    "02-filtering": [
        ("SPARQL 1.2 Query 3. RDF Term Constraints",
         SQ + "#x3-rdf-term-constraints-informative"),
        ("SPARQL 1.2 Query 10.1 BIND",
         SQ + "#x10-1-bind-assigning-to-variables"),
        ("SPARQL 1.2 Query 17.2.3 Effective Boolean Value",
         SQ + "#x17-2-3-effective-boolean-value-ebv"),
        ("SPARQL 1.2 Query 17.4.3 Functions on Strings",
         SQ + "#x17-4-3-functions-on-strings"),
        ("SPARQL 1.2 Query 17.4.5 Functions on Dates and Times",
         SQ + "#x17-4-5-functions-on-dates-and-times"),
    ],
    "03-optional-and-negation": [
        ("SPARQL 1.2 Query 6. Including Optional Values",
         SQ + "#x6-including-optional-values"),
        ("SPARQL 1.2 Query 7. Matching Alternatives",
         SQ + "#x7-matching-alternatives"),
        ("SPARQL 1.2 Query 8. Negation", SQ + "#x8-negation"),
        ("SPARQL 1.2 Query 8.3 NOT EXISTS and MINUS compared",
         SQ + "#x8-3-relationship-and-differences-between-not-exists-and-minus"),
        ("SPARQL 1.2 Query 10.2 VALUES",
         SQ + "#x10-2-values-providing-inline-data"),
    ],
    "04-aggregation": [
        ("SPARQL 1.2 Query 11. Aggregates", SQ + "#x11-aggregates"),
        ("SPARQL 1.2 Query 11.2 GROUP BY", SQ + "#x11-2-group-by"),
        ("SPARQL 1.2 Query 11.3 HAVING", SQ + "#x11-3-having"),
        ("SPARQL 1.2 Query 11.4 Aggregate Projection Restrictions",
         SQ + "#x11-4-aggregate-projection-restrictions"),
        ("SPARQL 1.2 Query 18.6.1 Aggregate Algebra",
         SQ + "#x18-6-1-aggregate-algebra"),
    ],
    "05-property-paths": [
        ("SPARQL 1.2 Query 9. Property Paths", SQ + "#x9-property-paths"),
        ("SPARQL 1.2 Query 9.1 Property Path Syntax",
         SQ + "#x9-1-property-path-syntax"),
        ("SPARQL 1.2 Query 9.4 Arbitrary Length Path Matching",
         SQ + "#x9-4-arbitrary-length-path-matching"),
        ("SPARQL 1.2 Query 18.5 Property Path Patterns",
         SQ + "#x18-5-property-path-patterns"),
    ],
    "06-subqueries": [
        ("SPARQL 1.2 Query 12. Subqueries", SQ + "#x12-subqueries"),
        ("SPARQL 1.2 Query 15. Solution Sequences and Modifiers",
         SQ + "#x15-solution-sequences-and-modifiers"),
        ("SPARQL 1.2 Query 18.3.1 Variable Scope",
         SQ + "#x18-3-1-variable-scope"),
        ("SPARQL 1.2 Query 10.2 VALUES",
         SQ + "#x10-2-values-providing-inline-data"),
    ],
    "07-construct-ask-describe": [
        ("SPARQL 1.2 Query 16. Query Forms", SQ + "#x16-query-forms"),
        ("SPARQL 1.2 Query 16.2 CONSTRUCT", SQ + "#x16-2-construct"),
        ("SPARQL 1.2 Query 16.2.4 CONSTRUCT WHERE",
         SQ + "#x16-2-4-construct-where"),
        ("SPARQL 1.2 Query 16.3 ASK", SQ + "#x16-3-ask"),
        ("SPARQL 1.2 Query 16.4 DESCRIBE",
         SQ + "#x16-4-describe-informative"),
    ],
    "08-named-graphs": [
        ("SPARQL 1.2 Query 13. RDF Dataset", SQ + "#x13-rdf-dataset"),
        ("SPARQL 1.2 Query 13.2 Specifying RDF Datasets",
         SQ + "#x13-2-specifying-rdf-datasets"),
        ("SPARQL 1.2 Query 13.3 Querying the Dataset",
         SQ + "#x13-3-querying-the-dataset"),
        ("SPARQL 1.2 Query 14. Basic Federated Query",
         SQ + "#x14-basic-federated-query"),
        ("SPARQL 1.2 Federated Query", SFED),
        ("SPARQL 1.2 Query, Security Considerations",
         SQ + "#c-security-considerations"),
        ("RDF 1.2 TriG", TRIG),
    ],
    "09-geo-without-geosparql": [
        ("SPARQL 1.2 Query 17.3 Operator Mapping",
         SQ + "#x17-3-operator-mapping"),
        ("SPARQL 1.2 Query 17.4.4 Functions on Numerics",
         SQ + "#x17-4-4-functions-on-numerics"),
        ("SPARQL 1.2 Query 15.1 ORDER BY", SQ + "#x15-1-order-by"),
    ],
    "10-geosparql": [
        ("OGC GeoSPARQL 1.1", GEOSPARQL),
        ("SPARQL 1.2 Query 17.6 Extensible Value Testing",
         SQ + "#x17-6-extensible-value-testing"),
        ("SPARQL 1.2 Service Description", SSD),
    ],
    "11-sparql-1-2": [
        ("SPARQL 1.2 Query 17.4.6 Functions on Triple Terms",
         SQ + "#x17-4-6-functions-on-triple-terms"),
        ("SPARQL 1.2 Query 17.4.2.9 LANGDIR", SQ + "#x17-4-2-9-langdir"),
        ("SPARQL 1.2 Query 17.4.2.17 STRLANGDIR",
         SQ + "#x17-4-2-17-strlangdir"),
        ("SPARQL 1.2 Query, Appendix A: changes since SPARQL 1.1",
         SQ + "#a-changes-between-sparql-1-1-query-language-and-sparql-1-2-"
              "query-language"),
        ("RDF 1.2 Concepts 3.6 Triple Terms", CONCEPTS + "#x3-6-triple-terms"),
        ("RDF 1.2 Concepts 3.4.3 Initial Text Direction",
         CONCEPTS + "#x3-4-3-initial-text-direction"),
        ("RDF 1.2 Turtle 2.11 Reifying Triples",
         TURTLE + "#x2-11-reifying-triples"),
    ],
    "12-graphs-in-graphs-out": [
        ("SPARQL 1.2 Query 16.2 CONSTRUCT", SQ + "#x16-2-construct"),
        ("SPARQL 1.2 Query 16.2.1 Templates with Blank Nodes",
         SQ + "#x16-2-1-templates-with-blank-nodes"),
        ("SPARQL 1.2 Query 16.4 DESCRIBE",
         SQ + "#x16-4-describe-informative"),
        ("SPARQL 1.2 Update", SUPD),
        ("SHACL", SHACL),
    ],
    "13-planning-and-debugging": [
        ("SPARQL 1.2 Query 18. Definition of SPARQL",
         SQ + "#x18-definition-of-sparql"),
        ("SPARQL 1.2 Query 18.3 Translation to the Algebraic Syntax",
         SQ + "#x18-3-translation-to-the-algebraic-syntax"),
        ("SPARQL 1.2 Query 18.6.2 Evaluation Semantics",
         SQ + "#x18-6-2-evaluation-semantics"),
        ("SPARQL 1.2 Query 17.2.2 Evaluation errors",
         SQ + "#x17-2-2-evaluation-errors"),
    ],
    "14-challenges": [
        ("SPARQL 1.2 Query Language", SQ),
        ("SPARQL 1.2 Query 17.4 Function Definitions",
         SQ + "#x17-4-function-definitions"),
    ],
    "15-beyond-the-standard": [
        ("SPARQL 1.2 Query 17.3.1 Operator Extensibility",
         SQ + "#x17-3-1-operator-extensibility"),
        ("SPARQL 1.2 Query 17.6 Extensible Value Testing",
         SQ + "#x17-6-extensible-value-testing"),
        ("SPARQL 1.2 Service Description", SSD),
        ("XPath and XQuery Functions and Operators 3.1", XPATH_FO),
    ],
    "16-blank-nodes": [
        ("SPARQL 1.2 Query 2.4 Blank Node Identifiers in Query Results",
         SQ + "#x2-4-blank-node-identifiers-in-query-results"),
        ("SPARQL 1.2 Query 4.1.4 Syntax for Blank Nodes",
         SQ + "#x4-1-4-syntax-for-blank-nodes"),
        ("SPARQL 1.2 Query 4.2.3 RDF Collections",
         SQ + "#x4-2-3-rdf-collections"),
        ("SPARQL 1.2 Query 5.1.1 Blank Node Identifiers",
         SQ + "#x5-1-1-blank-node-identifiers"),
        ("SPARQL 1.2 Query 18.4.2 Treatment of Blank Nodes",
         SQ + "#x18-4-2-treatment-of-blank-nodes"),
        ("RDF 1.2 Concepts 3.5 Blank Nodes", CONCEPTS + "#x3-5-blank-nodes"),
        ("RDF 1.2 Concepts, Appendix B: Replacing Blank Nodes with IRIs",
         CONCEPTS + "#b-replacing-blank-nodes-with-iris"),
        ("RDF 1.2 Turtle 2.9 Collections", TURTLE + "#x2-9-collections"),
    ],
}


# --- individual sections worth naming in a single query ------------------
#
# Only where the general module list would send a reader hunting.

QUERY_SPECS = {
    "q17": [("SPARQL 1.2 Query 8.3 NOT EXISTS and MINUS compared",
             SQ + "#x8-3-relationship-and-differences-between-not-exists-and-"
                  "minus"),
            ("SPARQL 1.2 Query 17.4.1.4 NOT EXISTS and EXISTS",
             SQ + "#x17-4-1-4-not-exists-and-exists")],
    "q109": [("SPARQL 1.2 Query 17.4.2.4 isBLANK",
              SQ + "#x17-4-2-4-isblank")],
    "q110": [("SPARQL 1.2 Query 2.4 Blank Node Identifiers in Query Results",
              SQ + "#x2-4-blank-node-identifiers-in-query-results"),
             ("SPARQL 1.2 Query 19.6 Blank Nodes and Blank Node Identifiers",
              SQ + "#x19-6-blank-nodes-and-blank-node-identifiers")],
    "q111": [("SPARQL 1.2 Query 4.2.3 RDF Collections",
              SQ + "#x4-2-3-rdf-collections"),
             ("RDF 1.2 Turtle 2.9 Collections", TURTLE + "#x2-9-collections")],
    "q113": [("SPARQL 1.2 Query 17.4.2.1 sameTerm",
              SQ + "#x17-4-2-1-sameterm")],
    "q114": [("RDF 1.2 Concepts, Appendix B: Replacing Blank Nodes with IRIs",
              CONCEPTS + "#b-replacing-blank-nodes-with-iris"),
             ("SPARQL 1.2 Query 17.4.2.14 BNODE",
              SQ + "#x17-4-2-14-bnode")],
    "q115": [("SPARQL 1.2 Query 16.2.1 Templates with Blank Nodes",
              SQ + "#x16-2-1-templates-with-blank-nodes")],
    "q105": [("SPARQL 1.2 Federated Query", SFED)],
    "q106": [("SPARQL 1.2 Federated Query", SFED)],
    "q107": [("SPARQL 1.2 Query 10.2.1 VALUES syntax",
              SQ + "#x10-2-1-values-syntax")],
    "q108": [("SPARQL 1.2 Query, Security Considerations",
              SQ + "#c-security-considerations")],
}


def for_query(qid: str, module: str, limit: int = 3):
    """The sections to name in one query's header."""
    out = list(QUERY_SPECS.get(qid, []))
    for entry in MODULE_SPECS.get(module, []):
        if len(out) >= limit:
            break
        if entry not in out:
            out.append(entry)
    return out[:limit]
