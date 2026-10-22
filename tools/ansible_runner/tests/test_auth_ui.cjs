const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../static/auth.js'), 'utf8');
(async () => {
  let sent, redirected;
  const context = {Headers, window: {location: {assign: url => { redirected = url; }}},
    document: {querySelector: selector => ({content: selector.includes('runner-role') ? 'operator' : 'csrf-token'})},
    fetch: async (url, options) => {sent = options; return {status: 401};}};
  vm.runInNewContext(source, context);
  await context.window.runnerFetch('/api/run', {method: 'POST', headers: {'Content-Type': 'application/json'}});
  assert.equal(context.window.runnerRole, 'operator');
  assert.equal(sent.headers.get('X-CSRF-Token'), 'csrf-token');
  assert.equal(sent.headers.get('Content-Type'), 'application/json');
  assert.equal(sent.credentials, 'same-origin');
  assert.equal(redirected, '/login');
  console.log('PASS: CSRF header, existing headers, session credentials and sign-in redirect');
})().catch(error => {console.error(error); process.exitCode = 1;});
