import json
import requests
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"

transcript_path = sys.argv[1]

with open(transcript_path) as f:
    transcript = f.read()

prompt = f"""
Extract structured configuration.

Return ONLY JSON.

Transcript:
{transcript}
"""

res = requests.post(
    OLLAMA_URL,
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
)


print(res.json()["response"])
