# Fermentation Game

Small Streamlit project for a fermentation troubleshooting game plus a separate analytics dashboard.

## Repository layout

- `streamlit_app/app.py` — main game UI
- `streamlit_app/game_logic.py` — scenario data, actions, and state transitions
- `streamlit_app/ui_components.py` — sensor chart rendering
- `streamlit_app/data_manager.py` — Google Sheets logging with local CSV fallback
- `dashboard.py` — analytics dashboard for logged gameplay data
- `game_logs_fallback.csv` — local gameplay log fallback
- `feedback_logs_fallback.csv` — local feedback log fallback
- `v01/` — older front-end prototype assets

## Local setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Game-specific dependencies are also listed in `streamlit_app/requirements.txt`.

## Run locally

Start the game:

```bash
streamlit run streamlit_app/app.py
```

Start the analytics dashboard:

```bash
streamlit run dashboard.py
```

## Data and logging

- The app tries Google Sheets first.
- If `st.secrets["gcp_service_account"]` is unavailable, it falls back to a local `credentials.json`.
- If Sheets logging or loading is unavailable, the project falls back to local CSV files in the repository root.
- Google Sheet name is hard-coded as `Beacon_v02`.

## Notes for future coding agents

- No automated test suite, linter config, or build pipeline was found in this clone.
- The main gameplay logic is data-driven from `SCENARIO_DATA` and `ACTIONS` in `streamlit_app/game_logic.py`.
- Winning the game means resolving causes until the state transitions to scenario `1` (`All Good`).
- `dashboard.py` expects the current CSV schema defined in its `GAME_LOG_COLS` and `FEEDBACK_LOG_COLS` lists.
- `streamlit_app/data_manager.py` and `dashboard.py` both depend on the same Google Sheets workbook name and fallback CSV files, so keep schema changes synchronized across them.
- Scenario `6` includes a repaired `wortTemp` key at runtime; preserve that fix or clean up the source data carefully if you refactor it.

## Known limitations

- No automated tests were found in the repository.
- Logging paths are simple relative paths, so local runs assume the repository root as the working directory.
