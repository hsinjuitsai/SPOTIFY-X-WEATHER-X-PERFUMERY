# Architecture

The repository separates UI, deterministic decisions, external integrations, and Pipedream adapters.

1. Streamlit sends `init`, `poll`, and `end` events with a stable `session_id`.
2. Pipedream Data Store keeps `session_started_at`; polling never resets it.
3. Spotify and weather steps collect context.
4. `logic_processor.py` calculates exclusions, rankings, ratios, and fan speed.
5. Gemini creates text only. It cannot control hardware values.
6. Airtable stores the display result and Streamlit reads the latest record.

Pipedream credentials and Data Store contents are deployment state and are never committed.

