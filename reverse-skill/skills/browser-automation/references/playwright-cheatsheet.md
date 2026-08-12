# Browser and Desktop Automation Cheatsheet

> Covers common commands and patterns for Playwright (browser automation) and OpenReverse (Windows desktop automation).
> For penetration testing, reverse engineering, and automated collection scenarios.

---

## Playwright / agent-browser Command Cheatsheet

### Navigation and Lifecycle

```bash
# open a page
agent-browser open "https://target.com/login"

# wait for the page to finish loading
agent-browser wait --load networkidle

# close the browser (mandatory, otherwise the process leaks)
agent-browser close
```

### Page Snapshots

```bash
# full accessibility tree (for debugging)
agent-browser snapshot

# interactive elements only (recommended, returns @e1, @e2... refs)
agent-browser snapshot -i
```

### Element Interaction

```bash
# click
agent-browser click @e1

# fill a text field
agent-browser fill @e2 "admin"

# type character by character (for inputs with JS listeners)
agent-browser type @e2 "password123"

# keys
agent-browser press Enter
agent-browser press Tab
agent-browser press Escape

# scrolling
agent-browser scroll down 500
agent-browser scroll up 300
```

### Getting Information

```bash
# get element text
agent-browser get text @e1

# get page title
agent-browser get title

# get current URL
agent-browser get url
```

### Wait Strategies

```bash
# wait for an element to appear
agent-browser wait @e1

# wait a fixed time (milliseconds)
agent-browser wait 2000

# wait for network idle
agent-browser wait --load networkidle

# wait for navigation to complete
agent-browser wait --load domcontentloaded
```

---

## Common Pentest Patterns

### Automated Login

```bash
agent-browser open "https://target.com/login"
agent-browser snapshot -i
agent-browser fill @username "admin"
agent-browser fill @password "password123"
agent-browser click @login_button
agent-browser wait --load networkidle
agent-browser get url                    # confirm whether it redirected to the backend
```

### XSS Payload Injection

```bash
agent-browser open "https://target.com/search"
agent-browser snapshot -i
agent-browser fill @search_input "<script>alert(1)</script>"
agent-browser click @search_button
agent-browser wait --load networkidle
agent-browser snapshot                   # check whether the payload was rendered
```

### Batch Form Submission (with a script)

```powershell
$payloads = @("' OR 1=1--", "<img src=x onerror=alert(1)>", "{{7*7}}")
foreach ($p in $payloads) {
    agent-browser open "https://target.com/form"
    agent-browser snapshot -i
    agent-browser fill @input "$p"
    agent-browser click @submit
    agent-browser wait --load networkidle
    agent-browser snapshot              # check the response
}
agent-browser close
```

### Cookie / LocalStorage Extraction

```bash
# via the Playwright API (Node.js script mode)
# agent-browser does not expose cookies directly; use script mode
```

```javascript
// playwright-extract.js
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto('https://target.com');
    
    // extract cookies
    const cookies = await context.cookies();
    console.log(JSON.stringify(cookies, null, 2));
    
    // extract localStorage
    const storage = await page.evaluate(() => JSON.stringify(localStorage));
    console.log(storage);
    
    await browser.close();
})();
```

### Screenshot Evidence

```bash
# agent-browser mode
agent-browser open "https://target.com/admin"
agent-browser wait --load networkidle
# screenshot capability depends on the agent-browser version
```

```javascript
// playwright script mode
await page.screenshot({ path: 'evidence.png', fullPage: true });
```

---

## Playwright Node.js API Cheatsheet

### Basic Template

```javascript
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({
        headless: true,           // headless mode
        // proxy: { server: 'http://127.0.0.1:8080' }  // route through Burp proxy
    });
    const context = await browser.newContext({
        ignoreHTTPSErrors: true,  // ignore certificate errors
        userAgent: 'Mozilla/5.0 ...',
    });
    const page = await context.newPage();
    
    await page.goto('https://target.com');
    // ... operations ...
    
    await browser.close();
})();
```

### Common Selectors

```javascript
// CSS selectors
await page.click('#login-btn');
await page.fill('input[name="username"]', 'admin');

// text selectors
await page.click('text=Submit');
await page.click('button:has-text("Login")');

// XPath
await page.click('xpath=//button[@type="submit"]');

// chaining
await page.click('form >> input[type="submit"]');
```

### Network Interception

```javascript
// intercept requests
await page.route('**/api/**', route => {
    console.log('API call:', route.request().url());
    route.continue();
});

// modify requests
await page.route('**/api/auth', route => {
    route.continue({
        headers: { ...route.request().headers(), 'X-Admin': 'true' }
    });
});

// intercept responses
await page.route('**/api/user', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.role = 'admin';  // tamper with the response
    route.fulfill({ response, json });
});
```

### Waiting and Assertions

