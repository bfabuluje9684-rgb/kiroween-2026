# Implementation Plan: FrankySense Game

## Overview

Implement the FrankySense Halloween quiz game as a Python/Flask backend paired with a React/JavaScript frontend. The backend owns all game logic (session management, question generation, answer validation, rate limiting, fallback question bank). The frontend renders questions, Franky's monster stage as a composite SVG, and end-of-game summaries. AI-generated questions are fetched in parallel at session start; all answer grading runs in backend code only.

## Tasks

- [ ] 1. Project scaffolding and configuration
  - Create the `backend/` directory and add `backend/config.py` that reads `AI_API_KEY`, `AI_API_URL`, and `AI_MODEL` from a `.env` file using `python-dotenv`; expose `AI_API_KEY`, `AI_API_URL`, `AI_MODEL`, and a `BANK_ONLY_MODE` flag (True when the key is absent); log a warning to stderr when the key is missing; add `requirements.txt` listing `flask`, `python-dotenv`, `requests`, `gunicorn`, `hypothesis`, `pytest`, `pytest-flask`; Create `backend/.env.example` with placeholder entries only (no real values):
    ```
    AI_API_KEY=your_api_key_here
    AI_API_URL=https://api.anthropic.com/v1/messages
    AI_MODEL=claude-haiku-5-5
    ```
    This file IS committed to the repo so developers know which variables to set.
  - Create `backend/pytest.ini` containing:
    ```
    [pytest]
    pythonpath = .
    ```
    This lets pytest find backend modules by their plain names (e.g. `import config`, `import question_bank`) when pytest is run from the `backend/` directory.
  - Create the `backend/tests/` directory without an `__init__.py` file, so pytest discovers tests automatically without needing a package structure.
  - Create the `frontend/` directory; scaffold a React + JavaScript app with Vite (`npm create vite@latest frontend -- --template react`); add a `.env.example` with `VITE_API_BASE_URL=http://localhost:5000`
  - Create a root `.gitignore` that excludes `.env`, `__pycache__/`, `*.pyc`, `node_modules/`, `frontend/dist/`, and `backend/static/`
  - _Requirements: 9.4, 11.1, 11.2_

- [ ] 2. Question bank JSON and loader
  - [ ] 2.1 Write `backend/question_bank.json` with at least 20 hand-written questions: at least 3 per topic (`variables`, `data_types`, `conditions`, `loops`, `functions`, `lists`); each entry must have keys `text`, `options` (array of 4 strings), `correct_index` (integer 0–3), `feedback` (non-empty string), and `topic`
    - _Requirements: 12.1, 12.4_
  - [ ] 2.2 Write `backend/question_bank.py` that loads `question_bank.json` at import time, validates that every entry has exactly 4 options and a valid `correct_index`, and exposes a `get_bank_questions(topic=None)` function that returns a filtered or unfiltered copy of the list; raise a startup error if the bank has fewer than 20 entries or any topic has fewer than 3 entries
    - _Requirements: 12.1, 12.4_
  - [ ]* 2.3 Write unit tests for `question_bank.py` in `backend/tests/test_question_bank.py`: verify bank loads ≥ 20 questions; each topic has ≥ 3 entries; every entry has exactly 4 options and a valid `correct_index`
    - _Requirements: 12.1, 12.4_

- [ ] 3. Session manager
  - [ ] 3.1 Write `backend/session_manager.py` defining the `Session` and `Question` dataclasses (fields exactly as in the design); a module-level `threading.Lock` guards all creates, lookups, deletes, and idle-cleanup operations on the `sessions` dict; expose `create_session(questions) -> Session`, `get_session(session_id) -> Session | None`, and `delete_session(session_id)`; implement Algorithm 4 idle-session reaper (`reap_idle_sessions()`) that removes sessions inactive for more than 3 600 seconds
    - _Requirements: 1.1, 10.1, 10.2_
  - [ ]* 3.2 Write unit tests for `session_manager.py` in `backend/tests/test_session_manager.py`: new session starts at Stage 1 with zero counts and `state == "active"`; answering an already-answered question returns the expected 409 error; `reap_idle_sessions` removes sessions older than 1 hour and keeps recent ones
    - _Requirements: 1.1, 10.1, 10.3_

