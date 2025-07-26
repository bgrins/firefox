const testContent = `import {
  html,
  ifDefined,
  when,
} from "chrome://global/content/vendor/lit.all.mjs";
import { MozLitElement } from "chrome://global/content/lit-utils.mjs";`;

const regex = /((?:import\s+(?:.*?\s+from\s+)?|href=|stylesheetUrl\s*=\s*)["'])(chrome:\/\/[^"']+)(["'])/g;

let matches = [];
let match;
while ((match = regex.exec(testContent)) !== null) {
  matches.push({
    fullMatch: match[0],
    prefix: match[1],
    chromeUrl: match[2],
    suffix: match[3]
  });
}

console.log('Found matches:', matches);

// Test replacement
const replaced = testContent.replace(regex, (match, prefix, chromeUrl, suffix) => {
  console.log('Replacing:', { match, prefix, chromeUrl, suffix });
  return prefix + 'REPLACED_URL' + suffix;
});

console.log('\nReplaced content:\n', replaced);