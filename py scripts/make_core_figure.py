import pandas as pd, networkx as nx, matplotlib.pyplot as plt, matplotlib.patches as mpatches

ann = pd.read_csv("out/circuit_annotated.csv")
fids = ann["FAFB"].tolist(); idset = set(fids)
type_of = dict(zip(ann["FAFB"], ann["type"].astype(str)))
sc = dict(zip(ann["FAFB"], ann["super_class"].fillna("other")))

df = pd.read_csv("data/fafb_783_edge_list.csv").iloc[:, :2]; df.columns = ["s", "t"]
edges = [(s, t) for s, t in zip(df["s"].tolist(), df["t"].tolist())
         if s in idset and t in idset and s != t]
G = nx.DiGraph(); G.add_nodes_from(fids); G.add_edges_from(edges)

U = G.to_undirected(); U.remove_edges_from(nx.selfloop_edges(U))
core = nx.k_core(U, k=2)                     # backbone: drop degree-1 stragglers
H = G.subgraph(core.nodes()).copy()
print("core:", H.number_of_nodes(), "neurons,", H.number_of_edges(), "connections")

palette = {"central": "#4C72B0", "descending": "#DD8452", "visual_projection": "#55A868",
           "optic": "#C44E52", "visual_centrifugal": "#8172B3", "other": "#999999"}
colors = [palette.get(sc.get(n, "other"), "#999999") for n in H.nodes()]
deg = dict(H.degree()); sizes = [120 + 35 * deg[n] for n in H.nodes()]

plt.figure(figsize=(15, 15))
pos = nx.kamada_kawai_layout(H)
nx.draw_networkx_edges(H, pos, edge_color="#bbbbbb", width=0.6, arrowsize=7, alpha=0.6)
nx.draw_networkx_nodes(H, pos, node_color=colors, node_size=sizes, linewidths=0.4, edgecolors="white")
nx.draw_networkx_labels(H, pos, {n: type_of.get(n, "") for n in H.nodes() if deg[n] >= 3}, font_size=7)
plt.legend(handles=[mpatches.Patch(color=c, label=l) for l, c in palette.items() if l != "other"],
           loc="lower left", fontsize=11, title="super-class")
plt.title(f"Densely-connected core of the conserved circuit (2-core)\n"
          f"{H.number_of_nodes()} neurons, {H.number_of_edges()} connections", fontsize=13)
plt.axis("off"); plt.tight_layout()
plt.savefig("out/circuit_core.png", dpi=220, bbox_inches="tight")
print("saved out/circuit_core.png")