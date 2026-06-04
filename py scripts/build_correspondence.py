import pandas as pd, re

# ---------- FAFB: join cell types + classification on root_id ----------
ft = pd.read_csv("meta/fafb_celltypes.csv")            # root_id, primary_type, ...
fc = pd.read_csv("meta/fafb_classification.csv")       # root_id, ..., side, super_class
fafb = ft.merge(fc[["root_id", "side", "super_class"]], on="root_id", how="left")
fafb = fafb.rename(columns={"root_id": "id", "primary_type": "type"})[["id", "type", "side"]]

# ---------- BANC: one combined file ----------
banc = pd.read_csv("meta/banc_neurons.csv").rename(columns={
    "Root ID": "id", "Primary Cell Type": "type", "Soma side": "side"})[["id", "type", "side"]]

# ---------- MCNS: parse side out of the instance string ----------
mcns = pd.read_csv("meta/mcns_celltypes.csv").rename(columns={"bodyId": "id"})
def side_from_instance(s):
    if not isinstance(s, str): return None
    for tok in re.split(r"[_()]", s):      # "DNp01(GF)_R" -> ... -> "R"
        if tok in ("L", "R", "M"): return tok
    return None
mcns["side"] = mcns["instance"].apply(side_from_instance)
mcns = mcns[["id", "type", "side"]]

# ---------- clean + normalise both fields ----------
def norm_side(x):
    if not isinstance(x, str) or not x.strip(): return "NA"
    x = x.strip().lower()
    return "L" if x[0] == "l" else "R" if x[0] == "r" else "M" if x[0] in "cm" else "NA"

bad_types = {"", "nan", "none", "no_cons", "na", "unknown"}
def prep(df):
    df = df.copy()
    df["type"] = df["type"].astype(str).str.strip()
    df["side"] = df["side"].apply(norm_side)
    return df[~df["type"].str.lower().isin(bad_types)]
fafb, banc, mcns = prep(fafb), prep(banc), prep(mcns)

# ---------- keep (type, side) keys that are UNIQUE in each dataset ----------
def singletons(df):
    g = df.groupby(["type", "side"]).agg(id=("id", "first"), n=("id", "size")).reset_index()
    return g[g["n"] == 1].set_index(["type", "side"])["id"].to_dict()

f, b, m = singletons(fafb), singletons(banc), singletons(mcns)
print(f"unique (type,side) keys -> FAFB {len(f)}, BANC {len(b)}, MCNS {len(m)}")

shared = set(f) & set(b) & set(m)
corr = pd.DataFrame([(f[k], b[k], m[k]) for k in sorted(shared)], columns=["FAFB", "BANC", "MCNS"])
corr.to_csv("meta/correspondence.csv", index=False)
print(f"\n{len(corr)} matched neurons across all three datasets")
print(corr.head())