# mediaboard-assignment

Techincal interview home assignment

## Setup

### Just running the app

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv run fastapi run"`

### Development

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv sync` - This will install the dependencies (and python 3.13 if required) into a virtual environment
3. Run `uv run fastapi dev"` - This will start the server that auto-reloads on changes

## Usage

After running the app, you can see the API docs at `http://localhost:8000/docs` (interactive) or `http://localhost:8000/redoc` (slightly better looking but you can't call the endpoints from there)

## Validation

### Tests

To run the tests, run `uv run python -m pytest tests/test_full_run`

### Linting

To run the linter, run `uv run ruff check`

### Type checking

To run the type checker, run `uv run pyright`
