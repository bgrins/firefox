#!/usr/bin/env node

import postcss from 'postcss';
import postcssImport from 'postcss-import';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * PostCSS plugin to transform chrome:// URLs
 */
const transformChromeUrls = (opts = {}) => {
  const { resolveChromeUrl, trackIcon, getRelativePath, filePath, fileMap, cssChromeMappings } = opts;
  
  return {
    postcssPlugin: 'transform-chrome-urls',
    
    // Transform @import rules with chrome URLs
    AtRule: {
      import(atRule) {
        const match = atRule.params.match(/url\(["']?(chrome:\/\/[^"')]+)["']?\)/);
        if (match) {
          const chromeUrl = match[1];
          // If we have a direct mapping for CSS, use it
          if (cssChromeMappings && cssChromeMappings[chromeUrl]) {
            atRule.params = `url("${cssChromeMappings[chromeUrl]}")`;
          } else {
            // Otherwise try to resolve it
            const resolved = resolveChromeUrl(chromeUrl, filePath, fileMap);
            if (resolved !== chromeUrl) {
              atRule.params = `url("${resolved}")`;
            }
          }
        }
      }
    },
    
    // Transform url() functions in declarations
    Declaration(decl) {
      if (decl.value.includes('chrome://')) {
        decl.value = decl.value.replace(
          /url\(["']?(chrome:\/\/[^"')]+)["']?\)/g,
          (match, chromeUrl) => {
            // Check if it's an icon (handle URLs with hash fragments)
            const urlWithoutHash = chromeUrl.split('#')[0];
            if (urlWithoutHash.match(/\.(svg|png|jpg|jpeg|gif)$/)) {
              trackIcon && trackIcon(urlWithoutHash);
              const filename = urlWithoutHash.split('/').pop();
              const relativePath = getRelativePath(filePath, `icons/${filename}`);
              // Preserve hash fragment if present
              const hashIndex = chromeUrl.indexOf('#');
              const finalPath = hashIndex > -1 ? relativePath + chromeUrl.substring(hashIndex) : relativePath;
              return `url("${finalPath}")`;
            } else {
              // For non-icon resources, try to resolve normally
              const resolved = resolveChromeUrl(chromeUrl, filePath, fileMap);
              return `url("${resolved}")`;
            }
          }
        );
      }
    }
  };
};

transformChromeUrls.postcss = true;

export { transformChromeUrls };

/**
 * Convert CSS to Lit css template literal
 */
function cssToLitTemplate(css) {
  // Escape backticks and ${} in the CSS
  const escaped = css
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$\{/g, '\\${');
  
  return `css\`${escaped}\``;
}

/**
 * Transform CSS file: resolve chrome URLs, inline imports, convert to Lit css
 */
export async function transformCssToLitStyles(filePath, fileMap, helpers, commonCss = '') {
  const content = await fs.readFile(filePath, 'utf-8');
  
  // Prepend common CSS before processing so imports get resolved
  const cssToProcess = commonCss ? `${commonCss}\n\n${content}` : content;
  
  // First pass: Transform chrome:// URLs
  const chromeTransformed = await postcss([
    transformChromeUrls({
      ...helpers,
      filePath,
      fileMap
    })
  ]).process(cssToProcess, { from: filePath });
  
  // Second pass: Inline @import statements
  // Create a resolver for chrome:// URLs if we have mappings
  const importOptions = {
    root: path.dirname(filePath)
  };
  
  if (helpers.cssChromeMappings) {
    importOptions.resolve = (id, basedir, importOptions) => {
      if (id.startsWith('chrome://') && helpers.cssChromeMappings[id]) {
        return helpers.cssChromeMappings[id];
      }
      return id;
    };
  }
  
  const inlined = await postcss([
    postcssImport(importOptions)
  ]).process(chromeTransformed.css, { from: filePath });
  
  // Transform :root to :host for shadow DOM compatibility
  // Keep :host(.anonymous-content-host) as is
  let finalCss = inlined.css;
  
  // Replace :root with :host, but not when it's part of :host(...)
  finalCss = finalCss.replace(/:root(?!\s*\.)/g, ':host');
  
  // Convert to Lit css template literal
  const litStyles = cssToLitTemplate(finalCss);
  
  return {
    css: finalCss,
    litStyles
  };
}

/**
 * Transform CSS file and save (for standalone CSS files like moz-input-common.css)
 */
export async function transformCssFile(filePath, fileMap, helpers) {
  const content = await fs.readFile(filePath, 'utf-8');
  
  // First pass: Transform chrome:// URLs
  const result = await postcss([
    transformChromeUrls({
      ...helpers,
      filePath,
      fileMap
    })
  ]).process(content, { from: filePath });
  
  if (result.css !== content) {
    await fs.writeFile(filePath, result.css);
    return true;
  }
  
  return false;
}