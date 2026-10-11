# Gephi Desktop: Step-by-Step Instructions

These steps recreate the project's visualization **by hand in Gephi Desktop**. They use
the same settings as the automated Gephi Toolkit run (`gephi_toolkit/GephiPipeline.java`),
so your numbers should match `analysis/gephi_statistics_summary.txt` and
`analysis/gephi_node_metrics.csv`.

Allow about 30–45 minutes the first time.

---

## 0. Install Gephi

1. Download **Gephi 0.10.1** (or newer) from <https://gephi.org/users/download/>.
2. Install and open it. When the *Welcome* window appears, close it.

---

## 1. Import the nodes (characters)

1. **File → Import spreadsheet…**
2. Select `data/nodes.csv` → **Open**.
3. In the wizard:
   - *Separator*: **Comma**
   - *Import as*: **Nodes table**
   - *Charset*: **UTF-8**
   - Click **Next**.
4. Column types (leave the rest as they are):
   - `schoolyear` → **Integer**
   - `books_with_ties` → **Integer**
   - Click **Finish**.
5. In the **Import report** window:
   - *Graph Type*: **Undirected**
   - Select **New workspace**
   - Click **OK**.

## 2. Import the edges (support links)

1. **File → Import spreadsheet…** → select `data/edges.csv`.
2. *Separator*: **Comma**, *Import as*: **Edges table** → **Next**.
3. Column types:
   - `Weight` → **Double**
   - `books` → **String** (it holds text like `2;3;5`)
   - `directed_ties` → **Integer**
   - Make sure **Create missing nodes** is **unticked**, so a wrong ID cannot create a fake character.
   - Click **Finish**.
4. In the **Import report** window:
   - *Graph Type*: **Undirected**
   - Select **Append to existing workspace** (important! otherwise the edges go into a new, empty workspace).
   - Click **OK**.

✅ **Check:** the *Context* panel (top right) should show **Nodes: 37, Edges: 116, Undirected Graph**.
If you see 116 nodes or a directed graph, delete the workspace and repeat steps 1–2.

---

## 3. Calculate the metrics (Statistics panel)

Open **Window → Statistics** if the panel is not visible. Click **Run** next to each item:

| Statistic | Settings | Expected result |
|---|---|---|
| **Average Degree** | none | 6.270 |
| **Avg. Weighted Degree** | none | 13.892 |
| **Network Diameter** | **Undirected**, *Normalize centralities* **unticked** | Diameter 4, Avg. path length 1.895 |
| **Modularity** | *Randomize* **unticked**, *Use weights* **ticked**, *Resolution* **1.0** | Modularity ≈ 0.271, 5 communities |

Network Diameter computes **Betweenness Centrality** (plus closeness and eccentricity).
Modularity adds a **Modularity Class** column, which is the community number.

> ℹ️ If you leave *Randomize* ticked, Modularity can give a slightly different split
> (Q between about 0.27 and 0.28) because the Louvain algorithm is randomised. That
> is normal; the main groups stay the same. See `analysis/findings.md`, Finding 4.

Check the values: **Data Laboratory** tab → *Data Table* → *Nodes*. Click the **Degree**
column header to sort. Harry should have Degree 28 and Betweenness Centrality ≈ 297.9.

---

## 4. Style the nodes (Appearance panel, Overview tab)

**Node size = Degree**
1. Appearance panel → **Nodes** → **Size** icon (the overlapping circles).
2. **Ranking** → choose **Degree**.
3. Min size **6**, Max size **32** → **Apply**.

**Node colour = community**
1. **Nodes** → **Color** icon (the palette).
2. **Partition** → choose **Modularity Class** → **Apply**.
3. (Optional, to match the project image) Click each colour square and type the hex code,
   biggest community first: `#0072B2` (blue), `#D55E00` (orange), `#009E73` (green),
   `#CC79A7` (pink), `#E69F00` (yellow). These are the colour-blind-friendly Okabe–Ito colours.

---

## 5. Run the layout (Layout panel)

1. **Window → Layout** if hidden. Choose **ForceAtlas 2**.
2. Settings:
   - *Scaling*: **60**
   - *Stronger Gravity*: **ticked**
   - *Gravity*: **1.0**
   - *Edge Weight Influence*: **1.0**
   - *LinLog mode*: unticked, *Prevent Overlap*: unticked
3. Click **Run**. Wait about 10–20 seconds until the nodes stop moving, then click **Stop**.
4. Tick **Prevent Overlap** → **Run** for a few seconds → **Stop**.
5. Choose **Label Adjust** from the layout list → **Run** for a few seconds → **Stop**.
6. If the graph is off-screen, click the magnifier icon ("Center on graph") at the bottom left.

Your picture will not be pixel-identical to the project image (the start positions are
random), but the groups and their arrangement should look the same.

---

## 6. Prepare the final image (Preview tab)

Open the **Preview** tab and set:

| Section | Setting | Value |
|---|---|---|
| Global | Background color | White |
| Nodes | Border width | 1.2, border colour white |
| Node Labels | Show Labels | ✔ |
| Node Labels | Font | Arial/SansSerif **Bold, 6** |
| Node Labels | Proportional size | ✘ |
| Node Labels | Outline size / colour / opacity | 2.5 / white / 85 |
| Edges | Rescale weight | ✔ (min 0.4, max 4.0) **← thickness = Weight** |
| Edges | Color | Custom, grey `#8A8A8A` |
| Edges | Opacity | 55 |
| Edges | Curved | ✘ |

Click **Refresh**.

---

## 7. Export and save

1. Preview tab → **Export: SVG/PDF/PNG** → choose **PNG** → **Options…** →
   width **4000**, height **3200**, margin 4 → save as
   `visualization/harry_potter_network_gephi_raw.png`.
2. Export again as **PDF** → `visualization/harry_potter_network.pdf`.
3. **File → Save as…** → `visualization/gephi_project.gephi`.
4. (Optional) Data Laboratory → **Export table** → save the node table as CSV.

## 8. Add the title and legend

Gephi cannot draw a legend, so run:

```bash
python scripts/add_legend.py
```

This frames the Gephi PNG with a title, legend and data source, and writes
`visualization/harry_potter_network.png`. The network drawing itself is not changed.
If you rerun Modularity with *Randomize* on, rerun `gephi_toolkit/run.sh` first or edit
`analysis/gephi_communities.csv` so the legend colours match your run.
