# Graph-Based Analysis and Visualization of Character Interactions in the Harry Potter Universe

*B.Tech Computer Science, Graph Visualization & Network Analysis Project*

## 1. Objective and dataset

**Objective.** Represent the relationships between Harry Potter characters as a graph,
visualize it in Gephi, compute centrality and community metrics, and use them to find
structural patterns.

**Dataset.** We use the peer-support network coded by Bossaert & Meidert (2013,
*Open Journal of Applied Sciences* 3(2):174–185, doi:10.4236/ojapps.2013.32024). The authors
read Books 1–6 and recorded each time one adolescent character gave another *voluntary
emotional, instrumental or informational support, or praise*. The data covers 64 Hogwarts
students and 544 directed ties, labelled by book. We took it from the `fict_potter` dataset
in the open-source R package *manynet* (github.com/stocnet/manynet). We chose it because it
is published, peer-reviewed and clearly defined. Every edge is a hand-coded observation from
the text, not an automatic name co-occurrence.

## 2. Graph representation

- **Nodes** are characters, with attributes for house, gender and school year.
- **Edges** are undirected. A–B are linked if either supported the other in any of Books 1–6.
- **Weight** is the number of books (1–6) in which the pair had a support tie. It measures how
  *persistent* a relationship is, not how many times they interacted.
- **Preprocessing** (scripts/prepare_data.py): we removed 110 self-loops, merged the 6 books,
  dropped edge direction, and excluded 27 characters with no ties. The final graph has
  **37 nodes and 116 edges** (density 0.174, 2 connected components).
  Automated checks (scripts/validate_data.py) confirmed there are no duplicate IDs,
  invalid or duplicate edges, self-loops or missing values.

## 3. Layout choice: ForceAtlas2

ForceAtlas2 is a force-directed layout. Every node pushes the others away, every edge pulls
its two ends together, and heavier edges pull harder (edge weight influence = 1). When the
layout settles, characters who share many links end up close together and weakly connected
groups drift apart. **Groups in the data therefore appear as visible clusters**, and bridge
characters sit between them. That is what this project needs. Circular or random layouts
would hide this.

Settings: scaling 60 (more space between nodes), *Stronger Gravity* (stops the disconnected
Slytherin component from floating far away), then *Prevent Overlap* and *Label Adjust* so
that all 37 labels are readable.

## 4. Network metrics and results

Gephi and an independent NetworkX calculation produced **identical** degree and betweenness
values for every character.

**Degree centrality** counts the characters a node is directly linked to.
Harry is highest with 28 (78% of all other characters), followed by Ron (17) and Hermione (15).

**Betweenness centrality** measures how often a node lies on the shortest path between two
other nodes, which shows how much it acts as a bridge. Harry is highest again (297.9), at
**7×** the second-placed Ron (42.4) and **66%** of all betweenness in the network.
Rank 3 is **Demelza Robins** (30.0), even though she has only 3 links: she is the only
connection of Jimmy Peakes. In contrast, Fred and George (degree 10) score only 2.3, because
their contacts already know each other. **High degree does not imply high betweenness.**

**Modularity (Louvain)** detects groups that are more densely linked inside than between.
Gephi found **5 communities, Q = 0.271**: Harry's core circle (17), the Weasley twins and
older Gryffindors (7), Hufflepuff/Ravenclaw students (6), Slytherin (5), and Demelza & Jimmy (2).
Using the four houses as communities gives only Q = 0.135, so the network is organised by
friendship and team groups more than by house.

## 5. Visual encoding

| Visual property | Data | Reason |
|---|---|---|
| Node size | Degree (6–32 px, linear ranking) | the most connected characters stand out |
| Node colour | Gephi Modularity Class | communities are visible at a glance |
| Edge thickness | Weight = number of books with support | long-lasting ties look stronger (shown because the weight has a clear, documented meaning) |
| Labels | Character name | every node is identifiable |

The colours are the colour-blind-safe Okabe–Ito palette. The final PNG adds a title, a legend
and the data source around the unmodified Gephi export.

## 6. Verified insights

1. **Harry is the hub and the bridge.** Removing him splits the main component into 4 pieces.
   Cho & Cedric, Colin & Dennis Creevey and Padma Patil connect to the student network only through him.
2. **Slytherin is isolated.** The 5 Slytherins form their own component, with **0 support links**
   to any other house. The other houses share 28 cross-house links.
3. **Bridging is not the same as popularity.** Demelza Robins (degree 3) has higher betweenness
   than Hermione (degree 15).
4. **Communities are finer than houses.** Gryffindor splits into three communities. Harry's own
   community assignment changes between Louvain runs (Gephi vs Python), which fits his role
   as a bridge between groups.

## 7. Limitations and assumptions

- **Fictional, narrator-biased data.** The ties reflect what the books show, and the books
  mostly follow Harry. His centrality is partly a result of the point of view, not a fact
  about a real social group.
- **Coding choices.** Ties were hand-coded by two researchers. Only "support" is captured;
  hostility and neutral interaction are not.
- **Simplifications.** Direction (who supports whom) and change across books were removed to
  produce one readable undirected graph. Weight counts books, not interaction frequency.
- **Excluded characters.** 27 students with no ties and all adults are absent, so metrics
  describe this subset only.
- **Heuristic communities.** Louvain can give slightly different partitions between runs.
  We report Gephi's deterministic run and checked it against 100 Python runs.
- **Betweenness ignores weights**, as in Gephi: shortest paths count steps, not tie strength.

*Reproduce:* `python scripts/prepare_data.py && python scripts/validate_data.py &&
python scripts/compute_metrics.py && bash gephi_toolkit/run.sh && python scripts/add_legend.py`.
