"""
compute_metrics.py
------------------
Independent (Python/NetworkX) calculation of the same metrics Gephi computes, used to
cross-check the Gephi results. Uses the SAME graph definition as the Gephi import:
undirected, 37 nodes, 116 edges.

  * degree               - number of distinct characters linked to (Gephi: "Degree")
  * weighted_degree      - sum of edge weights (Gephi: "Weighted Degree")
  * betweenness          - raw betweenness, UNWEIGHTED shortest paths, as Gephi's
                           "Network Diameter" statistic computes it
  * betweenness_norm     - betweenness scaled to 0-1 (Gephi: tick "Normalize centralities")
  * python_louvain_community - Louvain modularity communities (weighted, resolution 1.0)

Output: analysis/centrality_results.csv and a printed summary.

Run:  python scripts/compute_metrics.py
Needs: pandas, networkx
"""
from pathlib import Path

import networkx as nx
import pandas as pd
from networkx.algorithms import community as nxcom

ROOT = Path(__file__).resolve().parent.parent
nodes = pd.read_csv(ROOT / "data" / "nodes.csv")
edges = pd.read_csv(ROOT / "data" / "edges.csv")

G = nx.Graph()
for row in nodes.itertuples():
    G.add_node(row.Id, label=row.Label, house=row.house)
for row in edges.itertuples():
    G.add_edge(row.Source, row.Target, weight=row.Weight)

n, m = G.number_of_nodes(), G.number_of_edges()
print(f"Graph: {n} nodes, {m} edges, undirected")
print(f"Density: {nx.density(G):.4f}")
print(f"Connected components: {nx.number_connected_components(G)}")
print(f"Average degree: {2 * m / n:.3f}")
comps = sorted(nx.connected_components(G), key=len, reverse=True)
for c in comps[1:]:
    print("  separate component:", ", ".join(G.nodes[v]["label"] for v in c))
main = G.subgraph(comps[0])
print(f"Largest component: {main.number_of_nodes()} nodes | diameter {nx.diameter(main)}"
      f" | average path length {nx.average_shortest_path_length(main):.3f}")
print(f"Average clustering coefficient: {nx.average_clustering(G):.3f}")

degree = dict(G.degree())
wdegree = dict(G.degree(weight="weight"))
btw = nx.betweenness_centrality(G, normalized=False)      # unweighted, like Gephi
btw_norm = nx.betweenness_centrality(G, normalized=True)

# Louvain is randomised: run many seeds and keep the best-modularity partition
best, best_q = None, -1
for seed in range(100):
    parts = nxcom.louvain_communities(G, weight="weight", resolution=1.0, seed=seed)
    q = nxcom.modularity(G, parts, weight="weight")
    if q > best_q:
        best, best_q = parts, q
best = sorted(best, key=len, reverse=True)
community = {node: i for i, part in enumerate(best) for node in part}
print(f"Louvain (weighted): {len(best)} communities, modularity Q = {best_q:.3f}")
q_house = nxcom.modularity(G, [set(nodes.Id[nodes.house == h]) for h in nodes.house.unique()], weight="weight")
print(f"Modularity if communities = Hogwarts houses: Q = {q_house:.3f}")

res = pd.DataFrame({
    "Id": nodes["Id"],
    "Label": nodes["Label"],
    "house": nodes["house"],
    "degree": nodes["Id"].map(degree),
    "weighted_degree": nodes["Id"].map(wdegree),
    "betweenness": nodes["Id"].map(btw).round(3),
    "betweenness_norm": nodes["Id"].map(btw_norm).round(4),
    "python_louvain_community": nodes["Id"].map(community),
})
res["degree_rank"] = res["degree"].rank(ascending=False, method="min").astype(int)
res["betweenness_rank"] = res["betweenness"].rank(ascending=False, method="min").astype(int)
res = res.sort_values(["degree", "betweenness"], ascending=False)
res.to_csv(ROOT / "analysis" / "centrality_results.csv", index=False)

cols = ["Label", "house", "degree", "weighted_degree", "betweenness", "betweenness_norm"]
print("\nTop 10 by degree:\n", res[cols].head(10).to_string(index=False))
print("\nTop 10 by betweenness:\n", res.sort_values("betweenness", ascending=False)[cols].head(10).to_string(index=False))
print("\nCommunities:")
for i, part in enumerate(best):
    members = res[res.python_louvain_community == i]
    print(f"  {i}: " + ", ".join(f"{r.Label} ({r.house[0]})" for r in members.itertuples()))
print("\nWrote analysis/centrality_results.csv")

# ---------------------------------------------------------------------------
# Insight checks - every claim in analysis/findings.md is printed here
# ---------------------------------------------------------------------------
print("\n=== Insight checks ===")
harry = nodes.loc[nodes.Label == "Harry James Potter", "Id"].item()
print(f"Harry is linked to {degree[harry]} of the {n - 1} other characters "
      f"({degree[harry] / (n - 1):.0%}); share of all betweenness: {btw[harry] / sum(btw.values()):.0%}")
second = res.sort_values("betweenness", ascending=False).iloc[1]
print(f"Harry's betweenness is {btw[harry] / second.betweenness:.1f}x the next highest ({second.Label})")

house = nx.get_node_attributes(G, "house")
cross = [(u, v) for u, v in G.edges() if house[u] != house[v]]
via_harry = [e for e in cross if harry in e]
print(f"Cross-house edges: {len(cross)} of {m}; involving Harry: {len(via_harry)}")
for h in sorted(set(house.values())):
    ext = sum(1 for u, v in cross if h in (house[u], house[v]))
    print(f"  {h}: {ext} cross-house edges")

H = G.copy()
H.remove_node(harry)
sizes = sorted((len(c) for c in nx.connected_components(H)), reverse=True)
print(f"Without Harry: {len(sizes)} components, sizes {sizes}")
for c in nx.connected_components(H):
    if len(c) < max(sizes):
        print("  cut off:", ", ".join(G.nodes[v]["label"] for v in c))

demelza = nodes.loc[nodes.Label == "Demelza Robins", "Id"].item()
print("Demelza Robins' neighbours:", ", ".join(G.nodes[v]["label"] for v in G[demelza]))
jimmy = nodes.loc[nodes.Label == "Jimmy Peakes", "Id"].item()
print("Jimmy Peakes' neighbours:", ", ".join(G.nodes[v]["label"] for v in G[jimmy]))

top_w = edges.sort_values("Weight", ascending=False)
lab = dict(zip(nodes.Id, nodes.Label))
print("Pairs linked in all 6 books:", "; ".join(
    f"{lab[r.Source]} - {lab[r.Target]}" for r in top_w[top_w.Weight == 6].itertuples()))
