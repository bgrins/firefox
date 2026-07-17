/* Generated file — do not edit. Built from
 * https://github.com/mozilla/firefox-devtools-mcp (extension/build-moz.mjs).
 * Dual-licensed MIT OR Apache-2.0; see LICENSE-MIT / LICENSE-APACHE upstream. */
var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __esm = (fn, res) => function __init() {
  return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
};
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// src/moz-shim.ts
function configure(env) {
  browser = {
    bidi: env.bidi,
    runtime: {
      getBrowserInfo: async () => ({ version: env.version })
    }
  };
  setTimeout = env.setTimeout;
  clearTimeout = env.clearTimeout;
}
var browser, setTimeout, clearTimeout;
var init_moz_shim = __esm({
  "src/moz-shim.ts"() {
    "use strict";
  }
});

// ../src/firefox/snapshot/formatter.ts
var formatter_exports = {};
__export(formatter_exports, {
  formatSnapshotTree: () => formatSnapshotTree
});
function formatSnapshotTree(node, depth = 0, options = {}) {
  const { includeAttributes = true, includeText = true, maxDepth } = options;
  if (maxDepth !== void 0 && depth >= maxDepth) {
    return "";
  }
  const indent = "  ".repeat(depth);
  const attrs = [];
  attrs.push(`uid=${node.uid}`);
  const role = node.role || node.tag;
  attrs.push(role);
  if (node.name) {
    attrs.push(`"${truncate(node.name, MAX_ATTR_LENGTH)}"`);
  }
  if (node.role && node.role !== node.tag) {
    attrs.push(`tag=${node.tag}`);
  }
  if (node.value) {
    attrs.push(`value="${truncate(node.value, MAX_ATTR_LENGTH)}"`);
  }
  if (node.href) {
    attrs.push(`href="${truncate(node.href, MAX_ATTR_LENGTH)}"`);
  }
  if (node.src) {
    attrs.push(`src="${truncate(node.src, MAX_ATTR_LENGTH)}"`);
  }
  if (includeText && node.text) {
    attrs.push(`text="${truncate(node.text, MAX_ATTR_LENGTH)}"`);
  }
  if (includeAttributes && node.aria) {
    if (node.aria.disabled) {
      attrs.push("disabled");
    }
    if (node.aria.hidden) {
      attrs.push("hidden");
    }
    if (node.aria.selected) {
      attrs.push("selected");
    }
    if (node.aria.expanded !== void 0) {
      attrs.push(node.aria.expanded ? "expanded" : "collapsed");
    }
    if (node.aria.checked !== void 0) {
      if (node.aria.checked === "mixed") {
        attrs.push('checked="mixed"');
      } else {
        attrs.push(node.aria.checked ? "checked" : "unchecked");
      }
    }
    if (node.aria.pressed !== void 0) {
      if (node.aria.pressed === "mixed") {
        attrs.push('pressed="mixed"');
      } else {
        attrs.push(node.aria.pressed ? "pressed" : "unpressed");
      }
    }
    if (node.aria.autocomplete) {
      attrs.push(`autocomplete="${node.aria.autocomplete}"`);
    }
    if (node.aria.haspopup) {
      attrs.push(`haspopup="${node.aria.haspopup}"`);
    }
    if (node.aria.invalid) {
      attrs.push(`invalid="${node.aria.invalid}"`);
    }
    if (node.aria.level) {
      attrs.push(`level=${node.aria.level}`);
    }
  }
  if (includeAttributes && node.computed) {
    if (node.computed.focusable) {
      attrs.push("focusable");
    }
    if (node.computed.interactive) {
      attrs.push("interactive");
    }
    if (!node.computed.visible) {
      attrs.push("invisible");
    }
    if (!node.computed.accessible) {
      attrs.push("inaccessible");
    }
  }
  if (node.isIframe) {
    attrs.push("[iframe");
    if (node.frameSrc) {
      attrs.push(`src="${truncate(node.frameSrc, MAX_ATTR_LENGTH)}"`);
    }
    if (node.crossOrigin) {
      attrs.push("cross-origin");
    }
    attrs.push("]");
  }
  let result = indent + attrs.join(" ") + "\n";
  for (const child of node.children) {
    result += formatSnapshotTree(child, depth + 1, options);
  }
  return result;
}
function truncate(str, maxLen) {
  if (str.length <= maxLen) {
    return str;
  }
  return str.substring(0, maxLen - 3) + "...";
}
var MAX_ATTR_LENGTH;
var init_formatter = __esm({
  "../src/firefox/snapshot/formatter.ts"() {
    "use strict";
    init_moz_shim();
    MAX_ATTR_LENGTH = 30;
  }
});

// dist/snapshot.injected.txt
var snapshot_injected_default;
var init_snapshot_injected = __esm({
  "dist/snapshot.injected.txt"() {
    snapshot_injected_default = '"use strict";\nvar __SnapshotInjected = (() => {\n  var __defProp = Object.defineProperty;\n  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;\n  var __getOwnPropNames = Object.getOwnPropertyNames;\n  var __hasOwnProp = Object.prototype.hasOwnProperty;\n  var __export = (target, all) => {\n    for (var name in all)\n      __defProp(target, name, { get: all[name], enumerable: true });\n  };\n  var __copyProps = (to, from, except, desc) => {\n    if (from && typeof from === "object" || typeof from === "function") {\n      for (let key of __getOwnPropNames(from))\n        if (!__hasOwnProp.call(to, key) && key !== except)\n          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });\n    }\n    return to;\n  };\n  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);\n\n  // ../src/firefox/snapshot/injected/snapshot.injected.ts\n  var snapshot_injected_exports = {};\n  __export(snapshot_injected_exports, {\n    createSnapshot: () => createSnapshot\n  });\n\n  // ../src/firefox/snapshot/injected/elementCollector.ts\n  var INTERACTIVE_TAGS = [\n    "a",\n    "button",\n    "input",\n    "select",\n    "textarea",\n    "img",\n    "video",\n    "audio",\n    "iframe"\n  ];\n  var SEMANTIC_TAGS = ["nav", "main", "section", "article", "header", "footer", "form"];\n  var CONTAINER_TAGS = ["div", "span", "p", "li", "ul", "ol"];\n  var MAX_DIRECT_TEXT_CONTENT = 500;\n  function isVisible(el) {\n    if (el?.nodeType !== Node.ELEMENT_NODE) {\n      return false;\n    }\n    let current = el;\n    while (current && current !== document.documentElement) {\n      try {\n        const style = window.getComputedStyle(current);\n        const opacity = parseFloat(style.opacity);\n        if (style.display === "none" || style.visibility === "hidden" || opacity === 0 || isNaN(opacity)) {\n          return false;\n        }\n      } catch {\n        return false;\n      }\n      current = current.parentElement;\n    }\n    return true;\n  }\n  function getDirectTextContent(el) {\n    let text = "";\n    for (let i = 0; i < el.childNodes.length; i++) {\n      const node = el.childNodes[i];\n      if (node?.nodeType === Node.TEXT_NODE) {\n        text += node.textContent || "";\n      }\n    }\n    return text.trim();\n  }\n  function hasInteractiveDescendant(el) {\n    for (let i = 0; i < el.children.length; i++) {\n      const child = el.children[i];\n      if (child) {\n        const tag = child.tagName.toLowerCase();\n        if (INTERACTIVE_TAGS.indexOf(tag) !== -1 || child.hasAttribute("role")) {\n          return true;\n        }\n      }\n    }\n    return false;\n  }\n  function isRelevant(el) {\n    if (el?.nodeType !== Node.ELEMENT_NODE) {\n      return false;\n    }\n    if (!isVisible(el)) {\n      return false;\n    }\n    const tag = el.tagName.toLowerCase();\n    if (INTERACTIVE_TAGS.indexOf(tag) !== -1) {\n      return true;\n    }\n    if (el.hasAttribute("role")) {\n      return true;\n    }\n    if (el.hasAttribute("aria-label")) {\n      return true;\n    }\n    if (/^h[1-6]$/.test(tag)) {\n      return true;\n    }\n    if (SEMANTIC_TAGS.indexOf(tag) !== -1) {\n      return true;\n    }\n    if (CONTAINER_TAGS.indexOf(tag) !== -1) {\n      const directText = getDirectTextContent(el);\n      if (directText.length > 0 && directText.length < MAX_DIRECT_TEXT_CONTENT) {\n        return true;\n      }\n      if (el.id || el.className) {\n        return true;\n      }\n      if (hasInteractiveDescendant(el)) {\n        return true;\n      }\n    }\n    return false;\n  }\n  function isFocusable(el) {\n    const htmlEl = el;\n    if (htmlEl.tabIndex >= 0) {\n      return true;\n    }\n    const tag = el.tagName.toLowerCase();\n    if (["a", "button", "input", "select", "textarea"].indexOf(tag) !== -1) {\n      return true;\n    }\n    return false;\n  }\n  function isInteractive(el) {\n    const tag = el.tagName.toLowerCase();\n    if (INTERACTIVE_TAGS.indexOf(tag) !== -1) {\n      return true;\n    }\n    const role = el.getAttribute("role");\n    if (role && ["button", "link", "menuitem", "tab"].indexOf(role) !== -1) {\n      return true;\n    }\n    if (el.hasAttribute("onclick")) {\n      return true;\n    }\n    return false;\n  }\n\n  // ../src/firefox/snapshot/injected/attributeCollector.ts\n  var MAX_TEXT_LENGTH = 100;\n  function getElementName(el) {\n    if (el.hasAttribute("aria-label")) {\n      return el.getAttribute("aria-label") || void 0;\n    }\n    const htmlEl = el;\n    const elId = htmlEl.id;\n    if (elId) {\n      const label = document.querySelector(`label[for="${elId}"]`);\n      if (label?.textContent) {\n        return label.textContent.trim();\n      }\n    }\n    if (el.hasAttribute("placeholder")) {\n      return el.getAttribute("placeholder") || void 0;\n    }\n    if (el.hasAttribute("title")) {\n      return el.getAttribute("title") || void 0;\n    }\n    if (el.hasAttribute("alt")) {\n      return el.getAttribute("alt") || void 0;\n    }\n    const tag = el.tagName.toLowerCase();\n    if (["button", "a", "h1", "h2", "h3", "h4", "h5", "h6"].indexOf(tag) !== -1) {\n      return getTextContent(el);\n    }\n    return void 0;\n  }\n  function getTextContent(el) {\n    let text = "";\n    for (let i = 0; i < el.childNodes.length; i++) {\n      const node = el.childNodes[i];\n      if (node?.nodeType === Node.TEXT_NODE) {\n        text += node.textContent || "";\n      }\n    }\n    const trimmed = text.trim();\n    if (!trimmed) {\n      return void 0;\n    }\n    return trimmed.substring(0, MAX_TEXT_LENGTH);\n  }\n  function getAriaAttributes(el) {\n    const aria = {};\n    let hasAny = false;\n    const booleanAttrs = [\n      "disabled",\n      "hidden",\n      "selected",\n      "expanded"\n    ];\n    for (const attr of booleanAttrs) {\n      const value = el.getAttribute(`aria-${attr}`);\n      if (value !== null) {\n        aria[attr] = value === "true";\n        hasAny = true;\n      }\n    }\n    const mixedAttrs = ["checked", "pressed"];\n    for (const attr of mixedAttrs) {\n      const value = el.getAttribute(`aria-${attr}`);\n      if (value !== null) {\n        if (value === "mixed") {\n          aria[attr] = "mixed";\n        } else {\n          aria[attr] = value === "true";\n        }\n        hasAny = true;\n      }\n    }\n    const stringAttrs = ["autocomplete", "haspopup", "invalid", "label", "labelledby", "describedby", "controls"];\n    for (const attr of stringAttrs) {\n      const value = el.getAttribute(`aria-${attr}`);\n      if (value) {\n        if (attr === "haspopup" || attr === "invalid") {\n          aria[attr] = value;\n        } else {\n          aria[attr] = value;\n        }\n        hasAny = true;\n      }\n    }\n    const levelValue = el.getAttribute("aria-level");\n    if (levelValue) {\n      const level = parseInt(levelValue, 10);\n      if (!isNaN(level)) {\n        aria.level = level;\n        hasAny = true;\n      }\n    }\n    return hasAny ? aria : void 0;\n  }\n  function getComputedProperties(el) {\n    const computed = {};\n    try {\n      const style = window.getComputedStyle(el);\n      const opacity = parseFloat(style.opacity);\n      computed.visible = style.display !== "none" && style.visibility !== "hidden" && opacity !== 0 && !isNaN(opacity);\n    } catch {\n      computed.visible = false;\n    }\n    computed.accessible = computed.visible && !el.getAttribute("aria-hidden");\n    computed.focusable = isFocusable(el);\n    computed.interactive = isInteractive(el);\n    return computed;\n  }\n\n  // ../src/firefox/snapshot/injected/selectorGenerator.ts\n  var PREFERRED_ID_ATTRS = ["id", "data-testid", "data-test-id"];\n  var MAX_SEGMENT_LENGTH = 64;\n  function generateCssSelector(el) {\n    const path = [];\n    let current = el;\n    while (current?.nodeType === Node.ELEMENT_NODE) {\n      let selector = current.nodeName.toLowerCase();\n      let hasId = false;\n      for (const idAttr of PREFERRED_ID_ATTRS) {\n        const value = current.getAttribute(idAttr);\n        if (value) {\n          if (idAttr === "id") {\n            selector += "#" + CSS.escape(value);\n          } else {\n            selector += `[${idAttr}="${escapeCssAttributeValue(value)}"]`;\n          }\n          path.unshift(selector);\n          hasId = true;\n          break;\n        }\n      }\n      if (hasId) {\n        break;\n      }\n      const ariaLabel = current.getAttribute("aria-label");\n      const role = current.getAttribute("role");\n      if (ariaLabel && role) {\n        selector += `[role="${role}"][aria-label="${escapeCssAttributeValue(ariaLabel)}"]`;\n        path.unshift(selector);\n        current = current.parentElement;\n        continue;\n      }\n      const siblings = current.parentElement?.children;\n      if (siblings && siblings.length > 1) {\n        let nth = 1;\n        for (let i = 0; i < siblings.length; i++) {\n          const sibling = siblings[i];\n          if (!sibling) {\n            continue;\n          }\n          if (sibling === current) {\n            break;\n          }\n          if (sibling.nodeName === current.nodeName) {\n            nth++;\n          }\n        }\n        if (nth > 1 || siblings.length > 1 && siblings[0] !== current) {\n          selector += `:nth-of-type(${nth})`;\n        }\n      }\n      path.unshift(truncateSegment(selector));\n      current = current.parentElement;\n      if (current?.nodeName.toLowerCase() === "body") {\n        path.unshift("body");\n        break;\n      }\n    }\n    return path.join(" > ");\n  }\n  function generateXPath(el) {\n    const id = el.id;\n    if (id) {\n      return `//*[@id="${escapeXPathValue(id)}"]`;\n    }\n    const path = [];\n    let current = el;\n    while (current?.nodeType === Node.ELEMENT_NODE) {\n      const tagName = current.nodeName.toLowerCase();\n      let index = 1;\n      let sibling = current.previousElementSibling;\n      while (sibling) {\n        if (sibling.nodeName.toLowerCase() === tagName) {\n          index++;\n        }\n        sibling = sibling.previousElementSibling;\n      }\n      const parent = current.parentElement;\n      let needsIndex = false;\n      if (parent) {\n        const siblingsOfSameType = Array.from(parent.children).filter(\n          (child) => child.nodeName.toLowerCase() === tagName\n        );\n        needsIndex = siblingsOfSameType.length > 1;\n      }\n      const pathSegment = needsIndex ? `${tagName}[${index}]` : tagName;\n      path.unshift(pathSegment);\n      current = current.parentElement;\n      if (current?.nodeName.toLowerCase() === "html") {\n        path.unshift("html");\n        break;\n      }\n    }\n    return "/" + path.join("/");\n  }\n  function escapeCssAttributeValue(value) {\n    return value.replace(/"/g, \'\\\\"\').substring(0, MAX_SEGMENT_LENGTH);\n  }\n  function escapeXPathValue(value) {\n    if (value.indexOf(\'"\') === -1) {\n      return value;\n    }\n    if (value.indexOf("\'") === -1) {\n      return value;\n    }\n    const parts = value.split(\'"\').map((part, idx, arr) => {\n      if (idx === arr.length - 1) {\n        return part ? `"${part}"` : "";\n      }\n      return part ? `"${part}",\'"\'` : `"\'"`;\n    });\n    return `concat(${parts.filter((p) => p).join(",")})`;\n  }\n  function truncateSegment(segment) {\n    if (segment.length <= MAX_SEGMENT_LENGTH) {\n      return segment;\n    }\n    return segment.substring(0, MAX_SEGMENT_LENGTH);\n  }\n\n  // ../src/firefox/snapshot/injected/treeWalker.ts\n  var MAX_DEPTH = 10;\n  var MAX_NODES = 1e3;\n  function walkTree(rootElement, snapshotId, options = {}) {\n    const { includeAll = false, includeIframes = true } = options;\n    let counter = 0;\n    const uidMap = [];\n    let truncated = false;\n    function walk(el, depth) {\n      if (depth > MAX_DEPTH) {\n        truncated = true;\n        return { node: null, relevantChildren: [] };\n      }\n      if (counter >= MAX_NODES) {\n        truncated = true;\n        return { node: null, relevantChildren: [] };\n      }\n      const tag = el.tagName.toLowerCase();\n      const isRoot = tag === "body" || tag === "html";\n      let elementIsRelevant;\n      if (includeAll) {\n        elementIsRelevant = isRoot || isVisible(el);\n      } else {\n        elementIsRelevant = isRoot || isRelevant(el);\n      }\n      const childResults = [];\n      if (tag === "iframe" && includeIframes && elementIsRelevant) {\n        try {\n          const iframe = el;\n          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;\n          if (iframeDoc?.body) {\n            const iframeResult = walk(iframeDoc.body, depth + 1);\n            if (iframeResult.node) {\n              iframeResult.node.isIframe = true;\n              iframeResult.node.frameSrc = iframe.src;\n              childResults.push(iframeResult.node);\n            }\n          }\n        } catch {\n        }\n      } else {\n        for (let i = 0; i < el.children.length; i++) {\n          if (counter >= MAX_NODES) {\n            truncated = true;\n            break;\n          }\n          const child = el.children[i];\n          if (!child) {\n            continue;\n          }\n          const childResult = walk(child, depth + 1);\n          if (childResult.node) {\n            childResults.push(childResult.node);\n          } else if (childResult.relevantChildren.length > 0) {\n            childResults.push(...childResult.relevantChildren);\n          }\n        }\n      }\n      if (!elementIsRelevant) {\n        return { node: null, relevantChildren: childResults };\n      }\n      const uid = `${snapshotId}_${counter++}`;\n      const css = generateCssSelector(el);\n      const xpath = generateXPath(el);\n      uidMap.push({ uid, css, xpath });\n      const htmlEl = el;\n      const roleAttr = el.getAttribute("role");\n      const nameAttr = getElementName(el);\n      const textAttr = getTextContent(el);\n      const valueAttr = htmlEl.value;\n      const hrefAttr = htmlEl.href;\n      const srcAttr = htmlEl.src;\n      const ariaAttr = getAriaAttributes(el);\n      const computedAttr = getComputedProperties(el);\n      const node = {\n        uid,\n        tag,\n        ...roleAttr && { role: roleAttr },\n        ...nameAttr && { name: nameAttr },\n        ...valueAttr && { value: valueAttr },\n        ...hrefAttr && { href: hrefAttr },\n        ...srcAttr && { src: srcAttr },\n        ...textAttr && { text: textAttr },\n        ...ariaAttr && { aria: ariaAttr },\n        ...computedAttr && { computed: computedAttr },\n        children: childResults\n      };\n      if (tag === "iframe" && includeIframes) {\n        try {\n          const iframe = el;\n          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;\n          if (!iframeDoc?.body) {\n            node.isIframe = true;\n            node.frameSrc = iframe.src;\n            node.crossOrigin = true;\n          }\n        } catch {\n          node.isIframe = true;\n          node.frameSrc = el.src;\n          node.crossOrigin = true;\n        }\n      }\n      return { node, relevantChildren: [] };\n    }\n    const result = walk(rootElement, 0);\n    return {\n      tree: result.node,\n      uidMap,\n      truncated\n    };\n  }\n\n  // ../src/firefox/snapshot/injected/snapshot.injected.ts\n  function createSnapshot(snapshotId, options) {\n    try {\n      let rootElement = document.body;\n      if (options?.selector) {\n        try {\n          const selected = document.querySelector(options.selector);\n          if (!selected) {\n            return {\n              tree: null,\n              uidMap: [],\n              truncated: false,\n              selectorError: `Selector "${options.selector}" not found`\n            };\n          }\n          rootElement = selected;\n        } catch {\n          return {\n            tree: null,\n            uidMap: [],\n            truncated: false,\n            selectorError: `Invalid selector syntax: "${options.selector}"`\n          };\n        }\n      }\n      const treeOptions = {\n        includeIframes: options?.includeIframes ?? true\n      };\n      if (options?.includeAll !== void 0) {\n        treeOptions.includeAll = options.includeAll;\n      }\n      const result = walkTree(rootElement, snapshotId, treeOptions);\n      if (!result.tree) {\n        throw new Error("Failed to generate tree");\n      }\n      return result;\n    } catch {\n      return {\n        tree: null,\n        uidMap: [],\n        truncated: false\n      };\n    }\n  }\n  if (typeof window !== "undefined") {\n    window.__createSnapshot = createSnapshot;\n  }\n  return __toCommonJS(snapshot_injected_exports);\n})();\n';
  }
});

