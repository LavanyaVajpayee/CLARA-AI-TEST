import json
import sys

memo_path = sys.argv[1]

with open(memo_path) as f:
    memo = json.load(f)

agent = {
    "version": "v1",
    "agent_name": memo.get("company_name","Service Agent"),
    "voice_style": "professional calm",
    "variables": {
        "business_hours": memo.get("business_hours"),
        "address": memo.get("office_address")
    }
}


print(json.dumps(agent, indent=2))
