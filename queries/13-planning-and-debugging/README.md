# Module 13 · Planning and debugging

Why a query is slow, why it returns nothing, and why it returns far too much. All three engines will show you the plan they built; this module reads those plans, and collects the diagnostic queries worth reaching for before you start rewriting anything.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

**Read first: [PLANS.md](PLANS.md)** — Getting the plan out of each engine, and the debugging playbook.

| Query | Asks |
|---|---|
| [q90 How selective is each pattern](q90-how-selective-is-each-pattern.rq) | Before optimising anything: how many rows does each pattern in my query match on its own? |
| [q91 The cross product you did not mean to write](q91-the-cross-product-you-did-not-mean-to-write.rq) | What happens when two patterns in the same group share no variable? |
| [q92 The join that inflates an aggregate](q92-the-join-that-inflates-an-aggregate.rq) | Why does counting shops per council area give the wrong number when events are in the same query? |
| [q93 Why is my result empty](q93-why-is-my-result-empty.rq) | A query returns nothing. Which line is responsible? |
| [q94 Pin one case while you work on it](q94-pin-one-case-while-you-work-on-it.rq) | How do I run a complicated query against a single known resource? |
| [q95 The language tag that stops a match](q95-the-language-tag-that-stops-a-match.rq) | Why does comparing a label to a string find nothing? |
| [q96 Find the mistyped IRI](q96-find-the-mistyped-iri.rq) | A pattern matches nothing and the vocabulary looks right. How do I check? |
| [q97 Three spellings, one answer, three plans](q97-three-spellings-one-answer-three-plans.rq) | Do these three ways of asking 'which shops are in Scotland' give the same result? |
