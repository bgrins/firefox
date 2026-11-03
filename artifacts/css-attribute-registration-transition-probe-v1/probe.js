"use strict";

const images = {
  a: "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1'%20height='1'%3E%3Cpath%20fill='red'%20d='M0%200h1v1H0z'/%3E%3C/svg%3E",
  b: "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1'%20height='1'%3E%3Cpath%20fill='blue'%20d='M0%200h1v1H0z'/%3E%3C/svg%3E",
};
const cases = [
  { id: "registration-and-attribute-discrete", flip: true, changeAttribute: true, literal: false, behavior: "allow-discrete" },
  { id: "registration-attr-discrete", flip: true, literal: false, behavior: "allow-discrete" },
  { id: "registration-attr-normal", flip: true, changeAttribute: true, literal: false, behavior: "normal" },
  { id: "same-registration-attr-discrete", flip: false, changeAttribute: true, literal: false, behavior: "allow-discrete" },
  { id: "registration-literal-discrete", flip: true, literal: true, behavior: "allow-discrete" },
];
const registration = typed => `@property --source { syntax: "${typed ? "<string>" : "*"}"; inherits: false; ${typed ? 'initial-value: "initial";' : ""} }`;
async function withTimeout(promise, label) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(label)), 10000); }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

async function observe(spec) {
  const frame = document.createElement("iframe");
  frame.title = spec.id;
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, { once: true }));
  frame.srcdoc = `<!doctype html><meta charset="utf-8"><style id="registration">${registration(!spec.flip)}</style><style>
    #target { --source: ${spec.literal ? JSON.stringify(images.a) : "attr(data-ticket)"};
      transition-property: --source; transition-duration: 100s; transition-timing-function: linear;
      transition-behavior: ${spec.behavior}; background-image: image-set(var(--source)); }
    #registration-control { --source: 17px; }
    </style><div id="target" data-ticket="${images.a}">fixed image observation</div><div id="registration-control">registration control</div>`;
  document.body.append(frame);
  const row = {
    ...spec,
    samples: [],
    getterOrder: ["--source", "background-image", "registration-control --source"],
    expectedSourceA: JSON.stringify(images.a),
    expectedSourceB: JSON.stringify(images.b),
    expectedRegistrationBefore: spec.flip ? "17px" : '\"initial\"',
    expectedRegistrationAfter: '\"initial\"',
  };
  try {
    await withTimeout(loaded, "iframe load timeout");
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    const target = doc.getElementById("target");
    const values = () => {
      const style = win.getComputedStyle(target);
      return {
        source: style.getPropertyValue("--source").trim(),
        image: style.backgroundImage,
        registrationControl: win.getComputedStyle(doc.getElementById("registration-control")).getPropertyValue("--source").trim(),
      };
    };
    row.imageSyntaxSupported = win.CSS.supports("background-image", `image-set(${row.expectedSourceA})`);
    row.before = values();
    await withTimeout(new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve))), "initial frame timeout");
    row.beforeStable = values();
    row.animationsBefore = target.getAnimations().map(a => ({ type: a.constructor.name, property: a.transitionProperty ?? null }));
    if (spec.flip) {
      doc.getElementById("registration").textContent = registration(true);
    }
    if (spec.changeAttribute) {
      target.setAttribute("data-ticket", images.b);
    }
    row.afterChange = values();
    row.registration = doc.getElementById("registration").sheet.cssRules[0].cssText;
    const animations = target.getAnimations();
    row.animationsAfter = animations.map(a => ({ type: a.constructor.name, property: a.transitionProperty ?? null }));
    const transitions = animations.filter(a => a instanceof win.CSSTransition && a.transitionProperty === "--source");
    row.transitionCount = transitions.length;
    if (transitions.length === 1 && row.animationsBefore.length === 0) {
      const transition = transitions[0];
      transition.pause();
      await withTimeout(transition.ready, "transition pause timeout");
      row.duration = transition.effect.getComputedTiming().duration;
      row.keyframes = transition.effect.getKeyframes();
      for (const fraction of [0.25, 0.75]) {
        transition.currentTime = Number(row.duration) * fraction;
        const computed = values();
        const timing = transition.effect.getComputedTiming();
        row.samples.push({
          fraction,
          currentTime: transition.currentTime,
          progress: timing.progress,
          playState: transition.playState,
          expectedSource: spec.changeAttribute && fraction >= 0.5 ? row.expectedSourceB : row.expectedSourceA,
          ...computed,
        });
      }
      row.samplePrerequisites = row.duration === 100000 && row.samples.every(s => s.progress === s.fraction && s.playState === "paused");
    } else {
      row.samplePrerequisites = false;
      row.unmetPrerequisite = transitions.length !== 1 ? "No unique actual --source CSSTransition" : "Preexisting animation";
    }
    for (const animation of target.getAnimations()) {
      animation.cancel();
    }
    row.afterCancel = values();
    row.calibration = {
      registrationBefore: row.beforeStable.registrationControl === row.expectedRegistrationBefore,
      registrationAfter: row.afterChange.registrationControl === row.expectedRegistrationAfter,
      registrationAtSamples: row.samples.every(s => s.registrationControl === row.expectedRegistrationAfter),
      beforeSource: row.beforeStable.source === row.expectedSourceA,
      afterSource: row.afterCancel.source === (spec.changeAttribute ? row.expectedSourceB : row.expectedSourceA),
      sampledSources: row.samples.every(s => s.source === s.expectedSource),
      imageSyntax: row.imageSyntaxSupported,
    };
    row.sampleTimingPrerequisites = row.samplePrerequisites;
    row.samplePrerequisites = row.sampleTimingPrerequisites && Object.values(row.calibration).every(Boolean);
  } catch (error) {
    row.error = String(error);
    row.samplePrerequisites = false;
  } finally {
    frame.remove();
    row.frameRemoved = !frame.isConnected;
  }
  return row;
}

window.done = (async () => {
  const report = { kind: "observation only; no accepted defect or disclosure claim", userAgent: navigator.userAgent, cases: [] };
  for (const spec of cases) {
    report.cases.push(await observe(spec));
  }
  report.remainingFrames = document.querySelectorAll("iframe").length;
  window.REPORT = report;
  document.getElementById("output").textContent = JSON.stringify(report, null, 2);
  return report;
})();
