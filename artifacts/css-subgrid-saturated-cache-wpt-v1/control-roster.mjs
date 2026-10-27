import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const pins = JSON.parse(fs.readFileSync(path.join(here, 'CONTROL-PINS.json')));
const result = {};
for (const entry of pins.tests.filter(entry => entry.kind === 'testharness')) {
  const names = [];
  const context = vm.createContext({test: (_body, title) => names.push(title)});
  vm.runInContext(fs.readFileSync(path.join(here, 'controls/testing/web-platform/tests/css/support/parsing-testcommon.js'), 'utf8'), context);
  const html = fs.readFileSync(path.join(here, 'controls', entry.path), 'utf8');
  for (const script of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (!/\bsrc\s*=/.test(script[1])) vm.runInContext(script[2], context);
  }
  if (!names.length || new Set(names).size !== names.length) throw Error('invalid roster');
  result[entry.path.replace('testing/web-platform/tests', '')] = names;
}
process.stdout.write(JSON.stringify(result, null, 2) + '\n');
