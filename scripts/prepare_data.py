"""
prepare_data.py
---------------
Builds the Gephi-ready node and edge CSV files from the Bossaert & Meidert (2013)
Harry Potter peer-support dataset.

Input  : data/raw/fict_potter.rda   (copied unchanged from the `manynet` R package)
Outputs: data/raw/raw_nodes.csv           - all 64 coded characters, as published
         data/raw/raw_support_ties.csv    - every directed support tie, per book
         data/nodes.csv                   - Gephi node table (Id, Label, attributes)
         data/edges.csv                   - Gephi edge table (Source, Target, Type, Weight)

Processing decisions (also documented in data/README.md):
  1. Self-loops (a character "supporting" themself) are removed - they have no
     social meaning and Gephi would draw them as loops.
  2. The six books are aggregated into ONE network.
  3. Direction is dropped: A and B are linked if either supported the other.
  4. Weight = number of books (1-6) in which the pair had at least one support
     tie. It measures how PERSISTENT a relationship is, not how many
     individual interactions happened.
  5. Characters left with no ties after step 1 are excluded from the network.

Run:  python scripts/prepare_data.py
Needs: pandas, rdata   (pip install pandas rdata)
"""
from pathlib import Path
import warnings

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"


def extract_raw():
    """Convert the R data object into two plain CSV files (no changes to content)."""
    import rdata  # only needed for this step

    warnings.filterwarnings("ignore")  # rdata warns about unknown R classes (tibble etc.)
    obj = rdata.conversion.convert(rdata.parser.parse_file(RAW / "fict_potter.rda"))["fict_potter"]

    nodes = obj["nodes"].reset_index(drop=True)
    nodes.insert(0, "id", range(1, len(nodes) + 1))  # R row numbers, used by `ties`
    nodes = nodes.rename(columns={"label": "name", "active": "active_in_book1"})
    nodes.to_csv(RAW / "raw_nodes.csv", index=False)

    ties = obj["ties"].astype({"from": int, "to": int, "time": int})
    ties = ties.rename(columns={"from": "supporter_id", "to": "supported_id", "time": "book"})
    ties.to_csv(RAW / "raw_support_ties.csv", index=False)
    return nodes, ties


def build_network(nodes, ties):
    # 1. remove self-loops
    loops = ties["supporter_id"] == ties["supported_id"]
    print(f"Raw directed ties: {len(ties)}  |  self-loops removed: {loops.sum()}")
    ties = ties[~loops].copy()

    # 2+3. undirected pair key (smaller id first)
    ties["a"] = ties[["supporter_id", "supported_id"]].min(axis=1)
    ties["b"] = ties[["supporter_id", "supported_id"]].max(axis=1)

    # 4. weight = number of distinct books in which the pair is linked
    grouped = ties.groupby(["a", "b"])
    edges = pd.DataFrame({
        "Weight": grouped["book"].nunique(),
        "books": grouped["book"].apply(lambda s: ";".join(str(b) for b in sorted(s.unique()))),
        "directed_ties": grouped.size(),  # total directed support ties (both directions, all books)
    }).reset_index().rename(columns={"a": "Source", "b": "Target"})
    edges.insert(2, "Type", "Undirected")

    # 5. drop characters with no remaining ties
    connected = set(edges["Source"]) | set(edges["Target"])
    isolates = nodes[~nodes["id"].isin(connected)]
    if len(isolates):
        print("Excluded (no support ties):", ", ".join(isolates["name"]))
    out_nodes = nodes[nodes["id"].isin(connected)].copy()

    # books in which each character is involved in at least one tie
    involvement = pd.concat([
        ties[["supporter_id", "book"]].rename(columns={"supporter_id": "id"}),
        ties[["supported_id", "book"]].rename(columns={"supported_id": "id"}),
    ]).groupby("id")["book"].nunique()

    out_nodes = pd.DataFrame({
        "Id": out_nodes["id"],
        "Label": out_nodes["name"],
        "house": out_nodes["house"],
        "gender": out_nodes["gender"],
        "schoolyear": out_nodes["schoolyear"],
        "books_with_ties": out_nodes["id"].map(involvement).astype(int),
    })
    return out_nodes, edges


def main():
    nodes, ties = extract_raw()
    out_nodes, edges = build_network(nodes, ties)
    out_nodes.to_csv(DATA / "nodes.csv", index=False)
    edges.to_csv(DATA / "edges.csv", index=False)
    print(f"Wrote data/nodes.csv ({len(out_nodes)} nodes) and data/edges.csv ({len(edges)} edges)")


if __name__ == "__main__":
    main()
