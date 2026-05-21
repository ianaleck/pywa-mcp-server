# 💬 pywa MCP Server

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![pywa](https://img.shields.io/badge/pywa-3.9+-25D366)](https://github.com/david-lev/pywa)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Passing-green)](https://github.com/ianaleck/pywa-mcp-server)

> **Unofficial** Model Context Protocol (MCP) server that exposes the [pywa](https://github.com/david-lev/pywa) WhatsApp Cloud API client as MCP tools.

**⚠️ Disclaimer:** Unofficial, third-party integration. Not affiliated with, endorsed by, or sponsored by WhatsApp, Meta, or the pywa project.

## ✨ Features

- 🔗 **Full pywa surface** — ~100 tools auto-discovered from the pywa `WhatsApp` client
- 🛡️ **Type coercion** — auto-parses JSON strings, hydrates dataclasses, coerces enums
- 📦 **Smart serialization** — bytes → base64, datetime → ISO, Path → string, enum → value, dataclass → dict
- 🎛️ **Allowlist control** — restrict exposed tools via `PYWA_MCP_TOOLS` env
- ⚙️ **Var-args support** — pywa methods with `*args` exposed via an `_args` field
- 🧪 **Unit-tested** — 37 tests covering serialization, coercion, schema, discovery
- 📖 **MCP compliant** — works with Claude Code, Claude Desktop, Cursor, Cline, etc.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/)
- A Meta-approved WhatsApp Business phone number + access token
- An MCP-compatible client

### 1. Get pywa credentials

From the [Meta Business dashboard](https://business.facebook.com/):

- **Phone Number ID** — Meta → WhatsApp → API Setup
- **Access token** — system-user token (permanent) or temporary
- **WABA ID** — required for templates / flows / QR codes
- **App ID / App secret** — required for update validation + callback registration

### 2. Register with Claude Code

#### Option A — `claude mcp add` (recommended, zero-install)

Runs the server directly from PyPI via `uvx` — no clone required.

Basic syntax:

```bash
claude mcp add [options] <name> -- <command> [args...]
```

Real example:

```bash
claude mcp add --transport stdio --scope user \
  --env WHATSAPP_PHONE_ID=<phone-id> \
  --env WHATSAPP_TOKEN=<token> \
  --env WHATSAPP_WABA_ID=<waba-id> \
  --env WHATSAPP_APP_ID=<app-id> \
  --env WHATSAPP_APP_SECRET=<app-secret> \
  pywa \
  -- uvx --from pywa-mcp-server pywa-mcp-server
```

Scope (`--scope` / `-s`):
- `local` (default) — private to this project
- `user` — across all your projects
- `project` — committed via `.mcp.json`

Other useful commands:

```bash
claude mcp list                 # list all configured servers
claude mcp get pywa             # show details + health-check pywa
claude mcp remove pywa          # remove from config
claude mcp add-json pywa '<json>'  # add via raw JSON string
claude mcp add-from-claude-desktop # import servers from Claude Desktop (Mac/WSL)
claude mcp reset-project-choices   # reset approved/rejected project-scoped servers
claude mcp serve                   # run Claude Code itself as an MCP server
```

To run from latest git (unreleased changes) instead of PyPI:

```bash
... -- uvx --from git+https://github.com/ianaleck/pywa-mcp-server pywa-mcp-server
```

#### Option B — `.mcp.json` in the project

```bash
cp .mcp.json.example .mcp.json
# edit credentials; .mcp.json is gitignored
```

#### Option C — Claude Desktop / Cursor / Cline / other clients

Any MCP client that supports stdio works. Add:

```json
{
  "mcpServers": {
    "pywa": {
      "command": "uvx",
      "args": ["--from", "pywa-mcp-server", "pywa-mcp-server"],
      "env": {
        "WHATSAPP_PHONE_ID": "...",
        "WHATSAPP_TOKEN": "...",
        "WHATSAPP_WABA_ID": "...",
        "WHATSAPP_APP_ID": "...",
        "WHATSAPP_APP_SECRET": "..."
      }
    }
  }
}
```

### Local development install

If you're modifying the server, clone and run from source:

```bash
git clone https://github.com/ianaleck/pywa-mcp-server.git
cd pywa-mcp-server
uv sync
# then point claude mcp add at:
#   uv --directory /absolute/path/to/pywa-mcp-server run pywa-mcp-server
```

## 🎯 What You Can Do

Once connected, you can ask Claude to:

### 💬 Messaging
- "Send a WhatsApp text to +27..., 'Order confirmed'"
- "Send the totp template to +27... with code 483921"
- "React to message wamid.xxx with 🎉"

### 📋 Templates
- "List all my approved templates"
- "Create a UTILITY template called 'order_shipped' with one body variable"
- "Show me the totp template details"

### 🌊 Flows
- "List all published flows"
- "Show metrics for the customer_pick flow over the last 30 days"
- "Fetch the JSON for flow 903243286082414"

### 🖼️ Media
- "Upload this image URL and send it to +27..."
- "Download media wamid.xxx to /tmp"

### 🔗 QR Codes
- "Create a QR code with the message 'Hi Orana!'"
- "Update QR code XYZ123 with a new prefilled message"

### 🏥 Health & Diagnostics
- "Check my WABA health status"
- "What's blocking my business-initiated sends?"

## 🛠️ Tool Catalog

Auto-discovered from `pywa.WhatsApp`. Full pywa docs at [pywa.readthedocs.io](https://pywa.readthedocs.io).

<details>
<summary><strong>💬 Send messages (16 tools)</strong></summary>

- `send_text` / `send_message`
- `send_image` / `send_video` / `send_audio` / `send_voice`
- `send_document` / `send_sticker`
- `send_location` / `send_contact`
- `send_reaction` / `remove_reaction`
- `send_template`
- `send_catalog` / `send_product` / `send_products`
- `request_location`
</details>

<details>
<summary><strong>📋 Templates (9 tools)</strong></summary>

- `get_template` / `get_templates`
- `create_template` / `update_template` / `delete_template`
- `compare_templates` (uses `_args` for second template ID)
- `unpause_template`
- `upsert_authentication_template`
- `migrate_templates`
</details>

<details>
<summary><strong>🌊 Flows (11 tools)</strong></summary>

- `get_flow` / `get_flows` / `get_flow_assets` / `get_flow_metrics`
- `create_flow` / `update_flow_json` / `update_flow_metadata`
- `publish_flow` / `deprecate_flow` / `delete_flow`
- `migrate_flows`
</details>

<details>
<summary><strong>🖼️ Media (5 tools)</strong></summary>

- `upload_media` / `download_media`
- `get_media_url` / `get_media_bytes` (returns base64-wrapped bytes)
- `delete_media`
- ⚠️ `stream_media` returns a Python generator — unusable via MCP. Use `get_media_bytes` or `download_media` instead.
</details>

<details>
<summary><strong>🔗 QR Codes (5 tools)</strong></summary>

- `create_qr_code`
- `get_qr_code` / `get_qr_codes`
- `update_qr_code`
- `delete_qr_code`
</details>

<details>
<summary><strong>🏢 Business profile & account (5 tools)</strong></summary>

- `get_business_profile` / `update_business_profile`
- `get_business_account`
- `get_commerce_settings` / `update_commerce_settings`
</details>

<details>
<summary><strong>📞 Phone numbers (7 tools)</strong></summary>

- `get_business_phone_number` / `get_business_phone_numbers`
- `get_business_phone_number_settings` / `update_business_phone_number_settings`
- `update_display_name`
- `register_phone_number` / `deregister_phone_number`
</details>

<details>
<summary><strong>☎️ Calling API (6 tools)</strong></summary>

Requires SIP configuration; may be blocked if not enabled.

- `initiate_call` / `terminate_call`
- `pre_accept_call` / `accept_call` / `reject_call`
- `get_call_permissions`
</details>

<details>
<summary><strong>🪝 Webhook configuration (6 tools)</strong></summary>

Note: this server doesn't run a webhook receiver — registration only.

- `set_app_callback_url`
- `override_phone_callback_url` / `override_waba_callback_url`
- `delete_phone_callback_url` / `delete_waba_callback_url`
- `set_business_public_key`
</details>

<details>
<summary><strong>🚫 Block users (3 tools)</strong></summary>

- `block_users` / `unblock_users`
- `get_blocked_users`
</details>

<details>
<summary><strong>💬 Conversation utilities (3 tools)</strong></summary>

- `mark_message_as_read`
- `indicate_typing`
- `update_conversational_automation`
</details>

<details>
<summary><strong>🔧 Misc (1 tool)</strong></summary>

- `get_app_access_token`
</details>

## ⚙️ Environment Variables

| Variable | Required | Notes |
|---|---|---|
| `WHATSAPP_PHONE_ID` / `WA_PHONE_ID` | ✅ | Phone Number ID |
| `WHATSAPP_TOKEN` / `WA_TOKEN` | ✅ | System-user or business access token |
| `WHATSAPP_WABA_ID` / `WA_BUSINESS_ACCOUNT_ID` | ⚠️ | WABA-scoped methods (templates, flows, QR codes) |
| `WHATSAPP_APP_ID` / `WA_APP_ID` | ⚠️ | Callback registration with APP scope |
| `WHATSAPP_APP_SECRET` / `WA_APP_SECRET` | ⚠️ | Update validation + APP-scoped callbacks |
| `PYWA_MCP_TOOLS` | ❌ | Comma-separated allowlist. Unset = all minus `DEFAULT_SKIP`. |

## 🎛️ Tool Filtering

**Default:** every public pywa method except `listen` (which blocks indefinitely).

**Allowlist:** set `PYWA_MCP_TOOLS=send_text,get_templates,send_template` to expose only those.

## ⚠️ Caveats

- **No inbound webhook.** This server only sends/admin. `listen`, `on_*`, `webhook_*` register handlers / wait for inbound updates, but no FastAPI/Flask is run. For inbound support, run pywa's webhook in a separate process.
- **`stream_media`** returns a Python generator — unusable via MCP JSON transport. Use `get_media_bytes` (base64) or `download_media` (writes to disk, returns path).
- **24-hour window.** Free-form sends to a user require they messaged you in the last 24h. Otherwise use an approved template.
- **WABA health.** Check `get_business_account` / `get_business_phone_number` — payment, calling SIP, and other issues cause silent send failures (`can_send_message=BLOCKED`).
- **Schema drops type info for unions.** MCP transport may stringify complex args; this server compensates by JSON-parsing strings when target type expects list/dict/dataclass.

## 🔄 Response Serialization

| Input | Output |
|---|---|
| `bytes` | `{"_bytes_b64": "...", "size": N}` |
| `pathlib.Path` | string |
| `datetime` / `date` / `time` | ISO 8601 |
| `timedelta` | seconds (float) |
| `enum.Enum` | `.value` |
| dataclass | recursive dict |
| pydantic `BaseModel` | `model_dump(mode="json")` |
| other | JSON if serializable, else `repr()` |

## 🧪 Development

```bash
git clone https://github.com/ianaleck/pywa-mcp-server.git
cd pywa-mcp-server
uv sync

# Run tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=main --cov-report=term-missing
```

37 unit tests, ~70% coverage. Remainder is async server boot (not unit-testable).

## 📋 API Requirements

This server requires a [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) account. You must comply with:

- [WhatsApp Business Platform Terms](https://www.whatsapp.com/legal/business-policy)
- [WhatsApp Cloud API rate limits](https://developers.facebook.com/docs/whatsapp/cloud-api/overview#rate-limits)
- [Meta Platform Terms](https://developers.facebook.com/terms/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure all tests pass (`uv run pytest tests/`)
5. Commit your changes
6. Open a Pull Request

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🙏 Acknowledgments

- [pywa](https://github.com/david-lev/pywa) by David Lev — the underlying WhatsApp Cloud API client
- [Model Context Protocol](https://modelcontextprotocol.io/) — protocol spec
- [Anthropic](https://www.anthropic.com/) — Claude and the MCP SDK
- [Meta](https://developers.facebook.com/docs/whatsapp/cloud-api) — WhatsApp Cloud API

## 📞 Support

- 🐛 [Bug Reports](https://github.com/ianaleck/pywa-mcp-server/issues)
- 💡 [Feature Requests](https://github.com/ianaleck/pywa-mcp-server/discussions)
- 📖 [MCP Documentation](https://modelcontextprotocol.io/docs)
- 📖 [pywa Documentation](https://pywa.readthedocs.io)

---

<div align="center">

**Made with ❤️ for the MCP community**

[⭐ Star this project](https://github.com/ianaleck/pywa-mcp-server) if you find it useful!

</div>
