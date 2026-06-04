import pandas as pd

files = {
    "FAFB": "data/fafb_783_edge_list.csv",
    "BANC": "data/banc_626_edge_list.csv",
    "MCNS": "data/mcns_0.9_edge_list.csv",
    "MAOL": "data/maol_1.1_edge_list.csv",
    "MANC": "data/manc_1.2.1_edge_list.csv",
}

for name, path in files.items():
    df = pd.read_csv(path)
    df = df.iloc[:, :2]                 # first two columns = source, target
    df.columns = ["src", "dst"]
    n_edges = len(df)
    n_nodes = pd.unique(df[["src", "dst"]].values.ravel()).size
    sample = f"{df.iloc[0,0]} -> {df.iloc[0,1]}"
    print(f"{name:5s}: {n_nodes:>8,} neurons, {n_edges:>11,} connections | first edge: {sample}")