- [ ] 4. AI client
  - [ ] 4.1 Write `backend/ai_client.py` with a single function `generate_question(topic: str) -> dict` that calls the Anthropic Messages API: send `requests.post(AI_API_URL, timeout=10)` with headers `x-api-key: AI_API_KEY`, `anthropic-version: 2023-06-01`, and `content-type: application/json`; the request body must include `model` (read from `AI_MODEL` — never hardcoded), `max_tokens`, and a `messages` list containing the prompt; all provider-specific request and response formats live only in `ai_client.py` — the caller never sees them; the logical fields `topic`, `difficulty: "beginner"`, and `instruction` are wrapped into the Anthropic request format inside this function; parse the JSON text from the response `content` field into a normalised dict with keys `text`, `options`, `correct_index`, and `feedback`; raise an exception if the response `content` text is not valid JSON, if the HTTP request times out, or if any other HTTP error occurs — the caller decides what to do
    - _Requirements: 8.1, 8.5, 9.1, 9.2_
  - [ ]* 4.2 Write unit tests for `ai_client.py` in `backend/tests/test_ai_client.py`: mock `requests.post` to verify the prompt body contains `topic`, `difficulty`, and `instruction`; verify a timeout raises an exception; verify an HTTP error raises an exception
    - _Requirements: 8.1, 8.5_

- [ ] 5. Question generator
  - [ ] 5.1 Write `backend/question_generator.py` implementing Algorithm 1: build 10 topic slots (one per topic guaranteed, four random extras capped at 3 per topic, then shuffled); submit all slots to `ThreadPoolExecutor(max_workers=10)` using `executor.submit()`; call `concurrent.futures.wait(futures, timeout=15)` then `executor.shutdown(wait=False, cancel_futures=True)`; each worker calls `ai_client.generate_question`, validates `len(options)==4` and `correct_index in 0..3`, retries once on failure, marks as "needs bank fallback" on second failure or timeout; run deduplication pass (Algorithm 1 step 5) replacing duplicate texts with unused bank questions of the same topic first; return a list of 10 `Question` dataclass instances
    - _Requirements: 1.3, 1.4, 7.1, 7.2, 8.2, 8.3, 8.5, 13.1, 13.3, 13.4, 13.5_
  - [ ] 5.2 Write property test for question generator — Property 6: No duplicate questions
    - `# Feature: frankysense-game, Property 6: No duplicate questions per session`
    - Use Hypothesis to generate mocked AI responses; assert all `text` values in the returned 10-question list are unique
    - **Validates: Requirements 13.1, 13.4**
  - [ ] 5.3 Write property test for question generator — Property 8: Every session covers all six topics
    - `# Feature: frankysense-game, Property 8: Every session covers all six topics`
    - Use Hypothesis with mocked AI responses; assert the set of `topic` values in the returned list equals `{"variables", "data_types", "conditions", "loops", "functions", "lists"}`
    - **Validates: Requirements 7.1, 7.2**
  - [ ]* 5.4 Write unit tests for `question_generator.py` in `backend/tests/test_question_generator.py`: slot that times out is replaced with a bank question; slot that fails validation twice is replaced with a bank question; dedup removes identical question texts
    - _Requirements: 8.3, 8.5, 13.4_

