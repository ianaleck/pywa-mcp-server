# Contributing to pywa MCP Server

## Security First

Before contributing, review the [Security Policy](SECURITY.md) and ensure your contributions follow these guidelines:

### Never Commit Secrets

- WhatsApp access tokens, app secrets, or webhook verify tokens
- Phone Number IDs / WABA IDs from real Meta Business accounts
- Test data with real customer phone numbers
- `.mcp.json` (gitignored — use `.mcp.json.example` for shared config)

### Security Checklist

- [ ] No hardcoded credentials or tokens
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are secure and up-to-date (`uvx pip-audit`)
- [ ] No new exposed tools without considering destructive intent

## Development Setup

1. **Fork and clone**:

```bash
git clone https://github.com/<your-fork>/pywa-mcp-server.git
cd pywa-mcp-server
```

2. **Install dependencies**:

```bash
uv sync --all-groups
```

3. **Run tests**:

```bash
uv run pytest tests/
```

4. **Check coverage**:

```bash
uv run pytest tests/ --cov=pywa_mcp_server --cov-report=term-missing
```

## Code Standards

- **Python 3.13+**
- **Testing**: Add tests for any new helpers in `pywa_mcp_server/__init__.py`
- **No new MCP-breaking surface**: tools that hang (e.g. `listen`) belong in `DEFAULT_SKIP`
- **Type annotations**: keep helpers typed; the schema builder reads `inspect.signature`

## Pull Request Process

1. Create a feature branch from `main`
2. Make changes following code standards
3. Run the full test suite (`uv run pytest tests/`)
4. Submit a PR using the provided template
5. Address any security scan findings (CodeQL, pip-audit, TruffleHog)

## Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities. Use a [private security advisory](https://github.com/ianaleck/pywa-mcp-server/security/advisories/new) — see [SECURITY.md](SECURITY.md).