// src/snapshot-source-moz.ts
async function getSnapshotSource() {
  return snapshot_injected_default;
}
var init_snapshot_source_moz = __esm({
  "src/snapshot-source-moz.ts"() {
    init_moz_shim();
    init_snapshot_injected();
  }
});

// src/client.ts
function guessResourceType(url) {
  const pathPart = url.split("?")[0];
  if (!pathPart) return "document";
  const parts = pathPart.split(".");
  const ext = (parts.length > 1 ? parts[parts.length - 1] || "" : "").toLowerCase();
  if (["js", "mjs"].includes(ext)) return "script";
  if (ext === "css") return "stylesheet";
  if (["jpg", "jpeg", "png", "gif", "webp", "svg", "ico"].includes(ext)) return "image";
  if (["woff", "woff2", "ttf", "eot"].includes(ext)) return "font";
  if (["mp4", "webm", "ogg"].includes(ext)) return "media";
  if (url.includes("/api/") || url.includes(".json")) return "xhr";
  return "document";
}
function parseHeaders(headers) {
  const result = {};
  const normalize = (value) => {
    if (value === null || value === void 0) return null;
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
    if (Array.isArray(value)) {
      const parts = value.map(normalize).filter((v) => !!v);
      return parts.length ? parts.join(", ") : null;
    }
    if (typeof value === "object") {
      const obj = value;
      if ("value" in obj) return normalize(obj.value);
      if ("bytes" in obj) return normalize(obj.bytes);
      try {
        return JSON.stringify(obj);
      } catch {
        return null;
      }
    }
    return null;
  };
  for (const h of headers) {
    const name = typeof h?.name === "string" ? h.name : null;
    const value = normalize(h?.value);
    if (name && value !== null) result[name] = value;
  }
  return result;
}
function serializeArg(a) {
  if (a === null || a === void 0) return { type: "null" };
  switch (typeof a) {
    case "string":
      return { type: "string", value: a };
    case "number":
      return { type: "number", value: a };
    case "boolean":
      return { type: "boolean", value: a };
    default:
      return {
        type: "object",
        value: Object.entries(a).map(([k, v]) => [k, serializeArg(v)])
      };
  }
}
function fromRemoteValue(v) {
  if (v == null) return void 0;
  switch (v.type) {
    case "undefined":
      return void 0;
    case "null":
      return null;
    case "string":
    case "boolean":
      return v.value;
    case "number":
      return typeof v.value === "string" ? Number(v.value) : v.value;
    case "array":
      return (v.value ?? []).map(fromRemoteValue);
    case "object": {
      const out = {};
      for (const [k, val] of v.value ?? []) out[typeof k === "string" ? k : String(fromRemoteValue(k))] = fromRemoteValue(val);
      return out;
    }
    default:
      return `[${v.type}]`;
  }
}
var sleep, ExtensionFirefoxClient;
var init_client = __esm({
  "src/client.ts"() {
    "use strict";
    init_moz_shim();
    init_formatter();
    init_snapshot_source_moz();
    sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    ExtensionFirefoxClient = class {
      tabs = [];
      selectedTabIdx = 0;
      currentContextId = null;
      consoleMessages = [];
      // Same record shape as upstream events/network.ts — the network tools filter and
      // sort on id/resourceType/isXHR/timings, so the fields must match exactly.
      networkRecords = /* @__PURE__ */ new Map();
      requestStartTimes = /* @__PURE__ */ new Map();
      uidMap = /* @__PURE__ */ new Map();
      snapshotContextId = null;
      currentSnapshotId = 0;
      injectedScript = null;
      firefoxVersion = null;
      // ---------- lifecycle ----------
      async connect() {
        await browser.bidi.subscribe([
          "log.entryAdded",
          "network.beforeRequestSent",
          "network.responseStarted",
          "network.responseCompleted",
          "browsingContext.load",
          "browsingContext.domContentLoaded"
        ]);
        try {
          await browser.bidi.subscribe(["moz:debugging.paused", "moz:debugging.resumed"]);
        } catch {
        }
        browser.bidi.onEvent.addListener((event) => this.onBidiEvent(event));
        const info = await browser.runtime.getBrowserInfo?.().catch(() => null);
        this.firefoxVersion = info?.version ?? null;
        await this.refreshTabs();
        if (this.tabs.length) this.currentContextId = this.tabs[0].actor;
      }
      onBidiEvent(event) {
        const d = event.data ?? {};
        switch (event.name) {
          case "log.entryAdded":
            this.consoleMessages.push({
              level: d.level ?? "info",
              text: d.text ?? (d.args ? JSON.stringify(d.args) : ""),
              timestamp: d.timestamp ?? Date.now(),
              source: d.source?.realm,
              args: d.args
            });
            if (this.consoleMessages.length > 1e3) this.consoleMessages.splice(0, 500);
            break;
          case "browsingContext.load":
          case "browsingContext.domContentLoaded":
            this.networkRecords.clear();
            this.requestStartTimes.clear();
            if (d.context === this.snapshotContextId) this.clearSnapshot();
            break;
          case "network.beforeRequestSent": {
            const requestId = d.request?.request;
            if (!requestId) break;
            this.requestStartTimes.set(requestId, Date.now());
            this.networkRecords.set(requestId, {
              id: requestId,
              url: d.request?.url || "",
              method: d.request?.method || "GET",
              timestamp: Date.now(),
              resourceType: guessResourceType(d.request?.url || ""),
              isXHR: d.initiator?.type === "xmlhttprequest" || d.initiator?.type === "fetch",
              requestHeaders: parseHeaders(d.request?.headers || []),
              timings: { requestTime: Date.now() }
            });
            if (this.networkRecords.size > 500) {
              for (const key of [...this.networkRecords.keys()].slice(0, 250)) this.networkRecords.delete(key);
            }
            break;
          }
          case "network.responseStarted": {
            const existing = this.networkRecords.get(d.request?.request);
            if (existing) {
              existing.status = d.response?.status;
              existing.statusText = d.response?.statusText || "";
              existing.responseHeaders = parseHeaders(d.response?.headers || []);
            }
            break;
          }
          case "network.responseCompleted": {
            const requestId = d.request?.request;
            const existing = this.networkRecords.get(requestId);
            const startTime = this.requestStartTimes.get(requestId);
            if (existing && startTime) {
              existing.timings.responseTime = Date.now();
              existing.timings.duration = Date.now() - startTime;
              if (!existing.status && d.response?.status) {
                existing.status = d.response.status;
                existing.statusText = d.response.statusText || "";
              }
            }
            this.requestStartTimes.delete(requestId);
            break;
          }
          case "moz:debugging.paused": {
            const id = this.findLogpointByLocation(d.url, d.line);
            if (id) void this.handleLogpointPause(d.context, id);
            break;
          }
        }
      }
      // ---------- BiDi plumbing ----------
      async sendBiDiCommand(method, params = {}) {
        const dot = method.lastIndexOf(".");
        return browser.bidi.send(method.slice(0, dot), method.slice(dot + 1), params);
      }
      context() {
        if (!this.currentContextId) throw new Error("No tab selected");
        return this.currentContextId;
      }
      async callFunction(fn, args2 = [], context = this.context()) {
        const res = await browser.bidi.send("script", "callFunction", {
          functionDeclaration: fn,
          arguments: args2.map((a) => serializeArg(a)),
          target: { context },
          awaitPromise: true,
          resultOwnership: "none"
        });
        if (res.type === "exception") {
          throw new Error(res.exceptionDetails?.text ?? "Script threw");
        }
        return fromRemoteValue(res.result);
      }
      // Classic executeScript semantics: run a function body, JSON round-trip the result.
      async evaluate(script) {
        const wrapped = `function() {
      const r = (function() { ${script} })();
      if (r === undefined) return null;
      try { return JSON.parse(JSON.stringify(r)); } catch { return String(r); }
    }`;
        return this.callFunction(wrapped);
      }
      async getContent() {
        return await this.callFunction("function() { return document.documentElement.outerHTML; }");
      }
      // ---------- selector interactions ----------
      // Upstream dom.ts polls up to 5s for existence and visibility before interacting;
      // a one-shot lookup would click 0x0 rects of hidden/late elements.
      async selectorRect(selector) {
        const deadline = Date.now() + 5e3;
        let rect = null;
        for (; ; ) {
          rect = await this.callFunction(
            `function(sel) {
          const el = document.querySelector(sel);
          if (!el) return null;
          el.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
          const b = el.getBoundingClientRect();
          return { x: Math.round(b.x + b.width / 2), y: Math.round(b.y + b.height / 2), w: b.width, h: b.height };
        }`,
            [selector]
          );
          if (rect && rect.w > 0 && rect.h > 0) return { x: rect.x, y: rect.y };
          if (Date.now() > deadline) break;
          await sleep(100);
        }
        if (!rect) throw new Error(`No element matches selector: ${selector}`);
        throw new Error(`Element is not visible: ${selector}`);
      }
      // Upstream settles after input actions (rAF + 50ms) so follow-up snapshots see post-event state.
      async settle() {
        await this.callFunction("function() { return new Promise((r) => requestAnimationFrame(() => setTimeout(r, 50))); }").catch(() => {
        });
      }
      async performActions(actions) {
        await browser.bidi.send("input", "performActions", { context: this.context(), actions });
      }
      async clickAt(x, y, clickCount = 1) {
        const pointer = [{ type: "pointerMove", x, y }];
        for (let i = 0; i < clickCount; i++) {
          pointer.push({ type: "pointerDown", button: 0 }, { type: "pointerUp", button: 0 });
        }
        await this.performActions([{ type: "pointer", id: "mouse", actions: pointer }]);
      }
      async clickBySelector(selector, dblClick = false) {
        const { x, y } = await this.selectorRect(selector);
        await this.clickAt(x, y, dblClick ? 2 : 1);
        await this.settle();
      }
      async hoverBySelector(selector) {
        const { x, y } = await this.selectorRect(selector);
        await this.performActions([{ type: "pointer", id: "mouse", actions: [{ type: "pointerMove", x, y }] }]);
      }
      async fillBySelector(selector, text2) {
        const { x, y } = await this.selectorRect(selector);
        await this.clickAt(x, y);
        await this.callFunction(
          `function(sel) {
        const el = document.querySelector(sel);
        if (el && "value" in el) {
          el.value = "";
          el.dispatchEvent(new Event("input", { bubbles: true }));
        }
      }`,
          [selector]
        );
        const actions = [...text2].flatMap((ch) => [
          { type: "keyDown", value: ch },
          { type: "keyUp", value: ch }
        ]);
        await this.performActions([{ type: "key", id: "kb", actions }]);
        await this.settle();
      }
      async dragAndDropBySelectors(source, target) {
        await this.callFunction(
          `function(srcSel, dstSel) {
        const src = document.querySelector(srcSel);
        const dst = document.querySelector(dstSel);
        if (!src || !dst) throw new Error("drag: element not found");
        const dt = new DataTransfer();
        for (const [type, tgt] of [["dragstart", src], ["dragover", dst], ["drop", dst], ["dragend", src]]) {
          tgt.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt }));
        }
      }`,
          [source, target]
        );
      }
      async uploadFileBySelector(selector, filePath) {
        const res = await browser.bidi.send("script", "callFunction", {
          functionDeclaration: "function(sel) { return document.querySelector(sel); }",
          arguments: [{ type: "string", value: selector }],
          target: { context: this.context() },
          awaitPromise: false,
          resultOwnership: "root"
        });
        if (res.result?.type !== "node" || !res.result.sharedId) {
          throw new Error(`No element matches selector: ${selector}`);
        }
        await browser.bidi.send("input", "setFiles", {
          context: this.context(),
          element: { sharedId: res.result.sharedId },
          files: [filePath]
        });
      }
      // ---------- uid interactions ----------
      // Error wording matches upstream snapshot/resolver.ts — tool handlers substring-match
      // on 'stale'/'Snapshot'/'UID'/'not found' to produce friendly retry guidance.
      resolveUidToSelector(uid) {
        const uidSnapshotId = parseInt(uid.split("_")[0], 10);
        if (isNaN(uidSnapshotId)) throw new Error(`Invalid UID format: ${uid}`);
        if (uidSnapshotId !== this.currentSnapshotId) {
          throw new Error(
            `This uid is from a stale snapshot (snapshot ${uidSnapshotId}, current ${this.currentSnapshotId}). Take a fresh snapshot.`
          );
        }
        if (this.snapshotContextId !== this.currentContextId) {
          throw new Error("This uid is from a stale snapshot (different tab selected). Take a fresh snapshot.");
        }
        const entry = this.uidMap.get(uid);
        if (!entry) throw new Error(`UID not found: ${uid}. Take a fresh snapshot first.`);
        return entry.css;
      }
      // Upstream returns a Selenium WebElement; callers only use `await element.getId()`
      // (a BiDi sharedId), so a minimal shim keeps evaluate_script uid args working.
      async resolveUidToElement(uid) {
        const selector = this.resolveUidToSelector(uid);
        const res = await browser.bidi.send("script", "callFunction", {
          functionDeclaration: "function(sel) { return document.querySelector(sel); }",
          arguments: [{ type: "string", value: selector }],
          target: { context: this.context() },
          awaitPromise: false,
          resultOwnership: "root"
        });
        if (res.result?.type !== "node" || !res.result.sharedId) {
          throw new Error(`UID "${uid}" is stale: no element matches ${selector}`);
        }
        const sharedId = res.result.sharedId;
        return { getId: async () => sharedId };
      }
      async clickByUid(uid, dblClick = false) {
        await this.clickBySelector(this.resolveUidToSelector(uid), dblClick);
      }
      async hoverByUid(uid) {
        await this.hoverBySelector(this.resolveUidToSelector(uid));
      }
      async fillByUid(uid, value) {
        await this.fillBySelector(this.resolveUidToSelector(uid), value);
      }
      async dragByUidToUid(fromUid, toUid) {
        await this.dragAndDropBySelectors(this.resolveUidToSelector(fromUid), this.resolveUidToSelector(toUid));
      }
      async fillFormByUid(elements) {
        for (const { uid, value } of elements) await this.fillByUid(uid, value);
      }
      async uploadFileByUid(uid, filePath) {
        await this.uploadFileBySelector(this.resolveUidToSelector(uid), filePath);
      }
      // ---------- snapshot ----------
      async ensureInjected() {
        if (!this.injectedScript) {
          this.injectedScript = await getSnapshotSource();
        }
        const present = await this.callFunction("function() { return typeof window.__createSnapshot === 'function'; }");
        if (!present) {
          await browser.bidi.send("script", "evaluate", {
            expression: this.injectedScript,
            target: { context: this.context() },
            awaitPromise: false
          });
        }
      }
      async takeSnapshot(options) {
        await this.ensureInjected();
        const snapshotId = ++this.currentSnapshotId;
        const raw = await this.callFunction(
          "function(id, opts) { return JSON.stringify(window.__createSnapshot(id, opts)); }",
          [snapshotId, options ?? {}]
        );
        const result = JSON.parse(raw);
        if (result?.selectorError) throw new Error(result.selectorError);
        if (!result?.tree) throw new Error("Failed to generate snapshot");
        this.uidMap.clear();
        for (const entry of result.uidMap ?? []) this.uidMap.set(entry.uid, entry);
        this.snapshotContextId = this.currentContextId;
        return {
          text: formatSnapshotTree(result.tree),
          json: {
            root: result.tree,
            snapshotId,
            timestamp: Date.now(),
            truncated: result.truncated || false,
            uidMap: result.uidMap
          }
        };
      }
      clearSnapshot() {
        this.uidMap.clear();
        this.snapshotContextId = null;
      }
      // ---------- screenshots ----------
      async takeScreenshotPage() {
        const shot = await browser.bidi.send("browsingContext", "captureScreenshot", { context: this.context() });
        return shot.data;
      }
      async takeScreenshotByUid(uid) {
        const selector = this.resolveUidToSelector(uid);
        const rect = await this.callFunction(
          `function(sel) {
        const el = document.querySelector(sel);
        if (!el) return null;
        el.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
        const b = el.getBoundingClientRect();
        return { x: b.x, y: b.y, width: b.width, height: b.height };
      }`,
          [selector]
        );
        if (!rect || !rect.width || !rect.height) throw new Error(`Cannot screenshot uid "${uid}"`);
        const shot = await browser.bidi.send("browsingContext", "captureScreenshot", {
          context: this.context(),
          clip: { type: "box", ...rect }
        });
        return shot.data;
      }
      // ---------- console / network ----------
      // Upstream returns all contexts' messages/requests (no per-tab filtering).
      async getConsoleMessages() {
        return [...this.consoleMessages];
      }
      clearConsoleMessages() {
        this.consoleMessages.length = 0;
      }
      async startNetworkMonitoring() {
      }
      async stopNetworkMonitoring() {
      }
      async getNetworkRequests() {
        return [...this.networkRecords.values()];
      }
      clearNetworkRequests() {
        this.networkRecords.clear();
        this.requestStartTimes.clear();
      }
      // ---------- navigation / dialogs / viewport ----------
      async navigate(url) {
        const context = this.context();
        this.clearSnapshot();
        await browser.bidi.send("browsingContext", "navigate", { context, url, wait: "interactive" });
        await this.refreshTabs();
      }
      async navigateBack() {
        await browser.bidi.send("browsingContext", "traverseHistory", { context: this.context(), delta: -1 });
      }
      async navigateForward() {
        await browser.bidi.send("browsingContext", "traverseHistory", { context: this.context(), delta: 1 });
      }
      async setViewportSize(width, height) {
        await browser.bidi.send("browsingContext", "setViewport", { context: this.context(), viewport: { width, height } });
      }
      async acceptDialog(promptText) {
        try {
          await browser.bidi.send("browsingContext", "handleUserPrompt", {
            context: this.context(),
            accept: true,
            ...promptText != null ? { userText: promptText } : {}
          });
        } catch (e) {
          throw new Error(`Failed to accept dialog: ${e instanceof Error ? e.message : String(e)}`);
        }
      }
      async dismissDialog() {
        try {
          await browser.bidi.send("browsingContext", "handleUserPrompt", { context: this.context(), accept: false });
        } catch (e) {
          throw new Error(`Failed to dismiss dialog: ${e instanceof Error ? e.message : String(e)}`);
        }
      }
      // ---------- tabs ----------
      getTabs() {
        return this.tabs;
      }
      getSelectedTabIdx() {
        return this.selectedTabIdx;
      }
      async refreshTabs() {
        const tree = await browser.bidi.send("browsingContext", "getTree", {});
        this.tabs = (tree?.contexts ?? []).map((c) => ({
          actor: c.context,
          title: "",
          url: c.url ?? ""
        }));
        for (const tab of this.tabs) {
          tab.title = await this.callFunction("function() { return document.title; }", [], tab.actor).catch(() => "");
        }
        const idx = this.tabs.findIndex((t) => t.actor === this.currentContextId);
        this.selectedTabIdx = idx === -1 ? 0 : idx;
        if (idx === -1 && this.tabs.length) this.currentContextId = this.tabs[0].actor;
      }
      async selectTab(index) {
        if (!this.tabs[index]) throw new Error(`No tab at index ${index}`);
        this.currentContextId = this.tabs[index].actor;
        this.selectedTabIdx = index;
        await browser.bidi.send("browsingContext", "activate", { context: this.currentContextId }).catch(() => {
        });
      }
      async createNewPage(url) {
        const created = await browser.bidi.send("browsingContext", "create", { type: "tab" });
        this.currentContextId = created.context;
        await this.navigate(url);
        await this.refreshTabs();
        return this.selectedTabIdx;
      }
      async closeTab(index) {
        if (!this.tabs[index]) throw new Error(`No tab at index ${index}`);
        await browser.bidi.send("browsingContext", "close", { context: this.tabs[index].actor });
        await this.refreshTabs();
        if (this.tabs.length) {
          this.currentContextId = this.tabs[0].actor;
          this.selectedTabIdx = 0;
        }
      }
      // ---------- misc facade ----------
      getCurrentContextId() {
        return this.currentContextId;
      }
      setCurrentContextId(contextId) {
        this.currentContextId = contextId;
      }
      async isConnected() {
        return true;
      }
      getFirefoxVersion() {
        return this.firefoxVersion;
      }
      getOptions() {
        return { transport: "extension" };
      }
      getLogFilePath() {
        return null;
      }
      getDriver() {
        throw new Error("Selenium WebDriver is not available in the extension transport");
      }
      // Logpoints — ported from upstream events/debugging.ts, minus the Selenium socket.
      logpoints = /* @__PURE__ */ new Map();
      async setLogpoint(url, line, expression) {
        const result = await this.sendBiDiCommand("moz:debugging.setBreakpoint", {
          location: { url, line }
        });
        const logpointId = result.breakpoint;
        this.logpoints.set(logpointId, { expression, location: { url, line }, results: [], capped: false });
        return logpointId;
      }
      async removeLogpoint(logpointId) {
        await this.sendBiDiCommand("moz:debugging.removeBreakpoint", { breakpoint: logpointId });
        this.logpoints.delete(logpointId);
      }
      getLogpointResults(logpointId) {
        return this.logpoints.get(logpointId)?.results ?? null;
      }
      findLogpointByLocation(url, line) {
        for (const [id, entry] of this.logpoints) {
          if (entry.location.url === url && entry.location.line === line) return id;
        }
        return null;
      }
      async handleLogpointPause(contextId, logpointId) {
        const entry = this.logpoints.get(logpointId);
        if (!entry) return;
        try {
          const res = await this.sendBiDiCommand("script.evaluate", {
            expression: entry.expression,
            target: { context: contextId },
            awaitPromise: false
          });
          if (res.type === "exception") {
            entry.results.push({ value: null, error: res.exceptionDetails?.text ?? "Unknown error", timestamp: Date.now() });
          } else {
            entry.results.push({ value: res.result, timestamp: Date.now() });
          }
        } catch (error) {
          entry.results.push({ value: null, error: String(error), timestamp: Date.now() });
        } finally {
          if (entry.results.length > 100) {
            entry.results.splice(0, entry.results.length - 100);
            entry.capped = true;
          }
          await this.sendBiDiCommand("moz:debugging.resume", { context: contextId }).catch(() => {
          });
        }
      }
    };
  }
});

