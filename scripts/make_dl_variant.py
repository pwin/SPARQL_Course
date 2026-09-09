#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write data/bookshop-trail-owl-dl.ttl: the dataset, inside OWL 2 DL.

The vocabulary in 01-vocabulary.ttl is already an OWL 2 DL ontology.  The
instance data is not, and for exactly one reason that no amount of careful
declaration can fix: **xsd:gYear and xsd:date are not in the OWL 2 datatype
map**.  OWL 2 admits xsd:string, xsd:boolean, xsd:decimal, xsd:integer and its
subtypes, xsd:float, xsd:double, xsd:dateTime, xsd:dateTimeStamp, xsd:anyURI,
the binary types, the string subtypes, rdf:PlainLiteral, rdf:XMLLiteral,
owl:real and owl:rational.  gYear and date are absent from that list, so a
literal typed with either is outside the profile wherever it appears.

Declaring them makes it worse rather than better: `xsd:gYear a rdfs:Datatype`
turns a built-in into a *user-defined* datatype, and using a user-defined
datatype in an assertion is a second, different violation.  The validator
says so in as many words, which is a good demonstration that a profile is a
real constraint and not a style guide.

So this script produces a second copy of the data with:

    "1979"^^xsd:gYear      ->  "1979"^^xsd:integer
    "2025-03-08"^^xsd:date ->  "2025-03-08T00:00:00Z"^^xsd:dateTime

and nothing else changed.  The main dataset keeps gYear deliberately: the
portability trap it creates is one of the most useful things in the course
(q07, q13, q62, q95), and a learner who never meets gYear here will meet it
somewhere less forgiving.

    python scripts/make_dl_variant.py
    java -jar lib/owl/robot.jar validate-profile --profile DL \\
         --input data/bookshop-trail-owl-dl.ttl
"""
from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SOURCE = DATA / "bookshop-trail-1.1.ttl"
TARGET = DATA / "bookshop-trail-owl-dl.ttl"

GYEAR = re.compile(r'"(\d{4})"\^\^xsd:gYear')
DATE = re.compile(r'"(\d{4}-\d{2}-\d{2})"\^\^xsd:date\b')

HEADER = """#{rule}
#  THE BOOKSHOP TRAIL -- OWL 2 DL CONFORMANT VARIANT
#{rule}
{body}
#
"""

BLURB = (
    "The same data as bookshop-trail-1.1.ttl, with two datatypes changed and "
    "nothing else. xsd:gYear and xsd:date are perfectly good RDF and "
    "perfectly good SPARQL, but neither is in the OWL 2 datatype map, so an "
    "ontology that uses them sits outside OWL 2 DL however carefully it is "
    "declared -- and declaring them explicitly makes it worse, because a "
    "declared built-in becomes a user-defined datatype, which is a second "
    "violation. Here years are xsd:integer and dates are xsd:dateTime, and "
    "the file passes robot validate-profile --profile DL. "
    "The main dataset keeps gYear on purpose: the portability trap it "
    "creates is one of the most useful lessons in the course, so the "
    "conformant copy lives here rather than replacing it. Queries q07, q13 "
    "and q62 are the ones that read differently against this file -- against "
    "it, xsd:integer(?founded) simply works."
)


def main() -> int:
    if not SOURCE.exists():
        print(f"  {SOURCE} not found. Run: python scripts/build_dataset.py")
        return 1

    text = SOURCE.read_text(encoding="utf-8")
    years = len(GYEAR.findall(text))
    dates = len(DATE.findall(text))

    text = GYEAR.sub(lambda m: '"' + m.group(1) + '"^^xsd:integer', text)
    text = DATE.sub(lambda m: '"' + m.group(1) + 'T00:00:00Z"^^xsd:dateTime', text)
    # The vocabulary's ranges name them too.  The lookahead matters: a plain
    # replace runs over the xsd:dateTime this function has just written and
    # produces xsd:dateTimeTime, which the validator then reports as an
    # undeclared datatype -- a nicely self-inflicted example of the very
    # thing this file is about.
    text = re.sub(r"xsd:gYear", "xsd:integer", text)
    text = re.sub(r"xsd:date(?!Time)", "xsd:dateTime", text)
    text = text.replace(
        "#  THE BOOKSHOP TRAIL -- COMPLETE DATASET, RDF 1.1",
        "#  THE BOOKSHOP TRAIL -- OWL 2 DL CONFORMANT VARIANT")

    rule = "#" * 75
    body = "\n".join("#  " + line for line in textwrap.wrap(BLURB, 70))
    banner = HEADER.format(rule=rule, body=body)

    # slot the explanation in after the prefix block
    marker = "@prefix prov:"
    cut = text.index("\n", text.index(marker)) + 1
    text = text[:cut] + "\n" + banner + text[cut:]

    TARGET.write_text(text, encoding="utf-8")
    print(f"  wrote data/{TARGET.name}")
    print(f"    {years} xsd:gYear -> xsd:integer")
    print(f"    {dates} xsd:date  -> xsd:dateTime")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
