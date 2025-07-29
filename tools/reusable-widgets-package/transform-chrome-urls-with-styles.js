#!/usr/bin/env node

import jscodeshift from 'jscodeshift';
import { promises as fs } from 'fs';
import path from 'path';
import { transformCssToLitStyles } from './transform-css-inline.js';

const j = jscodeshift;

/**
 * Transform imports and other chrome:// URL references
 * Also inject static styles for components
 */
export function transformChromeUrlsWithStyles(fileInfo, api, options) {
  const source = fileInfo.source;
  const filePath = fileInfo.path;
  const fileMap = options.fileMap || {};
  const getRelativePath = options.getRelativePath;
  const resolveChromeUrl = options.resolveChromeUrl;
  
  const root = j(source);
  let hasChanges = false;
  
  // Check if this is a component that uses insertStylesheetIfNeeded
  let componentStylesheet = null;
  let hasInsertStylesheetCall = false;
  
  // Find insertStylesheetIfNeeded calls
  root.find(j.CallExpression, {
    callee: { name: 'insertStylesheetIfNeeded' }
  }).forEach(path => {
    const args = path.node.arguments;
    if (args.length >= 2 && args[1].type === 'Literal') {
      componentStylesheet = args[1].value;
      hasInsertStylesheetCall = true;
      // Remove the insertStylesheetIfNeeded call
      j(path).closest(j.ExpressionStatement).remove();
      hasChanges = true;
    }
  });
  
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
  
  // Transform template literals with chrome:// URLs
  root.find(j.TemplateLiteral).forEach(path => {
    path.node.quasis.forEach((quasi, index) => {
      const value = quasi.value.raw;
      if (value.includes('chrome://')) {
        const transformed = value.replace(
          /((?:href|src|stylesheetUrl|iconSrc|imageSrc|background|content)\s*[=:]\s*["']?)(chrome:\/\/[^"')\s]+)(["']?)/g,
          (match, prefix, chromeUrl, suffix) => {
            // Special handling for icon URLs
            if (chromeUrl.match(/\.(svg|png|jpg|jpeg|gif)$/)) {
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
  
  // Transform string literals
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
  
  // If we found a stylesheet and have the styles, inject them
  if (hasInsertStylesheetCall && componentStylesheet && options.componentStyles) {
    const styles = options.componentStyles[componentStylesheet];
    if (!styles) {
      console.warn(`No styles found for ${componentStylesheet}`);
      console.warn(`Available keys:`, Object.keys(options.componentStyles).slice(0, 5));
    } else {
      console.log(`Found styles for ${componentStylesheet}, injecting...`);
      // Find the class declaration
      const classDeclaration = root.find(j.ClassDeclaration).at(0);
      if (classDeclaration.length > 0) {
        // Check if static styles already exists
        const hasStaticStyles = classDeclaration.find(j.ClassProperty, {
          static: true,
          key: { name: 'styles' }
        }).length > 0;
        
        if (!hasStaticStyles) {
          // Import css from lit
          const litImport = root.find(j.ImportDeclaration, {
            source: { value: '../vendor/lit.all.mjs' }
          }).at(0);
          
          if (litImport.length > 0) {
            // Add css to the import if not already there
            const specifiers = litImport.get().node.specifiers;
            const hasCss = specifiers.some(spec => 
              spec.type === 'ImportSpecifier' && spec.imported.name === 'css'
            );
            
            if (!hasCss) {
              specifiers.push(j.importSpecifier(j.identifier('css')));
              hasChanges = true;
            }
          }
          
          // Create static styles property
          // The litStyles already includes the css`` template literal
          // We need to parse it as an expression
          const stylesExpression = j(`const temp = ${styles.litStyles}`).find(j.VariableDeclarator).at(0).get().node.init;
          
          // Use classProperty for jscodeshift
          const stylesProperty = j.classProperty(
            j.identifier('styles'),
            stylesExpression,
            null,
            true // static
          );
          
          // Find the right place to insert (after other static properties)
          const classBody = classDeclaration.get().node.body;
          let insertIndex = 0;
          
          // Find last static property
          classBody.body.forEach((member, index) => {
            if (member.type === 'ClassProperty' && member.static) {
              insertIndex = index + 1;
            }
          });
          
          classBody.body.splice(insertIndex, 0, stylesProperty);
          hasChanges = true;
        }
      }
    }
  }
  
  return hasChanges ? root.toSource() : null;
}

/**
 * Run transformation on a file
 */
export async function transformFile(filePath, fileMap, helpers, componentStyles) {
  const content = await fs.readFile(filePath, 'utf-8');
  
  const fileInfo = {
    path: filePath,
    source: content
  };
  
  const options = {
    fileMap,
    componentStyles,
    ...helpers
  };
  
  const result = transformChromeUrlsWithStyles(fileInfo, jscodeshift, options);
  
  if (result) {
    await fs.writeFile(filePath, result);
    return true;
  }
  
  return false;
}