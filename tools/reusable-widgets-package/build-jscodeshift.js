#!/usr/bin/env node

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { transformFile } from './transform-chrome-urls.js';
import { transformCssFile } from './transform-css.js';
import { transformCssToLitStyles, transformChromeUrls } from './transform-css-inline.js';
import { transformFile as transformFileWithStyles } from './transform-chrome-urls-with-styles.js';
import postcss from 'postcss';
import postcssImport from 'postcss-import';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIREFOX_TOOLKIT_PATH = path.join(__dirname, '../../toolkit/content/widgets');
const DIST_DIR = path.join(__dirname, 'dist');

// Feature flag: inline styles as Lit css templates (default: true)
const INLINE_STYLES = process.env.INLINE_STYLES !== 'false';

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
  console.log('Building Mozilla components for web...');
  console.log(`Style mode: ${INLINE_STYLES ? 'Inline Lit styles' : 'External stylesheets'}\n`);
  
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
      dest: path.join(DIST_DIR, 'design-system/text-and-typography.css')
    },
    {
      source: path.join(__dirname, '../../toolkit/themes/shared/design-system/tokens-brand.css'),
      dest: path.join(DIST_DIR, 'design-system/tokens-brand.css')
    },
    {
      source: path.join(__dirname, '../../toolkit/themes/shared/design-system/tokens-shared.css'),
      dest: path.join(DIST_DIR, 'design-system/tokens-shared.css')
    }
  ];
  
  for (const file of filesToCopy) {
    try {
      // Ensure destination directory exists
      await fs.mkdir(path.dirname(file.dest), { recursive: true });
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
  
  // Step 4: Prepare helpers
  const helpers = { 
    getRelativePath, 
    resolveChromeUrl,
    trackIcon: (chromeUrl) => buildMetadata.icons.add(chromeUrl)
  };
  
  // Step 5: If inline styles is enabled, collect component styles
  const componentStyles = {};
  if (INLINE_STYLES) {
    console.log('\nCollecting component styles for inlining...');
    
    // Chrome URL to file path mappings for CSS
    const cssChromeMappings = {
      'chrome://global/skin/design-system/tokens-brand.css': path.join(__dirname, '../../toolkit/themes/shared/design-system/tokens-brand.css'),
      'chrome://global/skin/design-system/text-and-typography.css': path.join(__dirname, '../../toolkit/themes/shared/design-system/text-and-typography.css'),
      'chrome://global/skin/design-system/tokens-shared.css': path.join(__dirname, '../../toolkit/themes/shared/design-system/tokens-shared.css'),
      'chrome://global/skin/in-content/common-shared.css': path.join(__dirname, '../../toolkit/themes/shared/in-content/common-shared.css'),
    };
    
    // First, load and transform common CSS
    const commonCssPath = cssChromeMappings['chrome://global/skin/in-content/common-shared.css'];
    let commonCss = '';
    try {
      const commonCssContent = await fs.readFile(commonCssPath, 'utf-8');
      
      // Create a resolver for chrome:// URLs in CSS imports
      const resolve = (id, basedir, importOptions) => {
        // postcss-import passes the URL without the url() wrapper
        console.log(`      Resolving import: ${id}`);
        if (id.startsWith('chrome://') && cssChromeMappings[id]) {
          console.log(`        Resolved to: ${cssChromeMappings[id]}`);
          return cssChromeMappings[id];
        }
        return id;
      };
      
      // Transform chrome URLs in @import statements using PostCSS AST
      console.log('    Transforming chrome URLs in common CSS...');
      
      // Create a PostCSS plugin to transform chrome URLs in @import rules
      const transformImports = () => {
        return {
          postcssPlugin: 'transform-imports',
          AtRule: {
            import(atRule) {
              // Extract the URL from the import
              const match = atRule.params.match(/url\(["']?([^"'\)]+)["']?\)/);
              if (match) {
                const url = match[1];
                if (url.startsWith('chrome://') && cssChromeMappings[url]) {
                  console.log(`      Found import: ${url}`);
                  console.log(`      Replacing with: ${cssChromeMappings[url]}`);
                  atRule.params = `url("${cssChromeMappings[url]}")`;
                }
              }
            }
          }
        };
      };
      transformImports.postcss = true;
      
      const transformed = await postcss([transformImports]).process(commonCssContent, { from: commonCssPath });
      const transformedCommonCss = transformed.css;
      
      // Now inline imports with postcss-import
      console.log('    Processing common CSS imports...');
      
      // We need to transform chrome URLs in nested imports too
      const commonInlined = await postcss([
        postcssImport({
          root: path.dirname(commonCssPath),
          resolve: (id, basedir, importOptions) => {
            // Handle chrome:// URLs
            if (id.startsWith('chrome://') && cssChromeMappings[id]) {
              console.log(`      Resolving nested import: ${id}`);
              console.log(`        -> ${cssChromeMappings[id]}`);
              return cssChromeMappings[id];
            }
            // If it's already an absolute path, use it
            if (path.isAbsolute(id)) {
              return id;
            }
            // Otherwise resolve relative to basedir
            return path.resolve(basedir, id);
          },
          load: async (filename, importOptions) => {
            const css = await fs.readFile(filename, 'utf-8');
            // Transform any chrome:// URLs in the loaded CSS before it gets processed
            const transformed = await postcss([transformImports()]).process(css, { from: filename });
            return transformed.css;
          }
        })
      ]).process(transformedCommonCss, { from: commonCssPath });
      console.log('    Common CSS imports processed');
      
      // Then transform any remaining chrome:// URLs in the inlined content
      const commonTransformed = await postcss([
        transformChromeUrls({
          ...helpers,
          filePath: commonCssPath,
          fileMap
        })
      ]).process(commonInlined.css, { from: commonCssPath });
      
      commonCss = commonTransformed.css;
      console.log('    ✓ Loaded common styles');
      // Check if common CSS still has any @import statements
      if (commonCss.includes('@import')) {
        console.warn('    ⚠ Common CSS still contains @import statements!');
        const imports = commonCss.match(/@import[^;]+;/g);
        if (imports) {
          imports.forEach(imp => console.warn(`      ${imp}`));
        }
      }
    } catch (e) {
      console.warn('    ⚠ Could not load common-shared.css:', e.message);
      console.warn('      Full error:', e);
    }
    
    // Collect all component CSS files and transform them
    async function collectComponentStyles(dir) {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory() && entry.name.startsWith('moz-')) {
          // Check the Firefox source file for insertStylesheetIfNeeded
          const firefoxMjsPath = path.join(FIREFOX_TOOLKIT_PATH, entry.name, `${entry.name}.mjs`);
          try {
            const mjsContent = await fs.readFile(firefoxMjsPath, 'utf-8');
            const styleSheetMatch = mjsContent.match(/insertStylesheetIfNeeded\s*\(\s*[^,]+,\s*["']([^"']+)["']/);
            
            if (styleSheetMatch) {
              const stylesheetUrl = styleSheetMatch[1];
              // Look for CSS file in dist
              const cssPath = path.join(fullPath, `${entry.name}.css`);
              try {
                await fs.access(cssPath);
                // Transform and inline the CSS with common styles prepended
                // Pass the chrome mappings so CSS imports can be resolved
                const helpersWithMappings = {
                  ...helpers,
                  cssChromeMappings
                };
                const result = await transformCssToLitStyles(cssPath, fileMap, helpersWithMappings, commonCss);
                componentStyles[stylesheetUrl] = result;
                console.log(`    ✓ Collected styles for ${entry.name} (${stylesheetUrl})`);
              } catch (e) {
                console.warn(`    ⚠ CSS file not found for ${entry.name}: ${e.message}`);
                console.warn(`      Looking for: ${cssPath}`);
              }
            }
          } catch (e) {
            // No mjs file in Firefox source or can't read it
          }
          
          await collectComponentStyles(fullPath);
        }
      }
    }
    
    await collectComponentStyles(DIST_DIR);
    console.log(`\nCollected ${Object.keys(componentStyles).length} component styles:`, Object.keys(componentStyles));
  }
  
  // Step 6: Transform files
  console.log('\nTransforming files...');
  
  // Main transformation pass
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
        
        // Transform with appropriate transformer
        if (INLINE_STYLES) {
          const transformed = await transformFileWithStyles(fullPath, fileMap, helpers, componentStyles);
          if (transformed) {
            buildMetadata.filesProcessed.push(relativePath);
          }
        } else {
          const transformed = await transformFile(fullPath, fileMap, helpers);
          if (transformed) {
            buildMetadata.filesProcessed.push(relativePath);
          }
        }
      } else if (entry.name.endsWith('.css')) {
        // Only transform standalone CSS files if not using inline styles
        // or if it's not a component CSS file
        const isComponentCss = fullPath.includes('/moz-') && path.basename(fullPath) === path.basename(path.dirname(fullPath)) + '.css';
        
        if (!INLINE_STYLES || !isComponentCss) {
          const relativePath = path.relative(DIST_DIR, fullPath);
          const transformed = await transformCssFile(fullPath, fileMap, helpers);
          if (transformed) {
            buildMetadata.filesProcessed.push(relativePath);
          }
        }
      }
    }
  }
  
  await transformDirectory(DIST_DIR);
  console.log(`  ✓ Processed ${buildMetadata.filesProcessed.length} files`);
  
  // Step 7: Generate index
  await generateIndex();
  
  // Step 8: Copy demo files
  console.log('\nCopying demo files...');
  const demoFiles = ['example.html', 'moz-button.html','kitchensink.html'];
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
  
  // Step 9: Copy icons
  await copyIcons();
  
  // Step 10: Write build metadata
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