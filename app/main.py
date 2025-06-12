from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import openai
import os
from jinja2 import Template

openai.api_key = os.getenv("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")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATE = """
📝 **Meeting Summary**
Date: {{ date }}
Participants: {{ participants }}
Main Points:
{% for point in summary_points %}- {{ point }}
{% endfor %}
Actions:
{% for action in actions %}- {{ action }}
{% endfor %}
"""

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
  <title>MS Teams Transcript Summarizer</title>
  <style>
    body { font-family: sans-serif; margin: 2em; }
    textarea { width: 100%; height: 300px; }
    pre { background: #eee; padding: 1em; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Paste MS Teams Transcript</h1>
  <form method="post">
    <textarea name="transcript" required></textarea><br><br>
    <input type="submit" value="Summarize">
  </form>
  {% if summary %}
    <h2>Summary</h2>
    <pre>{{ summary }}</pre>
  {% endif %}
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def form_get():
    return Template(HTML_FORM).render(summary=None)

@app.post("/", response_class=HTMLResponse)
async def form_post(transcript: str = Form(...)):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts into structured bullet point notes."},
            {"role": "user", "content": f"Summarize the following transcript into key points and action items:\n{transcript}"}
        ]
    )

    summary_text = response['choices'][0]['message']['content']
    summary_lines = summary_text.strip().split("\n")
    points = [line.lstrip("- ") for line in summary_lines if line.strip().startswith("- ")]
    mid = len(points) // 2

    template = Template(TEMPLATE)
    filled = template.render(
        date="{{ auto-detect or input }}",
        participants="{{ auto-detect or input }}",
        summary_points=points[:mid],
        actions=points[mid:]
    )

    return Template(HTML_FORM).render(summary=filled)
