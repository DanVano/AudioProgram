# Claude Code — Project Rules

## Folders to Ignore
- Never read, edit, or reference anything inside `legacy_code/` or its subfolders unless explicitly asked.
- Never read, edit, or reference anything inside `Notes/` unless explicitly asked by name.

## Testing
- After fixing any bug, always run a targeted test to verify the fix before reporting it as done.
- Tests are run inline with `python -` heredoc scripts — no separate test files exist.

## Code Style
- All user-facing errors go through the `print_output` callback — never use bare `print()` for anything visible in the UI.
- Keep modules decoupled. `input_handler.py` and `ui.py` must not import from each other.
- New features go in the appropriate existing file — do not create new Core files without asking.

## Architecture
- Two-folder system: `staging_folder` (downloads + cleaning) → `library_folder` (finished files). Never mix them.
- All long-running operations run in daemon threads via `run_task()` in `main.py`.
- Config is persisted in `user_config.txt` via `utils.py` — always use `update_user_config()` to save changes.
