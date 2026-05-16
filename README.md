# Git-Auto-PR

An AI-powered GitHub Actions bot that automatically reviews pull requests. When a PR is opened or updated, Git-Auto-PR runs flake8 linting, pytest with coverage, and generates a specific, line-cited code review using Claude AI — posted directly as a comment on the PR.

## Example Output

<!-- ADD SCREENSHOT 1 HERE (the check table / coverage breakdown) -->
<!-- ![PR Review Bot Report](.github/assets/screenshot-report.png) -->

<!-- ADD SCREENSHOT 2 HERE (the AI code review) -->
<!-- ![AI Code Review](.github/assets/screenshot-review.png) -->

## Quick Start

Create `.github/workflows/review.yml` in your repository:

```yaml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: masonbrogden/git-auto-pr@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Then add your Anthropic API key to `Settings → Secrets and variables → Actions` as `ANTHROPIC_API_KEY`. Every pull request will now receive an automated review.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `anthropic_api_key` | Yes | — | Anthropic API key for Claude AI reviews |
| `github_token` | No | `${{ github.token }}` | GitHub token for posting PR comments |
| `model` | No | `claude-sonnet-4-6` | Claude model to use |
| `run_linter` | No | `true` | Run flake8 linter on changed Python files |
| `run_tests` | No | `true` | Run pytest with coverage |
| `coverage_threshold` | No | `0` | Minimum coverage % required to pass |
| `database_url` | No | — | PostgreSQL URL to log review history |

## Outputs

| Output | Description |
|--------|-------------|
| `verdict` | `Approve`, `Request Changes`, or `Needs Discussion` |
| `coverage_pct` | Overall test coverage percentage |
| `linter_passed` | `true` or `false` |
| `tests_passed` | `true` or `false` |

You can use outputs to gate other steps:

```yaml
- uses: masonbrogden/git-auto-pr@v1
  id: review
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    coverage_threshold: '80'

- name: Fail if coverage too low
  if: steps.review.outputs.tests_passed == 'false'
  run: exit 1
```

## Configuration Examples

**Disable linting and tests (AI review only):**
```yaml
- uses: masonbrogden/git-auto-pr@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    run_linter: 'false'
    run_tests: 'false'
```

**Enforce 80% coverage:**
```yaml
- uses: masonbrogden/git-auto-pr@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    coverage_threshold: '80'
```

**Use a faster model:**
```yaml
- uses: masonbrogden/git-auto-pr@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    model: 'claude-haiku-4-5-20251001'
```

## Requirements

- Python repository
- An [Anthropic API key](https://console.anthropic.com/)

## License

MIT
