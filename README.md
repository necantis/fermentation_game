# Fermentation Game — Repository Guide

Interactive Streamlit suite consisting of two independent applications:

| Application | Entry point | Default port | Purpose |
|---|---|---|---|
| **Fermentation Game** | `streamlit_app/app.py` | 8501 | Troubleshooting simulation game |
| **Analytics Dashboard** | `dashboard.py` | 8501 | Legacy gameplay analytics |
| **Scientific Presentation** | `Presentation/app.py` | 8502 | Conference research dashboard (6-tab Streamlit app) |

---

## Repository layout

```
fermentation_game/
├── streamlit_app/            # ── Game application
│   ├── app.py                #    Main UI entry point
│   ├── game_logic.py         #    SCENARIO_DATA dict + ACTIONS list (all game content lives here)
│   ├── ui_components.py      #    Sensor chart rendering helpers
│   ├── data_manager.py       #    Google Sheets logging with local CSV fallback
│   └── requirements.txt      #    Game-specific dependencies
│
├── Presentation/             # ── Scientific Presentation (research dashboard)
│   ├── app.py                #    Entry point — must be run from repo root (see below)
│   ├── config.py             #    COLOR_PALETTE, page settings, CSS injection, Plotly theme
│   ├── state.py              #    Central st.session_state dictionary helpers
│   ├── data_loader.py        #    @st.cache_data loaders for game + workshop data
│   ├── lonza_pipeline.py     #    Data ingestion, Ridge regression, bootstrap CI (no scikit-learn)
│   ├── styles.css            #    Glassmorphism / dark-mode CSS
│   └── tabs/
│       ├── tab_0.py          #    01. The Overall Picture   (BCG vs Simon theory)
│       ├── tab_1.py          #    02. The Experiment (Game) (iframe + Pandas template)
│       ├── tab_2.py          #    03. The Efficiency Illusion (Plotly A/B/C + PLS)
│       ├── tab_3.py          #    04. Feedback & Actions    (reviewer scorecard)
│       ├── tab_4.py          #    05. The Second Iteration  (H1/H2/H3 + cost calc)
│       └── tab_5.py          #    06. Discussion & Conclusions (Toulmin cards)
│
├── Tests/
│   ├── Workshop_Wooclap.csv  #    Survey / Wooclap vote data  (anonymised)
│   ├── Workshop_Scores.csv   #    Peer-score data             (anonymised)
│   └── Beacon_Workshop_analysis_v07.ipynb
│
├── dashboard.py              # Legacy analytics dashboard
├── game_logs_fallback.csv    # Local gameplay log (Google Sheets fallback)
├── feedback_logs_fallback.csv
├── requirements.txt          # Root-level dependencies
└── v01/                      # Archived front-end prototype
```

---

## Quick start

### 1 — Install dependencies

```bash
# From the repository root
pip install -r requirements.txt
pip install -r streamlit_app/requirements.txt
```

### 2 — Start the Fermentation Game

```bash
# From the repository root
python -m streamlit run streamlit_app/app.py --server.port 8501
```

### 3 — Start the Scientific Presentation dashboard

```bash
# IMPORTANT: always launch from the repository root, NOT from inside Presentation/
# The module uses __file__-anchored paths; launching from a subdirectory breaks imports.
python -m streamlit run Presentation/app.py --server.port 8502
```

Open http://localhost:8502 in your browser. The dashboard loads 6 tabs automatically.

### 4 — Start the legacy analytics dashboard

```bash
python -m streamlit run dashboard.py --server.port 8503
```

---

## Architecture — Presentation dashboard

### Data flow

```
Tests/Workshop_Wooclap.csv  ──┐
Tests/Workshop_Scores.csv   ──┼─► lonza_pipeline.ingest_and_unify_lonza()
                               │        │
                               │        ▼
                               │   data_loader.load_lonza_and_stats()   (@st.cache_data ttl=120 s)
                               │        │
game_logs_fallback.csv ────────┼─► data_loader.load_and_preprocess_data()
                               │        │
                               └────────┴──► Presentation/app.py ──► tab_0…tab_5
```

### Key design decisions for agents

