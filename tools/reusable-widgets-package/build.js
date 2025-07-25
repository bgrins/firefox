#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration for components to build
const COMPONENTS = {
  'moz-label': {
    source: '../../toolkit/content/widgets/moz-label/moz-label.mjs',
    css: '../../toolkit/content/widgets/moz-label/moz-label.css',
    exports: ['MozTextLabel']
  }
  // Add more components here as needed
};

// Shared Firefox API shims
const FIREFOX_SHIMS = `
// Firefox API Shims for Web Compatibility
const FirefoxShims = {
  // Mock Services.prefs
  Services: {
    prefs: {
      getIntPref(name, defaultValue) {
        // Map Firefox prefs to web-compatible defaults
        const prefs = {
          'ui.key.menuAccessKey': navigator.platform.includes("Mac") ? 0 : 1
        };
        return prefs[name] ?? defaultValue;
      },
      getComplexValue(name, type) {
        // Return mock localized strings
        const values = {
          'intl.menuitems.insertseparatorbeforeaccesskeys': 'true',
          'intl.menuitems.alwaysappendaccesskeys': 'true'
        };
        return { data: values[name] || 'true' };
      }
    }
  },
  
  // Mock Ci interface
  Ci: {
    nsIPrefLocalizedString: class {}
  },
  
  // Configuration API for web usage
  config: {
    preferences: {
      underlineAccesskey: !navigator.platform.includes("Mac"),
      insertSeparatorBeforeAccesskeys: true,
      alwaysAppendAccesskeys: true,
    },
    configure(options) {
      Object.assign(this.preferences, options);
    }
  }
};

// Make shims available globally if needed
if (typeof window !== 'undefined') {
  window.Services = FirefoxShims.Services;
  window.Ci = FirefoxShims.Ci;
  window.IS_STORYBOOK = false;
}
`;

async function readSourceFile(filePath) {
  try {
    const fullPath = path.join(__dirname, filePath);
    return await fs.readFile(fullPath, 'utf-8');
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return null;
  }
}

async function transformComponent(componentName, config) {
  console.log(`Building ${componentName}...`);
  
  // Read source files
  const [jsSource, cssSource] = await Promise.all([
    readSourceFile(config.source),
    config.css ? readSourceFile(config.css) : Promise.resolve(null)
  ]);
  
  if (!jsSource) {
    console.error(`Failed to read source for ${componentName}`);
    return;
  }
  
  let transformed = jsSource;
  
  // Replace chrome:// URL references
  if (cssSource) {
    // Embed CSS directly
    const cssString = cssSource.replace(/`/g, '\\`');
    transformed = transformed.replace(
      /static stylesheetUrl = "chrome:\/\/[^"]+"/,
      `static styles = \`${cssString}\``
    );
    
    // Replace the stylesheet loading logic
    transformed = transformed.replace(
      /let style = document\.createElement\("link"\);[\s\S]*?container\.appendChild\(style\);/,
      `let style = document.createElement("style");
    style.textContent = this.constructor.styles || MozTextLabel.styles;
    container.appendChild(style);`
    );
  }
  
  // Fix Text.isInstance usage for web compatibility
  transformed = transformed.replace(
    /Text\.hasOwnProperty\("isInstance"\)[\s\S]*?element\.previousSibling instanceof Text/,
    'element.previousSibling instanceof Text'
  );
  
  // Add exports
  const exportNames = config.exports.join(', ');
  if (!transformed.includes('export')) {
    transformed += `\n\n// Auto-generated exports\nexport { ${exportNames} };`;
  }
  
  // Create output with shims
  const output = `/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// THIS FILE IS AUTO-GENERATED FROM FIREFOX SOURCE
// Source: ${config.source}
// Generated: ${new Date().toISOString()}

${FIREFOX_SHIMS}

${transformed}
`;
  
  // Write to dist
  const distDir = path.join(__dirname, 'dist');
  await fs.mkdir(distDir, { recursive: true });
  await fs.writeFile(path.join(distDir, `${componentName}.js`), output);
  
  // Also create a minimal ES module version
  const moduleOutput = `${output}\n\nexport default ${config.exports[0]};`;
  await fs.writeFile(path.join(distDir, `${componentName}.mjs`), moduleOutput);
  
  console.log(`✓ Built ${componentName}`);
}

async function build() {
  console.log('Building Mozilla components for web...\n');
  
  // Build all components
  for (const [name, config] of Object.entries(COMPONENTS)) {
    await transformComponent(name, config);
  }
  
  // Create index file
  const indexContent = Object.entries(COMPONENTS).map(([name, config]) => 
    `export { ${config.exports.join(', ')} } from './dist/${name}.mjs';`
  ).join('\n');
  
  await fs.writeFile(path.join(__dirname, 'index.mjs'), indexContent);
  
  console.log('\n✓ Build complete!');
}

// Run build
build().catch(console.error);