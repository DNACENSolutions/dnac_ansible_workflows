const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
const start = html.indexOf('    async function rerunHistoryPlay(');
const body = html.slice(start, html.indexOf('\n    }', start) + 6);
assert.ok(!body.includes('confirm('));
assert.ok(!body.includes('switchTab('));
assert.ok(!body.includes('populateRunPlanFromSuite'));
assert.ok(!body.includes('saved-suites'));
const factory = new Function('fetchJson', 'refreshHistory', 'refreshDashboardCards', 'showToast', 'document',
  'const pendingHistoryReruns = new Set(); ' + body + '; return rerunHistoryPlay;');
(async () => {
  let calls = [], refreshed = 0, toast, release;
  const button = {dataset: {rerunJob: 'abcdef01'}, disabled: false};
  const rerun = factory(async (url, options) => {
    calls.push([url, options.method]);
    await new Promise(resolve => release = resolve);
    return {job_id: 'abcdef02'};
  }, async () => refreshed++, status => assert.equal(status, 'running'),
  message => toast = message, {querySelectorAll: () => [button]});
  const first = rerun('abcdef01');
  assert.equal(button.disabled, true);
  await rerun('abcdef01');
  assert.equal(calls.length, 1);
  release();
  await first;
  assert.deepEqual(calls, [['/api/jobs/abcdef01/rerun', 'POST']]);
  assert.equal(refreshed, 1);
  assert.match(toast, /Retry started/);
  assert.equal(button.disabled, false);
  const fail = factory(async () => {throw Error('Saved controller no longer exists');},
    async () => assert.fail('Do not report successful launch'), () => {}, message => toast = message,
    {querySelectorAll: () => [button]});
  await fail('abcdef01');
  assert.equal(toast, 'Saved controller no longer exists');
  assert.equal(button.disabled, false);
  console.log('PASS: one-click POST, no navigation/save/confirmation, double-click prevention, error recovery');
})().catch(error => {console.error(error); process.exitCode = 1;});
