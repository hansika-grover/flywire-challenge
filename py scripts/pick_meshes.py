import pandas as pd
ann = pd.read_csv("out/circuit_annotated.csv")

def pick(mask, label):
    sub = ann[mask]
    if len(sub):
        r = sub.iloc[0]
        print(f"{label:12s} type={str(r['type']):18s} class={str(r['class']):16s} FAFB_id={r['FAFB']}")

print("representative neuron per system:\n")
pick(ann["type"] == "H2", "vision")
pick(ann["class"] == "MBON", "memory")
pick(ann["class"] == "CX", "navigation")
pick(ann["class"] == "ALPN", "olfaction")
pick(ann["super_class"] == "descending", "command")