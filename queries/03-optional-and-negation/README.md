# Module 03 · Optional data, alternatives and negation

Real data has holes. OPTIONAL keeps a row when the extra fact is missing, UNION merges two shapes, and MINUS and NOT EXISTS remove rows -- in ways that aren't quite interchangeable.

Each `.rq` file carries its own explanation: what it asks, how it works, a diagram of the mechanism, and what to take away. Read the header before running the query.

| Query | Asks |
|---|---|
| [q14 Shops, with a website if there's one](q14-shops-with-a-website-if-there-s-one.rq) | List every shop, showing its website where one is recorded. |
| [q15 Which books have no ISBN](q15-which-books-have-no-isbn.rq) | Find the books with no ISBN recorded, and say why. |
| [q16 Towns with no bookshop](q16-towns-with-no-bookshop.rq) | Which settlements on the map have no bookshop at all? |
| [q17 MINUS and NOT EXISTS aren't the same](q17-minus-and-not-exists-aren-t-the-same.rq) | Show the case where swapping MINUS for NOT EXISTS changes the answer. |
| [q18 Everyone who worked on a book](q18-everyone-who-worked-on-a-book.rq) | List every person credited on a work, whether as author or translator. |
| [q19 Why a FILTER inside OPTIONAL behaves oddly](q19-why-a-filter-inside-optional-behaves-oddly.rq) | Compare filtering inside an OPTIONAL with filtering after it. |
