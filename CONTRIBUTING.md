# Contributing

Thanks for helping improve this project.

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/crowd-detection-system.git
cd crowd-detection-system
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/download_models.py     # only needed to run the real detector
```

## Check your work

```bash
ruff check .      # style and common mistakes
pytest            # all tests must pass
```

Tests do not need the model files or a camera.

## Making a change

1. Open an issue first for large changes, so we can agree on the approach.
2. Create a branch: `git checkout -b feature/short-name`
3. Make your change. Add or update tests in `tests/`.
4. Run `ruff check .` and `pytest`.
5. Add a line under "Unreleased" in `CHANGELOG.md`.
6. Open a pull request and fill in the template.

## Code style

- Follow PEP 8 (enforced by ruff). Lines up to 100 characters.
- Add type hints to new functions.
- Keep logic that needs no camera separate from OpenCV code, so it stays easy to test.
- If you claim a detector is better, back it with numbers (see `docs/evaluation.md`).

## Reporting bugs

Use the bug report template. Include your Python and OpenCV versions, your config (remove any camera passwords first), and a short sample video if you can share one.

## Commit messages

Short and clear, in the present tense: `Add ROI filter`, `Fix crash on empty frame`.

## Conduct

Be respectful. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
