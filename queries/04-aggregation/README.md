# Module 04 · Counting, grouping and summarising

GROUP BY collapses many rows into one per group. HAVING filters the groups. The trap that catches everyone is putting an aggregate in the wrong place, and this module walks straight into it on purpose.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**In the standards.** The sections this module is defined by:

- [SPARQL 1.2 Query 11. Aggregates](https://www.w3.org/TR/sparql12-query/#x11-aggregates)
- [SPARQL 1.2 Query 11.2 GROUP BY](https://www.w3.org/TR/sparql12-query/#x11-2-group-by)
- [SPARQL 1.2 Query 11.3 HAVING](https://www.w3.org/TR/sparql12-query/#x11-3-having)
- [SPARQL 1.2 Query 11.4 Aggregate Projection Restrictions](https://www.w3.org/TR/sparql12-query/#x11-4-aggregate-projection-restrictions)
- [SPARQL 1.2 Query 18.6.1 Aggregate Algebra](https://www.w3.org/TR/sparql12-query/#x18-6-1-aggregate-algebra)

| Query | Asks |
|---|---|
| [q20 How many shops in each town](q20-how-many-shops-in-each-town.rq) | Count the bookshops town by town. |
| [q21 What each shop's stock is worth](q21-what-each-shop-s-stock-is-worth.rq) | Total the shelf value of every shop's stock. |
| [q22 Average attendance by kind of event](q22-average-attendance-by-kind-of-event.rq) | Which kinds of event draw the biggest crowds? |
| [q23 Only the busy shops](q23-only-the-busy-shops.rq) | Which shops held three or more events, and how many people came in total? |
| [q24 List each author's books on one line](q24-list-each-author-s-books-on-one-line.rq) | For each author, put all their titles into a single cell. |
| [q25 Counting things that aren't there](q25-counting-things-that-aren-t-there.rq) | Count events per shop, including the shops that held none. |
| [q26 One number for the whole dataset](q26-one-number-for-the-whole-dataset.rq) | How many shops, books, authors and events are there altogether? |
| [q132 DISTINCT, REDUCED, and what each costs](q132-distinct-reduced-and-what-each-costs.rq) | List the towns that have a bookshop, without repeating any. |
