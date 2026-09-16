# API Plugin — Tutorial

🌐 [English](tutorial.en.md) | [中文](tutorial.zh.md) | [한국어](tutorial.ko.md)

## Sections

 1. Quick start
 2. Configuration
 3. Import Swagger
 4. Search endpoints
 5. Field mapping
 6. Code generation
 7. Auto-detection
 8. FAQ

---

## 1. Quick start

Three steps to get going:

### Step 1: Initialize config

In the frontend project root:

```
/api:config init
```

Follow the prompts to enter the backend Swagger URL — generates `.api-config.json`.

### Step 2: Import endpoints

```
/api:import
```

Parses the Swagger doc and shows the endpoint overview by tag.

### Step 3: Use in development

```
/api:search user                       # Search endpoints
/api:map GET /api/v1/users/{id}        # View field mapping
/api:gen GET /api/v1/users/{id}        # Generate types + request functions
```

Full flow:

```
/api:config init → /api:import → /api:search → /api:map → /api:gen
Init config       Import doc    Search        Field map    Generate
```

---

## 2. Configuration

Config file: `.api-config.json` in the project root.

### Initialize

```
/api:config init
```

Interactive config generation; auto-detects `src/api/` and `src/types/` directories.

### View config

```
/api:config
```

Shows current data sources, codegen output dirs, and the detected request library.

### Add a data source

```
/api:config add
```

Supports URLs (live backend docs) and local files.

### Remove a data source

```
/api:config remove payment-service
```

### Config example

```json
{
  "swagger": {
    "sources": [
      { "name": "main", "url": "http://localhost:8080/swagger/doc.json", "prefix": "/api/v1" },
      { "name": "payment", "file": "./docs/payment-swagger.json", "prefix": "/pay/v1" }
    ]
  },
  "codegen": {
    "outputDir": "src/api",
    "typeDir": "src/types/api",
    "fieldCase": "camelCase"
  }
}
```

Recommended: commit `.api-config.json` so the team shares configuration.

---

## 3. Import Swagger

### Import all data sources

```
/api:import
```

### Import a specific source

```
/api:import --name=main
```

### One-shot import (without modifying config)

```
/api:import --url=http://other-service:8080/swagger/doc.json
```

### Supported formats

- OpenAPI 2.0 (Swagger)
- OpenAPI 3.0.x / 3.1.x
- JSON and YAML

Requires Python 3 — confirm it's installed before first use.

---

## 4. Search endpoints

### Keyword search

```
/api:search user
```

Matches against path, description, and tag name — supports multiple languages.

### Browse by tag

```
/api:search --tag=User Management
```

### Filter by method

```
/api:search user --method=GET
```

### Specify a data source

```
/api:search payment --name=payment
```

### Sample result

```
🔍 Search "user" — 5 endpoints found

┌────┬─────────┬──────────────────────┬──────────────┐
│ #  │ Method  │ Path                 │ Description  │
├────┼─────────┼──────────────────────┼──────────────┤
│ 1  │ GET     │ /api/v1/users        │ List users   │
│ 2  │ POST    │ /api/v1/users        │ Create user  │
│ 3  │ GET     │ /api/v1/users/{id}   │ Get user     │
└────┴─────────┴──────────────────────┴──────────────┘
```

---

## 5. Field mapping

Core feature: show the full backend ↔ frontend field mapping for an endpoint.

### Basic usage

```
/api:map GET /api/v1/users/{id}
```

### Output

- Path / query parameters
- Request body mapping (POST/PUT)
- Response body mapping
- TypeScript type preview

### Mapping rules

```
Backend snake_case  →  Frontend camelCase
user_name           →  userName
avatar_url          →  avatarUrl
created_at          →  createdAt
is_active           →  isActive
```

### Nested objects

Nested fields are numbered hierarchically (e.g., 7.1, 7.2) and produce nested TypeScript types.

### Batch mapping

```
/api:map * /api/v1/users/{id}
```

Shows mappings for every HTTP method on the path.

---

## 6. Code generation

Generates TypeScript types and request functions from endpoint definitions.

### Basic usage

```
/api:gen GET /api/v1/users/{id}
```

Produces two files:
- `src/types/api/user.ts` — type definitions
- `src/api/user.ts` — request functions

### Types only

```
/api:gen GET /api/v1/users/{id} --type-only
```

### Request functions only

```
/api:gen GET /api/v1/users/{id} --request-only
```

### Batch generation

```
/api:gen --tag=User Management   # Batch by tag
/api:gen * /api/v1/users          # All methods on this path
/api:gen * /api/v1/users/{id}     # All methods on this path
```

### Request library adapters

The plugin auto-detects the request library and generates matching code:
- Custom wrapper file (e.g., `src/utils/request.ts`) — imported directly
- axios — `axios.get/post` style
- umi-request — `request()` style
- `@tanstack/react-query` — `useQuery` / `useMutation` hooks
- swr — `useSWR` hooks
- Native fetch — async/await style

---

## 7. Auto-detection

### Request library detection

Done automatically at code-gen time. Detection order:

1. Project's request wrapper file (highest priority)
   - `src/utils/request.ts`
   - `src/lib/request.ts`
   - `src/services/request.ts`

2. Dependencies in `package.json`
   - axios / umi-request / `@tanstack/react-query` / swr / ky

3. None found → native fetch

### Skill auto-hooks

When editing frontend TypeScript / Vue files, the plugin detects API calls and highlights field mapping and potential mismatches.

Trigger: editing `src/**/*.ts`, `src/**/*.tsx`, `src/**/*.vue`

---

## 8. FAQ

### Python is missing

```
❌ Python 3 required

Fix: brew install python3 (macOS) or apt install python3 (Linux)
```

### Swagger URL unreachable

```
❌ Cannot reach http://localhost:8080/swagger/doc.json

Check:
- Is the backend running?
- Is the URL correct? (verify in a browser)
- Do you need a VPN / proxy?
```

### YAML document parse fails

```
❌ YAML requires pyyaml

Fix: pip3 install pyyaml
```

### Generated code uses the wrong casing

Edit `fieldCase` in `.api-config.json`:
- `"camelCase"` — default
- `"snake_case"`
- `"original"` — keep as-is

### Multiple backend services

Add multiple entries to `sources` in `.api-config.json`, each with its own `name` and `prefix`, and filter searches with `--name`.