```javascript
// wait for an element
await page.waitForSelector('#result');
await page.waitForSelector('.error', { state: 'visible' });

// wait for a network request
const [response] = await Promise.all([
    page.waitForResponse('**/api/login'),
    page.click('#login-btn'),
]);
console.log(response.status(), await response.json());

// wait for navigation
await Promise.all([
    page.waitForNavigation(),
    page.click('a[href="/admin"]'),
]);
```

---

## OpenReverse Desktop Automation Cheatsheet

### Mode Selection

| Mode | Command prefix | Best for |
|------|---------|---------|
| UIA | `openreverse uia ...` | Standard Windows controls (buttons, text fields, lists) |
| CUA | `openreverse cua ...` | Complex/non-standard GUIs (IDA disassembly views, custom-rendered UIs) |

### UIA Mode (structured control operations)

```bash
# launch an app
openreverse uia launch "C:\Tools\x64dbg\x64dbg.exe"

# get the window tree
openreverse uia tree

# click a button
openreverse uia click "Button:Open"

# fill a text field
openreverse uia fill "Edit:FilePath" "C:\sample.exe"

# select a menu
openreverse uia menu "File > Open"

# get control text
openreverse uia get-text "Edit:Output"
```

### CUA Mode (vision-driven interaction)

```bash
# screenshot the current screen
openreverse cua screenshot

# click screen coordinates
openreverse cua click 500 300

# double-click
openreverse cua dblclick 500 300

# type text
openreverse cua type "search string"

# keys
openreverse cua key "ctrl+g"    # IDA: Go to address
openreverse cua key "F5"        # IDA: Decompile
openreverse cua key "F9"        # x64dbg: Run
```

### Network Observation (mitmproxy)

```bash
# start proxy mode for observation
openreverse network start --mode proxy --port 8888

# start local capture mode
openreverse network start --mode local --filter "target.exe"

# get captured requests
openreverse network list

# export as HAR
openreverse network export har output.har

# stop observation
openreverse network stop
```

---

## Reverse Tool Automation Combos

### IDA Pro Automation (OpenReverse + ida-reverse)

```text
Scenario: batch analysis of multiple samples

1. openreverse cua launch "ida64.exe"
2. For each sample:
   a. openreverse cua key "ctrl+o"        # open file dialog
   b. openreverse uia fill "Edit:FileName" "sample_N.exe"
   c. openreverse uia click "Button:Open"
   d. wait for analysis to finish (poll the IDA title bar)
   e. extract results via the ida-reverse MCP tools
   f. openreverse cua key "ctrl+w"        # close the database
```

### x64dbg Automated Debugging

```text
Scenario: automated breakpoint setting and data collection

1. openreverse uia launch "x64dbg.exe"
2. openreverse cua key "F3"               # open file
3. openreverse uia fill "Edit:FileName" "target.exe"
4. openreverse uia click "Button:Open"
5. openreverse cua key "ctrl+g"           # Go to address
6. openreverse cua type "0x401000"
7. openreverse cua key "F2"               # set breakpoint
8. openreverse cua key "F9"               # run
9. openreverse cua screenshot             # screenshot to save state
```

---

## Common Problems and Solutions

| Problem | Cause | Solution |
|------|------|------|
| agent-browser unresponsive | process leak | `agent-browser close` first, then open again |
| Element refs invalid | page refreshed | re-run `snapshot -i` for new refs |
| Form fill ineffective | JS listens to input events | use `type` instead of `fill` |
| HTTPS certificate error | self-signed cert | Playwright: `ignoreHTTPSErrors: true` |
| Page load timeout | slow network/many resources | increase timeout or use `domcontentloaded` |
| UIA can't find controls | app uses custom-drawn controls | switch to CUA mode |
| CUA click offset | resolution/DPI mismatch | screenshot first to confirm coordinates |

---

## Installation and Dependencies

### Playwright

```powershell
# install Node.js (if not present)
winget install OpenJS.NodeJS.LTS

# install Playwright
npm install -g playwright
npx playwright install          # download browser engines

# install the agent-browser CLI
npm install -g agent-browser
```

### OpenReverse

```powershell
git clone https://github.com/zhexulong/openreverse.git
cd openreverse
npm install
npm run init:agents -- --target=all <project path>

# optional: CUA runtime
npm run install:cua-runtime
npm run doctor:cua-runtime

# optional: network observation
npm run install:mitmproxy
npm run doctor:network
```

---

## Related Resources

| Resource | Description | Link |
|------|------|------|
| Playwright official docs | API reference | https://playwright.dev/docs/intro |
| OpenReverse | desktop automation framework | https://github.com/zhexulong/openreverse |
| mitmproxy | HTTP/HTTPS proxy | https://mitmproxy.org/ |
| Windows UI Automation | UIA docs | https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32 |

