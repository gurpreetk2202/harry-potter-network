# Presentation Script (about 4 minutes)

*Show `visualization/harry_potter_network.png` on screen for most of the talk.
Approximate timings are in brackets.*

---

### 1. Introduction and objective (0:00–0:30)

"Good morning. My project is *Graph-Based Analysis and Visualization of Character
Interactions in the Harry Potter Universe*.

The goal was to turn relationships between characters into a graph, visualize it in Gephi,
and use network metrics to find patterns that are not obvious from reading the books.
That means not just drawing a pretty picture."

### 2. Dataset (0:30–1:05)

"I did not invent the links. I used a published academic dataset by Bossaert and Meidert,
2013, in the *Open Journal of Applied Sciences*. The researchers read Books 1 to 6 and
recorded every time one student supported another: emotional help, practical help,
information or praise.

I removed self-loops, combined the six books, and treated a link as undirected.
I also removed 27 students who had no support ties.
That gives **37 characters and 116 links**. The edge weight is the number of books in which
two characters supported each other, from 1 to 6. My validation script checks for duplicate
IDs, broken edges, self-loops and missing values, and all checks pass."

### 3. Method: Gephi and the layout (1:05–1:45)

"I imported the node and edge CSV files into Gephi as an undirected graph.

For the layout I used **ForceAtlas2**. It is force-directed: nodes repel each other and
edges act like springs, so characters who share many links are pulled together.
This makes groups appear as visible clusters, and bridge characters end up between them.
I used stronger gravity so the separate Slytherin group stays on screen, then
Prevent Overlap and Label Adjust so every name is readable."

### 4. Visual encoding (1:45–2:05)

*(Point at the legend.)*
"**Node size** shows degree, meaning how many characters someone is linked to.
**Node colour** shows the community found by Gephi's modularity algorithm.
**Edge thickness** shows how many books a relationship lasted."

### 5. Metrics and findings (2:05–3:35)

"I calculated two centrality measures in Gephi and checked them with Python;
the numbers match exactly.

**Degree centrality:** Harry is linked to 28 of the 36 other characters. Ron has 17 and Hermione 15.

**Betweenness centrality** measures how often a character lies on the shortest path between
two others, in other words how much they act as a bridge. Harry's score is seven times Ron's.
If we remove Harry, Cho and Cedric, the Creevey brothers and Padma Patil are completely cut off.
So Harry is not only popular; the network depends on him.

The surprising result is **Demelza Robins**. She has only three links, but she has the
third-highest betweenness, because she is Jimmy Peakes' only connection.
Meanwhile Fred and George have ten links each but almost no betweenness, because everyone
they know already knows each other. So **popular does not mean bridge**.

**Communities:** Gephi found five groups. *(Point at each colour.)*
Harry's core circle in blue, the Weasley twins and older Gryffindors in orange,
Hufflepuff and Ravenclaw students in green, the Demelza–Jimmy pair in yellow, and Slytherin in pink.
The pink group has **no links at all** to any other house. It is a separate component.
Grouping by house gives a much lower modularity than the communities Gephi found,
so friendship and team groups matter more than houses."

### 6. Limitations and conclusion (3:35–4:10)

"There are limitations. This is fictional data, and the story is told mostly from Harry's
point of view, so part of his centrality comes from the narration. I also simplified away
direction and change over time.

In conclusion, the graph shows a support network centralised around Harry, a Slytherin
group cut off from the rest of the school, and the result that a minor character can be a
more important bridge than a popular one. Thank you. I'm happy to take questions."

---

## Likely questions and short answers

- **Why undirected?** Modularity and the degree explanation are simpler. The direction is
  kept in `data/raw/raw_support_ties.csv` for future work.
- **Why is the weight not interaction frequency?** The original coding records whether
  support happened in each book, not how many times. Counting books is the honest measure available.
- **Is betweenness weighted?** No. Gephi counts steps, not tie strength, and Python was set up the same way.
- **Why might my Gephi communities differ?** Louvain is randomised. The main groups are stable;
  Harry's group changes, which itself shows his bridging role.
- **Why is the Slytherin group close to the others?** Only because of the Stronger Gravity
  layout setting. There are no edges between them and the rest.
