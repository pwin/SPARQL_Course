# Module 09 · Geospatial with nothing but arithmetic

Every engine can do geography if the coordinates are plain numbers. This module builds bounding boxes and a great-circle distance out of FILTER and BIND alone, so it runs anywhere -- on an engine with no GeoSPARQL support of any kind, which is most of them.

It is no longer the only geo module the lab can run: the browser editor moved to the HOLOS engine and module 10 executes there now. Read this one anyway. Knowing what `geof:distance` saves you is worth more than being handed it, and the arithmetic here is what you fall back on against an endpoint that has no geometry functions.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query 17.3 Operator Mapping](https://www.w3.org/TR/sparql12-query/#x17-3-operator-mapping)
- [SPARQL 1.2 Query 17.4.4 Functions on Numerics](https://www.w3.org/TR/sparql12-query/#x17-4-4-functions-on-numerics)
- [SPARQL 1.2 Query 15.1 ORDER BY](https://www.w3.org/TR/sparql12-query/#x15-1-order-by)

| Query | Asks |
|---|---|
| [q52 Shops in a box on the map](q52-shops-in-a-box-on-the-map.rq) | Which shops lie in the south west, between 50 and 52 degrees north and west of 2 degrees? |
| [q53 The nearest shops, with no square root](q53-the-nearest-shops-with-no-square-root.rq) | Which shops are closest to Hay-on-Wye? |
| [q54 Exact distances, by using a flat map](q54-exact-distances-by-using-a-flat-map.rq) | Which shop is nearest to each of the four towns that have none? |
| [q55 Where the flat-Earth shortcut breaks](q55-where-the-flat-earth-shortcut-breaks.rq) | Show a pair of places where degree arithmetic and grid arithmetic disagree. |
| [q56 Everything within fifty kilometres](q56-everything-within-fifty-kilometres.rq) | Which shops are within 50 km of York, and how far is each? |
