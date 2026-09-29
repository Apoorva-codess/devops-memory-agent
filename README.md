# PatchPilot

PatchPilot is a small release-advice prototype for engineering teams. It compares generic deployment guidance with guidance informed by a team's deployment history stored in Hindsight.

> **Prototype note:** The sample deployment records are simulated. PatchPilot does not connect to a live CI/CD system and should not be used to make production deployment decisions.

## What it demonstrates

- **Baseline advice:** Ask Groq for release guidance without team history.
- **Memory-informed advice:** Recall relevant past deployments from Hindsight and include them as evidence for the recommendation.
- **Feedback loop:** Record the engineer's decision and deployment outcome in Hindsight so a later interaction can recall that experience.

Hindsight is the persistent memory layer: the app uses recall before generating memory-informed advice and retain to store sample events and outcomes. Groq generates the recommendation; it does not replace Hindsight.

## Requirements

- Python 3.11 or newer
- A Hindsight Cloud account, memory bank, and API key
- A Groq API key

## Setup

1. Clone this repository and open its folder in a terminal.
2. Create and activate a virtual environment:

   ~~~bash
   python3 -m venv .venv
   source .venv/bin/activate
   ~~~

3. Install the packages:

   ~~~bash
   python -m pip install -r requirements.txt
   ~~~

4. Copy the example settings and edit .env with your own keys:

   ~~~bash
   cp .env.example .env
   ~~~

   Set HINDSIGHT_API_KEY, HINDSIGHT_BASE_URL, HINDSIGHT_BANK_ID, and GROQ_API_KEY. Never commit .env or share its contents.

5. Start the app:

   ~~~bash
   python -m streamlit run app.py
   ~~~

## Demo flow

1. In the sidebar, choose **Add sample team history**. These are fictional examples.
2. Check **Show generic advice without using team memory** and request advice.
3. Uncheck it and request advice again. Expand **See the Hindsight memories used** to inspect the evidence.
4. Record a decision and a simulated outcome to retain an experience, then try a similar release.

Use **Not deployed yet** until there is an outcome to record. For a presentation, identify simulated outcomes as simulated.

## Optional Hindsight connection check

Run:

~~~bash
python check_memory.py
~~~

This stores a test deployment memory in the configured Hindsight bank, recalls it, and prints the result.

## Project files

- app.py — Streamlit interface and Hindsight/Groq workflow
- check_memory.py — optional retain/recall connectivity check
- requirements.txt — pinned Python dependencies
- .env.example — settings template without secrets

## Current limitations

PatchPilot uses manually entered release descriptions and simulated examples. It does not inspect source code, read CI/CD logs, or deploy software. Recommendations are prototype guidance and require an engineer's review.
