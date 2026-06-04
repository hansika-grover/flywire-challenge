import pandas as pd
from neuprint import Client

c = Client('neuprint.janelia.org', dataset='male-cns:v0.9',
           token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImhhbnNpa2Fncm92ZXIwMUBnbWFpbC5jb20iLCJsZXZlbCI6Im5vYXV0aCIsImltYWdlLXVybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0o0N0dhNzlFX0hEUkhvaTBHaTNWdWllNndQTUx6NS1ld3RfYjctWmhVOE5jSXRmT2c9czk2LWM_c3o9NTA_c3o9NTAiLCJleHAiOjE5NjA2MDEzMTd9.EY44lbKfyrffAIfCPuYc3aDf3Tu-kLcb0KjzIPHuFDs')

# ":Neuron" label keeps it indexed so it won't time out like the unlabeled query did
q = "MATCH (n:Neuron) RETURN n.bodyId AS bodyId, n.type AS type, n.instance AS instance"
df = c.fetch_custom(q)

df.to_csv('meta/mcns_celltypes.csv', index=False)
print(len(df), 'neurons saved to meta/mcns_celltypes.csv')
print(df.head())