#!/usr/bin/env node

import jscodeshift from 'jscodeshift';
import { promises as fs } from 'fs';
import path from 'path';

const j = jscodeshift;

/**
 * Transform imports and other chrome:// URL references
 */
export function transformChromeUrls(fileInfo, api, options) {
  const source = fileInfo.source;
  const filePath = fileInfo.path;
  const fileMap = options.fileMap || {};
  const getRelativePath = options.getRelativePath;
  const resolveChromeUrl = options.resolveChromeUrl;
  
  const root = j(source);
  let hasChanges = false;
  
  // Transform import declarations
  root.find(j.ImportDeclaration).forEach(path => {
    const importPath = path.node.source.value;
    if (importPath.startsWith('chrome://')) {
      const relativePath = resolveChromeUrl(importPath, filePath, fileMap);
      if (relativePath !== importPath) {
        path.node.source.value = relativePath;
        hasChanges = true;
      }
    }
  });
  
  // Transform dynamic imports
  root.find(j.CallExpression, {
    callee: { type: 'Import' }
  }).forEach(path => {
    const arg = path.node.arguments[0];
    if (arg && arg.type === 'Literal' && arg.value.startsWith('chrome://')) {
      const relativePath = resolveChromeUrl(arg.value, filePath, fileMap);
      if (relativePath !== arg.value) {
        arg.value = relativePath;
        hasChanges = true;
      }
    }
  });
  
  // Transform template literals with chrome:// URLs (for href, stylesheetUrl, src, etc.)
  root.find(j.TemplateLiteral).forEach(path => {
    path.node.quasis.forEach((quasi, index) => {
      const value = quasi.value.raw;
      if (value.includes('chrome://')) {
        // Look for patterns like href="chrome://...", src="chrome://...", etc.
        const transformed = value.replace(
          /((?:href|src|stylesheetUrl|iconSrc|imageSrc|background|content)\s*[=:]\s*["']?)(chrome:\/\/[^"')\s]+)(["']?)/g,
          (match, prefix, chromeUrl, suffix) => {
            // Special handling for icon URLs
            if (chromeUrl.match(/\.(svg|png|jpg|jpeg|gif)$/)) {
              // Track icon for copying
              options.trackIcon && options.trackIcon(chromeUrl);
              const filename = chromeUrl.split('/').pop();
              const relativePath = getRelativePath(filePath, `icons/${filename}`);
              return prefix + relativePath + suffix;
            }
            
            const relativePath = resolveChromeUrl(chromeUrl, filePath, fileMap);
            return prefix + relativePath + suffix;
          }
        );
        if (transformed !== value) {
          quasi.value.raw = transformed;
          quasi.value.cooked = transformed;
          hasChanges = true;
        }
      }
    });
  });
  
  // Transform string literals (for stylesheetUrl assignments, etc.)
  root.find(j.Literal).forEach(path => {
    if (typeof path.node.value === 'string' && path.node.value.startsWith('chrome://')) {
      const chromeUrl = path.node.value;
      
      // Special handling for icon URLs
      if (chromeUrl.match(/\.(svg|png|jpg|jpeg|gif)$/)) {
        options.trackIcon && options.trackIcon(chromeUrl);
        const filename = chromeUrl.split('/').pop();
        path.node.value = getRelativePath(filePath, `icons/${filename}`);
        hasChanges = true;
      } else {
        const relativePath = resolveChromeUrl(chromeUrl, filePath, fileMap);
        if (relativePath !== chromeUrl) {
          path.node.value = relativePath;
          hasChanges = true;
        }
      }
    }
  });
  
  return hasChanges ? root.toSource() : null;
}

/**
 * Run transformation on a file
 */
export async function transformFile(filePath, fileMap, helpers) {
  const content = await fs.readFile(filePath, 'utf-8');
  
  const fileInfo = {
    path: filePath,
    source: content
  };
  
  const options = {
    fileMap,
    ...helpers
  };
  
  const result = transformChromeUrls(fileInfo, jscodeshift, options);
  
  if (result) {
    await fs.writeFile(filePath, result);
    return true;
  }
  
  return false;
}