// src/provider.ts
var provider_exports = {};
__export(provider_exports, {
  args: () => args,
  getFirefox: () => getFirefox,
  getFirefoxIfRunning: () => getFirefoxIfRunning,
  resetFirefox: () => resetFirefox,
  setNextLaunchOptions: () => setNextLaunchOptions
});
async function getFirefox() {
  if (client) return client;
  connecting ??= (async () => {
    try {
      const c = new ExtensionFirefoxClient();
      await c.connect();
      client = c;
      return c;
    } catch (e) {
      connecting = null;
      throw e;
    }
  })();
  return connecting;
}
function getFirefoxIfRunning() {
  return client;
}
function resetFirefox() {
  client = null;
  connecting = null;
}
function setNextLaunchOptions() {
  throw new Error("Launch options are not applicable in the extension transport");
}
var client, connecting, args;
var init_provider = __esm({
  "src/provider.ts"() {
    "use strict";
    init_moz_shim();
    init_client();
    client = null;
    connecting = null;
    args = { transport: "extension" };
  }
});

// src/moz-entry.ts
init_moz_shim();
init_moz_shim();

// src/mcp.ts
init_moz_shim();

// ../src/tools/index.ts
var tools_exports = {};
__export(tools_exports, {
  acceptDialogTool: () => acceptDialogTool,
  clearConsoleMessagesTool: () => clearConsoleMessagesTool,
  clearSnapshotTool: () => clearSnapshotTool,
  clickByUidTool: () => clickByUidTool,
  closePageTool: () => closePageTool,
  dismissDialogTool: () => dismissDialogTool,
  dragByUidToUidTool: () => dragByUidToUidTool,
  enableDebuggerTool: () => enableDebuggerTool,
  evaluatePrivilegedScriptTool: () => evaluatePrivilegedScriptTool,
  evaluateScriptTool: () => evaluateScriptTool,
  fillByUidTool: () => fillByUidTool,
  fillFormByUidTool: () => fillFormByUidTool,
  getFirefoxInfoTool: () => getFirefoxInfoTool,
  getFirefoxLogsTool: () => getFirefoxLogsTool,
  getFirefoxPrefsTool: () => getFirefoxPrefsTool,
  getLogpointResultsTool: () => getLogpointResultsTool,
  getNetworkRequestTool: () => getNetworkRequestTool,
  getScriptSourceTool: () => getScriptSourceTool,
  handleAcceptDialog: () => handleAcceptDialog,
  handleClearConsoleMessages: () => handleClearConsoleMessages,
  handleClearSnapshot: () => handleClearSnapshot,
  handleClickByUid: () => handleClickByUid,
  handleClosePage: () => handleClosePage,
  handleDismissDialog: () => handleDismissDialog,
  handleDragByUidToUid: () => handleDragByUidToUid,
  handleEnableDebugger: () => handleEnableDebugger,
  handleEvaluatePrivilegedScript: () => handleEvaluatePrivilegedScript,
  handleEvaluateScript: () => handleEvaluateScript,
  handleFillByUid: () => handleFillByUid,
  handleFillFormByUid: () => handleFillFormByUid,
  handleGetFirefoxInfo: () => handleGetFirefoxInfo,
  handleGetFirefoxLogs: () => handleGetFirefoxLogs,
  handleGetFirefoxPrefs: () => handleGetFirefoxPrefs,
  handleGetLogpointResults: () => handleGetLogpointResults,
  handleGetNetworkRequest: () => handleGetNetworkRequest,
  handleGetScriptSource: () => handleGetScriptSource,
  handleHoverByUid: () => handleHoverByUid,
  handleInstallExtension: () => handleInstallExtension,
  handleListConsoleMessages: () => handleListConsoleMessages,
  handleListExtensions: () => handleListExtensions,
  handleListNetworkRequests: () => handleListNetworkRequests,
  handleListPages: () => handleListPages,
  handleListPrivilegedContexts: () => handleListPrivilegedContexts,
  handleListScripts: () => handleListScripts,
  handleNavigateHistory: () => handleNavigateHistory,
  handleNavigatePage: () => handleNavigatePage,
  handleNewPage: () => handleNewPage,
  handleProfilerIsActive: () => handleProfilerIsActive,
  handleProfilerStart: () => handleProfilerStart,
  handleProfilerStop: () => handleProfilerStop,
  handleRemoveLogpoint: () => handleRemoveLogpoint,
  handleResolveUidToSelector: () => handleResolveUidToSelector,
  handleRestartFirefox: () => handleRestartFirefox,
  handleScreenshotByUid: () => handleScreenshotByUid,
  handleScreenshotPage: () => handleScreenshotPage,
  handleSelectPage: () => handleSelectPage,
  handleSelectPrivilegedContext: () => handleSelectPrivilegedContext,
  handleSetFirefoxPrefs: () => handleSetFirefoxPrefs,
  handleSetLogpoint: () => handleSetLogpoint,
  handleSetViewportSize: () => handleSetViewportSize,
  handleTakeSnapshot: () => handleTakeSnapshot,
  handleUninstallExtension: () => handleUninstallExtension,
  handleUploadFileByUid: () => handleUploadFileByUid,
  hoverByUidTool: () => hoverByUidTool,
  installExtensionTool: () => installExtensionTool,
  listConsoleMessagesTool: () => listConsoleMessagesTool,
  listExtensionsTool: () => listExtensionsTool,
  listNetworkRequestsTool: () => listNetworkRequestsTool,
  listPagesTool: () => listPagesTool,
  listPrivilegedContextsTool: () => listPrivilegedContextsTool,
  listScriptsTool: () => listScriptsTool,
  navigateHistoryTool: () => navigateHistoryTool,
  navigatePageTool: () => navigatePageTool,
  newPageTool: () => newPageTool,
  profilerIsActiveTool: () => profilerIsActiveTool,
  profilerStartTool: () => profilerStartTool,
  profilerStopTool: () => profilerStopTool,
  removeLogpointTool: () => removeLogpointTool,
  resolveUidToSelectorTool: () => resolveUidToSelectorTool,
  restartFirefoxTool: () => restartFirefoxTool,
  screenshotByUidTool: () => screenshotByUidTool,
  screenshotPageTool: () => screenshotPageTool,
  selectPageTool: () => selectPageTool,
  selectPrivilegedContextTool: () => selectPrivilegedContextTool,
  setFirefoxPrefsTool: () => setFirefoxPrefsTool,
  setLogpointTool: () => setLogpointTool,
  setViewportSizeTool: () => setViewportSizeTool,
  takeSnapshotTool: () => takeSnapshotTool,
  uninstallExtensionTool: () => uninstallExtensionTool,
  uploadFileByUidTool: () => uploadFileByUidTool
});
init_moz_shim();

