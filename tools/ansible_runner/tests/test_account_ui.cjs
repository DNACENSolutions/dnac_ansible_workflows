const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const events = {};
let closed = 0, focused = 0;
const menu = {contains: target => target === 'inside', removeAttribute: key => {assert.equal(key, 'open'); closed++;},
  querySelector: () => ({focus: () => focused++})};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/account.js'), 'utf8'), {
  document: {addEventListener: (event, handler) => events[event] = handler, querySelectorAll: () => [menu]},
});
events.click({target: 'inside'});
assert.equal(closed, 0);
events.click({target: 'outside'});
assert.equal(closed, 1);
events.keydown({key: 'Escape'});
assert.equal(closed, 2);
assert.equal(focused, 1);
console.log('PASS: account click-away, Escape dismissal and restored keyboard focus');
