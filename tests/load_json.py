import json
with open('./test_data/invalid.response','r') as f:
    content = f.read()
    req_object = json.loads(content)
    raw_input()