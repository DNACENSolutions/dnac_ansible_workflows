const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
function source(name) {
  const start = html.indexOf('    ' + name);
  assert.ok(start >= 0);
  return html.slice(start, html.indexOf('\n    }', start) + 6);
}
const build = new Function(source('function historyRerunSuite(') + '; return historyRerunSuite;')();
const job = {id: 'abcdef01', status: 'failed', can_delete: true, metadata: {
  suite_name: 'Refresh', workflow: 'edge', playbook: 'cleanup.yml', vars_file: 'vars.yml',
  inventory: 'hosts.yml', vars_source: {kind: 'git', id: 'repo_1'},
  inventory_source: {id: 'repo_1', kind: 'git'}, catalyst_connection_profile_id: 'profile-1',
  catalyst_connection_host: 'controller.test', catalyst_connection_username: 'admin',
  catalyst_connection_verify: 'true'}};
const suite = build(job, []);
assert.equal(suite.runs.length, 1);
assert.equal(suite.runs[0].playbook, 'cleanup.yml');
assert.equal(suite.runs[0].repo_details.source.id, 'repo_1');
assert.equal(suite.runs[0].target_details.profile_id, 'profile-1');
assert.equal(suite.runs[0].target_details.password, undefined);
for (const change of [{status: 'running'}, {status: 'completed'}, {can_delete: false}]) {
  assert.throws(() => build({...job, ...change}, []), /Only stopped failed/);
}
assert.throws(() => build({...job, metadata: {...job.metadata,
  inventory_source: {kind: 'git', id: 'different'}}}, []), /separate input repositories/);
const legacy = {...job, metadata: {...job.metadata}};
delete legacy.metadata.vars_source;
const saved = {name: 'Refresh', runs: [{workflow: 'edge', playbook: 'cleanup.yml',
  vars: 'vars.yml', inventory: 'hosts.yml', repo: 'repo_1'}]};
assert.equal(build(legacy, [saved]).runs.length, 1);
assert.throws(() => build(legacy, []), /older run/);
assert.throws(() => build(legacy, [saved, saved]), /older run/);
(async () => {
  let loaded, calls = [], toast, confirmed = true, active = 'original';
  const factory = new Function('window', 'fetchJson', 'loadAutomationSuites', 'historyRerunSuite',
    'populateRunPlanFromSuite', 'switchTab', 'showToast',
    'let activeSavedSuiteEdit = "original"; ' + source('async function rerunHistoryPlay(') +
    '; return {run: rerunHistoryPlay, edit: () => activeSavedSuiteEdit};');
  const instance = factory({confirm: () => confirmed}, async url => {
    calls.push(url);
    return url.startsWith('/api/jobs/') ? job : {vars: ['vars.yml'], inventories: ['hosts.yml']};
  }, () => [], build, value => loaded = value, tab => assert.equal(tab, 'run'), value => toast = value);
  await instance.run(job.id);
  assert.equal(loaded.runs.length, 1);
  assert.equal(instance.edit(), null);
  assert.deepEqual(calls, ['/api/jobs/abcdef01', '/api/git/catalog?source_id=repo_1']);
  assert.match(toast, /whole playbook/);
  confirmed = false;
  calls = [];
  await instance.run(job.id);
  assert.deepEqual(calls, []);
  console.log('PASS: failed-play review, single row, source/profile references, legacy ambiguity, permissions and no automatic launch');
})().catch(error => {console.error(error); process.exitCode = 1;});
