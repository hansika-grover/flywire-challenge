# FlyWire Qualification Challenge — Largest Shared Circuit Across Three Connectomes

## Result
The largest neuronal circuit with **identical directed connectivity** across three
FlyWire/Codex connectomes — **FAFB** (female brain), **BANC** (female brain + nerve
cord), and **MCNS** (male CNS) — contains **N = 340 neurons** and **481 directed
connections**. The induced subgraphs on these 340 neurons are byte-for-byte identical
across all three datasets and form a single weakly-connected component.

## Datasets chosen
FAFB, BANC, and MCNS were selected because all three contain the **central brain** —
the only anatomical region shared by three of the five available datasets (MANC is
nerve-cord-only; MAOL is optic-lobe-only). A circuit can only be shared where the same
region was imaged.

## Data sources
- **Edge lists** (neuron-to-neuron connectivity): provided Codex exports —
  `fafb_783`, `banc_626`, `mcns_0.9`. Edge weights (synapse counts) were ignored as
  instructed; graphs are treated as unweighted and directed.
- **Cell-type metadata**:
  - FAFB — Codex "Cell Types" + "Classification" exports.
  - BANC — Codex "Neuron Attributes" export.
  - MCNS — neuPrint `male-cns:v0.9` (Codex bulk export not yet released), pulled via
    `neuprint-python`.

## Method
1. **Graph construction.** Each edge list is loaded as a set of directed edges;
   self-loops (autapses) are removed.
2. **Cross-dataset correspondence.** Neurons have different IDs in each dataset, so
   they are matched by **(cell type, soma side)**. Only combinations that are a
   **singleton** (exactly one neuron) in all three datasets are kept, giving an
   unambiguous correspondence of **3,146 candidate matched neurons**.
3. **Largest identical connected subgraph.** With the correspondence fixed, testing
   isomorphism reduces to a per-pair agreement check: for each pair of matched
   neurons the connection must be present in all three datasets, or absent in all
   three. Two neurons *conflict* if their connectivity disagrees in either direction.
   The largest **connected, conflict-free** set is then found by:
   - deterministic greedy connected expansion (N = 234),
   - randomized multi-start greedy (N = 257),
   - large-neighborhood local search with simulated-annealing acceptance, worst-node
     removal, and big-destroy moves (N = 340, converged).
4. **Verification.** The final 340-neuron induced subgraphs are confirmed identical
   across all three datasets and weakly connected.

## Assumptions
- Edge weights ignored (per instructions); unweighted directed graphs.
- Correspondence restricted to unambiguous **singleton (cell type, side)** matches.
- **Self-loops excluded** — a self-connection is not a connection *between two
  matched neurons*.
- **Connectivity required** — without it, any set of mutually-unconnected neurons is
  trivially "identical" (an empty induced subgraph); requiring a connected circuit
  excludes this degenerate solution.
- Datasets use different synapse-count thresholds for calling an edge (e.g. FAFB
  counts a pair connected at ≥ 5 synapses), so "identical connectivity" is defined up
  to each dataset's thresholding.
- **N = 340 is a verified lower bound** from heuristic search, not a proven maximum;
  the search converged, but optimality is not claimed.

## Reproduce
Requirements: `python3`, `pandas`, `networkx`, `matplotlib`, `neuprint-python`.

Place the three edge lists in `data/` and the metadata files in `meta/`, then run:
```bash
python3 build_correspondence.py   # -> meta/correspondence.csv (3,146 matches)
python3 solve.py                  # greedy baseline (N=234)
python3 solve_more.py             # randomized multi-start (N=257)
python3 polish.py                 # local search (N=334)
python3 polish2.py                # enhanced local search -> out/solution.csv (N=340)
python3 characterize.py           # -> out/circuit_annotated.csv
python3 make_figure.py            # -> figures/circuit_network.png (overview)
python3 make_core_figure.py       # -> figures/circuit_core.png (2-core, labeled)
```
`network.csv` is the final matched-neuron table (identical to `out/solution.csv`).

## Repository structure
```
network.csv     final matched neurons: columns FAFB, BANC, MCNS; 340 rows
README.md       this file
science.md      one-page scientific summary
src/            analysis scripts (build_correspondence.py, solve*.py, polish*.py, ...)
figures/        circuit_network.png, circuit_core.png, circuit_meshes.png
```
