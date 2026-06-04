from neuprint import Client

c = Client('neuprint.janelia.org', dataset='male-cns:v0.9',
           token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImhhbnNpa2Fncm92ZXIwMUBnbWFpbC5jb20iLCJsZXZlbCI6Im5vYXV0aCIsImltYWdlLXVybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0o0N0dhNzlFX0hEUkhvaTBHaTNWdWllNndQTUx6NS1ld3RfYjctWmhVOE5jSXRmT2c9czk2LWM_c3o9NTA_c3o9NTAiLCJleHAiOjE5NjA2MDEzMTd9.EY44lbKfyrffAIfCPuYc3aDf3Tu-kLcb0KjzIPHuFDs')

# adding ":Segment" lets it use the index instead of scanning everything
q = "MATCH (n:Segment {bodyId: 10001}) RETURN n.bodyId AS bodyId, n.type AS type, n.instance AS instance"
print(c.fetch_custom(q))