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


async function readSourceFile(filePath) {
  try {
    const fullPath = path.join(__dirname, filePath);
    return await fs.readFile(fullPath, 'utf-8');
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return null;
  }
}

async function transformFile(filePath, isComponent = false, componentConfig = null) {
  const fullPath = path.join(__dirname, 'src/widgets', filePath);
  let content = await fs.readFile(fullPath, 'utf-8');
  
  // Replace all chrome:// URLs with relative paths
  content = content.replace(/chrome:\/\/global\/content\/elements\//g, './');
  content = content.replace(/chrome:\/\/global\/content\/widgets\//g, './');
  content = content.replace(/chrome:\/\/global\/content\/vendor\//g, './vendor/');
  content = content.replace(/chrome:\/\/global\/content\//g, './');
  content = content.replace(/chrome:\/\/global\/skin\/in-content\//g, './');
  content = content.replace(/chrome:\/\/global\/skin\/design-system\//g, './');
  
  // Fix relative imports for lit-utils
  content = content.replace(/from "\.\.\/lit-utils\.mjs"/g, 'from "../lit-utils.mjs"');
  
  // Fix Text.isInstance usage for web compatibility
  content = content.replace(
    /Text\.hasOwnProperty\("isInstance"\)[\s\S]*?element\.previousSibling instanceof Text/,
    'element.previousSibling instanceof Text'
  );
  
  return content;
}

async function transformComponent(componentName, config) {
  console.log(`Building ${componentName}...`);
  
  const distDir = path.join(__dirname, 'dist');
  await fs.mkdir(distDir, { recursive: true });
  
  // Transform the main JS file
  const jsPath = `${componentName}/${componentName}.mjs`;
  const jsContent = await transformFile(jsPath, true, config);
  
  if (jsContent) {
    await fs.writeFile(path.join(distDir, `${componentName}.mjs`), jsContent);
  }
  
  // Copy CSS file if it exists
  if (config.css) {
    const cssPath = `${componentName}/${componentName}.css`;
    try {
      const cssContent = await transformFile(cssPath);
      await fs.writeFile(path.join(distDir, `${componentName}.css`), cssContent);
      console.log(`✓ Built ${componentName} (JS + CSS)`);
    } catch (error) {
      console.log(`✓ Built ${componentName} (JS only)`);
    }
  } else {
    console.log(`✓ Built ${componentName}`);
  }
}

async function copyWidgetFiles() {
  const sourceDir = path.join(__dirname, '../../toolkit/content/widgets');
  const targetDir = path.join(__dirname, 'src/widgets');
  
  console.log('Copying widget files from Firefox source...');
  
  // Create target directory
  await fs.mkdir(targetDir, { recursive: true });
  
  // Get all entries in widgets directory
  const entries = await fs.readdir(sourceDir, { withFileTypes: true });
  
  // Only process subdirectories that start with "moz-" or "vendor"
  for (const entry of entries) {
    if (entry.isDirectory() && (entry.name.startsWith('moz-') || entry.name === 'vendor')) {
      const srcPath = path.join(sourceDir, entry.name);
      const destPath = path.join(targetDir, entry.name);
      
      console.log(`  Copying ${entry.name}/...`);
      
      // Recursively copy this subdirectory
      async function copyDir(src, dest) {
        await fs.mkdir(dest, { recursive: true });
        const subEntries = await fs.readdir(src, { withFileTypes: true });
        
        for (const subEntry of subEntries) {
          const subSrcPath = path.join(src, subEntry.name);
          const subDestPath = path.join(dest, subEntry.name);
          
          if (subEntry.isDirectory()) {
            await copyDir(subSrcPath, subDestPath);
          } else if (subEntry.name.endsWith('.css') || subEntry.name.endsWith('.mjs')) {
            await fs.copyFile(subSrcPath, subDestPath);
          }
        }
      }
      
      await copyDir(srcPath, destPath);
    }
  }
  
  // Copy lit-utils.mjs from widgets directory
  const litUtilsSource = path.join(sourceDir, 'lit-utils.mjs');
  const litUtilsTarget = path.join(targetDir, 'lit-utils.mjs');
  
  try {
    await fs.copyFile(litUtilsSource, litUtilsTarget);
    console.log('  Copied: lit-utils.mjs');
  } catch (error) {
    console.warn('  Warning: Could not copy lit-utils.mjs:', error.message);
  }
  
  // Copy moz-input-common.css from widgets directory
  const inputCommonCssSource = path.join(sourceDir, 'moz-input-common.css');
  const inputCommonCssTarget = path.join(targetDir, 'moz-input-common.css');
  
  try {
    await fs.copyFile(inputCommonCssSource, inputCommonCssTarget);
    console.log('  Copied: moz-input-common.css');
  } catch (error) {
    console.warn('  Warning: Could not copy moz-input-common.css:', error.message);
  }
  
  // Copy text-and-typography.css from design-system directory
  const textTypographyCssSource = path.join(__dirname, '../../toolkit/themes/shared/design-system/text-and-typography.css');
  const textTypographyCssTarget = path.join(targetDir, 'text-and-typography.css');
  
  try {
    await fs.copyFile(textTypographyCssSource, textTypographyCssTarget);
    console.log('  Copied: text-and-typography.css');
  } catch (error) {
    console.warn('  Warning: Could not copy text-and-typography.css:', error.message);
  }
  
  // Also copy chrome://global/skin/in-content/common.css
  const commonCssSource = path.join(__dirname, '../../toolkit/themes/shared/in-content/common.css');
  const commonCssTarget = path.join(__dirname, 'src/common.css');
  
  try {
    await fs.copyFile(commonCssSource, commonCssTarget);
    console.log('  Copied: common.css');
  } catch (error) {
    console.warn('  Warning: Could not copy common.css:', error.message);
  }
}

async function copyAndTransformSharedFiles() {
  const distDir = path.join(__dirname, 'dist');
  
  // Transform and copy lit-utils.mjs
  console.log('  Transforming lit-utils.mjs...');
  const litUtilsContent = await transformFile('lit-utils.mjs');
  await fs.writeFile(path.join(distDir, 'lit-utils.mjs'), litUtilsContent);
  
  // Transform and copy CSS files
  const cssFiles = ['moz-input-common.css', 'text-and-typography.css'];
  for (const cssFile of cssFiles) {
    console.log(`  Transforming ${cssFile}...`);
    try {
      const cssContent = await transformFile(cssFile);
      await fs.writeFile(path.join(distDir, cssFile), cssContent);
    } catch (error) {
      console.warn(`  Warning: Could not transform ${cssFile}:`, error.message);
    }
  }
  
  // Copy vendor directory
  const vendorSource = path.join(__dirname, 'src/widgets/vendor');
  const vendorTarget = path.join(distDir, 'vendor');
  
  try {
    await fs.mkdir(vendorTarget, { recursive: true });
    const vendorFiles = await fs.readdir(vendorSource);
    for (const file of vendorFiles) {
      if (file.endsWith('.mjs') || file.endsWith('.css')) {
        const content = await transformFile(`vendor/${file}`);
        await fs.writeFile(path.join(vendorTarget, file), content);
      }
    }
    console.log('  Copied vendor files');
  } catch (error) {
    console.warn('  Warning: Could not copy vendor files:', error.message);
  }
}

async function build() {
  console.log('Building Mozilla components for web...\n');
  
  const distDir = path.join(__dirname, 'dist');
  await fs.mkdir(distDir, { recursive: true });
  
  // First, copy all widget files locally
  await copyWidgetFiles();
  
  
  // Transform and copy shared files
  await copyAndTransformSharedFiles();
  
  // Build all components
  for (const [name, config] of Object.entries(COMPONENTS)) {
    await transformComponent(name, config);
  }
  
  // Create index file in dist directory
  const indexContent = Object.entries(COMPONENTS).map(([name, config]) => 
    `export { ${config.exports.join(', ')} } from './${name}.mjs';`
  ).join('\n');
  
  await fs.writeFile(path.join(distDir, 'index.mjs'), indexContent);
  
  console.log('\n✓ Build complete!');
}

// Run build
build().catch(console.error);