// ../src/tools/pages.ts
init_moz_shim();

// ../src/utils/response-helpers.ts
init_moz_shim();
var TOKEN_LIMITS = {
  /** Maximum characters for a single response (~12.5k tokens at ~4 chars/token) */
  MAX_RESPONSE_CHARS: 5e4,
  /** Maximum characters for screenshot base64 data (~10k tokens) */
  MAX_SCREENSHOT_CHARS: 4e4,
  /** Maximum characters per console message text */
  MAX_CONSOLE_MESSAGE_CHARS: 2e3,
  /** Maximum characters for network header values (per header) */
  MAX_HEADER_VALUE_CHARS: 500,
  /** Maximum total characters for all headers combined */
  MAX_HEADERS_TOTAL_CHARS: 5e3,
  /** Hard cap on snapshot lines (even if user requests more) */
  MAX_SNAPSHOT_LINES_CAP: 500,
  /** Warning threshold - show warning when response exceeds this */
  WARNING_THRESHOLD_CHARS: 3e4
};
function truncateText(text2, maxChars, suffix = "\n\n[... truncated - exceeded size limit]") {
  if (text2.length <= maxChars) {
    return text2;
  }
  return text2.slice(0, maxChars - suffix.length) + suffix;
}
function truncateHeaders(headers) {
  if (!headers) {
    return null;
  }
  const result = {};
  let totalChars = 0;
  for (const [key, value] of Object.entries(headers)) {
    const truncatedValue = value.length > TOKEN_LIMITS.MAX_HEADER_VALUE_CHARS ? value.slice(0, TOKEN_LIMITS.MAX_HEADER_VALUE_CHARS) + "...[truncated]" : value;
    const entrySize = key.length + truncatedValue.length;
    if (totalChars + entrySize > TOKEN_LIMITS.MAX_HEADERS_TOTAL_CHARS) {
      result["__truncated__"] = "Headers truncated due to size limit";
      break;
    }
    result[key] = truncatedValue;
    totalChars += entrySize;
  }
  return result;
}
function successResponse(message) {
  return {
    content: [
      {
        type: "text",
        text: message
      }
    ]
  };
}
function errorResponse(error) {
  const message = error instanceof Error ? error.message : error;
  return {
    content: [
      {
        type: "text",
        text: `Error: ${message}`
      }
    ],
    isError: true
  };
}
function jsonResponse(data) {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(data, null, 2)
      }
    ]
  };
}

