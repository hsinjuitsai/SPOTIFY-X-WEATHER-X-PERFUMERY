# Pipedream setup

1. Create an HTTP-triggered workflow.
2. Add `session_manager.js` as a Node.js code step named `session_manager`.
3. Add a `data_store` prop named `scent_db` and select a store called `scent_sessions`.
4. Add a Filter that continues only when `continue_processing` is true.
5. Add `fetch_context.py` as the Python step named `code`, connect the user's own Spotify account, and expose that connected account to the code step.
6. Store `OPENWEATHER_API_KEY` as a project secret. Never paste it into the code.
7. Add the Airtable Get All Records step as `get_all_records`.
8. Add `logic_processor.py` as `logic_processor`.
9. Configure Gemini with `prompt.txt`. Gemini returns text only.
10. Add `parse_ai_output.js`, then the Airtable Create Record step.
11. Add `update_session.js` and select the same `scent_sessions` Data Store.

Every user must connect their own Spotify/Airtable accounts and create their own OpenWeather secret. Never commit OAuth tokens, API keys, webhook event payloads, or Data Store exports.
