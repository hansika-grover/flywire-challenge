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

# starting point = your saved 257 circuit, mapped back to indices
f2i = {fid: k for k, fid in enumerate(corr["FAFB"].tolist())}
start = {f2i[fid] for fid in pd.read_csv("out/solution.csv")["FAFB"].tolist()}
print("starting from", len(start), "neurons")

def extend(S, rng, greedy_p=0.85):
    S = set(S); blocked = set(); link = defaultdict(int); frontier = set()
    for x in S: blocked |= conflict[x]
    for x in S:
        for w in nbr[x]:
            if w not in S: link[w] += 1; frontier.add(w)
    while True:
        cands = [w for w in frontier if w not in blocked]
        if not cands: break
        if rng.random() < greedy_p:
            m = max(link[w] for w in cands); w = rng.choice([w for w in cands if link[w] == m])
        else: w = rng.choice(cands)
        S.add(w); blocked |= conflict[w]
        for u in nbr[w]:
            if u not in S: link[u] += 1; frontier.add(u)
        frontier.discard(w)
    return S

def largest_wcc(S):
    S = set(S); seen = set(); best = set()
    for s in S:
        if s in seen: continue
        comp = set(); stack = [s]
        while stack:
            x = stack.pop()
            if x in comp: continue
            comp.add(x); seen.add(x)
            for y in nbr[x]:
                if y in S and y not in comp: stack.append(y)
        if len(comp) > len(best): best = comp
    return best

rng = random.Random(1)
best = set(start); cur = set(start)
for it in range(10000):
    trial = set(cur)
    for x in rng.sample(list(trial), min(rng.randint(1, 10), len(trial))): trial.discard(x)
    trial = largest_wcc(extend(trial, rng))
    if len(trial) >= len(cur): cur = trial
    if len(trial) > len(best): best = trial
    if it % 1000 == 999:
        print(f"  iter {it+1}: best so far {len(best)}"); cur = set(best)

S = sorted(best)
induced = lambda E: {(i, j) for i in S for j in S if (i, j) in E}
iA, iB, iC = induced(A), induced(B), induced(C)
assert iA == iB == iC, "not identical!"
g = nx.DiGraph(); g.add_nodes_from(S); g.add_edges_from(iA)
assert nx.is_weakly_connected(g), "not connected!"
print(f"VERIFIED: N = {len(S)} neurons, {len(iA)} connections")
pd.DataFrame([(ids['FAFB'][k], ids['BANC'][k], ids['MCNS'][k]) for k in S],
             columns=DS).to_csv("out/solution.csv", index=False)
print("saved out/solution.csv")