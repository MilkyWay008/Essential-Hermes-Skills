# Code Audit Checklist (condensed)

- [ ] List of all external input entry points
- [ ] AuthN/authZ middleware coverage
- [ ] Multi-tenant IDs bound to the session
- [ ] Deserialization / pickle / YAML load
- [ ] SSRF egress and protocol restrictions
- [ ] Secret and token storage
- [ ] File upload paths and types
- [ ] Dangerous exec/system/Runtime calls

