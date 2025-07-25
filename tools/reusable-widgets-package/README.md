# Reusable Firefox Widgets Package

This package provides web-compatible versions of Mozilla Firefox's internal UI components, automatically built from the Firefox source code in the toolkit/content/widgets directory.

## Components

### moz-label

An enhanced label element that provides:
- Accesskey styling and keyboard navigation
- Automatic underlining of accesskeys
- Smart accesskey formatting (appends in parentheses if not found in text)
- Platform-specific behavior (e.g., no underlining on macOS by default)

## Usage

```javascript
import './dist/moz-label.js';

// Or import the class directly
import { MozTextLabel } from './dist/moz-label.mjs';
```

```html
<label is="moz-label" accesskey="n" for="name">Name:</label>
<input type="text" id="name">
```

## Building

This package builds directly from Firefox source code:

```bash
npm run build
```

The build script:
1. Reads components from the Firefox source tree
2. Transforms Firefox-specific APIs to web-compatible alternatives
3. Embeds CSS directly (replacing chrome:// URLs)
4. Adds necessary shims for Services.prefs and other Firefox APIs

## Configuration

You can configure component behavior:

```javascript
import { MozTextLabel } from './dist/moz-label.mjs';

// Configure preferences
window.Services.prefs.getIntPref = (name, defaultValue) => {
  if (name === 'ui.key.menuAccessKey') {
    return 1; // Force accesskey underlining
  }
  return defaultValue;
};
```

## Adding New Components

Edit `build.js` and add new components to the `COMPONENTS` object:

```javascript
const COMPONENTS = {
  'moz-label': {
    source: '../../toolkit/content/widgets/moz-label/moz-label.mjs',
    css: '../../toolkit/content/widgets/moz-label/moz-label.css',
    exports: ['MozTextLabel']
  },
  // Add new component here
};
```

## Firefox API Shims

The package includes shims for:
- `Services.prefs` - Preference system
- `Ci.nsIPrefLocalizedString` - Localized strings
- Platform detection via `navigator.platform`

These shims provide sensible defaults for web usage while maintaining API compatibility.