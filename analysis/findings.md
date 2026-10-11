# Findings

Every number below comes from `scripts/compute_metrics.py` (output saved in
`metrics_log.txt`) or from Gephi (`gephi_statistics_summary.txt`,
`gephi_node_metrics.csv`, `gephi_communities.csv`). Gephi and Python give **identical**
degree, weighted degree and betweenness for all 37 characters (`gephi_vs_python_check.txt`).

**Graph analysed:** 37 Hogwarts students, 116 undirected peer-support links, Books 1–6
combined. Edge weight = number of books (1–6) in which the pair supported each other.

## Network overview

| Measure | Value | What it means |
|---|---|---|
| Nodes / edges | 37 / 116 | small enough to label every character |
| Density | 0.174 | 17% of all possible pairs are linked |
| Average degree | 6.27 | a typical character is linked to about 6 others |
| Connected components | 2 | the 5 Slytherins form a separate island |
| Diameter (main component) | 4 | any two connected characters are at most 4 steps apart |
| Average path length | 1.895 (Gephi) / 1.907 (Python, main component only)¹ | most pairs are 1–2 steps apart |
| Average clustering | 0.768 | a character's supporters usually also support each other |
| Modularity Q (Gephi) | 0.271, 5 communities | clear but moderate community structure |

¹ Gephi averages over every pair that has a path, including pairs *inside* the Slytherin
component. Python averages over the 32-node main component only. Both are correct.

## Top characters

| Rank | Degree (direct links) | | Betweenness (bridging) | |
|---|---|---|---|---|
| 1 | Harry Potter | 28 | Harry Potter | 297.9 |
| 2 | Ron Weasley | 17 | Ron Weasley | 42.4 |
| 3 | Hermione Granger | 15 | **Demelza Robins** | **30.0** |
| 4 | Fred Weasley | 10 | Hermione Granger | 21.9 |
| 5 | George Weasley | 10 | Dean Thomas / Seamus Finnigan | 12.7 |

Full table: `centrality_results.csv`.

---

## Finding 1: Harry is both the hub and the main bridge

- Harry is directly linked to **28 of the other 36 characters (78%)**, giving the highest degree.
- His betweenness (297.9) is **7.0 times** that of the next character (Ron, 42.4) and makes up
  **66% of all betweenness** in the network.
- **Removing Harry splits the main component.** Without him, the network falls into 5 pieces
  (sizes 26, 5, 2, 2, 1). The pieces cut off are Cho Chang & Cedric Diggory,
  Colin & Dennis Creevey, and Padma Patil, plus the Slytherin group that was already separate.
  These characters reach the rest of the student network **only through Harry**.

**Why it matters.** In network terms Harry is a *cut vertex*. The support network is
centralised around one person rather than spread evenly. This fits a story told mostly
from Harry's point of view: coders could only record support that the text shows, and the
text mostly follows Harry.

## Finding 2: Popularity ≠ bridging (degree and betweenness rank characters differently)

- **Demelza Robins** has only **3** links (rank 26 by degree) but the **3rd-highest
  betweenness (30.0)**. Her neighbours are Harry, Ginny and **Jimmy Peakes**, and Jimmy's *only*
  link is Demelza. All 30 shortest paths from Jimmy to the other 30 characters in the main
  component pass through her.
- **Fred and George Weasley** have degree **10** (joint 4th) but betweenness of only **2.3**.
  Their contacts already know each other (the orange group), so they are rarely "in between".
- **Alicia Spinnet, Angelina Johnson and Oliver Wood** each have degree 8 but betweenness **0**.

**Why it matters.** Degree measures how *active* a character is in the support network.
Betweenness measures how *structurally necessary* they are. A well-connected character
inside a tight group may be easy to replace as a connector, while a character with few
links can be the only bridge to someone else.

## Finding 3: Slytherin is completely cut off from the other houses

- The 5 Slytherin students in the network (Draco Malfoy, Vincent Crabbe, Gregory Goyle,
  Pansy Parkinson, Marcus Flint) form a **separate connected component**.
  There are **0 support links between Slytherin and any other house**.
- The other three houses are connected: 28 of the 116 links cross house lines, and
  11 of those 28 involve Harry.
- 10 of the 15 coded Slytherin students had no support ties at all (see `data/README.md`).

**Why it matters.** Gephi shows this at a glance: the pink group has no edges to the rest
of the graph. (ForceAtlas2's *Stronger Gravity* setting places it nearby, but it is not
connected.) Within this dataset, the house rivalry appears as a real structural gap.

## Finding 4: Communities follow friendship and team groups, not just houses

Gephi's Modularity (Louvain, weighted) found 5 communities (Q = 0.271):

| Community (colour) | Members | Interpretation |
|---|---|---|
| 2 (blue, 17) | Harry, Ron, Hermione, Ginny, Neville, Dean, Seamus, Lavender, Parvati, Luna, Percy, Leanne, Cho, Cedric, Padma, Colin, Dennis | Harry's core circle and his Gryffindor year group |
| 0 (orange, 7) | Fred, George, Katie Bell, Alicia Spinnet, Angelina Johnson, Oliver Wood, Lee Jordan | the Weasley twins and older Gryffindors (all except Lee Jordan played on the Quidditch team) |
| 3 (green, 6) | Hannah Abbott, Ernie Macmillan, Justin Finch-Fletchley, Susan Bones, Terry Boot, Anthony Goldstein | Hufflepuff & Ravenclaw students |
| 4 (pink, 5) | Draco, Crabbe, Goyle, Pansy, Flint | Slytherin (separate component) |
| 1 (yellow, 2) | Demelza Robins, Jimmy Peakes | the pair joined only through Demelza |

- Gryffindor alone is split into **three** communities (blue, orange, yellow), so the
  structure is finer than houses. Using the four houses as communities gives a much lower
  modularity (**Q = 0.135**) than the detected partition (0.271–0.283).
- **Robustness check:** the best of 100 Python Louvain runs found Q = 0.283 with nearly the
  same groups. The orange, green, pink and yellow groups match exactly. The only difference
  is that **Harry** (with Cho, Cedric, Padma, Percy and the Creevey brothers) joins the
  Hufflepuff/Ravenclaw group instead of the Ron/Hermione group.
  Harry's community is therefore *ambiguous*, which is consistent with Finding 1:
  as a bridge he belongs to more than one group.

## Strongest ties

8 pairs are linked in **all 6 books** (thickest edges): Harry–Ron, Harry–Hermione,
Ron–Hermione, Harry–Neville, Ron–Neville, Harry–Fred, Harry–George, Fred–George.

## Caveats

See *Limitations* in `report/project_report.md`. In short: the data is hand-coded from a
narrative told mostly from Harry's viewpoint; direction and per-book change were simplified
away; and community detection is heuristic.