- [ ] 6. Answer validator
  - [ ] 6.1 Write `backend/answer_validator.py` implementing Algorithm 2 (the pure validation and state-mutation logic, not the HTTP layer); the main entry point is `validate_answer(session, question_index, selected_option)`; accept `session` and `selected_option`; validate `selected_option` is an integer 0–3; acquire `session.lock`; check session state and question index; mark answered; compute result; update `correct_count`, `wrong_count`, `franky_stage`, `missed_topics`; update `session.state` to `"game_over"` or `"win"` or advance `current_index`; update `session.last_activity`; release lock; return a result dict containing `result`, `feedback` (with fallback), `franky_stage`, `correct_count`, `wrong_count`, `missed_topics`, `session_state`, and `next_question` (or `null`); `correct_index` is never included
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 4.1, 4.4, 5.1, 6.1, 10.2, 10.3, 10.4, 15.1_
  - [ ] 6.2 Write property test for answer validator — Property 1: Answer validation never delegates to AI
    - `# Feature: frankysense-game, Property 1: Answer validation never delegates to AI`
    - Generate random sessions with random `correct_index` values; assert `ai_client.generate_question` is never called during `validate_answer`
    - **Validates: Requirements 3.1, 3.2**
  - [ ] 6.3 Write property test for answer validator — Property 2: Franky stage increments only on wrong answers
    - `# Feature: frankysense-game, Property 2: Franky stage increments only on wrong answers`
    - Generate random sequences of correct and wrong submissions; assert `franky_stage == 1 + wrong_count` holds after each submission
    - **Validates: Requirements 4.1, 4.4**
  - [ ] 6.4 Write property test for answer validator — Property 3: Franky stage is bounded at 5
    - `# Feature: frankysense-game, Property 3: Franky stage is bounded at 5`
    - Generate sessions with any number of wrong submissions (up to and beyond 4); assert `1 <= franky_stage <= 5` always holds
    - **Validates: Requirements 4.1, 5.1**
  - [ ] 6.5 Write property test for answer validator — Property 4: Session terminates at Stage 5
    - `# Feature: frankysense-game, Property 4: Session terminates at Stage 5`
    - Generate sessions driven to exactly 4 wrong answers; assert `session.state == "game_over"` and a 5th submission returns a 409-equivalent error leaving state unchanged
    - **Validates: Requirements 5.1, 10.4**
  - [ ] 6.6 Write property test for answer validator — Property 5: Win condition
    - `# Feature: frankysense-game, Property 5: Win condition requires all questions answered before Stage 5`
    - Generate full 10-question sessions with varying `wrong_count` (0–3 → win; 4+ → game_over); assert `session.state == "win"` iff `wrong_count <= 3` at end
    - **Validates: Requirements 6.1, 5.1**
  - [ ] 6.7 Write property test for answer validator — Property 10: Already-answered questions are rejected
    - `# Feature: frankysense-game, Property 10: Already-answered questions are rejected`
    - Generate sessions; submit the same `question_index` twice; assert the second call returns a 409-equivalent error and `session.state` is unchanged
    - **Validates: Requirements 10.3**
  - [ ] 6.8 Write property test for answer validator — Property 11: Feedback fallback is always non-empty
    - `# Feature: frankysense-game, Property 11: Feedback fallback is always non-empty`
    - Generate questions with empty or `None` feedback; assert the returned `feedback` field is a non-empty string
    - **Validates: Requirements 3.5**
  - [ ] 6.9 Write property test for answer validator — Property 12: missed_topics mirrors Wrong_Answer topics in order
    - `# Feature: frankysense-game, Property 12: missed_topics mirrors Wrong_Answer topics in order`
    - Generate random sequences of correct and wrong submissions; assert `len(missed_topics) == wrong_count` and `missed_topics[i]` equals the topic of the i-th wrong answer submitted
    - **Validates: Requirements 15.1, 15.4**
  - [ ]* 6.10 Write unit tests for `answer_validator.py` in `backend/tests/test_answer_validator.py`: correct answer returns "correct" and does not increment `wrong_count`; wrong answer increments `franky_stage` by 1; fourth wrong answer sets `state = "game_over"`; submitting a wrong answer appends its topic to `missed_topics`; correct answer leaves `missed_topics` unchanged; a topic missed more than once appears multiple times in order
    - _Requirements: 3.1, 4.1, 5.1, 15.1_

- [ ] 7. Checkpoint — backend logic
  - Ensure all backend unit and property tests pass with `pytest tests/ -x` (run from the `backend/` directory); ask the user if any failures arise before continuing.

