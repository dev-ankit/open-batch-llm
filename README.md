# open-batch-llm

A CLI tool to manage and run batch LLM calls.

## Installation

```bash
pip install open-batch-llm
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install open-batch-llm
```

## Usage

### Validate a batch request file

```bash
open-batch-llm validate requests.json
```

### Run batch requests (dry-run)

```bash
open-batch-llm run --dry-run requests.json
```

### Run batch requests

```bash
open-batch-llm run requests.json --provider openai --model gpt-4o-mini --output results.json
```

### Input file format

The input file must be a JSON array of request objects. Each object must contain a `prompt` key:

```json
[
  {"id": "req-1", "prompt": "What is 2 + 2?"},
  {"id": "req-2", "prompt": "Name the planets of the solar system."}
]
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) as the package manager and build system.

```bash
# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Build the package
uv build
```

## Publishing

Releases are published to [PyPI](https://pypi.org/project/open-batch-llm/) automatically via GitHub Actions when a new GitHub Release is created. The workflow uses [Trusted Publishing (OIDC)](https://docs.pypi.org/trusted-publishers/) — no API token is needed.