// ../src/tools/pages.ts
var listPagesTool = {
  name: "list_pages",
  description: "List open tabs (index, title, URL). Selected tab is marked.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
var newPageTool = {
  name: "new_page",
  description: "Open new tab at URL. Returns tab index.",
  inputSchema: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "Target URL"
      }
    },
    required: ["url"]
  }
};
var navigatePageTool = {
  name: "navigate_page",
  description: "Navigate selected tab to URL.",
  inputSchema: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "Target URL"
      }
    },
    required: ["url"]
  }
};
var selectPageTool = {
  name: "select_page",
  description: "Select active tab by index, URL, or title. Index takes precedence.",
  inputSchema: {
    type: "object",
    properties: {
      pageIdx: {
        type: "number",
        description: "Tab index (0-based, most reliable)"
      },
      url: {
        type: "string",
        description: "URL substring (case-insensitive)"
      },
      title: {
        type: "string",
        description: "Title substring (case-insensitive)"
      }
    },
    required: []
  }
};
var closePageTool = {
  name: "close_page",
  description: "Close tab by index.",
  inputSchema: {
    type: "object",
    properties: {
      pageIdx: {
        type: "number",
        description: "Tab index to close"
      }
    },
    required: ["pageIdx"]
  }
};
function formatPageList(tabs, selectedIdx) {
  if (tabs.length === 0) {
    return "\u{1F4C4} No pages";
  }
  const lines = [`\u{1F4C4} ${tabs.length} pages (selected: ${selectedIdx})`];
  for (const tab of tabs) {
    const idx = tabs.indexOf(tab);
    const marker = idx === selectedIdx ? ">" : " ";
    const title = (tab.title || "Untitled").substring(0, 40);
    lines.push(`${marker}[${idx}] ${title}`);
  }
  return lines.join("\n");
}
async function handleListPages(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.refreshTabs();
    const tabs = firefox.getTabs();
    const selectedIdx = firefox.getSelectedTabIdx();
    return successResponse(formatPageList(tabs, selectedIdx));
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleNewPage(args2) {
  try {
    const { url } = args2;
    if (!url || typeof url !== "string") {
      throw new Error("url parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const newIdx = await firefox.createNewPage(url);
    return successResponse(`new page [${newIdx}] \u2192 ${url}`);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleNavigatePage(args2) {
  try {
    const { url } = args2;
    if (!url || typeof url !== "string") {
      throw new Error("url parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.refreshTabs();
    const tabs = firefox.getTabs();
    const selectedIdx = firefox.getSelectedTabIdx();
    const page = tabs[selectedIdx];
    if (!page) {
      throw new Error("No page selected");
    }
    await firefox.navigate(url);
    return successResponse(`[${selectedIdx}] \u2192 ${url}`);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleSelectPage(args2) {
  try {
    const { pageIdx, url, title } = args2;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.refreshTabs();
    const tabs = firefox.getTabs();
    let selectedIdx;
    if (typeof pageIdx === "number") {
      selectedIdx = pageIdx;
    } else if (url && typeof url === "string") {
      const urlLower = url.toLowerCase();
      const foundIdx = tabs.findIndex((tab) => tab.url?.toLowerCase().includes(urlLower));
      if (foundIdx === -1) {
        throw new Error(`No page matching URL "${url}"`);
      }
      selectedIdx = foundIdx;
    } else if (title && typeof title === "string") {
      const titleLower = title.toLowerCase();
      const foundIdx = tabs.findIndex((tab) => tab.title?.toLowerCase().includes(titleLower));
      if (foundIdx === -1) {
        throw new Error(`No page matching title "${title}"`);
      }
      selectedIdx = foundIdx;
    } else {
      throw new Error("Provide pageIdx, url, or title");
    }
    if (!tabs[selectedIdx]) {
      throw new Error(`Page [${selectedIdx}] not found`);
    }
    await firefox.selectTab(selectedIdx);
    return successResponse(`selected [${selectedIdx}]`);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleClosePage(args2) {
  try {
    const { pageIdx } = args2;
    if (typeof pageIdx !== "number") {
      throw new Error("pageIdx parameter is required and must be a number");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.refreshTabs();
    const tabs = firefox.getTabs();
    const pageToClose = tabs[pageIdx];
    if (!pageToClose) {
      throw new Error(`Page with index ${pageIdx} not found`);
    }
    await firefox.closeTab(pageIdx);
    return successResponse(`closed [${pageIdx}]`);
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/script.ts
init_moz_shim();

// ../src/utils/remote-value.ts
init_moz_shim();
function remoteValueToNative(rv) {
  if (!rv || typeof rv !== "object") {
    return rv;
  }
  const { type, value } = rv;
  switch (type) {
    case "undefined":
      return void 0;
    case "null":
      return null;
    case "string":
    case "boolean":
      return value;
    case "number":
      if (value === "NaN") {
        return "NaN";
      }
      if (value === "Infinity") {
        return "Infinity";
      }
      if (value === "-Infinity") {
        return "-Infinity";
      }
      if (value === "-0") {
        return "-0";
      }
      return value;
    case "bigint":
      return `${value}n`;
    case "array":
      return value.map(remoteValueToNative);
    case "object":
      return Object.fromEntries(
        value.map(([k, v]) => [k, remoteValueToNative(v)])
      );
    case "map":
      return Object.fromEntries(
        value.map(([k, v]) => [
          typeof k === "object" ? JSON.stringify(remoteValueToNative(k)) : String(k),
          remoteValueToNative(v)
        ])
      );
    case "set":
      return value.map(remoteValueToNative);
    case "regexp": {
      const { pattern, flags } = value;
      return `/${pattern}/${flags ?? ""}`;
    }
    case "date":
      return value;
    default:
      return `[${type}]`;
  }
}

// ../src/utils/js-validation.ts
init_moz_shim();
var MAX_FUNCTION_SIZE = 16 * 1024;
function validateFunction(fnString) {
  if (!fnString || typeof fnString !== "string") {
    throw new Error("function parameter is required and must be a string");
  }
  if (fnString.length > MAX_FUNCTION_SIZE) {
    throw new Error(
      `Function too large (${fnString.length} bytes, max ${MAX_FUNCTION_SIZE} bytes). This tool is not designed for massive scripts.`
    );
  }
  const trimmed = fnString.trim();
  const isFunctionLike = trimmed.startsWith("function") || trimmed.startsWith("async function") || trimmed.startsWith("(") || trimmed.startsWith("async (");
  if (!isFunctionLike) {
    throw new Error(
      `Invalid function format. Expected a function or arrow function, got: "${trimmed.substring(0, 50)}...".

Valid examples:
  () => document.title
  async () => { return await fetch("/api") }
  (el) => el.innerText
  function() { return window.location.href }`
    );
  }
}

// ../src/tools/script.ts
var evaluateScriptTool = {
  name: "evaluate_script",
  description: "Execute JS function in page. Prefer UID tools for interactions.",
  inputSchema: {
    type: "object",
    properties: {
      function: {
        type: "string",
        description: "JS function string, e.g. () => document.title"
      },
      args: {
        type: "array",
        description: "UIDs to pass as function arguments",
        items: {
          type: "object",
          properties: {
            uid: {
              type: "string",
              description: "Element UID from snapshot"
            }
          },
          required: ["uid"]
        }
      },
      timeout: {
        type: "number",
        description: "Timeout in ms (default: 5000)"
      }
    },
    required: ["function"]
  }
};
var DEFAULT_TIMEOUT = 5e3;
var TIMEOUT = Symbol("Timeout");
var EvaluateResultType = {
  Exception: "exception",
  Success: "success"
};
async function handleEvaluateScript(args2) {
  try {
    const {
      function: fnString,
      args: fnArgs,
      timeout
    } = args2;
    validateFunction(fnString);
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const scriptTimeout = timeout ?? DEFAULT_TIMEOUT;
    const resolvedArgs = [];
    if (fnArgs && fnArgs.length > 0) {
      for (const arg of fnArgs) {
        try {
          const element = await firefox.resolveUidToElement(arg.uid);
          resolvedArgs.push({ sharedId: await element.getId() });
        } catch (error) {
          const errorMsg = error.message;
          if (errorMsg.includes("stale") || errorMsg.includes("Snapshot") || errorMsg.includes("UID")) {
            throw new Error(
              `UID "${arg.uid}" is invalid or from an old snapshot.

The page may have changed since the snapshot was taken.
Please call take_snapshot to get fresh UIDs and try again.`
            );
          }
          throw new Error(`Failed to resolve UID "${arg.uid}": ${errorMsg}`);
        }
      }
    }
    const callFunctionPromise = firefox.sendBiDiCommand("script.callFunction", {
      functionDeclaration: fnString,
      awaitPromise: true,
      arguments: resolvedArgs,
      target: { context: firefox.getCurrentContextId() }
    });
    const result = await Promise.race([
      new Promise((r) => setTimeout(() => r(TIMEOUT), scriptTimeout)),
      callFunctionPromise
    ]);
    if (result === TIMEOUT) {
      return errorResponse(
        new Error(
          `Script execution timed out (exceeded ${scriptTimeout}ms).

The function may contain an infinite loop or be waiting for a slow operation.
Try simplifying the script or increasing the timeout parameter.`
        )
      );
    } else if (result.type === EvaluateResultType.Success) {
      let output = "Script ran on page and returned:\n";
      output += "```json\n";
      output += JSON.stringify(remoteValueToNative(result.result), null, 2);
      output += "\n```";
      return successResponse(output);
    } else if (result.type === EvaluateResultType.Exception) {
      const exceptionDetails = result.exceptionDetails;
      return errorResponse(
        new Error(
          `Script execution failed: ${exceptionDetails.text}

\`\`\`json
` + JSON.stringify(remoteValueToNative(exceptionDetails.exception), null, 2) + "\n```"
        )
      );
    } else {
      return errorResponse(`Unexpected script.callFunction result type: ${result.type}`);
    }
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/console.ts
init_moz_shim();
var listConsoleMessagesTool = {
  name: "list_console_messages",
  description: "List console messages. Supports filtering by level, time, text, source.",
  inputSchema: {
    type: "object",
    properties: {
      level: {
        type: "string",
        enum: ["debug", "info", "warn", "error"],
        description: "Filter by level"
      },
      limit: {
        type: "number",
        description: "Max messages (default: 50)"
      },
      sinceMs: {
        type: "number",
        description: "Only last N ms"
      },
      textContains: {
        type: "string",
        description: "Text filter (case-insensitive)"
      },
      source: {
        type: "string",
        description: "Filter by source"
      },
      format: {
        type: "string",
        enum: ["text", "json"],
        description: "Output format (default: text)"
      }
    }
  }
};
var clearConsoleMessagesTool = {
  name: "clear_console_messages",
  description: "Clear collected console messages.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
var DEFAULT_LIMIT = 50;
async function handleListConsoleMessages(args2) {
  try {
    const {
      level,
      limit,
      sinceMs,
      textContains,
      source,
      format = "text"
    } = args2 || {};
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    let messages = await firefox.getConsoleMessages();
    const totalCount = messages.length;
    if (level) {
      messages = messages.filter((msg) => msg.level.toLowerCase() === level.toLowerCase());
    }
    if (sinceMs !== void 0) {
      const cutoffTime = Date.now() - sinceMs;
      messages = messages.filter((msg) => msg.timestamp && msg.timestamp >= cutoffTime);
    }
    if (textContains) {
      const textLower = textContains.toLowerCase();
      messages = messages.filter((msg) => msg.text.toLowerCase().includes(textLower));
    }
    if (source) {
      messages = messages.filter((msg) => msg.source?.toLowerCase() === source.toLowerCase());
    }
    messages = messages.map((msg) => ({
      ...msg,
      text: truncateText(msg.text, TOKEN_LIMITS.MAX_CONSOLE_MESSAGE_CHARS, "...[truncated]")
    }));
    const maxLimit = limit ?? DEFAULT_LIMIT;
    const filteredCount = messages.length;
    const truncated = messages.length > maxLimit;
    messages = messages.slice(0, maxLimit);
    if (messages.length === 0) {
      const filterInfo = [];
      if (level) {
        filterInfo.push(`level=${level}`);
      }
      if (sinceMs) {
        filterInfo.push(`sinceMs=${sinceMs}`);
      }
      if (textContains) {
        filterInfo.push(`textContains="${textContains}"`);
      }
      if (source) {
        filterInfo.push(`source="${source}"`);
      }
      if (format === "json") {
        return jsonResponse({
          total: totalCount,
          filtered: 0,
          showing: 0,
          filters: filterInfo.length > 0 ? filterInfo.join(", ") : null,
          messages: []
        });
      }
      return successResponse(
        `No console messages found matching filters.
Total messages: ${totalCount}${filterInfo.length > 0 ? `, Filters: ${filterInfo.join(", ")}` : ""}`
      );
    }
    if (format === "json") {
      const filterInfo = [];
      if (level) {
        filterInfo.push(`level=${level}`);
      }
      if (sinceMs) {
        filterInfo.push(`sinceMs=${sinceMs}`);
      }
      if (textContains) {
        filterInfo.push(`textContains="${textContains}"`);
      }
      if (source) {
        filterInfo.push(`source="${source}"`);
      }
      return jsonResponse({
        total: totalCount,
        filtered: filteredCount,
        showing: messages.length,
        hasMore: truncated,
        filters: filterInfo.length > 0 ? filterInfo.join(", ") : null,
        messages: messages.map((msg) => ({
          level: msg.level,
          text: msg.text,
          source: msg.source || null,
          timestamp: msg.timestamp || null
        }))
      });
    }
    let output = `Console messages (showing ${messages.length}`;
    if (filteredCount > messages.length) {
      output += ` of ${filteredCount} matching`;
    }
    output += `, ${totalCount} total):
`;
    if (level || sinceMs || textContains || source) {
      output += `Filters:`;
      if (level) {
        output += ` level=${level}`;
      }
      if (sinceMs) {
        output += ` sinceMs=${sinceMs}`;
      }
      if (textContains) {
        output += ` textContains="${textContains}"`;
      }
      if (source) {
        output += ` source="${source}"`;
      }
      output += "\n";
    }
    output += "\n";
    for (const msg of messages) {
      const timestamp = msg.timestamp ? new Date(msg.timestamp).toISOString() : "";
      const source2 = msg.source ? ` [${msg.source}]` : "";
      const time = timestamp ? `[${timestamp}] ` : "";
      output += `${time}${msg.level.toUpperCase()}${source2}: ${msg.text}
`;
    }
    if (truncated) {
      output += `
[+${filteredCount - messages.length} more]`;
    }
    return successResponse(output);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleClearConsoleMessages(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const count = (await firefox.getConsoleMessages()).length;
    firefox.clearConsoleMessages();
    return successResponse(`cleared ${count} messages`);
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/network.ts
init_moz_shim();
var listNetworkRequestsTool = {
  name: "list_network_requests",
  description: "List network requests. Returns IDs for get_network_request.",
  inputSchema: {
    type: "object",
    properties: {
      limit: {
        type: "number",
        description: "Max requests (default: 50)"
      },
      sinceMs: {
        type: "number",
        description: "Only last N ms"
      },
      urlContains: {
        type: "string",
        description: "URL filter (case-insensitive)"
      },
      method: {
        type: "string",
        description: "HTTP method filter"
      },
      status: {
        type: "number",
        description: "Exact status code"
      },
      statusMin: {
        type: "number",
        description: "Min status code"
      },
      statusMax: {
        type: "number",
        description: "Max status code"
      },
      isXHR: {
        type: "boolean",
        description: "XHR/fetch only"
      },
      resourceType: {
        type: "string",
        description: "Resource type filter"
      },
      sortBy: {
        type: "string",
        enum: ["timestamp", "duration", "status"],
        description: "Sort field (default: timestamp)"
      },
      detail: {
        type: "string",
        enum: ["summary", "min", "full"],
        description: "Detail level (default: summary)"
      },
      format: {
        type: "string",
        enum: ["text", "json"],
        description: "Output format (default: text)"
      }
    }
  }
};
var getNetworkRequestTool = {
  name: "get_network_request",
  description: "Get request details by ID. URL lookup as fallback.",
  inputSchema: {
    type: "object",
    properties: {
      id: {
        type: "string",
        description: "Request ID from list_network_requests"
      },
      url: {
        type: "string",
        description: "URL fallback (may match multiple)"
      },
      format: {
        type: "string",
        enum: ["text", "json"],
        description: "Output format (default: text)"
      }
    }
  }
};
async function handleListNetworkRequests(args2) {
  try {
    const {
      limit = 50,
      sinceMs,
      urlContains,
      method,
      status,
      statusMin,
      statusMax,
      isXHR,
      resourceType,
      sortBy = "timestamp",
      detail = "summary",
      format = "text"
    } = args2 || {};
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    let requests = await firefox.getNetworkRequests();
    if (sinceMs !== void 0) {
      const cutoffTime = Date.now() - sinceMs;
      requests = requests.filter((req) => req.timestamp && req.timestamp >= cutoffTime);
    }
    if (urlContains) {
      const urlLower = urlContains.toLowerCase();
      requests = requests.filter((req) => req.url.toLowerCase().includes(urlLower));
    }
    if (method) {
      const methodUpper = method.toUpperCase();
      requests = requests.filter((req) => req.method.toUpperCase() === methodUpper);
    }
    if (status !== void 0) {
      requests = requests.filter((req) => req.status === status);
    }
    if (statusMin !== void 0) {
      requests = requests.filter((req) => req.status !== void 0 && req.status >= statusMin);
    }
    if (statusMax !== void 0) {
      requests = requests.filter((req) => req.status !== void 0 && req.status <= statusMax);
    }
    if (isXHR !== void 0) {
      requests = requests.filter((req) => req.isXHR === isXHR);
    }
    if (resourceType) {
      const typeLower = resourceType.toLowerCase();
      requests = requests.filter((req) => req.resourceType?.toLowerCase() === typeLower);
    }
    if (sortBy === "timestamp") {
      requests.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    } else if (sortBy === "duration") {
      requests.sort((a, b) => (b.timings?.duration || 0) - (a.timings?.duration || 0));
    } else if (sortBy === "status") {
      requests.sort((a, b) => (a.status || 0) - (b.status || 0));
    }
    const limitedRequests = requests.slice(0, limit);
    const hasMore = requests.length > limit;
    if (format === "json") {
      const responseData = {
        total: requests.length,
        showing: limitedRequests.length,
        hasMore,
        requests: []
      };
      if (detail === "summary" || detail === "min") {
        responseData.requests = limitedRequests.map((req) => ({
          id: req.id,
          url: req.url,
          method: req.method,
          status: req.status,
          statusText: req.statusText,
          resourceType: req.resourceType,
          isXHR: req.isXHR,
          duration: req.timings?.duration
        }));
      } else {
        responseData.requests = limitedRequests.map((req) => ({
          id: req.id,
          url: req.url,
          method: req.method,
          status: req.status,
          statusText: req.statusText,
          resourceType: req.resourceType,
          isXHR: req.isXHR,
          timings: req.timings || null,
          requestHeaders: truncateHeaders(req.requestHeaders),
          responseHeaders: truncateHeaders(req.responseHeaders)
        }));
      }
      return jsonResponse(responseData);
    }
    if (detail === "summary") {
      const formattedRequests = limitedRequests.map((req) => {
        const statusInfo = req.status ? `[${req.status}${req.statusText ? " " + req.statusText : ""}]` : "[pending]";
        return `${req.id} | ${req.method} ${req.url} ${statusInfo}${req.isXHR ? " (XHR)" : ""}`;
      });
      const header = `\u{1F4E1} ${requests.length} requests${hasMore ? ` (limit ${limit})` : ""}
`;
      return successResponse(header + formattedRequests.join("\n"));
    } else if (detail === "min") {
      const minData = limitedRequests.map((req) => ({
        id: req.id,
        url: req.url,
        method: req.method,
        status: req.status,
        statusText: req.statusText,
        resourceType: req.resourceType,
        isXHR: req.isXHR,
        duration: req.timings?.duration
      }));
      return successResponse(
        `\u{1F4E1} ${requests.length} requests${hasMore ? ` (limit ${limit})` : ""}
` + JSON.stringify(minData, null, 2)
      );
    } else {
      const fullData = limitedRequests.map((req) => ({
        id: req.id,
        url: req.url,
        method: req.method,
        status: req.status,
        statusText: req.statusText,
        resourceType: req.resourceType,
        isXHR: req.isXHR,
        timings: req.timings || null,
        requestHeaders: truncateHeaders(req.requestHeaders),
        responseHeaders: truncateHeaders(req.responseHeaders)
      }));
      return successResponse(
        `\u{1F4E1} ${requests.length} requests${hasMore ? ` (limit ${limit})` : ""}
` + JSON.stringify(fullData, null, 2)
      );
    }
  } catch (error) {
    return errorResponse(error instanceof Error ? error : new Error(String(error)));
  }
}
async function handleGetNetworkRequest(args2) {
  try {
    const {
      id,
      url,
      format = "text"
    } = args2;
    if (!id && !url) {
      return errorResponse("id or url required");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const requests = await firefox.getNetworkRequests();
    let request = null;
    if (id) {
      request = requests.find((req) => req.id === id);
      if (!request) {
        return errorResponse(`ID ${id} not found`);
      }
    } else if (url) {
      const matches = requests.filter((req) => req.url === url);
      if (matches.length === 0) {
        return errorResponse(`URL not found: ${url}`);
      }
      if (matches.length > 1) {
        const ids = matches.map((req) => req.id).join(", ");
        return errorResponse(`Multiple matches, use id: ${ids}`);
      }
      request = matches[0];
    }
    if (!request) {
      return errorResponse("Request not found");
    }
    const details = {
      id: request.id,
      url: request.url,
      method: request.method,
      status: request.status ?? null,
      statusText: request.statusText ?? null,
      resourceType: request.resourceType ?? null,
      isXHR: request.isXHR ?? false,
      timestamp: request.timestamp ?? null,
      timings: request.timings ?? null,
      requestHeaders: truncateHeaders(request.requestHeaders),
      responseHeaders: truncateHeaders(request.responseHeaders)
    };
    if (format === "json") {
      return jsonResponse(details);
    }
    return successResponse(JSON.stringify(details, null, 2));
  } catch (error) {
    return errorResponse(error instanceof Error ? error : new Error(String(error)));
  }
}

// ../src/tools/snapshot.ts
init_moz_shim();

// ../src/utils/uid-helpers.ts
init_moz_shim();
function handleUidError(error, uid) {
  const errorMsg = error.message;
  if (errorMsg.includes("stale") || errorMsg.includes("Snapshot") || errorMsg.includes("UID") || errorMsg.includes("not found")) {
    return new Error(`${uid} stale/invalid. Call take_snapshot first.`);
  }
  return error;
}

// ../src/tools/snapshot.ts
var DEFAULT_SNAPSHOT_LINES = 100;
var takeSnapshotTool = {
  name: "take_snapshot",
  description: "Capture DOM snapshot with stable UIDs. Retake after navigation.",
  inputSchema: {
    type: "object",
    properties: {
      maxLines: {
        type: "number",
        description: "Max lines (default: 100)"
      },
      includeAttributes: {
        type: "boolean",
        description: "Include ARIA attributes (default: false)"
      },
      includeText: {
        type: "boolean",
        description: "Include text (default: true)"
      },
      maxDepth: {
        type: "number",
        description: "Max tree depth"
      },
      includeAll: {
        type: "boolean",
        description: "Include all visible elements without relevance filtering. Useful for Vue/Livewire apps (default: false)"
      },
      selector: {
        type: "string",
        description: 'CSS selector to scope snapshot to specific element (e.g., "#app")'
      }
    }
  }
};
var resolveUidToSelectorTool = {
  name: "resolve_uid_to_selector",
  description: "Resolve UID to CSS selector. Fails if stale.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "UID from snapshot"
      }
    },
    required: ["uid"]
  }
};
var clearSnapshotTool = {
  name: "clear_snapshot",
  description: "Clear snapshot cache. Usually not needed.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
async function handleTakeSnapshot(args2) {
  try {
    const {
      maxLines: requestedMaxLines = DEFAULT_SNAPSHOT_LINES,
      includeAttributes = false,
      includeText = true,
      maxDepth,
      includeAll = false,
      selector
    } = args2 || {};
    const maxLines = Math.min(Math.max(1, requestedMaxLines), TOKEN_LIMITS.MAX_SNAPSHOT_LINES_CAP);
    const wasCapped = requestedMaxLines > TOKEN_LIMITS.MAX_SNAPSHOT_LINES_CAP;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const snapshotOptions = {};
    if (includeAll) {
      snapshotOptions.includeAll = includeAll;
    }
    if (selector) {
      snapshotOptions.selector = selector;
    }
    const snapshot = await firefox.takeSnapshot(
      Object.keys(snapshotOptions).length > 0 ? snapshotOptions : void 0
    );
    const { formatSnapshotTree: formatSnapshotTree2 } = await Promise.resolve().then(() => (init_formatter(), formatter_exports));
    const options = {
      includeAttributes,
      includeText
    };
    if (maxDepth !== void 0) {
      options.maxDepth = maxDepth;
    }
    const formattedText = formatSnapshotTree2(snapshot.json.root, 0, options);
    const lines = formattedText.split("\n");
    const truncated = lines.length > maxLines;
    const displayLines = truncated ? lines.slice(0, maxLines) : lines;
    let output = `\u{1F4F8} Snapshot (id=${snapshot.json.snapshotId})`;
    if (selector) {
      output += ` [selector: ${selector}]`;
    }
    if (includeAll) {
      output += " [includeAll: true]";
    }
    if (wasCapped) {
      output += ` [maxLines capped: ${TOKEN_LIMITS.MAX_SNAPSHOT_LINES_CAP}]`;
    }
    if (snapshot.json.truncated) {
      output += " [DOM truncated]";
    }
    output += "\n\n";
    output += displayLines.join("\n");
    if (truncated) {
      output += `

[+${lines.length - maxLines} lines, use maxLines to see more]`;
    }
    return successResponse(output);
  } catch (error) {
    return errorResponse(
      new Error(
        `Failed to take snapshot: ${error.message}

The page may not be fully loaded or accessible.`
      )
    );
  }
}
async function handleResolveUidToSelector(args2) {
  try {
    const { uid } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      const selector = firefox.resolveUidToSelector(uid);
      return successResponse(`${uid} \u2192 ${selector}`);
    } catch (error) {
      throw handleUidError(error, uid);
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleClearSnapshot(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    firefox.clearSnapshot();
    return successResponse("\u{1F9F9} Snapshot cleared");
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/input.ts
init_moz_shim();
var clickByUidTool = {
  name: "click_by_uid",
  description: "Click element by UID. Set dblClick for double-click.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "Element UID from snapshot"
      },
      dblClick: {
        type: "boolean",
        description: "Double-click (default: false)"
      }
    },
    required: ["uid"]
  }
};
var hoverByUidTool = {
  name: "hover_by_uid",
  description: "Hover over element by UID.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "Element UID from snapshot"
      }
    },
    required: ["uid"]
  }
};
var fillByUidTool = {
  name: "fill_by_uid",
  description: "Fill text input/textarea by UID.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "Input element UID from snapshot"
      },
      value: {
        type: "string",
        description: "Text to fill"
      }
    },
    required: ["uid", "value"]
  }
};
var dragByUidToUidTool = {
  name: "drag_by_uid_to_uid",
  description: "Drag element to another (HTML5 drag events).",
  inputSchema: {
    type: "object",
    properties: {
      fromUid: {
        type: "string",
        description: "Source element UID"
      },
      toUid: {
        type: "string",
        description: "Target element UID"
      }
    },
    required: ["fromUid", "toUid"]
  }
};
var fillFormByUidTool = {
  name: "fill_form_by_uid",
  description: "Fill multiple form fields at once.",
  inputSchema: {
    type: "object",
    properties: {
      elements: {
        type: "array",
        description: "Array of {uid, value} pairs",
        items: {
          type: "object",
          properties: {
            uid: {
              type: "string",
              description: "Field UID"
            },
            value: {
              type: "string",
              description: "Field value"
            }
          },
          required: ["uid", "value"]
        }
      }
    },
    required: ["elements"]
  }
};
var uploadFileByUidTool = {
  name: "upload_file_by_uid",
  description: "Upload file to file input by UID.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "File input UID from snapshot"
      },
      filePath: {
        type: "string",
        description: "Local file path"
      }
    },
    required: ["uid", "filePath"]
  }
};
async function handleClickByUid(args2) {
  try {
    const { uid, dblClick } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.clickByUid(uid, dblClick);
      return successResponse(`${dblClick ? "dblclick" : "click"} ${uid}`);
    } catch (error) {
      throw handleUidError(error, uid);
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleHoverByUid(args2) {
  try {
    const { uid } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.hoverByUid(uid);
      return successResponse(`hover ${uid}`);
    } catch (error) {
      throw handleUidError(error, uid);
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleFillByUid(args2) {
  try {
    const { uid, value } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid parameter is required and must be a string");
    }
    if (value === void 0 || typeof value !== "string") {
      throw new Error("value parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.fillByUid(uid, value);
      return successResponse(`fill ${uid}`);
    } catch (error) {
      throw handleUidError(error, uid);
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleDragByUidToUid(args2) {
  try {
    const { fromUid, toUid } = args2;
    if (!fromUid || typeof fromUid !== "string") {
      throw new Error("fromUid parameter is required and must be a string");
    }
    if (!toUid || typeof toUid !== "string") {
      throw new Error("toUid parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.dragByUidToUid(fromUid, toUid);
      return successResponse(`drag ${fromUid}\u2192${toUid}`);
    } catch (error) {
      const errorMsg = error.message;
      if (errorMsg.includes("stale") || errorMsg.includes("Snapshot") || errorMsg.includes("UID")) {
        throw new Error(`UIDs stale/invalid. Call take_snapshot first.`);
      }
      throw error;
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleFillFormByUid(args2) {
  try {
    const { elements } = args2;
    if (!elements || !Array.isArray(elements) || elements.length === 0) {
      throw new Error("elements parameter is required and must be a non-empty array");
    }
    for (const el of elements) {
      if (!el.uid || typeof el.uid !== "string") {
        throw new Error(`Invalid element: uid is required and must be a string`);
      }
      if (el.value === void 0 || typeof el.value !== "string") {
        throw new Error(`Invalid element for uid "${el.uid}": value must be a string`);
      }
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.fillFormByUid(elements);
      return successResponse(`filled ${elements.length} fields`);
    } catch (error) {
      const errorMsg = error.message;
      if (errorMsg.includes("stale") || errorMsg.includes("Snapshot") || errorMsg.includes("UID")) {
        throw new Error(`UIDs stale/invalid. Call take_snapshot first.`);
      }
      throw error;
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleUploadFileByUid(args2) {
  try {
    const { uid, filePath } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid parameter is required and must be a string");
    }
    if (!filePath || typeof filePath !== "string") {
      throw new Error("filePath parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.uploadFileByUid(uid, filePath);
      return successResponse(`upload ${uid}`);
    } catch (error) {
      const errorMsg = error.message;
      if (errorMsg.includes("stale") || errorMsg.includes("Snapshot") || errorMsg.includes("UID")) {
        throw handleUidError(error, uid);
      }
      if (errorMsg.includes("not a file input") || errorMsg.includes('type="file"')) {
        throw new Error(`${uid} is not a file input`);
      }
      if (errorMsg.includes("hidden") || errorMsg.includes("not visible")) {
        throw new Error(`${uid} is hidden/not interactable`);
      }
      throw error;
    }
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/screenshot.ts
init_moz_shim();

// src/node-shims.ts
init_moz_shim();
async function writeFile() {
  throw new Error("Saving to a host path is not supported in the extension transport");
}
async function mkdir() {
  throw new Error("Saving to a host path is not supported in the extension transport");
}
function readFileSync() {
  throw new Error("Host file access is not supported in the extension transport");
}
function existsSync() {
  return false;
}
function statSync() {
  throw new Error("Host file access is not supported in the extension transport");
}
function resolve(...parts) {
  return parts.join("/");
}
function dirname(p) {
  return p.split("/").slice(0, -1).join("/") || "/";
}

// ../src/tools/screenshot.ts
var SAVE_TO_SCHEMA = {
  type: "string",
  description: "Optional file path to save the screenshot to instead of returning it as image data in the response."
};
var screenshotPageTool = {
  name: "screenshot_page",
  description: "Capture page screenshot as base64 PNG.",
  inputSchema: {
    type: "object",
    properties: {
      saveTo: SAVE_TO_SCHEMA
    }
  }
};
var screenshotByUidTool = {
  name: "screenshot_by_uid",
  description: "Capture element screenshot by UID as base64 PNG.",
  inputSchema: {
    type: "object",
    properties: {
      uid: {
        type: "string",
        description: "Element UID from snapshot"
      },
      saveTo: SAVE_TO_SCHEMA
    },
    required: ["uid"]
  }
};
async function saveScreenshot(base64Png, saveTo) {
  const buffer = Buffer.from(base64Png, "base64");
  const resolvedPath = resolve(saveTo);
  await mkdir(dirname(resolvedPath), { recursive: true });
  await writeFile(resolvedPath, buffer);
  return successResponse(
    `Screenshot saved to: ${resolvedPath} (${(buffer.length / 1024).toFixed(1)}KB)`
  );
}
function imageResponse(base64Png) {
  return {
    content: [
      {
        type: "image",
        data: base64Png,
        mimeType: "image/png"
      }
    ]
  };
}
async function handleScreenshotPage(args2) {
  try {
    const { saveTo } = args2 ?? {};
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const base64Png = await firefox.takeScreenshotPage();
    if (!base64Png || typeof base64Png !== "string") {
      throw new Error("Invalid screenshot data");
    }
    if (saveTo) {
      return await saveScreenshot(base64Png, saveTo);
    }
    return imageResponse(base64Png);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleScreenshotByUid(args2) {
  try {
    const { uid, saveTo } = args2;
    if (!uid || typeof uid !== "string") {
      throw new Error("uid required");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      const base64Png = await firefox.takeScreenshotByUid(uid);
      if (!base64Png || typeof base64Png !== "string") {
        throw new Error("Invalid screenshot data");
      }
      if (saveTo) {
        return await saveScreenshot(base64Png, saveTo);
      }
      return imageResponse(base64Png);
    } catch (error) {
      throw handleUidError(error, uid);
    }
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/utilities.ts
init_moz_shim();
var acceptDialogTool = {
  name: "accept_dialog",
  description: "Accept browser dialog. Provide promptText for prompts.",
  inputSchema: {
    type: "object",
    properties: {
      promptText: {
        type: "string",
        description: "Text for prompt dialogs"
      }
    }
  }
};
var dismissDialogTool = {
  name: "dismiss_dialog",
  description: "Dismiss browser dialog.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
var navigateHistoryTool = {
  name: "navigate_history",
  description: "Navigate history back/forward. UIDs become stale.",
  inputSchema: {
    type: "object",
    properties: {
      direction: {
        type: "string",
        enum: ["back", "forward"],
        description: "back or forward"
      }
    },
    required: ["direction"]
  }
};
var setViewportSizeTool = {
  name: "set_viewport_size",
  description: "Set viewport dimensions in pixels.",
  inputSchema: {
    type: "object",
    properties: {
      width: {
        type: "number",
        description: "Width in pixels"
      },
      height: {
        type: "number",
        description: "Height in pixels"
      }
    },
    required: ["width", "height"]
  }
};
async function handleAcceptDialog(args2) {
  try {
    const { promptText } = args2 || {};
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.acceptDialog(promptText);
      return successResponse(promptText ? `Accepted: "${promptText}"` : "Accepted");
    } catch (error) {
      const errorMsg = error.message;
      if (errorMsg.includes("no such alert") || errorMsg.includes("No dialog")) {
        throw new Error("No active dialog");
      }
      throw error;
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleDismissDialog(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    try {
      await firefox.dismissDialog();
      return successResponse("Dismissed");
    } catch (error) {
      const errorMsg = error.message;
      if (errorMsg.includes("no such alert") || errorMsg.includes("No dialog")) {
        throw new Error("No active dialog");
      }
      throw error;
    }
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleNavigateHistory(args2) {
  try {
    const { direction } = args2;
    if (!direction || direction !== "back" && direction !== "forward") {
      throw new Error('direction parameter is required and must be "back" or "forward"');
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    if (direction === "back") {
      await firefox.navigateBack();
    } else {
      await firefox.navigateForward();
    }
    return successResponse(`${direction}`);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleSetViewportSize(args2) {
  try {
    const { width, height } = args2;
    if (typeof width !== "number" || width <= 0) {
      throw new Error("width parameter is required and must be a positive number");
    }
    if (typeof height !== "number" || height <= 0) {
      throw new Error("height parameter is required and must be a positive number");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.setViewportSize(width, height);
    return successResponse(`${width}x${height}`);
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/firefox-management.ts
init_moz_shim();
init_provider();
var getFirefoxLogsTool = {
  name: "get_firefox_output",
  description: "Retrieve Firefox output (stdout/stderr including MOZ_LOG, warnings, crashes, stack traces). Returns recent output from the capture file. Use filters to focus on specific content.",
  inputSchema: {
    type: "object",
    properties: {
      lines: {
        type: "number",
        description: "Number of recent log lines to return (default: 100, max: 10000)"
      },
      grep: {
        type: "string",
        description: "Filter log lines containing this string (case-insensitive)"
      },
      since: {
        type: "number",
        description: "Only show logs written in the last N seconds"
      }
    }
  }
};
async function handleGetFirefoxLogs(input) {
  try {
    const {
      lines = 100,
      grep,
      since
    } = input;
    const firefox = await getFirefox();
    const logFilePath = firefox.getLogFilePath();
    if (!logFilePath) {
      return successResponse(
        "No output capture configured. Use --env to set environment variables or --output-file to enable output capture."
      );
    }
    if (!existsSync(logFilePath)) {
      return successResponse(`Output file not found: ${logFilePath}`);
    }
    if (since !== void 0) {
      const stats = statSync(logFilePath);
      const ageSeconds = (Date.now() - stats.mtimeMs) / 1e3;
      if (ageSeconds > since) {
        return successResponse(
          `Output file is ${Math.floor(ageSeconds)}s old, but only output from last ${since}s was requested. File may not have recent entries.`
        );
      }
    }
    const content = readFileSync(logFilePath, "utf-8");
    let allLines = content.split("\n").filter((line) => line.trim().length > 0);
    if (grep) {
      const grepLower = grep.toLowerCase();
      allLines = allLines.filter((line) => line.toLowerCase().includes(grepLower));
    }
    const maxLines = Math.min(lines, 1e4);
    const recentLines = allLines.slice(-maxLines);
    const result = [
      `Firefox Output File: ${logFilePath}`,
      `Total lines in file: ${allLines.length}`,
      grep ? `Lines matching "${grep}": ${allLines.length}` : "",
      `Showing last ${recentLines.length} lines:`,
      "",
      "\u2500".repeat(80),
      recentLines.join("\n")
    ].filter(Boolean).join("\n");
    return successResponse(result);
  } catch (error) {
    return errorResponse(error);
  }
}
var getFirefoxInfoTool = {
  name: "get_firefox_info",
  description: "Get information about the current Firefox instance configuration, including binary path, environment variables, and output file location.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
async function handleGetFirefoxInfo(_input) {
  try {
    const firefox = await getFirefox();
    const options = firefox.getOptions();
    const logFilePath = firefox.getLogFilePath();
    const version = firefox.getFirefoxVersion();
    const info = [];
    info.push("Firefox Instance Configuration");
    info.push("");
    info.push(`Binary: ${options.firefoxPath ?? "System Firefox (default)"}`);
    info.push(`Firefox version: ${version ?? "(unknown)"}`);
    info.push(`Headless: ${options.headless ? "Yes" : "No"}`);
    if (options.viewport) {
      info.push(`Viewport: ${options.viewport.width}x${options.viewport.height}`);
    }
    if (options.profilePath) {
      info.push(`Profile: ${options.profilePath}`);
    }
    if (options.startUrl) {
      info.push(`Start URL: ${options.startUrl}`);
    }
    if (options.args && options.args.length > 0) {
      info.push(`Arguments: ${options.args.join(" ")}`);
    }
    if (options.env && Object.keys(options.env).length > 0) {
      info.push("");
      info.push("Environment Variables:");
      for (const [key, value] of Object.entries(options.env)) {
        info.push(`  ${key}=${value}`);
      }
    }
    if (options.prefs && Object.keys(options.prefs).length > 0) {
      info.push("");
      info.push("Preferences:");
      for (const [key, value] of Object.entries(options.prefs)) {
        info.push(`  ${key} = ${JSON.stringify(value)}`);
      }
    }
    if (logFilePath) {
      info.push("");
      info.push(`Output File: ${logFilePath}`);
      if (existsSync(logFilePath)) {
        const stats = statSync(logFilePath);
        const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
        info.push(`  Size: ${sizeMB} MB`);
        info.push(`  Last Modified: ${stats.mtime.toISOString()}`);
      } else {
        info.push("  (file not created yet)");
      }
    }
    return successResponse(info.join("\n"));
  } catch (error) {
    return errorResponse(error);
  }
}
var restartFirefoxTool = {
  name: "restart_firefox",
  description: "Restart Firefox with different configuration. Allows changing binary path, environment variables, and other options. All current tabs will be closed.",
  inputSchema: {
    type: "object",
    properties: {
      firefoxPath: {
        type: "string",
        description: "New Firefox binary path (optional, keeps current if not specified)"
      },
      profilePath: {
        type: "string",
        description: "Firefox profile path (optional, keeps current if not specified)"
      },
      env: {
        type: "array",
        items: {
          type: "string"
        },
        description: 'New environment variables in KEY=VALUE format (optional, e.g., ["MOZ_LOG=HTMLMediaElement:5", "MOZ_LOG_FILE=/tmp/ff.log"])'
      },
      headless: {
        type: "boolean",
        description: "Run in headless mode (optional, keeps current if not specified)"
      },
      startUrl: {
        type: "string",
        description: "URL to navigate to after restart (optional, uses about:blank if not specified)"
      },
      prefs: {
        type: "object",
        description: "Firefox preferences to set at startup. Values are auto-typed: true/false become booleans, integers become numbers, everything else is a string. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.",
        additionalProperties: {
          oneOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }]
        }
      }
    }
  }
};
async function handleRestartFirefox(input) {
  try {
    const { firefoxPath, profilePath, env, headless, startUrl, prefs } = input;
    let newEnv;
    if (env && Array.isArray(env) && env.length > 0) {
      newEnv = {};
      for (const envStr of env) {
        const [key, ...valueParts] = envStr.split("=");
        if (key && valueParts.length > 0) {
          newEnv[key] = valueParts.join("=");
        }
      }
    }
    const currentFirefox = getFirefoxIfRunning();
    const isConnected = currentFirefox ? await currentFirefox.isConnected() : false;
    if (currentFirefox && isConnected) {
      const currentOptions = currentFirefox.getOptions();
      const mergedPrefs = prefs !== void 0 ? { ...currentOptions.prefs || {}, ...prefs } : currentOptions.prefs;
      const newOptions = {
        ...currentOptions,
        firefoxPath: firefoxPath ?? currentOptions.firefoxPath,
        profilePath: profilePath ?? currentOptions.profilePath,
        env: newEnv !== void 0 ? newEnv : currentOptions.env,
        headless: headless !== void 0 ? headless : currentOptions.headless,
        startUrl: startUrl ?? currentOptions.startUrl ?? "about:blank",
        prefs: mergedPrefs
      };
      setNextLaunchOptions(newOptions);
      await resetFirefox();
      const changes = [];
      if (firefoxPath && firefoxPath !== currentOptions.firefoxPath) {
        changes.push(`Binary: ${firefoxPath}`);
      }
      if (profilePath && profilePath !== currentOptions.profilePath) {
        changes.push(`Profile: ${profilePath}`);
      }
      if (newEnv !== void 0 && JSON.stringify(newEnv) !== JSON.stringify(currentOptions.env)) {
        changes.push(`Environment variables updated:`);
        for (const [key, value] of Object.entries(newEnv)) {
          changes.push(`  ${key}=${value}`);
        }
      }
      if (headless !== void 0 && headless !== currentOptions.headless) {
        changes.push(`Headless: ${headless ? "enabled" : "disabled"}`);
      }
      if (startUrl && startUrl !== currentOptions.startUrl) {
        changes.push(`Start URL: ${startUrl}`);
      }
      if (changes.length === 0) {
        return successResponse(
          "Firefox closed. Will restart with same configuration on next tool call."
        );
      }
      return successResponse(
        `Firefox closed. Will restart with new configuration on next tool call:
${changes.join("\n")}`
      );
    } else {
      if (currentFirefox) {
        await resetFirefox();
      }
      const resolvedFirefoxPath = firefoxPath ?? args.firefoxPath ?? void 0;
      if (!resolvedFirefoxPath) {
        return errorResponse(
          new Error(
            "Firefox is not running and no firefoxPath provided. Please specify firefoxPath to start Firefox."
          )
        );
      }
      const newOptions = {
        firefoxPath: resolvedFirefoxPath,
        profilePath: profilePath ?? args.profilePath ?? void 0,
        env: newEnv,
        headless: headless ?? false,
        startUrl: startUrl ?? "about:blank"
      };
      setNextLaunchOptions(newOptions);
      const config = [`Binary: ${resolvedFirefoxPath}`];
      const resolvedProfilePath = profilePath ?? args.profilePath;
      if (resolvedProfilePath) {
        config.push(`Profile: ${resolvedProfilePath}`);
      }
      if (newEnv) {
        config.push("Environment variables:");
        for (const [key, value] of Object.entries(newEnv)) {
          config.push(`  ${key}=${value}`);
        }
      }
      if (headless) {
        config.push("Headless: enabled");
      }
      if (startUrl) {
        config.push(`Start URL: ${startUrl}`);
      }
      return successResponse(
        `Firefox configured. Will start on next tool call:
${config.join("\n")}`
      );
    }
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/privileged-context.ts
init_moz_shim();
var listPrivilegedContextsTool = {
  name: "list_privileged_contexts",
  description: "List privileged (privileged) browsing contexts. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var. Use restart_firefox with env parameter to enable.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
var selectPrivilegedContextTool = {
  name: "select_privileged_context",
  description: 'Select a privileged browsing context by ID and set WebDriver Classic context to "chrome" . Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var.',
  inputSchema: {
    type: "object",
    properties: {
      contextId: {
        type: "string",
        description: "Privileged browsing context ID from list_privileged_contexts"
      }
    },
    required: ["contextId"]
  }
};
var evaluatePrivilegedScriptTool = {
  name: "evaluate_privileged_script",
  description: "Execute JS function in the current privileged context. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var. Use select_privileged_context first to target a chrome context.",
  inputSchema: {
    type: "object",
    properties: {
      function: {
        type: "string",
        description: 'JS function string, e.g. () => Services.prefs.getBoolPref("foo")'
      }
    },
    required: ["function"]
  }
};
function formatContextList(contexts) {
  if (contexts.length === 0) {
    return "No privileged contexts found";
  }
  const lines = [`${contexts.length} privileged contexts`];
  for (const ctx of contexts) {
    const id = ctx.context;
    const url = ctx.url || "(no url)";
    const children = ctx.children ? ` [${ctx.children.length} children]` : "";
    lines.push(`  ${id}: ${url}${children}`);
  }
  return lines.join("\n");
}
async function handleListPrivilegedContexts(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const result = await firefox.sendBiDiCommand("browsingContext.getTree", {
      "moz:scope": "chrome"
    });
    const contexts = result.contexts || [];
    return successResponse(formatContextList(contexts));
  } catch (error) {
    if (error instanceof Error && error.message.includes("UnsupportedOperationError")) {
      return errorResponse(
        new Error(
          "Privileged context access not enabled. Set MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable and restart Firefox."
        )
      );
    }
    return errorResponse(error);
  }
}
async function handleSelectPrivilegedContext(args2) {
  try {
    const { contextId } = args2;
    if (!contextId || typeof contextId !== "string") {
      throw new Error("contextId parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const driver = firefox.getDriver();
    await driver.switchTo().window(contextId);
    try {
      await driver.setContext("chrome");
    } catch {
      return errorResponse(
        new Error(
          `Switched to context ${contextId} but failed to set Marionette privileged context. Your Firefox build may not support privileged context or MOZ_REMOTE_ALLOW_SYSTEM_ACCESS is not set.`
        )
      );
    }
    firefox.setCurrentContextId(contextId);
    return successResponse(
      `Switched to privileged context: ${contextId} (Marionette context set to privileged)`
    );
  } catch (error) {
    return errorResponse(error);
  }
}
var EvaluateResultType2 = {
  Exception: "exception",
  Success: "success"
};
async function handleEvaluatePrivilegedScript(args2) {
  try {
    const { function: fnString } = args2;
    validateFunction(fnString);
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const result = await firefox.sendBiDiCommand("script.callFunction", {
      functionDeclaration: fnString,
      awaitPromise: true,
      arguments: [],
      target: { context: firefox.getCurrentContextId() }
    });
    if (result.type === EvaluateResultType2.Success) {
      let output = "Script ran in chrome context and returned:\n";
      output += "```json\n";
      output += JSON.stringify(remoteValueToNative(result.result), null, 2);
      output += "\n```";
      return successResponse(output);
    } else if (result.type === EvaluateResultType2.Exception) {
      const exceptionDetails = result.exceptionDetails;
      return errorResponse(
        new Error(
          `Script execution failed: ${exceptionDetails.text}

\`\`\`json
` + JSON.stringify(remoteValueToNative(exceptionDetails.exception), null, 2) + "\n```"
        )
      );
    } else {
      return errorResponse(`Unexpected script.callFunction result type: ${result.type}`);
    }
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/firefox-prefs.ts
init_moz_shim();

// ../src/firefox/pref-utils.ts
init_moz_shim();
function generatePrefScript(name, value) {
  const escapedName = JSON.stringify(name);
  if (typeof value === "boolean") {
    return `Services.prefs.setBoolPref(${escapedName}, ${value})`;
  } else if (typeof value === "number") {
    return `Services.prefs.setIntPref(${escapedName}, ${value})`;
  } else {
    return `Services.prefs.setStringPref(${escapedName}, ${JSON.stringify(value)})`;
  }
}

// ../src/tools/firefox-prefs.ts
var setFirefoxPrefsTool = {
  name: "set_firefox_prefs",
  description: "Set Firefox preferences at runtime a privileged API. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var.",
  inputSchema: {
    type: "object",
    properties: {
      prefs: {
        type: "object",
        description: "Object mapping preference names to values. Values are auto-typed: true/false become booleans, integers become numbers, everything else is a string.",
        additionalProperties: {
          oneOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }]
        }
      }
    },
    required: ["prefs"]
  }
};
async function handleSetFirefoxPrefs(args2) {
  try {
    const { prefs } = args2;
    if (!prefs || typeof prefs !== "object") {
      throw new Error("prefs parameter is required and must be an object");
    }
    const prefEntries = Object.entries(prefs);
    if (prefEntries.length === 0) {
      return successResponse("No preferences to set");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const result = await firefox.sendBiDiCommand("browsingContext.getTree", {
      "moz:scope": "chrome"
    });
    const contexts = result.contexts || [];
    if (contexts.length === 0) {
      throw new Error(
        "No privileged contexts available. Ensure MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 is set."
      );
    }
    const driver = firefox.getDriver();
    const chromeContextId = contexts[0].context;
    const originalContextId = firefox.getCurrentContextId();
    try {
      await driver.switchTo().window(chromeContextId);
      await driver.setContext("chrome");
      const results = [];
      const errors = [];
      for (const [name, value] of prefEntries) {
        try {
          const script = generatePrefScript(name, value);
          await driver.executeScript(script);
          results.push(`  ${name} = ${JSON.stringify(value)}`);
        } catch (error) {
          errors.push(`  ${name}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      const output = [];
      if (results.length > 0) {
        output.push(`Set ${results.length} preference(s):`);
        output.push(...results);
      }
      if (errors.length > 0) {
        output.push(`
Failed to set ${errors.length} preference(s):`);
        output.push(...errors);
      }
      return successResponse(output.join("\n"));
    } finally {
      try {
        if (originalContextId && originalContextId !== chromeContextId) {
          await driver.setContext("content");
          await driver.switchTo().window(originalContextId);
        }
      } catch {
      }
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes("UnsupportedOperationError")) {
      return errorResponse(
        new Error(
          "Chrome context access not enabled. Set MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable and restart Firefox."
        )
      );
    }
    return errorResponse(error);
  }
}
var getFirefoxPrefsTool = {
  name: "get_firefox_prefs",
  description: "Get Firefox preference values via a privileged API. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var.",
  inputSchema: {
    type: "object",
    properties: {
      names: {
        type: "array",
        items: { type: "string" },
        description: "Array of preference names to read"
      }
    },
    required: ["names"]
  }
};
async function handleGetFirefoxPrefs(args2) {
  try {
    const { names } = args2;
    if (!names || !Array.isArray(names) || names.length === 0) {
      throw new Error("names parameter is required and must be a non-empty array");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const result = await firefox.sendBiDiCommand("browsingContext.getTree", {
      "moz:scope": "chrome"
    });
    const contexts = result.contexts || [];
    if (contexts.length === 0) {
      throw new Error(
        "No privileged contexts available. Ensure MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 is set."
      );
    }
    const driver = firefox.getDriver();
    const chromeContextId = contexts[0].context;
    const originalContextId = firefox.getCurrentContextId();
    try {
      await driver.switchTo().window(chromeContextId);
      await driver.setContext("chrome");
      const results = [];
      const errors = [];
      for (const name of names) {
        try {
          const script = `
            (function() {
              const type = Services.prefs.getPrefType(${JSON.stringify(name)});
              if (type === Services.prefs.PREF_INVALID) {
                return { exists: false };
              } else if (type === Services.prefs.PREF_BOOL) {
                return { exists: true, value: Services.prefs.getBoolPref(${JSON.stringify(name)}) };
              } else if (type === Services.prefs.PREF_INT) {
                return { exists: true, value: Services.prefs.getIntPref(${JSON.stringify(name)}) };
              } else {
                return { exists: true, value: Services.prefs.getStringPref(${JSON.stringify(name)}) };
              }
            })()
          `;
          const prefResult = await driver.executeScript(`return ${script}`);
          if (prefResult.exists) {
            results.push(`  ${name} = ${JSON.stringify(prefResult.value)}`);
          } else {
            results.push(`  ${name} = (not set)`);
          }
        } catch (error) {
          errors.push(`  ${name}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      const output = [];
      if (results.length > 0) {
        output.push(`Firefox Preferences:`);
        output.push(...results);
      }
      if (errors.length > 0) {
        output.push(`
Failed to read ${errors.length} preference(s):`);
        output.push(...errors);
      }
      return successResponse(output.join("\n"));
    } finally {
      try {
        if (originalContextId && originalContextId !== chromeContextId) {
          await driver.setContext("content");
          await driver.switchTo().window(originalContextId);
        }
      } catch {
      }
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes("UnsupportedOperationError")) {
      return errorResponse(
        new Error(
          "Chrome context access not enabled. Set MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable and restart Firefox."
        )
      );
    }
    return errorResponse(error);
  }
}

// ../src/tools/webextension.ts
init_moz_shim();
var installExtensionTool = {
  name: "install_extension",
  description: "Install a Firefox extension using WebDriver BiDi webExtension.install command. Supports installing from archive (.xpi/.zip), base64-encoded data, or unpacked directory.",
  inputSchema: {
    type: "object",
    properties: {
      type: {
        type: "string",
        enum: ["archivePath", "base64", "path"],
        description: 'Extension data type: "archivePath" for .xpi/.zip, "base64" for encoded data, "path" for unpacked directory'
      },
      path: {
        type: "string",
        description: "File path (for archivePath or path types)"
      },
      value: {
        type: "string",
        description: "Base64-encoded extension data (for base64 type)"
      },
      permanent: {
        type: "boolean",
        description: "Firefox-specific: Install permanently (requires signed extension). Default: false (temporary install)"
      }
    },
    required: ["type"]
  }
};
async function handleInstallExtension(args2) {
  try {
    const { type, path, value, permanent } = args2;
    if (!type) {
      throw new Error("type parameter is required");
    }
    if ((type === "archivePath" || type === "path") && !path) {
      throw new Error(`path parameter is required for type "${type}"`);
    }
    if (type === "base64" && !value) {
      throw new Error('value parameter is required for type "base64"');
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const extensionData = { type };
    if (path) {
      extensionData.path = path;
    }
    if (value) {
      extensionData.value = value;
    }
    const params = { extensionData };
    if (permanent !== void 0) {
      params["moz:permanent"] = permanent;
    }
    const result = await firefox.sendBiDiCommand("webExtension.install", params);
    const extensionId = result?.extension || "unknown";
    const installType = permanent ? "permanent" : "temporary";
    return successResponse(
      `Extension installed (${installType}):
  ID: ${extensionId}
  Type: ${type}${path ? `
  Path: ${path}` : ""}`
    );
  } catch (error) {
    return errorResponse(error);
  }
}
var uninstallExtensionTool = {
  name: "uninstall_extension",
  description: "Uninstall a Firefox extension using WebDriver BiDi webExtension.uninstall command. Requires the extension ID returned by install_extension or obtained from list_extensions.",
  inputSchema: {
    type: "object",
    properties: {
      id: {
        type: "string",
        description: 'Extension ID (e.g., "addon@example.com")'
      }
    },
    required: ["id"]
  }
};
async function handleUninstallExtension(args2) {
  try {
    const { id } = args2;
    if (!id || typeof id !== "string") {
      throw new Error("id parameter is required and must be a string");
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    await firefox.sendBiDiCommand("webExtension.uninstall", { extension: id });
    return successResponse(`Extension uninstalled:
  ID: ${id}`);
  } catch (error) {
    return errorResponse(error);
  }
}
var listExtensionsTool = {
  name: "list_extensions",
  description: (
    // MOZ_REMOTE_ALLOW_SYSTEM_ACCESS is required because the tool relies on the
    // privileged AddonManager API as a workaround for the currently missing
    // webExtension.getExtensions WebDriver BiDi command.
    "List installed Firefox extensions with UUIDs and background scripts. Requires MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env var."
  ),
  inputSchema: {
    type: "object",
    properties: {
      ids: {
        type: "array",
        items: { type: "string" },
        description: 'Optional: Filter by exact extension IDs (e.g., ["addon@example.com"])'
      },
      name: {
        type: "string",
        description: 'Optional: Filter by partial name match (case-insensitive, e.g., "shopify")'
      },
      isActive: {
        type: "boolean",
        description: "Optional: Filter by enabled (true) or disabled (false) status"
      },
      isSystem: {
        type: "boolean",
        description: "Optional: Filter by system/built-in (true) or user-installed (false) extensions"
      }
    }
  }
};
function formatExtensionList(extensions, filterId) {
  if (extensions.length === 0) {
    return filterId ? `Extension not found: ${filterId}` : "No extensions installed";
  }
  const lines = [
    `${extensions.length} extension(s)${filterId ? ` (filtered by: ${filterId})` : ""}`
  ];
  for (const ext of extensions) {
    lines.push("");
    lines.push(`  ${ext.name} (v${ext.version})`);
    lines.push(`     ID: ${ext.id}`);
    lines.push(`     Type: ${ext.isSystem ? "System/Built-in" : "User-installed"}`);
    lines.push(`     UUID: ${ext.uuid}`);
    lines.push(`     Base URL: ${ext.baseURL}`);
    lines.push(`     Manifest: v${ext.manifestVersion || "unknown"}`);
    lines.push(`     Active: ${ext.isActive ? "yes" : "no"}`);
    if (ext.backgroundScripts.length > 0) {
      lines.push(`     Background scripts:`);
      for (const script of ext.backgroundScripts) {
        const scriptName = script.split("/").pop();
        lines.push(`       \u2022 ${scriptName}`);
      }
    } else {
      lines.push(`     Background scripts: (none)`);
    }
  }
  return lines.join("\n");
}
async function handleListExtensions(args2) {
  try {
    const { ids, name, isActive, isSystem } = args2 || {};
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    const result = await firefox.sendBiDiCommand("browsingContext.getTree", {
      "moz:scope": "chrome"
    });
    const contexts = result.contexts || [];
    if (contexts.length === 0) {
      throw new Error(
        "No privileged contexts available. Ensure MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 is set."
      );
    }
    const driver = firefox.getDriver();
    const chromeContextId = contexts[0].context;
    const originalContextId = firefox.getCurrentContextId();
    try {
      await driver.switchTo().window(chromeContextId);
      await driver.setContext("chrome");
      const filterParams = { ids, name, isActive, isSystem };
      const script = `
        const callback = arguments[arguments.length - 1];
        const filter = ${JSON.stringify(filterParams)};
        (async () => {
          try {
            const { AddonManager } = ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs");
            let addons = await AddonManager.getAllAddons();

            // Filter to only extensions (not themes, plugins, etc.)
            addons = addons.filter(addon => addon.type === "extension");

            // Apply filters
            if (filter.ids && filter.ids.length > 0) {
              addons = addons.filter(addon => filter.ids.includes(addon.id));
            }
            if (filter.name) {
              const search = filter.name.toLowerCase();
              addons = addons.filter(addon => addon.name.toLowerCase().includes(search));
            }
            if (typeof filter.isActive === 'boolean') {
              addons = addons.filter(addon => addon.isActive === filter.isActive);
            }
            if (typeof filter.isSystem === 'boolean') {
              addons = addons.filter(addon => addon.isSystem === filter.isSystem);
            }

            const extensions = [];
            for (const addon of addons) {
              const policy = WebExtensionPolicy.getByID(addon.id);
              if (!policy) continue; // Skip if no policy (addon not loaded)

              extensions.push({
                id: addon.id,
                name: addon.name,
                version: addon.version,
                isActive: addon.isActive,
                isSystem: addon.isSystem,
                uuid: policy.mozExtensionHostname,
                baseURL: policy.baseURL,
                backgroundScripts: policy.extension?.backgroundScripts || [],
                manifestVersion: policy.extension?.manifest?.manifest_version || null
              });
            }

            callback(extensions);
          } catch (error) {
            callback([]);
          }
        })();
      `;
      const extensions = await driver.executeAsyncScript(script);
      const filterDesc = [
        ids && ids.length > 0 ? `ids: [${ids.join(", ")}]` : null,
        name ? `name: "${name}"` : null,
        typeof isActive === "boolean" ? `active: ${isActive}` : null,
        typeof isSystem === "boolean" ? `system: ${isSystem}` : null
      ].filter(Boolean).join(", ");
      return successResponse(formatExtensionList(extensions, filterDesc || void 0));
    } finally {
      try {
        if (originalContextId && originalContextId !== chromeContextId) {
          await driver.setContext("content");
          await driver.switchTo().window(originalContextId);
        }
      } catch {
      }
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes("UnsupportedOperationError")) {
      return errorResponse(
        new Error(
          "Chrome context access not enabled. Set MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable and restart Firefox."
        )
      );
    }
    return errorResponse(error);
  }
}

// ../src/tools/debugging.ts
init_moz_shim();

// ../src/utils/version.ts
init_moz_shim();
function getMajorVersion(version) {
  const [major, _rhs] = version.split(".");
  if (!major) {
    throw new Error(`Unable to parse Firefox version ${version}`);
  }
  return Number.parseInt(major, 10);
}
function compareVersions(versionA, versionB) {
  const majorA = getMajorVersion(versionA);
  const majorB = getMajorVersion(versionB);
  if (majorA < majorB) {
    return -1;
  }
  if (majorA > majorB) {
    return 1;
  }
  return 0;
}

// ../src/tools/debugging.ts
var MIN_VERSION = "153";
function requireDebuggingSupport(firefox) {
  const version = firefox.getFirefoxVersion();
  if (version !== null && compareVersions(version, MIN_VERSION) < 0) {
    throw new Error(
      `moz:debugging requires Firefox ${MIN_VERSION}+, current version is ${version}`
    );
  }
}
function requireContext(contextId) {
  if (!contextId) {
    throw new Error("No active browsing context");
  }
  return contextId;
}
var enableDebuggerTool = {
  name: "enable_debugger",
  description: "Enable the JS debugger for the current page. Required before set_logpoint works. Requires Firefox 153+.",
  inputSchema: { type: "object", properties: {} }
};
var listScriptsTool = {
  name: "list_scripts",
  description: "List all JavaScript files currently loaded in the page. Requires enable_debugger to have been called.",
  inputSchema: { type: "object", properties: {} }
};
var getScriptSourceTool = {
  name: "get_script_source",
  description: "Get the source code of a JavaScript file loaded in the page. Requires enable_debugger to have been called.",
  inputSchema: {
    type: "object",
    properties: {
      scriptUrl: { type: "string", description: "URL of the script to retrieve." }
    },
    required: ["scriptUrl"]
  }
};
var setLogpointTool = {
  name: "set_logpoint",
  description: "Set a logpoint at a specific location. When execution reaches that line, the expression is evaluated and the result is stored without pausing. Use get_logpoint_results to retrieve collected values. Requires enable_debugger to have been called.",
  inputSchema: {
    type: "object",
    properties: {
      url: { type: "string", description: "URL of the script." },
      line: { type: "number", description: "Line number (1-based)." },
      expression: {
        type: "string",
        description: "JavaScript expression to evaluate each time the logpoint is hit."
      }
    },
    required: ["url", "line", "expression"]
  }
};
var removeLogpointTool = {
  name: "remove_logpoint",
  description: "Remove a previously set logpoint.",
  inputSchema: {
    type: "object",
    properties: {
      logpoint: { type: "string", description: "Logpoint id returned by set_logpoint." }
    },
    required: ["logpoint"]
  }
};
var getLogpointResultsTool = {
  name: "get_logpoint_results",
  description: "Get the results collected by a logpoint since it was set.",
  inputSchema: {
    type: "object",
    properties: {
      logpoint: { type: "string", description: "Logpoint id returned by set_logpoint." }
    },
    required: ["logpoint"]
  }
};
async function handleEnableDebugger(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    await firefox.sendBiDiCommand("moz:debugging.setDebuggerEnabled", { enabled: true });
    return successResponse("Debugger enabled");
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleListScripts(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    const contextId = requireContext(firefox.getCurrentContextId());
    const result = await firefox.sendBiDiCommand("moz:debugging.listScripts", {
      context: contextId
    });
    const scripts = result.scripts;
    if (scripts.length === 0) {
      return successResponse("No scripts found");
    }
    return successResponse(scripts.join("\n"));
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleGetScriptSource(args2) {
  try {
    const { scriptUrl } = args2;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    const contextId = requireContext(firefox.getCurrentContextId());
    const result = await firefox.sendBiDiCommand("moz:debugging.getScriptSource", {
      context: contextId,
      scriptUrl
    });
    return successResponse(result.source);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleSetLogpoint(args2) {
  try {
    const { url, line, expression } = args2;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    const logpointId = await firefox.setLogpoint(url, line, expression);
    return successResponse(`Logpoint set (id: ${logpointId})`);
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleRemoveLogpoint(args2) {
  try {
    const { logpoint } = args2;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    await firefox.removeLogpoint(logpoint);
    return successResponse("Logpoint removed");
  } catch (error) {
    return errorResponse(error);
  }
}
async function handleGetLogpointResults(args2) {
  try {
    const { logpoint } = args2;
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    requireDebuggingSupport(firefox);
    const results = firefox.getLogpointResults(logpoint);
    if (results === null) {
      return errorResponse(new Error(`Logpoint ${logpoint} not found`));
    }
    if (results.length === 0) {
      return successResponse("No results collected yet");
    }
    const lines = results.map((r, i) => {
      if (r.error) {
        return `[${i + 1}] Error: ${r.error}`;
      }
      return `[${i + 1}] ${JSON.stringify(remoteValueToNative(r.value))}`;
    });
    return successResponse(lines.join("\n"));
  } catch (error) {
    return errorResponse(error);
  }
}

// ../src/tools/profiler.ts
init_moz_shim();
var MIN_FIREFOX_VERSION = "154.0";
function checkProfilerSupported(firefox) {
  const version = firefox.getFirefoxVersion();
  if (version !== null && compareVersions(version, MIN_FIREFOX_VERSION) < 0) {
    throw new Error(
      `moz:profiler requires Firefox ${MIN_FIREFOX_VERSION.split(".")[0]} or later (connected: ${version})`
    );
  }
}
var VALID_PRESETS = [
  "web-developer",
  "firefox-platform",
  "graphics",
  "media",
  "ml",
  "networking",
  "power",
  "debug"
];
var profilerIsActiveTool = {
  name: "profiler_is_active",
  description: "Check whether the Firefox profiler is currently recording.",
  inputSchema: {
    type: "object",
    properties: {}
  }
};
async function handleProfilerIsActive(_args) {
  try {
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    checkProfilerSupported(firefox);
    const result = await firefox.sendBiDiCommand("moz:profiler.isActive", {});
    return successResponse(`Profiler is ${result.active ? "active" : "inactive"}`);
  } catch (error) {
    return errorResponse(error);
  }
}
var profilerStartTool = {
  name: "profiler_start",
  description: `Start the Firefox profiler. Provide either a preset name or explicit recording options (entries, interval, features, threads). Cannot combine both. Valid presets: ${VALID_PRESETS.join(", ")}.`,
  inputSchema: {
    type: "object",
    properties: {
      preset: {
        type: "string",
        enum: VALID_PRESETS,
        description: "Profiler preset name. Cannot be combined with entries, interval, features, or threads."
      },
      entries: {
        type: "integer",
        description: "Number of entries to keep in the sampling buffer. Required when no preset is given."
      },
      interval: {
        type: "number",
        description: "Sampling interval in milliseconds. Required when no preset is given."
      },
      features: {
        type: "array",
        items: { type: "string" },
        description: "Profiler features to enable. Required when no preset is given."
      },
      threads: {
        type: "array",
        items: { type: "string" },
        description: "Thread names to profile. Required when no preset is given."
      },
      activeContext: {
        type: "string",
        description: "Id of the top-level navigable to mark as the active tab in the profile. Does not restrict profiling to that tab."
      }
    }
  }
};
async function handleProfilerStart(args2) {
  try {
    const { preset, entries, interval, features, threads, activeContext } = args2;
    const params = {};
    if (preset !== void 0) {
      params.preset = preset;
    } else {
      if (entries === void 0 || interval === void 0 || features === void 0 || threads === void 0) {
        throw new Error(
          "When no preset is given, entries, interval, features, and threads are all required."
        );
      }
      params.entries = entries;
      params.interval = interval;
      params.features = features;
      params.threads = threads;
    }
    if (activeContext !== void 0) {
      params.activeContext = activeContext;
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    checkProfilerSupported(firefox);
    await firefox.sendBiDiCommand("moz:profiler.start", params);
    return successResponse("Profiler started");
  } catch (error) {
    return errorResponse(error);
  }
}
var profilerStopTool = {
  name: "profiler_stop",
  description: "Stop the Firefox profiler and save the recorded profile to a file in the downloads directory. Returns the path to the saved file, or null when nothing was saved.",
  inputSchema: {
    type: "object",
    properties: {
      discard: {
        type: "boolean",
        description: "If true, stop the profiler and discard the recording instead of saving it to disk. Defaults to false."
      }
    }
  }
};
async function handleProfilerStop(args2) {
  try {
    const { discard } = args2;
    const params = {};
    if (discard !== void 0) {
      params.discard = discard;
    }
    const { getFirefox: getFirefox2 } = await Promise.resolve().then(() => (init_provider(), provider_exports));
    const firefox = await getFirefox2();
    checkProfilerSupported(firefox);
    const result = await firefox.sendBiDiCommand("moz:profiler.stop", params);
    if (result.path) {
      return successResponse(`Profile saved to: ${result.path}`);
    }
    return successResponse("Profiler stopped. No profile was saved.");
  } catch (error) {
    return errorResponse(error);
  }
}

// src/mcp.ts
init_provider();
var SERVER_INFO = { name: "firefox-devtools-mcp-extension", version: "0.0.1" };
var DEV_TOKEN = "bidi-bridge-dev";
var DEFAULT_PORT = 9339;
var NODE_ONLY_TOOLS = /* @__PURE__ */ new Set([
  "restart_firefox",
  "get_firefox_output",
  "list_extensions",
  "install_extension",
  "uninstall_extension"
]);
var text = (t) => ({ content: [{ type: "text", text: t }] });
var errText = (e) => ({
  content: [{ type: "text", text: `Error: ${e instanceof Error ? e.message : String(e)}` }],
  isError: true
});
var OVERRIDDEN_HANDLERS = {
  get_firefox_prefs: async (args2) => {
    const { names } = args2;
    if (!names || !Array.isArray(names) || names.length === 0) {
      return errText(new Error("names parameter is required and must be a non-empty array"));
    }
    const results = [];
    const errors = [];
    for (const name of names) {
      try {
        const res = await browser.bidi.getPref(name);
        results.push(
          res.type === "invalid" ? `  ${name} = (not set)` : `  ${name} = ${JSON.stringify(res.value)}`
        );
      } catch (e) {
        errors.push(`  ${name}: ${e instanceof Error ? e.message : String(e)}`);
      }
    }
    const out = [];
    if (results.length) out.push("Firefox Preferences:", ...results);
    if (errors.length) out.push(`
Failed to read ${errors.length} preference(s):`, ...errors);
    return text(out.join("\n"));
  },
  set_firefox_prefs: async (args2) => {
    const { prefs } = args2;
    if (!prefs || typeof prefs !== "object") {
      return errText(new Error("prefs parameter is required and must be an object"));
    }
    const entries = Object.entries(prefs);
    if (entries.length === 0) return text("No preferences to set");
    const results = [];
    const errors = [];
    for (const [name, value] of entries) {
      try {
        await browser.bidi.setPref(name, value);
        results.push(`  ${name} = ${JSON.stringify(value)}`);
      } catch (e) {
        errors.push(`  ${name}: ${e instanceof Error ? e.message : String(e)}`);
      }
    }
    const out = [];
    if (results.length) out.push(`Set ${results.length} preference(s):`, ...results);
    if (errors.length) out.push(`
Failed to set ${errors.length} preference(s):`, ...errors);
    return text(out.join("\n"));
  }
};
function buildRegistry() {
  const registry = /* @__PURE__ */ new Map();
  const exports = tools_exports;
  for (const [key, value] of Object.entries(exports)) {
    if (!key.endsWith("Tool") || !value?.name) continue;
    const base = key.slice(0, -4);
    const handlerName = `handle${base[0].toUpperCase()}${base.slice(1)}`;
    const handler = exports[handlerName];
    if (typeof handler !== "function") {
      console.warn(`[fdm-ext] no handler ${handlerName} for ${value.name}`);
      continue;
    }
    if (NODE_ONLY_TOOLS.has(value.name)) continue;
    registry.set(value.name, { definition: value, handler: OVERRIDDEN_HANDLERS[value.name] ?? handler });
  }
  return registry;
}
var sleep2 = (ms) => new Promise((r) => setTimeout(r, ms));
function rpcResult(id, result) {
  return JSON.stringify({ jsonrpc: "2.0", id, result });
}
function rpcError(id, code, message) {
  return JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } });
}
async function startMcp(port) {
  const registry = buildRegistry();
  console.log(`[fdm-ext] serving ${registry.size} tools`);
  browser.bidi.onHttpRequest.addListener(async (req) => {
    const respond = (status, body, contentType = "application/json") => browser.bidi.sendHttpResponse(req.id, status, { "Content-Type": contentType }, body);
    try {
      if (req.headers["origin"]) return void await respond(403, "browser origins not allowed", "text/plain");
      if (req.path !== "/mcp") return void await respond(404, "not found", "text/plain");
      if (req.method === "GET") return void await respond(405, "SSE stream not supported", "text/plain");
      if (req.method !== "POST") return void await respond(405, "", "text/plain");
      if ((req.headers["authorization"] ?? "") !== `Bearer ${DEV_TOKEN}`) {
        return void await respond(401, "bad or missing bearer token", "text/plain");
      }
      const msg = JSON.parse(req.body);
      const { id, method, params } = msg;
      if (method?.startsWith("notifications/")) return void await respond(202, "");
      switch (method) {
        case "initialize":
          return void await respond(200, rpcResult(id, {
            protocolVersion: ["2024-11-05", "2025-03-26", "2025-06-18"].includes(params?.protocolVersion) ? params.protocolVersion : "2025-03-26",
            capabilities: { tools: {} },
            serverInfo: SERVER_INFO
          }));
        case "ping":
          return void await respond(200, rpcResult(id, {}));
        case "tools/list":
          return void await respond(200, rpcResult(id, {
            tools: [...registry.values()].map((t) => t.definition)
          }));
        case "tools/call": {
          const entry = registry.get(params?.name);
          if (!entry) return void await respond(200, rpcError(id, -32602, `Unknown tool: ${params?.name}`));
          let result;
          try {
            await getFirefox();
            result = await Promise.race([
              entry.handler(params?.arguments ?? {}),
              sleep2(6e4).then(() => ({
                content: [{ type: "text", text: "Error: tool timed out after 60s" }],
                isError: true
              }))
            ]);
          } catch (e) {
            result = errText(e);
          }
          return void await respond(200, rpcResult(id, result));
        }
        default:
          return void await respond(200, rpcError(id, -32601, `Method not found: ${method}`));
      }
    } catch (e) {
      console.error("[fdm-ext] http handler error", e);
      try {
        await respond(400, rpcError(null, -32700, "parse error"));
      } catch {
      }
    }
  });
  return browser.bidi.startServer(port);
}
export {
  DEFAULT_PORT,
  configure,
  startMcp
};
