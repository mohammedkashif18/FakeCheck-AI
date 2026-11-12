# FakeCheck AI — MVP Web Application

A local Flask web app that highlights common warning patterns in suspicious messages and URLs.

## Features
- Message scanner for suspicious recruitment offers, upfront fees, credential requests, urgency and links.
- URL structure scanner. It does **not** open or visit submitted URLs.
- Risk indicator score, explanations and safety recommendations.
- Recent scan history stored in the current browser using localStorage.
- Responsive dark cybersecurity dashboard.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

## Important limitations
This is a prototype using transparent, rule-based heuristics. It does not use a trained AI model, visit submitted URLs, query live threat-intelligence feeds, verify recruiters, or guarantee whether content is safe or fraudulent. Scores are illustrative indicators, not calibrated probabilities. A low score is not proof of safety.

## Suggested next development steps
1. Add unit tests and a labelled dataset for evaluation.
2. Train and validate a text classification model with precision/recall reporting.
3. Integrate a reputable URL reputation API with explicit user consent and secure key storage.
4. Add rate limiting, logging controls, privacy notice and deployment hardening before public launch.
