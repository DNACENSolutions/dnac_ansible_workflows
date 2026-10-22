const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
for (const [, source] of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
  new Function(source);
}

function sourceFor(name) {
  let start = html.indexOf('    function ' + name + '(');
  if (start < 0) start = html.indexOf('    async function ' + name + '(');
  assert(start >= 0, name);
  return html.slice(start, html.indexOf('\n    }', start) + 6);
}

const row = { dataset: { planRow: '1' } };
const values = { workflow: 'provision', playbook: 'provision.yml', vars: 'combined.yml', inventory: '', repo: 'local' };
const elements = {};
const requests = [];
let editorContent = '';
const context = {
  URLSearchParams,
  document: { activeElement: null },
  $: id => elements[id] ||= { dataset: {}, textContent: '', scrollIntoView() {} },
  alert: message => assert.fail(message),
  htmlEscape: value => String(value || ''),
  fileOptionLabel: value => value,
  targetInputClass: () => '',
  suiteRunTarget: () => ({password: 'test-only'}),
  suiteRunRepoReady: () => true,
  activeRunPlanRow: () => row,
  runPlanRows: () => [row],
  runPlanRowValues: () => values,
  setActiveRunPlanRow() {},
  runPlanVarsSourcePayload: () => ({ kind: 'local' }),
  runPlanSchemaStatus: () => 'Ready for schema',
  runWorkflows: () => [{ name: 'provision', schemas: ['schema.yml'] }],
  basename: value => value,
  matchingSchemaForPlaybook: () => 'schema.yml',
  schemaOptionValue: () => 'schema.yml',
  updateRunPlanRow() {},
  moveEditorToAnchor() {},
  show() {}, hide() {}, showToast() {},
  setTimeout: fn => fn(),
  editorVarsSourcePayload: () => ({ kind: 'local' }),
  editor: { setValue: value => editorContent = value, getValue: () => editorContent, refresh() {} },
  async fetchJson(url, options) {
    requests.push({ url, body: options && JSON.parse(options.body) });
    if (url.startsWith('/api/file?')) return { path: values.vars, content: 'inventory:\n  all:\n    hosts:\n      catc: {}\nprovision_details: []\n' };
    return { ok: true, out: 'Validation completed' };
  },
};
vm.createContext(context);
for (const name of ['suiteCanRun', 'runPlanSelectHtml', 'sourceQueryParamsForSource',
  'loadRunPlanVarsFile', 'validateRunPlanRowSchema', 'saveFile']) {
  vm.runInContext(sourceFor(name), context);
}

(async () => {
  assert(context.suiteCanRun({ runs: [values] }));
  assert(!context.suiteCanRun({ runs: [{ ...values, vars: '' }] }));
  assert(context.suiteCanRun({ runs: [{ ...values, inventory: 'hosts.yml' }] }));
  assert(context.runPlanSelectHtml('inventory', [], 'Select inventory', '').includes('From vars file'));
  await context.loadRunPlanVarsFile();
  assert(editorContent.includes('inventory:'));
  assert.equal(elements['editor-path'].textContent, 'combined.yml');
  editorContent += '# edited\n';
  await context.saveFile();
  const save = requests.find(request => request.body && request.body.content);
  assert.equal(save.body.path, 'combined.yml');
  assert(save.body.content.endsWith('# edited\n'));
  assert(await context.validateRunPlanRowSchema(row));
  let validation = requests.at(-1).body;
  assert.equal(validation.data, 'combined.yml');
  assert.equal(validation.require_embedded_inventory, true);
  values.inventory = 'hosts.yml';
  assert(await context.validateRunPlanRowSchema(row));
  validation = requests.at(-1).body;
  assert.equal(validation.require_embedded_inventory, false);
  console.log('PASS: JavaScript syntax, both suite inputs, Customize/Save, Validate with and without separate inventory');
})().catch(error => { console.error(error); process.exitCode = 1; });
