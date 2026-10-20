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
  const records = [{id: 'repo_one', source: {kind: 'git', id: 'repo_one', repo_url: 'https://github.com/example/inputs.git', ref: 'main'}, vars: ['data.yml'], inventories: []}];
  const context = {JSON, GIT_SOURCE_STORAGE_KEY: 'catalog', gitRepositories: [], gitSource: null, gitVars: [], gitInventories: [],
    localStorage: {removeItem() {}}, sessionStorage: {getItem: () => '{"active_id":"repo_one"}', removeItem() {}, setItem: (key, value) => {context.stored = JSON.parse(value);}},
    fetchJson: async url => {assert.equal(url, '/api/git/repositories'); return records;},
    updateGitRepositoryView() {}, refreshInputRepoOptions() {}, renderAutomationSuites() {}, setGitStatus() {}};
  vm.createContext(context);
  for (const name of ['persistGitRepository', 'restoreGitRepository']) vm.runInContext(sourceFor(name), context);
  await context.restoreGitRepository();
  assert.equal(context.gitRepositories.length, 1);
  assert.equal(context.gitSource.id, 'repo_one');
  assert.deepEqual(JSON.parse(JSON.stringify(context.stored)), {active_id: 'repo_one'});
  // A new user has no browser state but still receives the shared catalog.
  context.gitSource = null;
  context.sessionStorage.getItem = () => null;
  await context.restoreGitRepository();
  assert.equal(context.gitRepositories.length, 1);
  assert.equal(context.gitSource, null);
  context.fetchJson = async () => {throw Error('Storage unavailable');};
  await assert.rejects(context.restoreGitRepository());
  assert.equal(context.gitRepositories.length, 0);
  assert.equal(context.gitSource, null);
  assert(html.includes('refresh: !!preserveInputs'));
  assert(sourceFor('removeGitRepository').includes("{method: 'DELETE'}"));
  console.log('PASS: shared repository reload, independent selection, metadata-only browser state and fail-closed catalog');
})().catch(error => {console.error(error); process.exitCode = 1;});
