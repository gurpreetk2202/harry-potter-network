# Dataset

## Source and attribution

**Bossaert, G. & Meidert, N. (2013).** "'We are only as strong as we are united, we are only as
weak as we are divided'. A dynamic analysis of the peer support networks in the Harry Potter
books." *Open Journal of Applied Sciences*, 3(2), 174–185.
DOI: [10.4236/ojapps.2013.32024](https://doi.org/10.4236/ojapps.2013.32024)

The authors released the data for general use through Tom Snijders' RSiena data page
(<https://www.stats.ox.ac.uk/~snijders/siena/HarryPotterData.html>). That site was not
reachable from the build environment, so the copy used here comes from the
**`fict_potter`** dataset in the R package **manynet**
(<https://github.com/stocnet/manynet>, file `data/fict_potter.rda`, documented in
`man/fict_potter.Rd`). It is the same 64-character, 6-book support data.

`raw/fict_potter.rda` is an unmodified copy of that file.

## What the data means

The researchers read the books and **coded peer-support ties by hand** (using NVivo).
According to the dataset documentation, a tie from A to B means that in that book A gave B
*"voluntary emotional, instrumental, or informational support, or praise"*, between living,
adolescent characters. The 64 characters are Hogwarts students, and each has a house,
gender and school year.

So an edge is **a coded act of support**, not a co-appearance and not a friendship rating.
This is fictional data: it describes the story, not real people.

## Files

| File | Description |
|---|---|
| `raw/fict_potter.rda` | Original R data file (manynet) |
| `raw/raw_nodes.csv` | All 64 coded characters, as published (`id`, `name`, `schoolyear`, `gender`, `house`, `active_in_book1`) |
| `raw/raw_support_ties.csv` | All 544 directed ties: `supporter_id`, `supported_id`, `book` (1–6) |
| `nodes.csv` | **Gephi node table**, 37 characters |
| `edges.csv` | **Gephi edge table**, 116 undirected edges |

### `nodes.csv`

| Column | Meaning |
|---|---|
| `Id` | Character ID (same as the original dataset's row number) |
| `Label` | Character name, as spelled in the dataset |
| `house` | Hogwarts house |
| `gender` | Gender |
| `schoolyear` | Year the character started at Hogwarts, as coded by the authors |
| `books_with_ties` | Number of books (1–6) in which the character has at least one support tie |

### `edges.csv`

| Column | Meaning |
|---|---|
| `Source`, `Target` | Character IDs (smaller ID first, since the graph is undirected) |
| `Type` | Always `Undirected` |
| `Weight` | **Number of books (1–6) in which the pair had at least one support tie, in either direction** |
| `books` | Which books, e.g. `2;3;5` |
| `directed_ties` | Total directed ties behind the edge (A→B and B→A, summed over books; max 12) |

**Edge weight meaning.** `Weight` measures how **persistent** a relationship is across the
series. It is **not** a count of individual interactions; the original coding records only
whether support happened in a book, not how often.

## Preprocessing (`scripts/prepare_data.py`)

1. **Self-loops removed:** 110 of the 544 raw ties have the same supporter and receiver.
   Self-support has no meaning in a social network, so they were dropped. This leaves 434 directed ties.
2. **Six books aggregated** into one network, giving a readable static picture of the whole series.
3. **Direction dropped:** A–B are linked if *either* supported the other. This is needed for
   modularity, keeps degree easy to explain, and keeps Gephi and Python on the same graph definition.
   The directed data is kept in `raw/raw_support_ties.csv`.
4. **Weight** = number of distinct books with a tie (see above).
5. **Isolates excluded:** 27 characters have no support ties to anyone once self-loops are removed.
   They are left out of `nodes.csv` because they would only add disconnected dots.
   They are: Adrian Pucey, Blaise Zabini, C. Warrington, Cormac McLaggen, Eddie Carmichael,
   Eleanor Branstone, Euan Abercrombie, Graham Pritchard, Kevin Whitby, Lucian Bole,
   Malcolm Baddock, Mandy Brocklehurst, Marcus Belby, Michael Corner, Miles Bletchley,
   Millicent Bulstrode, Natalie McDonald, Orla Quirke, Owen Cauldwell, Penelope Clearwater,
   Peregrine Derrick, Roger Davies, Romilda Vane, Rose Zeller, Stewart Ackerley,
   Theodore Nott, Zacharias Smith.

No values were missing, and no interactions were added or inferred.

## Validation (`scripts/validate_data.py`)

All checks pass: unique IDs and names, no missing values, every edge points to an existing
node, no self-loops, no duplicate edges (A–B and B–A count as the same edge), all edges
undirected, weights between 1 and 6 that match the `books` column, and no isolated nodes.
