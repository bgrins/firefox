async () => JSON.stringify(await (
(async () => {
  const result = { schema: "animation-root-unit-style-dependency-v1", userAgent: navigator.userAgent, frames: [], errors: [], cleanup: false };
  const number = raw => {
    const match = /^"wdth"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$/i.exec(raw);
    return match ? Number(match[1]) : null;
  };
  const settle = async win => {
    await win.document.fonts.ready;
    await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
  };
  const owned = [];
  const allAnimations = [];
  try {
    for (const unit of ["rem", "rlh"]) {
      for (const order of ["ordinary-none", "ordinary-relative"]) {
        const frame = document.createElement("iframe");
        frame.title = `${unit} ${order} animation invalidation`;
        const loaded = new Promise(resolve => { frame.onload = resolve; });
        frame.srcdoc = `<!doctype html><meta charset="utf-8"><title>Root unit animation</title><style>
          html { font: 23px/37px monospace; writing-mode: horizontal-tb; }
          #parent { font: 30px/61px monospace; }
          .box { font: 60px/99px monospace; display:block; height:0; padding:0; border:0; }
          #variation, #width, #opacity { margin-left: ${order === "ordinary-relative" ? `1${unit}` : "0px"}; }
          #static-variation { font-variation-settings: "wdth" calc(2${unit} / 1px); }
          #static-width { width: 2${unit}; }
          #static-opacity { opacity: calc(2${unit} / 1000px); }
          #root-reference { width: 100${unit}; }
          #absolute-variation { font-variation-settings: "wdth" calc(30px / 1px); }
          #nonfont { opacity: calc(1em / 100px); }
        </style><div id="parent">
          <div class="box" id="variation"></div><div class="box" id="width"></div><div class="box" id="opacity"></div>
          <div class="box" id="static-variation"></div><div class="box" id="static-width"></div><div class="box" id="static-opacity"></div>
          <div class="box" id="root-reference"></div><div class="box" id="absolute-variation"></div>
          <div class="box" id="literal-variation"></div><div class="box" id="literal-width"></div>
          <div class="box" id="nonfont"></div></div>`;
        owned.push(frame);
        document.body.append(frame);
        await loaded;
        const win = frame.contentWindow;
        const doc = frame.contentDocument;
        const root = doc.documentElement;
        const parent = doc.getElementById("parent");
        const anims = [];
        const make = (element, property, values) => {
          const animation = element.animate(values.map(value => ({ [property]: value })), { duration: 1000, fill: "both" });
          animation.pause(); animation.currentTime = 500; anims.push(animation); allAnimations.push(animation); return animation;
        };
        const expressions = [1, 3].map(n => `"wdth" calc(${n}${unit} / 1px)`);
        let variationTarget = doc.getElementById("variation");
        let widthTarget = doc.getElementById("width");
        let opacityTarget = doc.getElementById("opacity");
        let variation = make(variationTarget, "fontVariationSettings", expressions);
        let width = make(widthTarget, "width", [1, 3].map(n => `${n}${unit}`));
        let opacity = make(opacityTarget, "opacity", [1, 3].map(n => `calc(${n}${unit} / 1000px)`));
        const literalVariation = make(doc.getElementById("literal-variation"), "fontVariationSettings", ['"wdth" 20', '"wdth" 40']);
        const literalWidth = make(doc.getElementById("literal-width"), "width", ["20px", "40px"]);
        const entry = { unit, order, compatMode: doc.compatMode, supports: {
          variation: expressions.map(value => win.CSS.supports("font-variation-settings", value)),
          width: win.CSS.supports("width", `1${unit}`),
          opacity: win.CSS.supports("opacity", `calc(1${unit} / 1000px)`),
        }, rows: [] };
        result.frames.push(entry);
        const animationInfo = animation => ({ progress: animation.effect.getComputedTiming().progress, playState: animation.playState, currentTime: animation.currentTime, keyframes: animation.effect.getKeyframes() });
        const take = (phase, timing, rootSize, rootLine, progress) => {
          let variationRaw, widthRaw, opacityRaw;
          const readVariation = () => { variationRaw = win.getComputedStyle(variationTarget).fontVariationSettings; };
          const readWidth = () => { widthRaw = win.getComputedStyle(widthTarget).width; };
          const readOpacity = () => { opacityRaw = win.getComputedStyle(opacityTarget).opacity; };
          readVariation(); readWidth(); readOpacity();
          const css = id => win.getComputedStyle(doc.getElementById(id));
          const base = unit === "rem" ? rootSize : rootLine;
          entry.rows.push({ phase, timing, rootSize, rootLine, progress,
            targetMargins: [variationTarget, widthTarget, opacityTarget].map(target => win.getComputedStyle(target).marginLeft),
            variationRaw, variationValue: number(variationRaw), widthRaw, widthValue: parseFloat(widthRaw),
            opacityRaw, opacityRatioValue: Number(opacityRaw),
            expectedCurrent: (1 + 2 * progress) * base,
            expectedOriginal: (1 + 2 * progress) * (unit === "rem" ? 23 : 37),
            staticVariationRaw: css("static-variation").fontVariationSettings,
            staticVariationValue: number(css("static-variation").fontVariationSettings),
            staticWidthValue: parseFloat(css("static-width").width),
            staticOpacityRatioValue: Number(css("static-opacity").opacity),
            rootReference: doc.getElementById("root-reference").getBoundingClientRect().width / 100,
            absoluteVariationValue: number(css("absolute-variation").fontVariationSettings),
            literalVariationValue: number(css("literal-variation").fontVariationSettings),
            literalWidthValue: parseFloat(css("literal-width").width),
            opacity: Number(css("nonfont").opacity),
            rootFontSize: win.getComputedStyle(root).fontSize, rootLineHeight: win.getComputedStyle(root).lineHeight,
            parentFontSize: win.getComputedStyle(parent).fontSize,
            childFontSize: win.getComputedStyle(variationTarget).fontSize,
            variationAnimation: animationInfo(variation), widthAnimation: animationInfo(width), opacityAnimation: animationInfo(opacity),
            literalVariationAnimation: animationInfo(literalVariation), literalWidthAnimation: animationInfo(literalWidth),
          });
        };
        const sample = async (phase, rootSize, rootLine, progress) => {
          take(phase, "first", rootSize, rootLine, progress);
          await settle(win);
          take(phase, "settled", rootSize, rootLine, progress);
        };
        await sample("initial", 23, 37, 0.5);
        root.style.fontSize = "31px"; root.style.lineHeight = "47px";
        await sample("root-change", 31, 47, 0.5);
        for (const animation of anims) animation.cancel();
        frame.remove();
      }
    }
  } catch (error) {
    result.errors.push({ name: error.name, message: error.message, stack: error.stack });
  } finally {
    for (const animation of allAnimations) animation.cancel();
    for (const frame of owned) frame.remove();
    result.cleanup = owned.every(frame => !frame.isConnected);
  }
  return result;
})()

))