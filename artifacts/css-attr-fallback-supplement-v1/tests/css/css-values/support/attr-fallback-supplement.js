"use strict";

const attrFallbackSupplementCases = [
  "empty-selected-direct",
  "empty-selected-unregistered",
  "empty-selected-universal",
  "unused-tainted-fallback",
];

function runAttrFallbackSupplementCase(name) {
  const iframe = document.createElement("iframe");
  iframe.title = name;
  document.body.append(iframe);
  try {
    const doc = iframe.contentDocument;
    doc.open();
    doc.write("<!doctype html><meta charset=utf-8><title>Fallback supplement</title><body>");
    doc.close();
    const win = iframe.contentWindow;
    const quotedURL = '"data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"';
    const image = `image-set(${quotedURL})`;
    const unused = name === "unused-tainted-fallback";
    let registered = false;
    if (name === "empty-selected-universal") {
      win.CSS.registerProperty({ name: "--source", syntax: "*", inherits: false });
      registered = true;
    }
    const style = doc.createElement("style");
    const expression = `${image} var(--empty)`;
    style.textContent = `
      #control { background-image: ${image}; }
      #target {
        ${unused ? `--clean: ${quotedURL};
          background-image: image-set(var(--clean, attr(data-absent raw-string, ${quotedURL})));`
          : `--empty: attr(data-absent type(*),);
          --source: ${expression};
          padding-left: calc(3px var(--empty, + 13px));
          background-image: ${name === "empty-selected-direct" ? expression : "var(--source)"};`}
      }`;
    doc.head.append(style);
    const target = doc.createElement("div");
    target.id = "target";
    const control = doc.createElement("div");
    control.id = "control";
    doc.body.append(target, control);
    const computed = win.getComputedStyle(target);
    const actual = computed.backgroundImage;
    const literal = win.getComputedStyle(control).backgroundImage;
    const padding = unused ? null : computed.paddingLeft;
    const expected = unused || name === "empty-selected-direct" ? literal : "none";
    return {
      name, actual, expected, literal, padding, registered,
      standards: doc.compatMode === "CSS1Compat",
      typedAttr: win.CSS.supports("padding-left", "attr(data-absent type(<length>), 3px)"),
      missingAttribute: !target.hasAttribute("data-absent"),
      empty: unused ? null : computed.getPropertyValue("--empty"),
      source: unused ? null : computed.getPropertyValue("--source"),
      matchesExpected: actual === expected,
      validEmpty: unused ? null : padding === "3px",
      literalValid: literal !== "none",
    };
  } finally {
    iframe.remove();
  }
}

function runAttrFallbackSupplement() {
  return {
    userAgent: navigator.userAgent,
    rows: attrFallbackSupplementCases.map(name => {
      try {
        return runAttrFallbackSupplementCase(name);
      } catch (error) {
        return { name, error: String(error) };
      }
    }),
  };
}
