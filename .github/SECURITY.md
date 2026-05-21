# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. Open a private security advisory: https://github.com/ianaleck/pywa-mcp-server/security/advisories/new
3. Include: affected versions, reproduction steps, potential impact
4. You will receive acknowledgment within 48 hours
5. We'll work together to understand and resolve the issue

## Security Considerations for Contributors

### Credential Safety

- Never commit WhatsApp access tokens, app secrets, webhook verify tokens, or WABA / phone IDs from real Meta Business accounts
- Use environment variables (`WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, etc.)
- `.mcp.json` is gitignored — only `.mcp.json.example` is committed

### Code Security

- Avoid exposing destructive pywa methods without operator opt-in via `PYWA_MCP_TOOLS`
- Error handling shouldn't leak access tokens or full request payloads
- The `_serialize` helper falls back to `repr()` — verify it doesn't repr sensitive in-memory state

### Dependencies

- `pip-audit` runs in CI on every push / PR + weekly
- CodeQL (security-extended queries) runs on every push / PR + weekly
- Report suspicious packages

## Responsible Disclosure

We appreciate security researchers who help keep users safe. We'll acknowledge your contribution once the issue is resolved.
