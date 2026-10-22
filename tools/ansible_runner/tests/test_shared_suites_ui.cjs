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
(async () => {
  const context = {JSON, sharedAutomationSuites: [], AUTOMATION_SUITES_STORAGE_KEY: 'old',
    localStorage: {getItem: () => '[{"id":"browser-one","name":"Demo","runs":[{"target_details":{"password":"secret"}}]}]',
      setItem: (key, value) => {context.remaining = value;}},
    confirm: () => true, $: () => ({textContent: ''}), renderAutomationSuites() {}, showToast() {},
    fetchJson: async (url, options) => {
      context.requests.push({url, options});
      return options ? {id: 'shared-one'} : [{id: 'shared-one', name: 'Demo', runs: []}];
    }, requests: []};
  vm.createContext(context);
  for (const name of ['loadAutomationSuites', 'safeSuiteRuns', 'refreshSharedAutomationSuites', 'importBrowserAutomationSuites']) {
    vm.runInContext(sourceFor(name), context);
  }
  const cleaned = context.safeSuiteRuns([{name: 'Play', password: 'secret', target_details: {name: 'CatC', password: 'secret'},
    repo_details: {password: 'secret', source: {id: 'repo-one', token: 'secret'}}}]);
  assert(!JSON.stringify(cleaned).includes('secret'));
  await context.refreshSharedAutomationSuites();
  assert.equal(context.loadAutomationSuites()[0].id, 'shared-one');
  await context.importBrowserAutomationSuites();
  const imported = context.requests.find(item => item.options);
  assert.equal(imported.url, '/api/saved-suites');
  assert.equal(JSON.parse(imported.options.body).legacy_id, 'browser-one');
  assert(!imported.options.body.includes('secret'));
  assert.equal(context.remaining, '[]');
  context.fetchJson = async () => {throw Error('Storage unavailable');};
  await assert.rejects(context.refreshSharedAutomationSuites());
  assert.equal(context.loadAutomationSuites().length, 0);
  console.log('PASS: server cache, password-free import, migration cleanup and no browser fallback on server failure');
})().catch(error => {console.error(error); process.exitCode = 1;});
