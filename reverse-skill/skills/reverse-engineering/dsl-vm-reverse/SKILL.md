---
name: dsl-vm-reverse
description: Reverse JavaScript-based custom DSL/VM interpreters, non-standard WASM-like runtimes, and risk-control engines. Use when analyzing IIFE or switch-based opcode dispatchers, extracting instruction tables, recovering bytecode semantics, capturing VM state at runtime, or reconstructing execution flow.
---

# 🔄 DSL Custom VM Reverse Engineering

> For reverse-engineering custom WASM VMs / risk-control engines implemented in JavaScript

---

## Table of Contents

- [1. Scope](#1-scope)
- [2. DSL VM Identification Features](#2-dsl-vm-identification-features)
- [3. General Reverse-Engineering Workflow](#3-general-reverse-engineering-workflow)
- [4. Opcode Extraction and Classification](#4-opcode-extraction-and-classification)
- [5. Runtime Capture Approaches](#5-runtime-capture-approaches)
- [6. Common Status Codes](#6-common-status-codes)
- [7. Skill Self-Check Checklist](#7-skill-self-check-checklist)

---

## 1. Scope

Use this skill when the target file matches **any** of the following features:

| # | Feature | Description |
|---|------|------|
| 1 | IIFE start + many single-letter variable names | `!function(){var U=void 0,y=parseInt,E0=Function,...}` |
| 2 | Contains `DG()` or a similar function with a switch-case loop | Interpreter main loop; `d[7]&31` decodes the opcode |
| 3 | Large file (500KB+) but zero-byte ratio < 1% | Non-standard WASM, pure JS |
| 4 | Contains `C[number]` constant-table references | `C[9][xxx]` function table / string table |
| 5 | Single-line minified code | 583KB single line, obfuscated variable names |

### Exclusion Rules

| Condition | Not this skill | Go to |
|------|-----------|------|
| File starts with `\x00asm` | Standard WASM binary | `../languages.md` |
| File starts with `Uint8Array([0,97,115,109])` (WASM magic) | Embedded WASM | Extract .wasm then switch to IDA/Ghidra |
| Standard Webpack bundle (`function(e,t,n){...}`) | Plain JS | `js-reverse/` |
| Zero-byte ratio > 20% | WASM binary | `../languages.md` |

---

## 2. DSL VM Identification Features

### Code Features

```javascript
// 特征 1: IIFE 入口，单字母变量映射数字常量
!function(){
    var U=void 0, y=parseInt, E0=Function, AN=Uint8Array;
    var E=15, l=10, m=12, x=16, S=13, $=11;
    // 数字常量映射为变量名，替代原始数字
    ...
}

// 特征 2: 解释器主循环 DG()
function DG(C, d, ...) {
    var d = [];  // 数组模拟 WASM stack/locals
    for (d[7] = x; d[7] !== U;) {
        var aE = d[7] & 31;         // 低 5 位 = opcode
        var O = d[7] >> 5 & 31;      // 高 5 位 = sub-operation
        switch (aE) {
            case 0: /* ... */ d[7] = 612; break;
            case 1: /* ... */
            // ... N 个 case
        }
    }
}

// 特征 3: 常量表 C[9] 存储函数索引和字符串
// C[9][0] = ["pc"]      → 函数参数描述
// C[9][667] = "string"  → 字符串常量
// C[9][x] = number      → 函数索引

// 特征 4: W(C[index], null, ...) 调用模式
// W = Function.prototype.call.bind(call)
// 所有内置函数通过 C[index] 索引调用

// 特征 5: 指令编码格式
// d[7] = opcode(bit 0-4) | subop(bit 5-9) | operand(bit 10+)
```

### Opcode Encoding Format

Each instruction is encoded as a 32-bit integer:

```
bit 0-4:   opcode (0-N)
bit 5-9:   sub-operation (0-31)
bit 10-31: operand/立即数

解码:
  aE = d[7] & 31        → opcode
  O  = d[7] >> 5 & 31   → sub-operation
  d[other] = d[7] >> 10  → operand
```

---

## 3. General Reverse-Engineering Workflow

### Phase 1: File Classification (5 min)

```bash
# 检查是否为 DSL VM
python3 << 'EOF'
with open('target.js', 'rb') as f:
    head = f.read(100)

# 1. 检查 WASM 魔术字
if head[:4] == b'\x00asm':
    print("标准 WASM 二进制")
    exit()

# 2. 检查零字节占比
data = open('target.js', 'rb').read()
zero_pct = data.count(b'\x00') / len(data) * 100
print(f"零字节占比: {zero_pct:.1f}%")

if zero_pct > 20:
    print("WASM 二进制")
elif head[:2] == b'!f':
    # 检查单字母变量模式
    if b'var U=void 0' in head or b'U=void 0,y=parseInt' in head:
        print("→ DSL VM!")
    else:
        print("普通 JS IIFE")
EOF
```

### Phase 2: Variable Mapping Table Extraction (10 min)

```python
import re

with open('target.js', 'r', errors='replace') as f:
    s = f.read()

# 提取开头 2000 字符的 var X=数字 映射
mappings = re.findall(r'var\s+(\w+)\s*=\s*(\d+)', s[:2000])
print('常量映射:')
for name, val in mappings:
    print(f"  {name:4s} = {val:3d} (0x{int(val):02x})")
```

### Phase 3: Opcode Extraction and Classification (15 min)

```python
# 1. 提取所有 case
all_cases = re.findall(r'case\s+(\d+):', s)
unique = sorted(set(int(c) for c in all_cases))

print(f"总 case: {len(all_cases)} 个")
print(f"唯一 opcode: {len(unique)} 个: {unique}")

# 2. 分类每个 opcode
for op in unique:
    idx = s.find(f'case {op}:')
    snippet = s[idx:idx+200]
    if 'd[7]=' in snippet:
        op_type = 'BRANCH'
    elif 'return' in snippet:
        op_type = 'RETURN'
    elif 'W(C[' in snippet:
        op_type = 'CALL'
    elif 'new' in snippet:
        op_type = 'ALLOC'
    elif 'try' in snippet or 'catch' in snippet:
        op_type = 'EXCEPTION'
    else:
        op_type = 'ARITH/STORE'
    print(f"  opcode {op:2d}: {op_type}")
```

### Phase 4: Constant Table Analysis (30 min)

```python
const_refs = re.findall(r'C\[9\]\[(\d+)\]', s)
unique_refs = sorted(set(int(x) for x in const_refs))

print(f"C[9] 引用: {len(unique_refs)} 个索引")
print(f"范围: {min(unique_refs)} - {max(unique_refs)}")

# 对每个引用分析上下文
for ref in unique_refs[:20]:
    idx = s.find(f'C[9][{ref}]')
    ctx = s[max(0,idx-50):idx+80]
    clean = ''.join(c if c.isprintable() else ' ' for c in ctx)
    print(f"  C[9][{ref}] → {clean}")
```

### Phase 5: Exported Function Tracing (1-2 hours)

Exported functions (e.g. `getToken`) are located via the following path:

```
1. 找 AWSCInner.register() 或类似注册调用
2. 确定注册的模块和工厂函数
3. 找工厂函数返回的对象 → 导出函数定义位置
4. 若函数名不在 JS 中 → 在 C[9] 常量表中作字节码存储
5. 追踪调用链:
   AWSCInner._modules['fy'].getToken()
   → W(C[函数索引], null, ...)
   → DG() 解释器执行编码后的指令序列
```

### Phase 6: Runtime Injection (if pure static analysis isn't enough)

```javascript
// 注入最小 AWSC 兼容环境
const fakeEnv = {
    AWSCInner: {
        _modules: {},
        register(name, moduleName, factory) {
            this._modules[moduleName] = factory();
        }
    }
};

// 执行 DSL VM 代码
dslVmCode();

// 获取导出
const token = fakeEnv.AWSCInner._modules['fy'].getToken({});
```

---

## 4. Opcode Extraction and Classification

### Reference Opcode Table (based on existing cases)

| Opcode | Operation type | Signature |
|--------|---------|------|
| 0 | **BRANCH** | `d[7]=xxx` unconditional jump |
| 1 | **CALL** | `W(C[Y],null,function(){...})` embedded function call |
| 2 | **ARITH** | `d[4]=0`, `d[7]=72` variable assignment |
| 3 | **ARITH** | `d[0]=d[1][C[x]]`, `d[5]=d[0]<d[3]` comparison operations |
| 4 | **STORE** | `d[8]=d[5]in d[4]` property access / existence check |
| 5 | **ARITH** | `d[8]=d[4]-d[8]` arithmetic operations |
| 6 | **RETURN** | `return gV`, `throw` return / throw exception |
| 7 | **ALLOC** | `d[6]=[]`, `d[6][C[8]](...)` push operation |
| 8 | **BRANCH** | `d[7]=d[k]?512:425` conditional jump |
| 9 | **STRING** | `d[6][C[t]]=d[m]`, `new fh(...)` regex |
| 10 | **ALLOC** | function-argument preparation, call-stack creation |
| 11 | **STRING** | `new fh("\\s",d[5])` regex matching |
| 12 | **STORE** | `P[d[9]]=d[4][C[H]](d[3])` data passing |
| 13 | **CALL** | `C[9][113]=d[9]` module initialization |
| 14 | **STRING** | `d[8]=d[9]+d[m]` string concatenation |
| 15 | **RETURN** | `return EL;` function return |
| 16 | **ALLOC** | `var r,P,Z,B...` local variable declarations |
| 17 | **ALLOC** | `(Z=[])[C[8]](69,T,445)` static array initialization |
| 18 | **TABLE** | function table / type table initialization |
| 19 | **EXCEPTION** | `try{for(var RK=x;...` try-catch loop |
| 20 | **DOM** | `Is[d[o]]` DOM operations |
| 21 | **STORE** | safely get global/object properties |
| 22 | **STRING** | `new fh(r,v)` string/regex handling |
| 23 | **BRANCH** | `try...catch` safe retrieval + conditional jump |
| 24 | **CALL** | `W(C[2],null,8,z,FL)` multi-argument function call |
| 25 | **EXCEPTION** | `try{...}catch(C){...}` exception catching + jump |

---

## 5. Runtime Capture Approaches

### Approach A: Selenium + native CDP events (recommended, highest success rate)

```python
from selenium import webdriver

driver = webdriver.Chrome()

# 注入反检测
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": r"""
        Object.defineProperty(navigator, 'webdriver', {get: () => false});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN','zh','en']});
    """
})

# 发送 CDP 原生鼠标事件
driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
    "type": "mousePressed",
    "x": 549.5, "y": 441.2,
    "button": "left", "buttons": 1,
    "clickCount": 1, "pointerType": "mouse"
})
```

### Approach B: Playwright headless browser

```javascript
const { chromium } = require('playwright');

async function run() {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // 拦截网络请求
    await page.route('**/api/**', async route => {
        await route.continue_();
    });

    await page.goto('https://target-page.com');

    // 等待 DSL VM 初始化
    await page.waitForFunction(() => {
        return window.AWSCInner &&
               window.AWSCInner._modules &&
               window.AWSCInner._modules['fy'];
    });

    // 执行操作
    await page.mouse.move(500, 400);
    await page.mouse.down();
    // ... 操作序列
    await page.mouse.up();
}
```

### Approach C: Pure protocol verification (very low success rate)

> Tokens generated by the DSL VM are usually strongly bound to the browser context (TLS JA3 fingerprint, IP, cookies, request headers, etc.); outside the browser the server can detect the context mismatch. **Pure protocol approaches are not recommended.**

---

## 6. Common Status Codes

| Code | Meaning | Handling |
|------|------|------|
| 0 | **Verification passed** ✅ | Extract sessionId + sig |
| 300 | **Risk-control block** | Blocked; cannot pass |
| 8778 | **Verification failed, retry needed** | Retry the operation |
| 8776 | **Operation too fast, retry needed** | Retry after adding delay |
| 69634 | **Generic failure** | Check whether the parameters are correct |

---

## 7. Skill Self-Check Checklist

- [ ] Did I complete DSL VM identification (IIFE + single-letter variables + DG() interpreter)?
- [ ] Did I extract the variable mapping table (`var X=<number>`)?
- [ ] Did I extract and classify the opcode list?
- [ ] Did I analyze the reference range of the constant table C[9]?
- [ ] Did I locate the exported-function registration point?
- [ ] When pure static analysis wasn't enough, did I try runtime injection?
- [ ] Did I write back to field-journal after the task?
- [ ] Did I find new tools/scenarios → update routing.md?

---

## Routing Registration

| Type | Route |
|------|------|
| **Target type**: WASM / DSL VM / custom instruction set | `reverse-engineering/dsl-vm-reverse/SKILL.md` |
| **User intent**: "DSL VM / risk-control engine reverse engineering" | this skill |
| **Toolchain**: Playwright / Selenium CDP | browser injection approach |

### Path Crossings

```
DSL VM 逆向路径:
  reverse-engineering/dsl-vm-reverse/ → Phase 1-6 工作流
  ↓ 若需要捕获运行时数据
  browser-automation/ → Playwright/Selenium CDP
  ↓ 若需要分析 API 协议层
  js-reverse/ → Observe→Capture→Rebuild
```
