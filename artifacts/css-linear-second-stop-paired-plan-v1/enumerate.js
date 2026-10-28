const fs = require('fs'), vm = require('vm'), path = require('path');
const result = {};
for (const file of ['linear-contextual-second-position-crash.html', 'linear-timing-functions-syntax.html', 'linear-timing-functions-output.html', 'feature-calibration.html']) {
  const names = [];
  const context = vm.createContext({test: (_, name) => names.push(name)});
  const html = fs.readFileSync(path.join(__dirname, file), 'utf8');
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
    const src = /src=["']([^"']+)["']/.exec(match[1]);
    if (src) {
      if (src[1].startsWith('/resources/') || src[1] === 'support/util.js') continue;
      vm.runInContext(fs.readFileSync(path.join(__dirname, path.basename(src[1])), 'utf8'), context);
    } else vm.runInContext(match[2], context);
  }
  if (new Set(names).size !== names.length) throw Error('duplicate');
  result[file] = names;
}
fs.writeFileSync(path.join(__dirname, 'ENUMERATED-SUBTESTS.json'), JSON.stringify(result, null, 2) + '\n');
console.log(Object.fromEntries(Object.entries(result).map(([k,v]) => [k,v.length])));
