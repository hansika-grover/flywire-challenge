import pandas as pd, networkx as nx, random, math
from collections import defaultdict

DS = ["FAFB", "BANC", "MCNS"]
FILES = {"FAFB": "data/fafb_783_edge_list.csv",
         "BANC": "data/banc_626_edge_list.csv",
         "MCNS": "data/mcns_0.9_edge_list.csv"}
corr = pd.read_csv("meta/correspondence.csv"); ids = {d: corr[d].tolist() for d in DS}

def load_edges(p):
    df = pd.read_csv(p).iloc[:, :2]; df.columns = ["src", "dst"]
    return set(zip(df["src"].tolist(), df["dst"].tolist()))

edgesets = []
for d in DS:
    print("loading", d, "..."); G = load_edges(FILES[d]); pos = {n: k for k, n in enumerate(ids[d])}
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

f2i = {fid: k for k, fid in enumerate(corr["FAFB"].tolist())}
start = {f2i[fid] for fid in pd.read_csv("out/solution.csv")["FAFB"].tolist()}
print("starting from", len(start))

def extend(S, rng, gp=0.85):
    S = set(S); blocked = set(); link = defaultdict(int); frontier = set()
    for x in S: blocked |= conflict[x]
    for x in S:
        for w in nbr[x]:
            if w not in S: link[w] += 1; frontier.add(w)
    while True:
        cands = [w for w in frontier if w not in blocked]
        if not cands: break
        if rng.random() < gp:
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
        comp = set(); st = [s]
        while st:
            x = st.pop()
            if x in comp: continue
            comp.add(x); seen.add(x)
            for y in nbr[x]:
                if y in S and y not in comp: st.append(y)
        if len(comp) > len(best): best = comp
    return best

def save(S):
    S = sorted(S)
    ind = lambda E: {(i, j) for i in S for j in S if (i, j) in E}
    iA, iB, iC = ind(A), ind(B), ind(C)
    assert iA == iB == iC
    g = nx.DiGraph(); g.add_nodes_from(S); g.add_edges_from(iA)
    assert nx.is_weakly_connected(g)
    pd.DataFrame([(ids['FAFB'][k], ids['BANC'][k], ids['MCNS'][k]) for k in S],
                 columns=DS).to_csv("out/solution.csv", index=False)
    return len(iA)

rng = random.Random(7); best = set(start); cur = set(start); T = 3.0
for it in range(30000):
    trial = set(cur); r = rng.random()
    if r < 0.3 and len(trial) > 5:
        k = rng.randint(1, 6)
        worst = sorted(trial, key=lambda x: len(conflict[x]), reverse=True)[:max(3, k * 2)]
        for x in rng.sample(worst, min(k, len(worst))): trial.discard(x)
    elif r < 0.85 and len(trial) > 2:
        k = rng.randint(1, 12)
        for x in rng.sample(list(trial), min(k, len(trial))): trial.discard(x)
    else:
        trial = set(rng.sample(list(trial), max(2, int(len(trial) * rng.uniform(0.4, 0.8)))))
    trial = largest_wcc(extend(trial, rng))
    d = len(trial) - len(cur)
    if d >= 0 or rng.random() < math.exp(d / max(T, 1e-6)): cur = trial
    if len(trial) > len(best): best = trial
    T *= 0.9997
    if it % 2000 == 1999:
        cur = set(best); T = max(T, 0.6); ne = save(best)
        print(f"  iter {it+1}: best {len(best)} ({ne} conns) [saved]")

print(f"FINAL: N = {len(best)} neurons, {save(best)} connections (saved)")