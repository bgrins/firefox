const fs = require('fs');
const vm = require('vm');
const path = require('path');
const source = fs.readFileSync(path.join(__dirname, 'proposed-test.html'), 'utf8');
const scripts = [...source.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw Error('script identity');
const records = [];
for (const mode of ['supported-fixed', 'supported-before', 'unsupported-large']) {
  const statuses = { PASS: 0, FAIL: 0, PRECONDITION_FAILED: 0 };
  let finalChecks = 0;
  class OptionalFeatureUnsupportedError extends Error {}
  const context = {
    test(callback) {
      try { callback({ add_cleanup() {} }); statuses.PASS++; }
      catch (error) {
        if (error instanceof OptionalFeatureUnsupportedError) statuses.PRECONDITION_FAILED++;
        else if (error.message === 'final-height') statuses.FAIL++;
        else throw error;
      }
    },
    assert_implements_optional(condition, description) {
      if (!condition) throw new OptionalFeatureUnsupportedError(description);
    },
    assert_equals(actual, expected, description) {
      if (description.startsWith('baseline cross-size')) finalChecks++;
      if (actual !== expected) throw Error(description.startsWith('baseline cross-size') ? 'final-height' : description);
    },
    document: {
      body: { append() {} },
      createElement() {
        const host = {
          style: { setProperty(name, value) { this[name] = value; } },
          remove() {},
          getBoundingClientRect() {
            const size = parseFloat(this.style['--size']);
            return { width: 20, height: mode === 'supported-before' && size >= 12000000 && this.style.alignItems !== 'flex-start' ? 0 : 100 };
          },
        };
        host.children = [0, 1].map(index => ({ host, index }));
        return host;
      },
    },
    getComputedStyle({ host, index }) {
      let size = parseFloat(host.style['--size']);
      if (mode === 'unsupported-large') size = Math.min(size, 1000000);
      return { height: `${size}px`, marginTop: `${index ? size : -size}px`, marginBottom: `${index ? -size : size}px` };
    },
  };
  vm.runInNewContext(scripts[0][1], context);
  const expected = mode === 'supported-fixed' ? [54,0,0,54] : mode === 'supported-before' ? [42,12,0,54] : [12,0,42,12];
  if (JSON.stringify([...Object.values(statuses),finalChecks]) !== JSON.stringify(expected)) throw Error(mode);
  records.push({ mode, statuses, finalChecks });
}
console.log(JSON.stringify({ scope: 'Control flow only; no browser layout simulation claim', records }, null, 2));
