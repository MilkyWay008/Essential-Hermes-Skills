# BurpSuite MCP Full Control Extension

Full control of all BurpSuite core features over the MCP protocol. Cross-platform: Windows / Linux (Kali) / macOS.

## Quick Start

### 1. Build the Extension

**Windows**:
```cmd
cd burp-mcp-full
build.bat
```

**Linux / Kali / macOS**:
```bash
cd burp-mcp-full
chmod +x build.sh
./build.sh
```

The build script automatically: detects JDK 21+, downloads dependencies (montoya-api 2025.5 / gson / nanohttpd), compiles, embeds the extension descriptor (`META-INF/extensions/burp-extension.properties`) into the jar, and packages a fat jar. No Gradle needed.

Output: `build/libs/burp-mcp-full.jar`.

### 2. Load into Burp

```
Burp Suite -> Extensions -> Add -> Java -> select build/libs/burp-mcp-full.jar
```

After loading you should see in Output:
```
[MCP] Server started on http://127.0.0.1:9876
```

### 3. Authentication (enabled by default since v2)

On startup the extension generates a random token and writes it to `~/.burp-mcp-token`. `mcp-bridge.js` automatically reads that file and attaches an `Authorization: Bearer <token>` header to every request - no manual configuration needed.

For a fixed token (e.g. shared across multiple clients), use:
- JVM argument: `-Dburp.mcp.token=<token>`
- Environment variable: `BURP_MCP_TOKEN=<token>` (also used bridge-side)

All `/health`, `/tools`, `/` (POST) requests require that header, otherwise 403 is returned. CORS is narrowed to allow only `http://127.0.0.1` origins.

### 4. Configure an MCP Client

In any MCP client (Claude Code / Kiro / Cursor / Cline / Windsurf), add (stdio mode):

```json
{
  "mcpServers": {
    "burpsuite": {
      "command": "node",
      "args": ["<path-to-this-directory>/mcp-bridge.js"]
    }
  }
}
```

### 5. Start Using It

Tell the AI: "Analyze the requests in Burp's proxy history and find security vulnerabilities"

## Feature List

The extension exposes 78 tools. Common categories below (full list in `getToolList()` of `src/main/java/com/burpmcp/McpHttpServer.java`, or `GET http://127.0.0.1:9876/tools` with the Authorization header):

| Category | Tools |
|------|------|
| Proxy history | `proxy_history`, `proxy_detail`, `proxy_history_filtered`, `proxy_websocket`, `proxy_clear`, `search_history`, `highlight`, `annotate`, `compare` |
| Send requests | `send_request`, `send_to_repeater`, `repeater_send`, `repeater_modify_send`, `send_to_intruder` |
| Intruder attacks | `intruder_attack`, `intruder_attack_async`, `intruder_attack_wordlist`, `intruder_pitchfork`, `intruder_cluster_bomb`, `intruder_battering_ram`, `intruder_with_options`, `payload_process` |
| Scan / crawl | `scan` (active/passive), `scan_active`, `scan_results`, `scan_issue_detail`, `crawl`, `sequencer` |
| Scope / Sitemap | `sitemap`, `target_info`, `get_scope`, `add_to_scope`, `remove_from_scope`, `add_issue` |
| Intercept / rules | `intercept_toggle`, `register_http_handler`, `remove_http_handler`, `register_proxy_rule`, `remove_proxy_rule` |
| Encode / decode | `encode`, `decode`, `convert_request`, `export_request`, `generate_csrf_poc`, `extract_from_response`, `token_analysis` |
| Collaborator | `collaborator_generate`, `collaborator_poll` |
| Configuration | `export_config`, `import_config`, `set_upstream_proxy`, `set_dns_override`, `set_http2`, `cookie_jar`, `save_project`, `burp_version`, `extensions_list`, `log` |

> Scan/crawl (`scan`, `scan_active`, `crawl`) requires **Burp Professional**. The Community edition returns a clear license error. Manually added issues (`add_issue`) are written to the Site map.

## Key Tool Parameters

### `intruder_attack` - automated enumeration attack

| Parameter | Description |
|------|------|
| `url_template` | URL template; placeholder defaults to `@@` |
| `placeholder` | Placeholder string (default `@@`) |
| `from` / `to` | Enumeration start/end values |
| `pad_digits` | Zero-padding digits (0 = no padding) |
| `method` | HTTP method (default GET) |
| `body_template` | Request-body template (with placeholders) |
| `headers` | Request-headers object |
| `success_length_not` | Hit condition: response length != this value |
| `success_contains` | Hit condition: response body contains this string |

### `scan` - start an audit

| Parameter | Description |
|------|------|
| `url` | Target URL (required, auto-added to scope) |
| `mode` | `active` (default) or `passive` |

After starting, poll `scan_results` for issues and the live audit status (request count, error count, insertion-point count).

### `register_proxy_rule` - proxy request interception rule

| Parameter | Description |
|------|------|
| `url_contains` | Hit condition: URL contains this string |
| `intercept` | `true` intercept / `false` pass through (default true) |

Deregister rules via `remove_proxy_rule` (based on `Registration.deregister()`, truly unloaded from Burp).

## Usage Examples

### View proxy history
```json
POST http://127.0.0.1:9876
{"tool": "proxy_history", "params": {"limit": 10, "url_filter": "personalblog"}}
```

### Send a request
```json
POST http://127.0.0.1:9876
{"tool": "send_request", "params": {"method": "GET", "url": "https://example.com/api/test"}}
```

### Automated enumeration attack (core feature)
```json
POST http://127.0.0.1:9876
{
  "tool": "intruder_attack",
  "params": {
    "url_template": "https://target.com/api/verify?code=@@",
    "method": "POST",
    "from": 0,
    "to": 999999,
    "pad_digits": 6,
    "success_length_not": 176,
    "headers": {"User-Agent": "Mozilla/5.0"}
  }
}
```

### Toggle interception
```json
POST http://127.0.0.1:9876
{"tool": "intercept_toggle", "params": {"enable": false}}
```

## Port Configuration

Listens on `127.0.0.1:9876` by default. To change it (e.g. port conflict with PortSwigger's official MCP extension):

1. **Burp side**: pass JVM argument `-Dburp.mcp.port=9877` when starting Burp, or set env var `BURP_MCP_PORT=9877`.
2. **Bridge side**: set env vars `BURP_MCP_PORT=9877` and `BURP_MCP_HOST=127.0.0.1` in the MCP client config.

Both sides must use the same port. If Burp isn't running or the port is unreachable, the bridge returns clear connection-error guidance on `tools/list` and `tools/call`.

## Troubleshooting

| Symptom | Fix |
|------|------|
| No "[MCP] Server started" in Burp Output | Port in use or extension failed to load; check the Burp Errors panel |
| MCP client reports "Burp MCP not connected" | Confirm Burp is running and the extension is loaded; confirm both sides use the same port |
| Scan returns "requires Burp Professional" | Normal; the Community edition doesn't support the Scanner API |
| `remove_http_handler` / `remove_proxy_rule` ineffective | Confirm the earlier `register_*` returned success=true |

## Building from Source (Gradle optional)

```bash
cd burp-mcp-full
gradle jar      # requires Gradle 8.7+ installed locally
# Output: build/libs/burp-mcp-full.jar
```

> Prefer `build.bat` / `build.sh` (zero dependencies, auto-downloads the jar). The Gradle path is only a fallback.
