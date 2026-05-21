## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Security Checklist

- [ ] No WhatsApp tokens, app secrets, or real phone numbers committed
- [ ] Error handling doesn't leak sensitive info (tokens, payloads)
- [ ] Dependencies are secure and up-to-date (`uvx pip-audit`)
- [ ] New exposed tools considered for destructive intent (`DEFAULT_SKIP` if MCP-breaking)

## Testing

- [ ] Tests pass locally (`uv run pytest tests/`)
- [ ] New functionality includes tests
- [ ] Coverage hasn't dropped significantly

## Documentation

- [ ] Code is self-documenting with clear names
- [ ] Non-obvious logic includes comments
- [ ] README updated for user-facing changes
- [ ] Breaking changes documented