- [ ] 8. Rate limiter
  - [ ] 8.1 Write `backend/rate_limiter.py` implementing Algorithm 3: module-level `threading.Lock` guards all reads/writes of `ip_hourly` and `global_daily`; `check_and_consume(ip_address) -> str` returns `"ai_allowed"` or `"bank_only"`; reset daily counter when the date changes; reset per-IP window when 3 600 seconds have elapsed; return `"bank_only"` immediately when `BANK_ONLY_MODE` is True (no key configured)
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  - [ ] 8.2 Write property test for rate limiter — Property 9: Rate limiting caps AI session counts correctly
    - `# Feature: frankysense-game, Property 9: Rate limiting caps AI session counts correctly`
    - Use Hypothesis to generate random sequences of requests from a single IP address within a 60-minute window; assert AI is used for at most 5 requests and all subsequent requests in that window return `"bank_only"`
    - **Validates: Requirements 14.1, 14.2**
  - [ ]* 8.3 Write unit tests for `rate_limiter.py` in `backend/tests/test_rate_limiter.py`: 5th request within an hour is allowed; 6th is denied; counter resets after the hour window; daily counter resets at midnight; daily limit of 200 is enforced
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 9. AI response round-trip property test
  - [ ] 9.1 Write property test for `question_generator.py` — Property 7: Question serialization round-trip
    - `# Feature: frankysense-game, Property 7: Question serialization round-trip`
    - Use Hypothesis to generate random dicts matching the AI response schema; parse them into `Question` objects and re-serialize; assert `text`, `options`, `correct_index`, and `feedback` are equivalent to the originals
    - **Validates: Requirements 8.4**

- [ ] 10. Routes and Flask app
  - [ ] 10.1 Write `backend/routes.py` with two route handlers: `POST /sessions` calls `reap_idle_sessions()`, calls `rate_limiter.check_and_consume(ip)`, calls `question_generator.generate_questions(mode)`, calls `session_manager.create_session(questions)`, and returns the `201` response body from the design; `POST /sessions/<session_id>/answers` delegates to `answer_validator.validate_answer(session, question_index, selected_option)` and maps its return value to the appropriate `200`, `400`, `404`, or `409` JSON response
    - _Requirements: 1.1, 1.2, 3.1, 3.3, 10.1, 10.3, 10.4_
  - [ ] 10.2 Write `backend/app.py` as the Flask application factory: create the Flask app; register `ProxyFix(app, x_for=1)`; register the blueprint from `routes.py`; configure CORS headers for the local dev origin (controlled by an env var so they are absent in production); in production, serve React's `frontend/dist/` as static files from `/`
    - _Requirements: 9.1, 11.1_
  - [ ]* 10.3 Write integration tests in `backend/tests/test_integration.py`: full session lifecycle (POST `/sessions` → submit 10 correct answers → verify `session_state == "win"`); Stage 5 path (submit 4 wrong answers → verify `session_state == "game_over"` on the 4th); bank-only mode (start server with no API key, verify sessions are created with bank questions); duplicate answer submission returns 409; out-of-order submission returns 409
    - _Requirements: 5.1, 6.1, 10.3, 10.4, 12.2_

- [ ] 11. Checkpoint — full backend
  - Run `pytest tests/ -x` (run from the `backend/` directory); ensure all unit, property, and integration tests pass. Ask the user if any failures arise before continuing.

- [ ] 12. Frontend API layer and app shell
  - [ ] 12.1 Write `frontend/src/api.js` with thin `fetch()` wrappers: `createSession() -> Promise<SessionResponse>` (POST `/sessions`) and `submitAnswer(sessionId, questionIndex, selectedOption) -> Promise<AnswerResponse>` (POST `/sessions/:id/answers`); read `import.meta.env.VITE_API_BASE_URL` for the base URL; re-throw non-OK responses with the parsed error body
    - _Requirements: 11.2_
  - [ ] 12.2 Write `frontend/src/App.jsx` as the top-level component: hold `sessionData` state (session response from `createSession`), `currentQuestion`, `frankyStage`, `correctCount`, `wrongCount`, `missedTopics`, `sessionState`, and `screen` (one of `"start"`, `"question"`, `"game_over"`, `"victory"`); pass setters down as props; render the active screen component
    - _Requirements: 10.1, 11.2_

- [ ] 13. StartScreen component
  - Write `frontend/src/StartScreen.jsx`: render the Start button; on click, call `api.createSession()`, update App state with the returned session data, and transition to the `"question"` screen; display a loading message ("Summoning Franky…") while the POST is in-flight; handle errors with a visible error message
  - _Requirements: 1.1, 1.2, 11.2_

