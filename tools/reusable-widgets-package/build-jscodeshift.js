#!/usr/bin/env node

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { transformFile } from './transform-chrome-urls.js';
import { transformCssFile } from './transform-css.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIREFOX_TOOLKIT_PATH = path.join(__dirname, '../../toolkit/content/widgets');
const DIST_DIR = path.join(__dirname, 'dist');

// Track build metadata
const buildMetadata = {
  chromeUrlMappings: {},
  filesProcessed: [],
  warnings: [],
  icons: new Set(),
  fileMap: {}
};

/**
 * Build a map of all files for URL resolution
 */
async function buildFileMap(dir, baseDir = dir, map = {}) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relativePath = path.relative(baseDir, fullPath);
    
    if (entry.isDirectory()) {
      await buildFileMap(fullPath, baseDir, map);
    } else if (entry.isFile()) {
      const filename = entry.name;
      if (!map[filename]) {
        map[filename] = [];
      }
      map[filename].push(relativePath);
    }
  }
  
  return map;
}

/**
 * Calculate relative path from one file to another
 */
function getRelativePath(fromFile, toFile) {
  const fromDir = path.dirname(fromFile);
  let relativePath = path.relative(fromDir, toFile);
  
  if (!relativePath.startsWith('.')) {
    relativePath = './' + relativePath;
  }
  
  return relativePath.replace(/\\/g, '/');
}

/**
 * Resolve a chrome:// URL to a relative path
 */
function resolveChromeUrl(chromeUrl, currentFilePath, fileMap) {
  // Extract filename from URL - match any file extension
  const urlMatch = chromeUrl.match(/([^/]+\.[a-zA-Z0-9]+)$/);
  if (!urlMatch) {
    const warning = `Could not extract filename from chrome URL: ${chromeUrl}`;
    console.warn(warning);
    buildMetadata.warnings.push({ 
      file: path.relative(DIST_DIR, currentFilePath), 
      warning, 
      chromeUrl 
    });
    return chromeUrl;
  }

  const filename = urlMatch[1];
  const possiblePaths = fileMap[filename] || [];
  
  if (possiblePaths.length === 0) {
    const warning = `No file found for: ${filename}`;
    console.warn(warning);
    buildMetadata.warnings.push({ 
      file: path.relative(DIST_DIR, currentFilePath), 
      warning, 
      chromeUrl 
    });
    return chromeUrl;
  }
  
  if (possiblePaths.length > 1) {
    buildMetadata.warnings.push({
      file: path.relative(DIST_DIR, currentFilePath),
      warning: `Multiple files found for ${filename}: ${possiblePaths.join(', ')}`,
      chromeUrl
    });
  }
  
  const targetPath = possiblePaths[0];
  const relativePath = getRelativePath(currentFilePath, targetPath);
  
  buildMetadata.chromeUrlMappings[chromeUrl] = {
    from: path.relative(DIST_DIR, currentFilePath),
    to: targetPath,
    relative: relativePath
  };
  
  return relativePath;
}


/**
 * Special transformation for lit-utils.mjs
 */
async function transformLitUtils(filePath) {
  const content = await fs.readFile(filePath, 'utf-8');
  let transformed = content;
  
  // Add special handling for insertStylesheetIfNeeded
  if (transformed.includes('insertStylesheetIfNeeded')) {
    transformed = transformed.replace(
      /\/\/ Do not remove the following comment[^}]+export function insertStylesheetIfNeeded/,
      `// Do not remove the following comment, as it's used to fix paths at build time for published components:

  if (!BrowserChrome.IS_CHROME && !BrowserChrome.IS_STORYBOOK) {
    // For web usage, resolve the stylesheet URL based on the original path
    if (stylesheetUrl.startsWith("chrome://")) {
      // Extract the component directory and filename from the chrome URL
      const match = stylesheetUrl.match(/chrome:\\/\\/global\\/content\\/elements\\/(moz-[^\\/]+)\\/(.*\\.css)$/);
      if (match) {
        const [, componentDir, cssFile] = match;
        const baseUrl = new URL('./', import.meta.url).href;
        resolvedUrl = new URL(\`\${componentDir}/\${cssFile}\`, baseUrl).href;
      }
    }
  }

export function insertStylesheetIfNeeded`
    );
  }
  
  // Fix Text.isInstance for web compatibility
  transformed = transformed.replace(
    /Text\.hasOwnProperty\("isInstance"\)[\s\S]*?element\.previousSibling instanceof Text/,
    'element.previousSibling instanceof Text'
  );
  
  if (transformed !== content) {
    await fs.writeFile(filePath, transformed);
  }
}

