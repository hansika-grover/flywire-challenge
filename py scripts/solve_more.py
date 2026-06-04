import pandas as pd, networkx as nx, random
from collections import defaultdict

DS = ["FAFB", "BANC", "MCNS"]
FILES = {"FAFB": "data/fafb_783_edge_list.csv",
         "BANC": "data/banc_626_edge_list.csv",
         "MCNS": "data/mcns_0.9_edge_list.csv"}

corr = pd.read_csv("meta/correspondence.csv")
ids = {d: corr[d].tolist() for d in DS}

def load_edges(p):
    df = pd.read_csv(p).iloc[:, :2]; df.columns = ["src", "dst"]
    return set(zip(df["src"].tolist(), df["dst"].tolist()))

edgesets = []
for d in DS:
    print("loading", d, "...")
    G = load_edges(FILES[d]); pos = {n: k for k, n in enumerate(ids[d])}
    edgesets.append({(pos[u], pos[v]) for (u, v) in G if u in pos and v in pos and u != v})
A, B, C = edgesets
present_all = A & B & C
def agree(i, j):
    v = ((i, j) in A, (i, j) in B, (i, j) in C); return all(v) or not any(v)
conflict = defaultdict(set); seen = set()
for (i, j) in (A | B | C):
    key = (i, j) if i < j else (j, i)
    if key in seen: continue
    seen.add(key)
    if not (agree(i, j) and agree(j, i)): conflict[i].add(j); conflict[j].add(i)
nbr = defaultdict(set)
for (i, j) in present_all: nbr[i].add(j); nbr[j].add(i)

def grow(seed, rng=None, greedy_p=1.0):
    S, blocked, frontier, link = set(), set(), set(), defaultdict(int)
    def add(x):
        S.add(x); blocked.update(conflict[x])
        for w in nbr[x]:
            if w not in S: link[w] += 1; frontier.add(w)
        frontier.discard(x)
    for s in seed: add(s)
    while True:
        cands = [w for w in frontier if w not in blocked]
        if not cands: break
        if rng is None or rng.random() < greedy_p:
            m = max(link[w] for w in cands); top = [w for w in cands if link[w] == m]
            w = top[0] if rng is None else rng.choice(top)
        else:
            w = rng.choice(cands)
        add(w)
    return S

seeds = [(i, j) for (i, j) in present_all if j not in conflict[i]]
seeds.sort(key=lambda e: len(nbr[e[0]]) + len(nbr[e[1]]), reverse=True)

best = set()
for s in seeds[:800]:                      # broader deterministic pass
    S = grow(s)
    if len(S) > len(best): best = S
print("after deterministic search:", len(best))

rng = random.Random(0)
for t in range(3000):                       # randomized restarts
    S = grow(rng.choice(seeds), rng, greedy_p=0.85)
    if len(S) > len(best): best = S
    if (t + 1) % 500 == 0: print(f"  trial {t+1}: best so far {len(best)}")

S = sorted(best)
induced = lambda E: {(i, j) for i in S for j in S if (i, j) in E}
iA, iB, iC = induced(A), induced(B), induced(C)
assert iA == iB == iC and nx.is_weakly_connected(nx.DiGraph(list(iA)).to_directed())
print(f"VERIFIED: N = {len(S)} neurons, {len(iA)} connections")
pd.DataFrame([(ids['FAFB'][k], ids['BANC'][k], ids['MCNS'][k]) for k in S],
             columns=DS).to_csv("out/solution.csv", index=False)
print("saved out/solution.csv")