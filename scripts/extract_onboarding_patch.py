import json
import requests
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"

transcript_path = sys.argv[1]

with open(transcript_path) as f:
    transcript = f.read()

prompt = f"""
You are updating an existing system configuration.

Extract ONLY configuration updates mentioned in the onboarding transcript.

Rules:
- Return JSON only
- Do NOT repeat existing fields unless they changed
- Do NOT guess missing values
- Only include fields explicitly mentioned

Allowed fields:
business_hours
emergency_definition
emergency_routing_rules
call_transfer_rules
integration_constraints
office_address

Return JSON patch.

Transcript:
{transcript}
"""

response = requests.post(
    OLLAMA_URL,
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
)

result = response.json()["response"]


print(result)