- [ ] 14. ScoreDisplay component
  - Write `frontend/src/ScoreDisplay.jsx`: accept `correctCount` and `wrongCount` as props; render both counts; use inline comments to explain the display logic
  - _Requirements: 5.3, 6.3, 11.2_

- [ ] 15. QuestionCard component
  - Write `frontend/src/QuestionCard.jsx`: accept `question` (with `text` and `options`), `onAnswer` callback, and `disabled` bool as props; render the question text and exactly four labeled answer buttons; disable all buttons when `disabled` is true (after answer is submitted); apply spooky dark styling with sufficient contrast (WCAG AA)
  - _Requirements: 2.1, 2.2, 2.3, 11.2_

- [ ] 16. StitchedMonster component
  - Write `frontend/src/StitchedMonster.jsx`: accept `frankyStage` (1–5) and `missedTopics` (ordered list of topic keys) as props; render Franky as a composite SVG that scales overall size with `frankyStage` (stage 1 = tiny, stage 5 = huge); map each of the six canonical topic keys (`variables`, `data_types`, `conditions`, `loops`, `functions`, `lists`) to a distinct SVG body part; show the body part for each unique topic in `missedTopics`; if a topic appears more than once, render that part with an extra stitch or glow effect rather than adding a duplicate part; add inline comments explaining the topic-to-body-part mapping and glow logic
  - _Requirements: 4.2, 4.3, 15.2, 15.3, 11.2_

- [ ] 17. FeedbackPanel component
  - Write `frontend/src/FeedbackPanel.jsx`: accept `result` ("correct"|"wrong"), `feedback` (string), `frankyStage`, `sessionState`, `onNext` callback as props; display the result clearly; display feedback text if present (non-blocking — always show the Next/Continue button regardless); label the button "Continue" when `sessionState == "game_over"` (wrong answer hit Stage 5) or when `sessionState == "win"` (final question answered), otherwise label it "Next"; call `onNext` on button click; show a positive confirmation (no Franky change) for correct answers
  - _Requirements: 3.3, 3.5, 3.6, 4.5, 4.6, 11.2_

- [ ] 18. WeakSpotsSummary component
  - Write `frontend/src/WeakSpotsSummary.jsx`: accept `missedTopics` (ordered list of topic keys) as props; count occurrences per topic; render a human-readable summary (e.g., "Franky is stitched from your weak spots: loops (2), functions (1)"); convert internal topic keys to display names (`data_types` → "data types", etc.); if `missedTopics` is empty, render "Franky stayed tiny because there were no weak spots"; add inline comments for the key-to-display-name mapping
  - _Requirements: 15.5, 15.6, 11.2_

- [ ] 19. GameOverScreen component
  - Write `frontend/src/GameOverScreen.jsx`: accept `correctCount`, `wrongCount`, `totalQuestions`, `missedTopics`, and `onPlayAgain` callback as props; display Franky's Stage 5 visual (or a "devoured" message); show final score (correct answers and total questions attempted); render `<WeakSpotsSummary missedTopics={missedTopics} />`; render a Play Again button that calls `onPlayAgain`
  - _Requirements: 5.2, 5.3, 5.4, 15.5, 11.2_

- [ ] 20. VictoryScreen component
  - Write `frontend/src/VictoryScreen.jsx`: accept `correctCount`, `wrongCount`, `missedTopics`, and `onPlayAgain` callback as props; display a congratulatory message; show final score (correct answers and wrong answers); render `<WeakSpotsSummary missedTopics={missedTopics} />`; render a Play Again button that calls `onPlayAgain`; handle the zero-wrong-answers case (WeakSpotsSummary will display the "stayed tiny" message automatically)
  - _Requirements: 6.2, 6.3, 6.4, 15.5, 15.6, 11.2_

- [ ] 21. Wire App.jsx and apply global styling
  - [ ] 21.1 Connect all screen components inside `App.jsx`: handle `onPlayAgain` by calling `api.createSession()` again and resetting all state; handle `onAnswer` by calling `api.submitAnswer()`, updating `frankyStage`, `correctCount`, `wrongCount`, `missedTopics`, and `sessionState` from the response; the screen transition to `game_over` or `victory` happens only when the player clicks Continue in `FeedbackPanel`, not when the answer response arrives; `onNext` in `FeedbackPanel` triggers the screen change based on the already-stored `sessionState`; display a generic error message and stay on the current question for 400/404/409 responses
    - _Requirements: 1.1, 4.6, 5.2, 5.4, 6.4, 10.1_
  - [ ] 21.2 Add global CSS in `frontend/src/index.css`: dark background (`#1a0a2e` or similar), orange/green accent palette, legible font with WCAG AA contrast ratio; import the CSS in `main.jsx`
    - _Requirements: 2.2_

