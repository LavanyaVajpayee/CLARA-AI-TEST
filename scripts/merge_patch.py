import json
import sys

v1_path = sys.argv[1]
patch_path = sys.argv[2]

with open(v1_path) as f:
    v1 = json.load(f)

with open(patch_path) as f:
    patch = json.load(f)

v2 = {**v1, **patch}


print(json.dumps(v2, indent=2))
