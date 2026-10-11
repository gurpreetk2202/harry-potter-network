"""
add_legend.py
-------------
Gephi's Preview/export cannot draw a title or legend. This script places the UNCHANGED
Gephi export (visualization/harry_potter_network_gephi_raw.png) on a larger canvas and
adds a title, legend and source note around it. The network drawing itself is not
modified - it remains the Gephi output.

Colours are read from analysis/gephi_communities.csv (written by the Gephi run), so the
legend always matches the colours Gephi actually used.

Output: visualization/harry_potter_network.png
Run:    python scripts/add_legend.py
Needs:  pandas, pillow
"""
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
VIS = ROOT / "visualization"

graph = Image.open(VIS / "harry_potter_network_gephi_raw.png").convert("RGB")
communities = pd.read_csv(ROOT / "analysis" / "gephi_communities.csv")
nodes = pd.read_csv(ROOT / "analysis" / "gephi_node_metrics.csv")


def font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for d in ["/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", "/Library/Fonts/", ""]:
        for n in names + (["arialbd.ttf"] if bold else ["arial.ttf"]):
            try:
                return ImageFont.truetype(d + n, size)
            except OSError:
                continue
    return ImageFont.load_default()


def describe(cls):
    """Legend text for a community: built from its actual members, never hard-coded."""
    members = nodes[nodes.modularity_class == cls].sort_values("degree", ascending=False)
    names = [n.replace("Harry James Potter", "Harry Potter") for n in members.Label]
    shown = ", ".join(names[:4]) + (f" + {len(names) - 4} more" if len(names) > 4 else "")
    return f"{shown}  ({len(names)} characters)"


W_LEGEND = 1750
PAD = 80
H_TITLE = 260
canvas = Image.new("RGB", (graph.width + W_LEGEND, graph.height + H_TITLE + 120), "white")
canvas.paste(graph, (0, H_TITLE))
d = ImageDraw.Draw(canvas)
ink, grey = (34, 34, 34), (110, 110, 110)

d.text((PAD, 60), "Peer-Support Network of Hogwarts Students, Harry Potter Books 1-6", font=font(84, True), fill=ink)
d.text((PAD, 170), f"{len(nodes)} characters, 116 undirected links  |  Layout: ForceAtlas2 in Gephi 0.10  |  "
       "Communities: Gephi Modularity (Louvain)", font=font(46), fill=grey)

x, y = graph.width + 20, H_TITLE + 40
d.text((x, y), "Legend", font=font(64, True), fill=ink)
y += 110
d.text((x, y), "Node colour = detected community", font=font(44, True), fill=ink)
y += 75
for row in communities.itertuples():
    d.ellipse((x, y + 4, x + 44, y + 48), fill=row.color_hex)
    d.text((x + 64, y), f"Community {row.modularity_class}", font=font(40, True), fill=ink)
    d.text((x + 64, y + 50), describe(row.modularity_class), font=font(30), fill=grey)
    y += 120

y += 40
d.text((x, y), "Node size = degree", font=font(44, True), fill=ink)
y += 65
d.text((x, y), "(characters linked by support; sizes illustrative)", font=font(32), fill=grey)
y += 60
lo, hi = int(nodes.degree.min()), int(nodes.degree.max())
for r, label in [(10, f"{lo}"), (26, "~14"), (48, f"{hi}")]:
    d.ellipse((x + 50 - r, y + 50 - r, x + 50 + r, y + 50 + r), fill=(150, 150, 150))
    d.text((x + 120, y + 30), label, font=font(36), fill=ink)
    y += 110

y += 30
d.text((x, y), "Edge thickness = tie persistence", font=font(44, True), fill=ink)
y += 65
d.text((x, y), "(number of books, 1-6, in which the pair", font=font(32), fill=grey)
d.text((x, y + 42), "had at least one support tie)", font=font(32), fill=grey)
y += 110
for w, label in [(2, "1 book"), (8, "3 books"), (16, "6 books")]:
    d.line((x, y + 20, x + 100, y + 20), fill=(150, 150, 150), width=w)
    d.text((x + 130, y), label, font=font(36), fill=ink)
    y += 70

y += 30
d.text((x, y), "Position has no absolute meaning: closeness", font=font(30), fill=grey)
d.text((x, y + 40), "reflects shared links (ForceAtlas2). The pink group", font=font(30), fill=grey)
d.text((x, y + 80), "is NOT connected to the rest of the network.", font=font(30), fill=grey)

d.text((PAD, canvas.height - 100),
       "Data: Bossaert & Meidert (2013), Open Journal of Applied Sciences 3(2):174-185, "
       "doi:10.4236/ojapps.2013.32024; distributed in the R package 'manynet' (fict_potter).",
       font=font(34), fill=grey)

canvas.save(VIS / "harry_potter_network.png", dpi=(300, 300))
print(f"Wrote visualization/harry_potter_network.png ({canvas.width}x{canvas.height})")
