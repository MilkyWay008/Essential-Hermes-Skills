# Local Reproduction

Confirm the following on the page side before returning to Node:

- The real entry function
- Call order
- Parameter sources
- Dependent browser objects
- Whether it depends on time, randomness, storage, cookies, UA, canvas, or crypto

Reproduce minimally first, then patch the environment step by step; do not try to simulate the whole browser at once.