- **No scikit-learn.** `lonza_pipeline.py` implements its own Ridge regression solver (`fit_ridge_coeffs`) and TF-IDF generator (`simple_tfidf`) using NumPy/SciPy only. Do not add sklearn imports.
- **Paths are `__file__`-anchored.** `data_loader.py` and `lonza_pipeline.py` both resolve CSV paths relative to `os.path.abspath(__file__)`, walking up one level to the repo root. Never use `os.getcwd()` or bare relative paths for these files.
- **Central state dictionary.** All cross-tab state lives in `st.session_state` via helpers in `state.py` (`get_state`, `set_state`). Do not read `st.session_state` directly in tab files.
- **Color tokens.** All colours come from `config.COLOR_PALETTE`. Never hardcode hex values in tab files.
- **Accessibility & Contrast.** The application uses a dark academic palette with accessibility rules in `styles.css`.
  * **Headings:** Do not use CSS `-webkit-background-clip: text` or transparent text fill gradients, as they fail on certain browsers and projectors. Use solid colors like `#0ea5e9`.
  * **Text inside Cards:** Paragraphs (`p`) and lists (`li`, `ul`, `ol`) inside `.glass-card` elements must inherit the `#e2e8f0` text color defined in `styles.css` to maintain legibility on dark card backgrounds under any light/dark theme settings.
- **HTML Indentation in Markdown.** When rendering custom HTML structures via `st.markdown(..., unsafe_allow_html=True)`, **never indent the HTML tags** (align the lines to the absolute left margin of the f-string). Indenting HTML by 4 or more spaces will cause the Markdown parser to treat them as preformatted code blocks (`<pre><code>`), exposing raw tags like `</tbody>` or `</table>` on the interface.
- **Tab numbering.** Tabs are displayed as `01`–`06` but the Python files are `tab_0.py`–`tab_5.py` (0-indexed). `app.py` maps `idx 0 → tab_0`, etc.
- **Caching.** `@st.cache_data(ttl=120)` is applied to both loaders. If you change CSV schemas, clear the Streamlit cache with the top-right menu or restart the server.
- **Firm anonymisation.** The firm name has been removed to keep the presentation anonymous. Workshop CSV files are named `Workshop_*.csv`. Do not reintroduce firm-specific names (such as "Lonza") in any user-facing strings or telemetry labels.


---

## Architecture — Game application

- All game content (scenarios, sensor readings, causes, actions) is declared in **`SCENARIO_DATA`** and **`ACTIONS`** in `streamlit_app/game_logic.py`. Editing these dicts is the only way to add/change game scenarios — no database or external config.
- Winning the game means resolving causes until the state transitions to scenario `1` (`All Good`).
- Scenario `6` includes a runtime-patched `wortTemp` key. Preserve this fix if you refactor `game_logic.py`.
- `dashboard.py` and `streamlit_app/data_manager.py` share the same Google Sheets workbook name (`Beacon_v02`) and the same CSV schema (`GAME_LOG_COLS`, `FEEDBACK_LOG_COLS`). Keep them in sync when changing log structure.

---

## Data and logging

| Source | Priority | Configuration |
|---|---|---|
| Google Sheets | 1st | `st.secrets["gcp_service_account"]` required; workbook = `Beacon_v02` |
| Local `credentials.json` | 2nd | File must be present in repo root |
| `game_logs_fallback.csv` / `feedback_logs_fallback.csv` | 3rd | Always present; safe default |

---

## Known constraints and gotchas

- **No automated test suite or linter config.** Verify changes with `python -c "import py_compile; py_compile.compile('path/to/file.py', doraise=True)"`.
- **No build pipeline.** All deployments are manual Streamlit runs.
- **Presentation must be launched from the repo root.** Launching from `Presentation/` breaks the `Presentation.*` package imports in `app.py`.
- **Streamlit cache** can serve stale data after CSV renames or schema changes. Use the "Clear cache" option in the browser's Streamlit menu or restart the server.
- **Bootstrap pre-rendering** in `lonza_pipeline.pre_render_bootstrap_importance()` runs 400 resampling iterations on first load (~2–5 s). This is intentional to prevent slider lag. Do not move it inside a slider callback.
- **Port conventions:** game on 8501, presentation on 8502, legacy dashboard on 8503. Running both game and presentation simultaneously requires explicit `--server.port` flags.
