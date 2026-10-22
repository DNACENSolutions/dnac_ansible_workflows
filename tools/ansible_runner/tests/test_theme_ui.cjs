const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/theme.js'), 'utf8');
function start(saved, blocked = false) {
  const events = {}, buttons = [{
    attrs: {},
    setAttribute(k, v) { this.attrs[k] = v; },
    addEventListener(k, callback) { this[k] = callback; },
  }];
  const document = {documentElement: {dataset: {}}, querySelectorAll: () => buttons,
    addEventListener: (event, callback) => { events[event] = callback; }};
  const context = {document, localStorage: {
    getItem() { if (blocked) throw Error('blocked'); return saved; },
    setItem(k, value) { if (blocked) throw Error('blocked'); saved = value; },
  }, window: {addEventListener: (event, callback) => { events[event] = callback; }}};
  vm.runInNewContext(source, context);
  events.DOMContentLoaded();
  return {document, buttons, events, saved: () => saved};
}
const light = start(null);
assert.equal(light.document.documentElement.dataset.theme, 'light');
light.buttons[0].click();
assert.equal(light.saved(), 'dark');
assert.equal(light.buttons[0].attrs['aria-pressed'], 'true');
assert.equal(light.buttons[0].attrs['aria-label'], 'Switch to light theme');
assert.equal(start(light.saved()).document.documentElement.dataset.theme, 'dark');
light.buttons[0].click();
assert.equal(light.saved(), 'light');
assert.equal(light.buttons[0].attrs.title, 'Switch to dark theme');
light.events.storage({key: 'runner-theme', newValue: 'dark'});
assert.equal(light.document.documentElement.dataset.theme, 'dark');
light.events.storage({key: 'runner-theme', newValue: 'invalid'});
assert.equal(light.document.documentElement.dataset.theme, 'light');
const blocked = start(null, true);
blocked.buttons[0].click();
assert.equal(blocked.document.documentElement.dataset.theme, 'dark');
console.log('PASS: light/dark selection, persistence, cross-tab sync and blocked storage');
