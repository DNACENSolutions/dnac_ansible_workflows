const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
const start = html.indexOf('    async function deleteHistory(');
const end = html.indexOf('\n    }', start) + '\n    }'.length;
const factory = new Function('window', 'fetchJson', 'refreshHistory', 'refreshDashboardCards', 'showToast',
  html.slice(start, end) + '; return deleteHistory;');
(async () => {
  let confirmed = false, calls = [], refreshed = 0, toast;
  const remove = factory({confirm: () => confirmed}, async (url, options) => calls.push([url, options.method]),
    async () => refreshed++, async () => refreshed++, message => toast = message);
  await remove('play', 'abcdef01');
  assert.equal(calls.length, 0);
  confirmed = true;
  await remove('play', 'abcdef01');
  assert.deepEqual(calls[0], ['/api/jobs/abcdef01', 'DELETE']);
  assert.equal(refreshed, 2);
  await remove('suite', 'suite-a');
  assert.deepEqual(calls[1], ['/api/suites/suite-a', 'DELETE']);
  const failing = factory({confirm: () => true}, async () => {throw Error('Forbidden');},
    async () => assert.fail('Must not report successful deletion'), async () => {}, message => toast = message);
  await failing('play', 'abcdef01');
  assert.equal(toast, 'Forbidden');
  assert.ok(html.includes('job.can_delete'));
  assert.ok(html.includes('Awaiting cleanup or permission'));
  assert.ok(html.includes('Deletion requires the run owner or an administrator, and all suite processes must have stopped.'));
  assert.ok(html.includes("job.status === 'interrupted'"));
  console.log('PASS: confirmation, play/suite DELETE, refreshed counts and permission errors');
})().catch(error => {console.error(error); process.exitCode = 1;});