- [ ] 22. Checkpoint — full frontend
  - Verify the app runs with `npm run dev` in `frontend/` and manually confirm: Start screen loads; questions display with 4 options; Franky SVG grows on wrong answers; FeedbackPanel shows result and feedback; GameOverScreen and VictoryScreen display correct scores and WeakSpotsSummary; Play Again restarts session.

- [ ] 23. Production build and deployment wiring
  - [ ] 23.1 Add a build script (or document the steps) in a `Makefile` or `README.md`: `npm run build` in `frontend/`; copy or symlink `frontend/dist/` to `backend/static/`; Flask route in `app.py` already serves `index.html` from `backend/static/` for all non-API routes
    - _Requirements: 11.1_
  - [ ] 23.2 Write a `README.md` at the project root documenting: prerequisites (Python 3.11+, Node 18+); local development setup (create `.env` with API key, `pip install -r requirements.txt`, `npm install` in `frontend/`, run Flask dev server and React dev server separately); production build steps; running tests (`pytest tests/` (run from the `backend/` directory)); gunicorn command (`gunicorn --workers 1 --threads 8 'app:create_app()'` from the `backend/` directory)
    - _Requirements: 9.4, 11.1_

- [ ] 24. Final checkpoint — all tests pass
  - Run `pytest tests/ -v` (run from the `backend/` directory); ensure every unit, property-based, and integration test passes. Ask the user if any failures arise.

## Notes

- Property-based tests (Properties 1–12) are required and must pass before moving on. Unit tests are marked `*` optional and can be skipped for a faster MVP.
- The `correct_index` field must **never** appear in any API response to the frontend; `answer_validator.py` is the only module that reads it.
- All six canonical topic keys (`variables`, `data_types`, `conditions`, `loops`, `functions`, `lists`) must be used consistently across the backend, API responses, and frontend components. Only `WeakSpotsSummary.jsx` converts them to display names.
- The session `threading.Lock` hierarchy has two levels: a module-level lock in `session_manager.py` guards the `sessions` dict, and a per-session `session.lock` in `answer_validator.py` guards state mutations. Never acquire the per-session lock while holding the module-level lock.
- Each property-based test must include the comment `# Feature: frankysense-game, Property N: <text>` as specified in the design's testing strategy section.
- Gunicorn must run with `--workers 1` to keep all sessions and counters in a single process; `--threads 8` handles concurrency within that process.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3", "4.1"] },
    { "id": 4, "tasks": ["3.2", "4.2", "5.1"] },
    { "id": 5, "tasks": ["5.2", "5.3", "5.4", "6.1"] },
    { "id": 6, "tasks": ["6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10"] },
    { "id": 7, "tasks": ["7"] },
    { "id": 8, "tasks": ["8.1"] },
    { "id": 9, "tasks": ["8.2", "8.3", "9.1"] },
    { "id": 10, "tasks": ["10.1"] },
    { "id": 11, "tasks": ["10.2"] },
    { "id": 12, "tasks": ["10.3"] },
    { "id": 13, "tasks": ["11"] },
    { "id": 14, "tasks": ["12.1"] },
    { "id": 15, "tasks": ["12.2"] },
    { "id": 16, "tasks": ["13", "14"] },
    { "id": 17, "tasks": ["15", "16"] },
    { "id": 18, "tasks": ["17", "18"] },
    { "id": 19, "tasks": ["19", "20"] },
    { "id": 20, "tasks": ["21.1"] },
    { "id": 21, "tasks": ["21.2"] },
    { "id": 22, "tasks": ["22"] },
    { "id": 23, "tasks": ["23.1"] },
    { "id": 24, "tasks": ["23.2"] },
    { "id": 25, "tasks": ["24"] }
  ]
}
```
