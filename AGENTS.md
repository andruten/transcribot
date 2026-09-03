# AGENTS.md

Telegram bot (python-telegram-bot + faster-whisper) that transcribes voice/audio/video-note messages from allowlisted chats. Flat single-package layout; entrypoint is `main.py`, run as `python -m main`.

## Commands

- `make run_local` — run the bot locally; needs `.venv` (create with `make setup_local`) and sources `.env` (auto-copied from `env.sample`; fill in a real `BOT_TOKEN` and `ALLOWED_CHAT_IDS`).
- `make test` — builds the dev image (`--build-arg requirements=dev`) and runs `pytest` inside Docker. Code under test is **baked into the image**, not volume-mounted.
- Single test locally: `.venv/bin/pytest test_streaming.py` (dev deps in `requirements/dev.txt`).
- Lint/format: `pre-commit run --all-files` (deps in `requirements/lint.txt`) or `make lint` / `make format` (ruff in Docker, applies fixes); read-only: `make lint_check` / `make format_check`.

## CI / deploy

- CI (`.github/workflows/test.yml`) runs **only pre-commit** (ruff check + ruff format, pre-commit-hooks) on PRs to main. pytest never runs in CI — run `make test` locally.
- Pushes to main / tags build and push the image to `registry.juanmadiaz.com/apps/transcribot`; tags and releases dispatch an `image-published` event to the `torgus/k8s-infra` repo, which deploys via GitOps. `chart/` is an older Helm chart pointing at `andruten/transcribot` on Docker Hub — not the current deploy path.
- Commit messages use conventional prefixes (`feat:`, `fix:`, `ci:`, `chore:`, `build(deps):`).

## Gotchas

- `transcriber.py` instantiates the faster-whisper model at **import time** (module-level `WhisperModel(...)` reading `WHISPER_*` env vars). Importing it directly or via `message_transcriber` triggers a model download/load — keep tests importing only pure modules like `streaming`.
- Pipeline: Telegram file → temp download → pydub ogg→mp3 conversion (requires **ffmpeg**, installed in the image) → streaming transcription → placeholder message progressively edited (`streaming.next_reveal`).
- Telegram Bot API download cap is 20 MB (`MAX_DOWNLOAD_SIZE` in `telegram_file_manager.py`); larger files are rejected.
- All user-facing bot replies are in **Spanish**.
- `whisper_models/` is a local HF model cache (gitignored) mounted into containers at `/root/.cache/whisper` (`HF_HOME`) so models don't re-download on each run.

## Style

- Ruff via pre-commit (`ruff check --fix` + `ruff format`), same setup as comanditabot: no config file — defaults apply (line length 88, double quotes). `check-yaml` excludes `chart/` (Helm templates).
- Local dev and CI use Python 3.12; the Docker image is python:3.12.
