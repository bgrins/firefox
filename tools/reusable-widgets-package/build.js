#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration
const FIREFOX_TOOLKIT_PATH = '../../toolkit';
const SRC_WIDGETS_DIR = path.join(__dirname, 'src/widgets');
const DIST_DIR = path.join(__dirname, 'dist');

// Build metadata tracking
const buildMetadata = {
  timestamp: new Date().toISOString(),
  chromeUrlMappings: {},
  filesProcessed: [],
  warnings: []
};

/**
 * Create a map of all files in the dist directory for chrome:// URL resolution
 */
async function buildFileMap(dir, baseDir = dir, map = {}) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relativePath = path.relative(baseDir, fullPath);
    
    if (entry.isDirectory()) {
      await buildFileMap(fullPath, baseDir, map);
    } else if (entry.isFile()) {
      // Store by filename for easy lookup
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
 * Get the relative path from one file to another
 */
function getRelativePath(fromFile, toFile) {
  // Normalize paths
  const from = fromFile.split('/').filter(Boolean);
  const to = toFile.split('/').filter(Boolean);
  
  // If toFile is just a filename, it's in the root
  if (to.length === 1) {
    // If fromFile is in a subdirectory, need to go up
    return from.length > 1 ? '../'.repeat(from.length - 1) + to[0] : './' + to[0];
  }
  
  // If both are in subdirectories
  if (from.length > 1 && to.length > 1) {
    // Check if they're in the same directory
    const fromDir = from.slice(0, -1).join('/');
    const toDir = to.slice(0, -1).join('/');
    
    if (fromDir === toDir) {
      return './' + to[to.length - 1];
    }
  }
  
  // Otherwise, go up to root and then down to target
  const upCount = from.length - 1;
  return '../'.repeat(upCount) + to.join('/');
}

/**
 * Resolve a chrome:// URL to a relative path based on file map
 */
function resolveChromeUrl(chromeUrl, currentFilePath, fileMap) {
  // Extract the filename from the chrome URL
  const urlMatch = chromeUrl.match(/([^/]+\.(mjs|css))$/);
  if (!urlMatch) {
    const warning = `Could not extract filename from chrome URL: ${chromeUrl}`;
    console.warn(warning);
    buildMetadata.warnings.push({ file: currentFilePath, warning, chromeUrl });
    return chromeUrl;
  }
  
  const filename = urlMatch[1];
  const possiblePaths = fileMap[filename];
  
  if (!possiblePaths || possiblePaths.length === 0) {
    const warning = `No file found for: ${filename} from ${chromeUrl}`;
    console.warn(warning);
    buildMetadata.warnings.push({ file: currentFilePath, warning, chromeUrl });
    return chromeUrl;
  }
  
  let targetPath;
  
  // If there's only one match, use it
  if (possiblePaths.length === 1) {
    targetPath = possiblePaths[0];
  } else {
    // If multiple matches, try to be smart about which one to use
    // For chrome://global/content/elements/ URLs, prefer files in component subdirectories
    if (chromeUrl.includes('/elements/')) {
      const componentMatch = possiblePaths.find(p => p.includes('/'));
      if (componentMatch) {
        targetPath = componentMatch;
      }
    }
    
    // Otherwise use the first match
    if (!targetPath) {
      targetPath = possiblePaths[0];
    }
  }
  
  const relativePath = getRelativePath(currentFilePath, targetPath);
  
  // Track the mapping
  if (!buildMetadata.chromeUrlMappings[currentFilePath]) {
    buildMetadata.chromeUrlMappings[currentFilePath] = [];
  }
  buildMetadata.chromeUrlMappings[currentFilePath].push({
    from: chromeUrl,
    to: relativePath,
    targetFile: targetPath,
    possibleMatches: possiblePaths.length
  });
  
  return relativePath;
}

/**
 * Transform file content by replacing Firefox chrome:// URLs with relative paths
 * and fixing imports for the web environment
 */
async function transformContent(content, filePath, fileMap) {
  // Track that we're processing this file
  buildMetadata.filesProcessed.push(filePath);
  
  // Replace all chrome:// URLs with relative paths
  content = content.replace(
    /((?:import\s+(?:.*?\s+from\s+)?|href=|stylesheetUrl\s*=\s*)["'])(chrome:\/\/[^"']+)(["'])/g,
    (match, prefix, chromeUrl, suffix) => {
      const relativePath = resolveChromeUrl(chromeUrl, filePath, fileMap);
      return prefix + relativePath + suffix;
    }
  );

  // Fix Text.isInstance usage for web compatibility
  content = content.replace(
    /Text\.hasOwnProperty\("isInstance"\)[\s\S]*?element\.previousSibling instanceof Text/,
    'element.previousSibling instanceof Text'
  );
  
  // Add build-time path resolution for stylesheet loading
  if (content.includes('BUILDTIME_REPLACE_WITH_PATH_RESOLUTION')) {
    const pathResolutionCode = `
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
  }`;
    content = content.replace(
      '  // BUILDTIME_REPLACE_WITH_PATH_RESOLUTION',
      pathResolutionCode
    );
  }
  
  return content;
}

/**
 * Recursively copy a directory, filtering for specific file types
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
 * Copy widget files from Firefox source to local src directory
 */
async function copyWidgetFilesFromFirefox() {
  const sourceDir = path.join(__dirname, FIREFOX_TOOLKIT_PATH, 'content/widgets');
  
  console.log('Copying widget files from Firefox source...');
  
  // Create target directory
  await fs.mkdir(SRC_WIDGETS_DIR, { recursive: true });
  
  // Get all entries in widgets directory
  const entries = await fs.readdir(sourceDir, { withFileTypes: true });
  
  // Copy moz-* component directories and vendor
  for (const entry of entries) {
    if (entry.isDirectory() && (entry.name.startsWith('moz-') || entry.name === 'vendor')) {
      const srcPath = path.join(sourceDir, entry.name);
      const destPath = path.join(SRC_WIDGETS_DIR, entry.name);
      
      console.log(`  Copying ${entry.name}/...`);
      
      // Only copy .css and .mjs files
      await copyDirectory(srcPath, destPath, 
        (filename) => filename.endsWith('.css') || filename.endsWith('.mjs')
      );
    }
  }
  
  // Copy individual files
  const filesToCopy = [
    {
      name: 'lit-utils.mjs',
      source: path.join(sourceDir, 'lit-utils.mjs'),
      dest: path.join(SRC_WIDGETS_DIR, 'lit-utils.mjs')
    },
    {
      name: 'lit-select-control.mjs',
      source: path.join(sourceDir, 'lit-select-control.mjs'),
      dest: path.join(DIST_DIR, 'lit-select-control.mjs')
    },
    {
      name: 'moz-input-common.css',
      source: path.join(sourceDir, 'moz-input-common.css'),
      dest: path.join(SRC_WIDGETS_DIR, 'moz-input-common.css')
    },
    {
      name: 'text-and-typography.css',
      source: path.join(__dirname, FIREFOX_TOOLKIT_PATH, 'themes/shared/design-system/text-and-typography.css'),
      dest: path.join(SRC_WIDGETS_DIR, 'text-and-typography.css')
    }
  ];
  
  for (const file of filesToCopy) {
    try {
      await fs.copyFile(file.source, file.dest);
      console.log(`  Copied: ${file.name}`);
    } catch (error) {
      console.warn(`  Warning: Could not copy ${file.name}:`, error.message);
    }
  }
}

/**
 * Transform and copy all moz-* components maintaining directory structure
 */
async function buildComponents(fileMap) {
  const entries = await fs.readdir(SRC_WIDGETS_DIR, { withFileTypes: true });
  
  console.log('\nBuilding moz-* components...');
  
  for (const entry of entries) {
    if (entry.isDirectory() && entry.name.startsWith('moz-')) {
      const srcDir = path.join(SRC_WIDGETS_DIR, entry.name);
      const destDir = path.join(DIST_DIR, entry.name);
      await fs.mkdir(destDir, { recursive: true });
      
      const files = await fs.readdir(srcDir);
      
      for (const file of files) {
        if (file.endsWith('.mjs') || file.endsWith('.css')) {
          const srcPath = path.join(srcDir, file);
          const content = await fs.readFile(srcPath, 'utf-8');
          const relativePath = `${entry.name}/${file}`;
          const transformedContent = await transformContent(content, relativePath, fileMap);
          
          await fs.writeFile(path.join(destDir, file), transformedContent);
        }
      }
      console.log(`  ✓ ${entry.name}`);
    }
  }
}

/**
 * Transform and copy shared files (lit-utils, CSS, vendor)
 */
async function buildSharedFiles(fileMap) {
  console.log('\nBuilding shared files...');
  
  // Transform and copy lit-utils.mjs
  const litUtilsPath = path.join(SRC_WIDGETS_DIR, 'lit-utils.mjs');
  const litUtilsContent = await fs.readFile(litUtilsPath, 'utf-8');
  const transformedLitUtils = await transformContent(litUtilsContent, 'lit-utils.mjs', fileMap);
  await fs.writeFile(path.join(DIST_DIR, 'lit-utils.mjs'), transformedLitUtils);
  console.log('  ✓ lit-utils.mjs');
  
  // Transform and copy lit-select-control.mjs
  try {
    const litSelectPath = path.join(SRC_WIDGETS_DIR, 'lit-select-control.mjs');
    const litSelectContent = await fs.readFile(litSelectPath, 'utf-8');
    const transformedLitSelect = await transformContent(litSelectContent, 'lit-select-control.mjs', fileMap);
    await fs.writeFile(path.join(DIST_DIR, 'lit-select-control.mjs'), transformedLitSelect);
    console.log('  ✓ lit-select-control.mjs');
  } catch (error) {
    console.warn('  Warning: Could not transform lit-select-control.mjs:', error.message);
  }
  
  // Transform and copy CSS files
  const cssFiles = ['moz-input-common.css', 'text-and-typography.css'];
  for (const cssFile of cssFiles) {
    try {
      const cssPath = path.join(SRC_WIDGETS_DIR, cssFile);
      const cssContent = await fs.readFile(cssPath, 'utf-8');
      const transformedCss = await transformContent(cssContent, cssFile, fileMap);
      await fs.writeFile(path.join(DIST_DIR, cssFile), transformedCss);
      console.log(`  ✓ ${cssFile}`);
    } catch (error) {
      console.warn(`  Warning: Could not transform ${cssFile}:`, error.message);
    }
  }
  
  // Copy vendor directory
  const vendorSource = path.join(SRC_WIDGETS_DIR, 'vendor');
  const vendorDest = path.join(DIST_DIR, 'vendor');
  
  try {
    await fs.mkdir(vendorDest, { recursive: true });
    const vendorFiles = await fs.readdir(vendorSource);
    
    for (const file of vendorFiles) {
      if (file.endsWith('.mjs') || file.endsWith('.css')) {
        const content = await fs.readFile(path.join(vendorSource, file), 'utf-8');
        const transformedContent = await transformContent(content, `vendor/${file}`, fileMap);
        await fs.writeFile(path.join(vendorDest, file), transformedContent);
      }
    }
    console.log('  ✓ vendor/');
  } catch (error) {
    console.warn('  Warning: Could not copy vendor files:', error.message);
  }
}

/**
 * Generate index.mjs that imports all components with customElements.define
 */
async function generateIndex() {
  const entries = await fs.readdir(DIST_DIR, { withFileTypes: true });
  const imports = [];
  
  // Find all component files that define custom elements
  for (const entry of entries) {
    if (entry.isDirectory() && entry.name.startsWith('moz-')) {
      const componentDir = path.join(DIST_DIR, entry.name);
      const files = await fs.readdir(componentDir);
      
      for (const file of files) {
        if (file.endsWith('.mjs') && !file.endsWith('.stories.mjs')) {
          const content = await fs.readFile(path.join(componentDir, file), 'utf-8');
          if (content.includes('customElements.define')) {
            imports.push(`import './${entry.name}/${file}';`);
          }
        }
      }
    }
  }
  
  const indexContent = `// Auto-generated index of all Mozilla components
${imports.join('\n')}

// Export utility modules
export { BrowserChrome } from './lit-utils.mjs';
`;
  
  await fs.writeFile(path.join(DIST_DIR, 'index.mjs'), indexContent);
  console.log('\n✓ Generated index.mjs');
}

/**
 * Copy demo HTML files and update their paths
 */
async function copyDemoFiles() {
  console.log('\nCopying demo files...');
  const htmlFiles = ['example.html', 'kitchensink.html'];
  
  for (const file of htmlFiles) {
    try {
      let content = await fs.readFile(path.join(__dirname, file), 'utf-8');
      // Update paths to remove dist/ prefix since these will be served from package root
      content = content.replace(/\.\/dist\//g, './');
      await fs.writeFile(path.join(DIST_DIR, file), content);
      console.log(`  ✓ ${file}`);
    } catch (error) {
      console.warn(`  Warning: Could not copy ${file}:`, error.message);
    }
  }
}

/**
 * Main build function
 */
async function build() {
  console.log('Building Mozilla components for web...\n');
  
  // Clean dist directory
  try {
    await fs.rm(DIST_DIR, { recursive: true, force: true });
    console.log('Cleaned dist directory');
  } catch (error) {
    // Directory might not exist, that's ok
  }
  
  await fs.mkdir(DIST_DIR, { recursive: true });
  
  // Step 1: Copy files from Firefox source
  await copyWidgetFilesFromFirefox();
  
  // Step 2: Build shared files (lit-utils, CSS, vendor)
  await buildSharedFiles();
  
  // Step 3: Build all moz-* components
  await buildComponents();
  
  // Step 4: Generate index file
  await generateIndex();
  
  // Step 5: Copy demo files
  await copyDemoFiles();
  
  console.log('\n✓ Build complete!');
}

// Run build
build().catch(console.error);