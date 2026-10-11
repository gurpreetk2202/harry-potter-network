"""
compare_gephi_python.py
-----------------------
Checks that the metrics Gephi computed (analysis/gephi_node_metrics.csv) match the
independent NetworkX calculation (analysis/centrality_results.csv).
Degree and betweenness must agree exactly (same graph definition, unweighted
shortest paths, undirected). Louvain communities may differ slightly because the
algorithm is heuristic - the script reports how much they agree.

Run:  python scripts/compare_gephi_python.py
"""
from pathlib import Path
import sys

import pandas as pd
from sklearn.metrics import adjusted_rand_score

A = Path(__file__).resolve().parent.parent / "analysis"
g = pd.read_csv(A / "gephi_node_metrics.csv")
p = pd.read_csv(A / "centrality_results.csv")
m = g.merge(p, on="Id", suffixes=("_gephi", "_python"))
assert len(m) == len(g) == len(p), "node sets differ"

ok = True
for col in ["degree", "weighted_degree", "betweenness"]:
    diff = (m[f"{col}_gephi"] - m[f"{col}_python"]).abs().max()
    good = diff < 0.01
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {col:16s} max difference = {diff:.4f}")

ari = adjusted_rand_score(m["modularity_class"], m["python_louvain_community"])
print(f"INFO  communities: adjusted Rand index Gephi vs Python = {ari:.3f} (1.0 = identical)")
ct = pd.crosstab(m["modularity_class"], m["python_louvain_community"])
print(ct.to_string())
moved = m.groupby("modularity_class")["python_louvain_community"].agg(lambda s: s.mode()[0])
diff = m[m["python_louvain_community"] != m["modularity_class"].map(moved)]
print("Characters grouped differently by the two runs:", ", ".join(diff["Label_gephi"]) or "none")
sys.exit(0 if ok else 1)
