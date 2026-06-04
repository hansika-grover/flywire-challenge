import pandas as pd

sol = pd.read_csv("out/solution.csv")                       # FAFB, BANC, MCNS (340 rows)
ft = pd.read_csv("meta/fafb_celltypes.csv").rename(columns={"root_id": "FAFB", "primary_type": "type"})
fc = pd.read_csv("meta/fafb_classification.csv").rename(columns={"root_id": "FAFB"})

df = (sol.merge(ft[["FAFB", "type"]], on="FAFB", how="left")
         .merge(fc[["FAFB", "super_class", "class", "side"]], on="FAFB", how="left"))

print("=== cell types (top 25) ===")
print(df["type"].value_counts().head(25))
print("\n=== super_class ===")
print(df["super_class"].value_counts())
print("\n=== class (top 15) ===")
print(df["class"].value_counts().head(15))

df.to_csv("out/circuit_annotated.csv", index=False)
print(f"\n{len(df)} neurons annotated; saved out/circuit_annotated.csv")