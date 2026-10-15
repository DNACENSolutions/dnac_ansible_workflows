const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
function sourceFor(name) {
  let start = html.indexOf('    function ' + name + '(');
  if (start < 0) start = html.indexOf('    async function ' + name + '(');
  assert(start >= 0, name);
  return html.slice(start, html.indexOf('\n    }', start) + 6);
}
const elements = {};
const rows = [{ id: 1 }, { id: 2 }];
const values = { vars: 'data.yml', repo: 'repo_other', target: 'catc' };
const requests = [], callbacks = [], statuses = [], visible = new Set();
let gate;
const context = {
  activeRunPlan: null, fileDirty: false, URLSearchParams,
  $: id => elements[id] ||= { value: '', dataset: {}, textContent: '', innerHTML: '' },
  runPlanRows: () => rows,
  runPlanRowValues: () => values,
  runPlanVarsSourcePayload: () => ({ kind: 'git', id: values.repo }),
  gitRepositories: [],
  validateRunPlanRows: async () => !context.runPlanHasUnsavedInputs(),
  runPlanStatus: () => 'Ready',
  catcTargetForPlanValue: () => null, runtimePayload: () => ({}),
  show: id => visible.add(id), hide: id => visible.delete(id),
  showToast() {}, refreshRunSummary() {}, closeBatchStreams() {},
  appendLine() {}, refreshDashboardCards() {}, refreshHistory() {},
  clearRunOutputPanel() {}, showLaunchAssurancePrompt() {},
  updateRunStatus: status => statuses.push(status),
  streamBatchJob: (job, output, done) => callbacks.push(done),
  currentBatchJobIds: [], editor: { getValue: () => 'edited: true' },
  alert: message => assert.fail(message),
  async fetchJson(url, options) {
    requests.push({ url, body: options && options.body && JSON.parse(options.body) });
    if (gate && url === '/api/run') await gate;
    return { job_id: 'id-' + requests.length, command: 'ansible-playbook' };
  },
};
vm.createContext(context);
for (const name of ['runPlanHasUnsavedInputs', 'runSelectedPlanRows', 'stopRunPlan',
  'editorVarsSourcePayload', 'saveFile', 'cancelHistorySuite']) {
  vm.runInContext(sourceFor(name), context);
}
(async () => {
  elements['editor-section'] = { dataset: { varsPath: 'data.yml', varsSource: 'repo_other' } };
  elements['editor-path'] = { textContent: 'data.yml' };
  context.fileDirty = true;
  assert(context.runPlanHasUnsavedInputs());
  await context.runSelectedPlanRows();
  assert.equal(requests.length, 0, 'dirty inputs must not launch');
  elements['editor-section'].dataset.varsSource = 'repo_unrelated';
  assert(!context.runPlanHasUnsavedInputs(), 'same path in a different repo is not dirty for this plan');
  elements['editor-section'].dataset.varsSource = 'repo_other';
  await context.saveFile();
  assert.equal(requests[0].body.source.id, 'repo_other', 'save must not depend on legacy active repo');
  assert.equal(context.fileDirty, false);
  requests.length = 0;
  await context.runSelectedPlanRows();
  assert(visible.has('btn-stop-plan'));
  callbacks.shift()('random-job-id', 'completed');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests.filter(r => r.url === '/api/run').length, 2);
  callbacks.shift()('another-job-id', 'completed');
  assert.equal(statuses.at(-1), 'completed', 'callback must use status, not job ID');
  assert(!visible.has('btn-stop-plan'));

  // Editing while an asynchronous validation is running must also block launch.
  requests.length = 0;
  context.validateRunPlanRows = async () => { context.fileDirty = true; return true; };
  await context.runSelectedPlanRows();
  assert.equal(requests.length, 0);
  context.fileDirty = false;
  context.validateRunPlanRows = async () => true;

  // Stop while submission is in flight; no later row may be submitted.
  requests.length = 0;
  let release;
  gate = new Promise(resolve => release = resolve);
  const launch = context.runSelectedPlanRows();
  await new Promise(resolve => setImmediate(resolve));
  await context.stopRunPlan();
  release();
  await launch;
  callbacks.shift()('late-job', 'cancelled');
  assert.equal(requests.filter(r => r.url === '/api/run').length, 1);
  assert(requests.some(r => r.url.endsWith('/cancel')));
  assert.equal(statuses.at(-1), 'cancelled');
  assert(!visible.has('btn-stop-plan'));
  assert.equal(context.activeRunPlan, null);

  const sources = [];
  context.batchEventSources = [];
  context.EventSource = function() { this.close = () => {}; sources.push(this); };
  vm.runInContext(sourceFor('streamBatchJob'), context);
  let completions = 0;
  context.streamBatchJob({ job_id: 'once', label: 'test' }, {}, () => completions++);
  sources[0].onmessage({ data: JSON.stringify({ t: 'd', s: 'completed' }) });
  sources[0].onerror();
  sources[0].onmessage({ data: JSON.stringify({ t: 'd', s: 'completed' }) });
  assert.equal(completions, 1, 'duplicate stream events must not advance the queue twice');
  console.log('PASS: correct repo Save, dirty launch guard, completion status, visible Stop suite, in-flight cancellation');
})().catch(error => { console.error(error); process.exitCode = 1; });
