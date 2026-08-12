# Environment Patching Rules

- Only patch objects that page evidence has proven are needed
- Patch one minimal causal unit at a time
- Patch values first, then function stubs, then the returned-object contract
- Re-run after every patch and record whether the first divergence moved forward

