#!/usr/bin/env node

import postcss from 'postcss';
import { promises as fs } from 'fs';

/**
 * PostCSS plugin to transform chrome:// URLs
 */
const transformChromeUrls = (opts = {}) => {
  const { resolveChromeUrl, trackIcon, getRelativePath, filePath, fileMap } = opts;
  
  return {
    postcssPlugin: 'transform-chrome-urls',
    
    // Transform @import rules
    AtRule: {
      import(atRule) {
        // Match @import url("chrome://...")
        const match = atRule.params.match(/url\(["']?(chrome:\/\/[^"')]+)["']?\)/);
        if (match) {
          const chromeUrl = match[1];
          const resolved = resolveChromeUrl(chromeUrl, filePath, fileMap);
          atRule.params = `url("${resolved}")`;
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

/**
 * Transform CSS file using PostCSS
 */
export async function transformCssFile(filePath, fileMap, helpers) {
  const content = await fs.readFile(filePath, 'utf-8');
  
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