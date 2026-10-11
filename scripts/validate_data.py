"""
validate_data.py
----------------
Data-quality checks on data/nodes.csv and data/edges.csv before they go into Gephi.
Exits with code 1 if any check fails.

Run:  python scripts/validate_data.py
"""
from pathlib import Path
import sys

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

nodes = pd.read_csv(DATA / "nodes.csv")
edges = pd.read_csv(DATA / "edges.csv")
failures = []


def check(ok, message):
    print(("PASS  " if ok else "FAIL  ") + message)
    if not ok:
        failures.append(message)


# --- nodes ---
check(nodes["Id"].is_unique, "node Ids are unique")
check(nodes["Label"].is_unique, "node labels (character names) are unique")
check(not nodes[["Id", "Label"]].isna().any().any(), "no missing Id or Label")
missing_attr = nodes.isna().sum()
check(missing_attr.sum() == 0, f"no missing node attributes ({dict(missing_attr[missing_attr > 0]) or 'none'})")

# --- edges ---
ids = set(nodes["Id"])
bad = edges[~edges["Source"].isin(ids) | ~edges["Target"].isin(ids)]
check(bad.empty, f"every edge references an existing node ({len(bad)} invalid)")
check((edges["Source"] != edges["Target"]).all(), "no self-loops")
pair = edges[["Source", "Target"]].min(axis=1).astype(str) + "-" + edges[["Source", "Target"]].max(axis=1).astype(str)
check(pair.is_unique, "no duplicate edges (A-B and B-A count as the same undirected edge)")
check((edges["Type"] == "Undirected").all(), "all edges are marked Undirected")
check(edges["Weight"].between(1, 6).all(), "weights are whole numbers of books between 1 and 6")
books_count = edges["books"].astype(str).str.split(";").str.len()
check((books_count == edges["Weight"]).all(), "Weight equals the number of books listed in 'books'")
check(not edges.isna().any().any(), "no missing edge values")

# --- every node used ---
used = set(edges["Source"]) | set(edges["Target"])
check(used == ids, "every node has at least one edge (no isolates)")

print(f"\n{len(nodes)} nodes, {len(edges)} edges, total weight {edges['Weight'].sum()}")
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("All checks passed.")
