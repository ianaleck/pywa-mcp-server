# GitHub Actions Setup

## Workflows

- **test.yml** — Runs pytest on every push / PR to `main` / `master`.
- **publish.yml** — Builds and publishes to PyPI when a GitHub release is created (or via manual dispatch).
- **security.yml** — Runs pip-audit, CodeQL, and TruffleHog on push / PR + weekly schedule.

## Automated Publishing

This repo publishes to PyPI when releases are created.

### Setup: PyPI Trusted Publishing (recommended)

Trusted publishing uses OIDC — no long-lived tokens to manage.

1. Go to [pypi.org](https://pypi.org/) → your project → **Settings** → **Publishing**
2. Add a new pending publisher:
   - **Owner**: `ianaleck`
   - **Repository name**: `pywa-mcp-server`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. In the GitHub repo: **Settings** → **Environments** → **New environment** → name it `pypi`

That's it — the publish workflow uses `pypa/gh-action-pypi-publish` which mints a one-time OIDC token. No `PYPI_API_TOKEN` secret needed.

### Setup: API token (alternative)

If you can't use trusted publishing, drop the `environment:` block and add:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

Then add `PYPI_API_TOKEN` as a repository secret.

## How It Works

- **Release published**: Auto-publishes when you create a new GitHub release.
- **Manual dispatch**: Trigger from the Actions tab.

## Security

- **pip-audit** flags vulnerable dependencies (fails on any finding).
- **CodeQL** static analysis for Python (security-extended queries).
- **TruffleHog** scans diffs for committed secrets.
