import pandas as pd, networkx as nx, matplotlib.pyplot as plt, matplotlib.patches as mpatches

ann = pd.read_csv("out/circuit_annotated.csv")
fids = ann["FAFB"].tolist(); idset = set(fids)

df = pd.read_csv("data/fafb_783_edge_list.csv").iloc[:, :2]; df.columns = ["s", "t"]
edges = [(s, t) for s, t in zip(df["s"].tolist(), df["t"].tolist())
         if s in idset and t in idset and s != t]

G = nx.DiGraph(); G.add_nodes_from(fids); G.add_edges_from(edges)

palette = {"central": "#4C72B0", "descending": "#DD8452", "visual_projection": "#55A868",
           "optic": "#C44E52", "visual_centrifugal": "#8172B3", "other": "#999999"}
sc = dict(zip(ann["FAFB"], ann["super_class"].fillna("other")))
colors = [palette.get(sc.get(n, "other"), "#999999") for n in G.nodes()]
deg = dict(G.degree()); sizes = [30 + 9 * deg[n] for n in G.nodes()]

plt.figure(figsize=(13, 13))
pos = nx.spring_layout(G, k=0.35, iterations=90, seed=1)
nx.draw_networkx_edges(G, pos, edge_color="#cccccc", width=0.4, arrowsize=5, alpha=0.6)
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, linewidths=0.3, edgecolors="white")
plt.legend(handles=[mpatches.Patch(color=c, label=l) for l, c in palette.items() if l != "other"],
           loc="lower left", fontsize=11, title="super-class")
plt.title(f"Conserved circuit across FAFB, BANC & MCNS\n{G.number_of_nodes()} neurons, "
          f"{G.number_of_edges()} connections — identical in all three", fontsize=13)
plt.axis("off"); plt.tight_layout()
plt.savefig("out/circuit_network.png", dpi=220, bbox_inches="tight")
print(f"saved out/circuit_network.png ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")