import pandas as pd
import networkx as nx
from collections import defaultdict

DS = ["FAFB", "BANC", "MCNS"]
FILES = {"FAFB": "data/fafb_783_edge_list.csv",
         "BANC": "data/banc_626_edge_list.csv",
         "MCNS": "data/mcns_0.9_edge_list.csv"}

# candidate correspondence (row k = the same cell across the three datasets)
corr = pd.read_csv("meta/correspondence.csv")
ids = {d: corr[d].tolist() for d in DS}
M = len(corr)
print(f"{M} candidate matched neurons")

def load_edges(path):
    df = pd.read_csv(path).iloc[:, :2]; df.columns = ["src", "dst"]
    return set(zip(df["src"].tolist(), df["dst"].tolist()))

# express each dataset's wiring among the matched neurons, in shared index space
edgesets = []
for d in DS:
    print("loading", d, "...")
    G = load_edges(FILES[d])
    pos = {nid: k for k, nid in enumerate(ids[d])}
    E = {(pos[u], pos[v]) for (u, v) in G if u in pos and v in pos and u!=v}
    edgesets.append(E)
    print(f"   {d}: {len(E)} connections among candidates")
A, B, C = edgesets

present_all = A & B & C                 # edges present in ALL three
union = A | B | C

def agree(i, j):
    v = ((i, j) in A, (i, j) in B, (i, j) in C)
    return all(v) or not any(v)

# two neurons conflict if their connection disagrees across datasets (either direction)
conflict = defaultdict(set); nconf = 0
seen = set()
for (i, j) in union:
    key = (i, j) if i < j else (j, i)
    if key in seen: continue
    seen.add(key)
    if not (agree(i, j) and agree(j, i)):
        conflict[i].add(j); conflict[j].add(i); nconf += 1
print(f"{len(present_all)} edges present in all three; {nconf} conflicting pairs")

nbr = defaultdict(set)                  # connectivity via edges present in all three
for (i, j) in present_all:
    nbr[i].add(j); nbr[j].add(i)

def grow(seed):
    S = set(seed)
    blocked = set().union(*(conflict[s] for s in S)) if S else set()
    frontier = set().union(*(nbr[s] for s in S)) - S
    while True:
        best_w, best_link = None, -1
        for w in frontier:
            if w in blocked: continue
            link = len(nbr[w] & S)
            if link > best_link: best_link, best_w = link, w
        if best_w is None: break
        S.add(best_w); blocked |= conflict[best_w]
        frontier |= nbr[best_w]; frontier -= S
    return S

seeds = [(i, j) for (i, j) in present_all if j not in conflict[i]]
seeds.sort(key=lambda e: len(nbr[e[0]]) + len(nbr[e[1]]), reverse=True)
best = set()
for s in seeds[:200]:                   # densest seeds first; raise cap to search harder
    S = grow(s)
    if len(S) > len(best): best = S
print(f"\nlargest circuit found: N = {len(best)} neurons")

# verify it's genuinely identical across all three AND connected
S = sorted(best)
induced = lambda E: {(i, j) for i in S for j in S if (i, j) in E}
iA, iB, iC = induced(A), induced(B), induced(C)
assert iA == iB == iC, "not identical!"
g = nx.DiGraph(); g.add_nodes_from(S); g.add_edges_from(iA)
assert nx.is_weakly_connected(g), "not connected!"
print(f"VERIFIED identical & connected: {len(S)} neurons, {len(iA)} connections")

rows = [(ids["FAFB"][k], ids["BANC"][k], ids["MCNS"][k]) for k in S]
pd.DataFrame(rows, columns=DS).to_csv("out/solution.csv", index=False)
print("saved out/solution.csv")