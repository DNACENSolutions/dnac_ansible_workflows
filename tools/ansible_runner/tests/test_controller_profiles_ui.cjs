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
  const profile = {profile_id: 'a'.repeat(32), name: 'Lab', host: 'catc.example.test', username: 'demo', verify: 'true', credential_saved: true};
  const fields = Object.fromEntries(Object.entries({...profile, password: 'test-only-credential'}).map(([key, value]) => [key, {value}]));
  const row = {dataset: {}, querySelector(selector) {
    const match = /data-target-field="([^"]+)"/.exec(selector);
    return fields[match[1]];
  }};
  const context = {JSON, confirm: () => true, savedControllerProfiles: [], requests: [],
    refreshRunPlanRows() {}, refreshRunSummary() {}, renderAutomationSuites() {}, showToast() {},
    targetRows: () => [], selectedCatcTargetSnapshot: () => null,
    fetchJson: async (url, options) => {context.requests.push({url, options}); return profile;}};
  vm.createContext(context);
  for (const name of ['normalizeCatcTargetDetails', 'safeSuiteRuns', 'saveControllerProfile', 'catcTargetFingerprint', 'suiteRunTarget']) {
    vm.runInContext(sourceFor(name), context);
  }
  const button = {closest: () => row};
  await context.saveControllerProfile(button);
  assert.equal(button.disabled, false);
  assert.equal(row.dataset.profileId, profile.profile_id);
  assert.equal(fields.password.value, '');
  assert.equal(fields.password.placeholder, 'Credential saved');
  assert.equal(JSON.parse(context.requests[0].options.body).password, 'test-only-credential');
  const target = context.normalizeCatcTargetDetails(profile);
  assert.equal(target.credential_saved, true);
  const runs = context.safeSuiteRuns([{target_details: {...target, password: 'never-save-this'}}]);
  assert.equal(runs[0].target_details.profile_id, profile.profile_id);
  assert(!JSON.stringify(runs).includes('never-save-this'));
  // Simulate a new page with no active target rows: suite uses the server catalog.
  assert.equal(context.suiteRunTarget({target_details: runs[0].target_details}).credential_saved, true);
  context.savedControllerProfiles = [];
  assert(!context.suiteRunTarget({target_details: runs[0].target_details}).credential_saved);
  context.savedControllerProfiles = [profile];
  assert(!context.normalizeCatcTargetDetails({...profile, host: 'changed.example.test'}).credential_saved);
  assert(html.indexOf('await loadControllerProfiles()') < html.indexOf('await refreshSharedAutomationSuites().catch', html.indexOf("window.addEventListener('DOMContentLoaded'")));
  assert((html.match(/profile_id: target.profile_id \|\| ''/g) || []).length >= 2);
  console.log('PASS: saved profiles clear password, preserve references, restore suites and reject stale credentials');
})().catch(error => {console.error(error); process.exitCode = 1;});