/**
 * Copy directory recursively
 */
async function copyDirectory(src, dest, fileFilter = null) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath, fileFilter);
    } else if (!fileFilter || fileFilter(entry.name)) {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Copy icons from Firefox source
 */
async function copyIcons() {
  if (buildMetadata.icons.size === 0) {
    console.log('\nNo icons to copy');
    return;
  }
  
  console.log(`\nCopying ${buildMetadata.icons.size} icons...`);
  const iconsDir = path.join(DIST_DIR, 'icons');
  await fs.mkdir(iconsDir, { recursive: true });
  
  let copiedCount = 0;
  let failedIcons = [];
  
  for (const chromeUrl of buildMetadata.icons) {
    const filename = chromeUrl.split('/').pop();
    
    // Try various possible source paths
    const possiblePaths = [
      path.join(__dirname, '../../toolkit/content/widgets/images', filename),
      path.join(__dirname, '../../browser/themes/shared/icons', filename),
      path.join(__dirname, '../../toolkit/themes/shared/icons', filename),
      path.join(__dirname, '../../toolkit/content/global/icons', filename),
      path.join(__dirname, '../../browser/components/customizableui/content', filename),
      path.join(__dirname, '../../browser/themes/shared', filename)
    ];
    
    let copied = false;
    for (const sourcePath of possiblePaths) {
      try {
        await fs.copyFile(sourcePath, path.join(iconsDir, filename));
        copiedCount++;
        copied = true;
        break;
      } catch (error) {
        // Try next path
      }
    }
    
    if (!copied) {
      failedIcons.push({ url: chromeUrl, filename });
    }
  }
  
  console.log(`  ✓ Copied ${copiedCount} icons`);
  if (failedIcons.length > 0) {
    console.warn(`  ⚠ Failed to copy ${failedIcons.length} icons:`);
    failedIcons.forEach(icon => {
      console.warn(`    - ${icon.filename} (${icon.url})`);
    });
    buildMetadata.warnings.push({ 
      type: 'icon-copy-failures', 
      count: failedIcons.length,
      icons: failedIcons 
    });
  }
}

/**
 * Generate index.mjs
 */
async function generateIndex() {
  console.log('\nGenerating index.mjs...');
  
  const entries = await fs.readdir(DIST_DIR, { withFileTypes: true });
  const components = entries
    .filter(entry => entry.isDirectory() && entry.name.startsWith('moz-'))
    .map(entry => entry.name)
    .sort();
  
  let indexContent = '// Auto-generated index of all Mozilla components\n';
  for (const component of components) {
    indexContent += `import './${component}/${component}.mjs';\n`;
  }
  
  indexContent += '\n// Export utility modules\n';
  indexContent += "export { BrowserChrome } from './lit-utils.mjs';\n";
  
  await fs.writeFile(path.join(DIST_DIR, 'index.mjs'), indexContent);
  console.log('  ✓ Generated index.mjs');
}

/**
 * Main build function
 */
async function build() {
  console.log('Building Mozilla components for web...\n');
  
  // Clean dist directory
  try {
    await fs.rm(DIST_DIR, { recursive: true, force: true });
  } catch (error) {
    // Directory might not exist
  }
  
  await fs.mkdir(DIST_DIR, { recursive: true });
  
  // Step 1: Copy widget directories from Firefox
  console.log('Copying widget files from Firefox...');
  const entries = await fs.readdir(FIREFOX_TOOLKIT_PATH, { withFileTypes: true });
  
  for (const entry of entries) {
    if (entry.isDirectory() && (entry.name.startsWith('moz-') || entry.name === 'vendor')) {
      const srcPath = path.join(FIREFOX_TOOLKIT_PATH, entry.name);
      const destPath = path.join(DIST_DIR, entry.name);
      
      console.log(`  Copying ${entry.name}/...`);
      await copyDirectory(srcPath, destPath,
        (filename) => filename.endsWith('.css') || filename.endsWith('.mjs')
      );
    }
  }
  
  // Step 2: Copy individual files
  const filesToCopy = [
    {
      source: path.join(FIREFOX_TOOLKIT_PATH, 'lit-utils.mjs'),
      dest: path.join(DIST_DIR, 'lit-utils.mjs')
    },
    {
      source: path.join(FIREFOX_TOOLKIT_PATH, 'lit-select-control.mjs'),
      dest: path.join(DIST_DIR, 'lit-select-control.mjs')
    },
    {
      source: path.join(FIREFOX_TOOLKIT_PATH, 'moz-input-common.css'),
      dest: path.join(DIST_DIR, 'moz-input-common.css')
    },
    {
      source: path.join(FIREFOX_TOOLKIT_PATH, 'moz-box-common.css'),
      dest: path.join(DIST_DIR, 'moz-box-common.css')
    },
    {
      source: path.join(__dirname, '../../toolkit/themes/shared/design-system/text-and-typography.css'),
      dest: path.join(DIST_DIR, 'text-and-typography.css')
    }
  ];
  
  for (const file of filesToCopy) {
    try {
      await fs.copyFile(file.source, file.dest);
      console.log(`  Copied: ${path.basename(file.dest)}`);
    } catch (error) {
      console.warn(`  Warning: Could not copy ${path.basename(file.dest)}: ${error.message}`);
    }
  }
  
  // Step 3: Build file map
  const fileMap = await buildFileMap(DIST_DIR, DIST_DIR);
  buildMetadata.fileMap = fileMap;
  console.log(`\nBuilt file map with ${Object.keys(fileMap).length} unique filenames`);
  
  // Step 4: Transform all JavaScript files using jscodeshift
  console.log('\nTransforming JavaScript files...');
  const helpers = { 
    getRelativePath, 
    resolveChromeUrl,
    trackIcon: (chromeUrl) => buildMetadata.icons.add(chromeUrl)
  };
  
  async function transformDirectory(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await transformDirectory(fullPath);
      } else if (entry.name.endsWith('.mjs')) {
        const relativePath = path.relative(DIST_DIR, fullPath);
        
        // Special handling for lit-utils.mjs
        if (entry.name === 'lit-utils.mjs') {
          await transformLitUtils(fullPath);
        }
        
        // Transform with jscodeshift
        const transformed = await transformFile(fullPath, fileMap, helpers);
        if (transformed) {
          buildMetadata.filesProcessed.push(relativePath);
        }
      } else if (entry.name.endsWith('.css')) {
        // Transform CSS files with PostCSS
        const relativePath = path.relative(DIST_DIR, fullPath);
        const transformed = await transformCssFile(fullPath, fileMap, helpers);
        if (transformed) {
          buildMetadata.filesProcessed.push(relativePath);
        }
      }
    }
  }
  
  await transformDirectory(DIST_DIR);
  console.log(`  ✓ Processed ${buildMetadata.filesProcessed.length} files`);
  
  // Step 5: Generate index
  await generateIndex();
  
  // Step 6: Copy demo files
  console.log('\nCopying demo files...');
  const demoFiles = ['example.html', 'kitchensink.html'];
  for (const file of demoFiles) {
    try {
      await fs.copyFile(
        path.join(__dirname, file),
        path.join(DIST_DIR, file)
      );
      console.log(`  ✓ ${file}`);
    } catch (error) {
      console.warn(`  Warning: Could not copy ${file}: ${error.message}`);
    }
  }
  
  // Step 7: Copy icons
  await copyIcons();
  
  // Step 8: Write build metadata
  console.log('\nWriting build metadata...');
  await fs.writeFile(
    path.join(DIST_DIR, 'build-metadata.json'),
    JSON.stringify(buildMetadata, null, 2)
  );
  
  // Summary
  console.log('\n✨ Build complete!');
  console.log(`  - Components: ${Object.keys(fileMap).filter(f => f.startsWith('moz-') && f.endsWith('.mjs')).length}`);
  console.log(`  - Files processed: ${buildMetadata.filesProcessed.length}`);
  console.log(`  - Chrome URLs replaced: ${Object.keys(buildMetadata.chromeUrlMappings).length}`);
  console.log(`  - Icons: ${buildMetadata.icons.size}`);
  if (buildMetadata.warnings.length > 0) {
    console.log(`  - Warnings: ${buildMetadata.warnings.length}`);
  }
}

// Run the build
build().catch(console.error);