# Module 10 · GeoSPARQL proper

The same questions, asked with geof: functions against WKT geometries. Shorter, exact, and dependent on an engine that implements them. HOLOS and a GeoSPARQL-enabled Fuseki do; the browser editor doesn't.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [OGC GeoSPARQL 1.1](https://docs.ogc.org/is/22-047r1/22-047r1.html)
- [SPARQL 1.2 Query §17.6 Extensible Value Testing](https://www.w3.org/TR/sparql12-query/#x17-6-extensible-value-testing)
- [SPARQL 1.2 Service Description](https://www.w3.org/TR/sparql12-service-description/)

| Query | Asks |
|---|---|
| [q57 The same question, one function](q57-the-same-question-one-function.rq) | How far is each shop from Hay-on-Wye, in kilometres? |
| [q58 Which area is this point inside](q58-which-area-is-this-point-inside.rq) | Verify that every settlement really does fall inside the polygon of the council area it claims to be in. |
| [q59 How long is the trail](q59-how-long-is-the-trail.rq) | Measure each trail segment from its geometry, and compare with the distance recorded in the data. |
| [q60 Two coordinate systems, one query](q60-two-coordinate-systems-one-query.rq) | Confirm that the National Grid geometry and the WGS84 geometry describe the same place. |
