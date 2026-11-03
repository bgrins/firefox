async () => JSON.stringify(await (async () => {
  const cases = [{"unit":"rem","target":"child-existing-font","history":"em-cancel","barrier":"root-read"}];
  const result = {schema: "root-self-animation-order-v1", userAgent: navigator.userAgent,
    cases: [], errors: [], cleanup: false};
  const frames = [], animations = [];
  const close = (a, b) => Number.isFinite(a) && Math.abs(a - b) < 0.06;
  const px = value => Number.parseFloat(value);
  const settle = async win => {
    await win.document.fonts.ready;
    await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
  };
  const animate = (target, property, from, to, pseudo) => {
    const animation = target.animate([{[property]: from}, {[property]: to}],
      {duration: 1000, fill: "both", pseudoElement: pseudo});
    animations.push(animation);
    animation.pause(); animation.currentTime = 500;
    return animation;
  };
  const frameFor = async () => {
    const frame = document.createElement("iframe");
    frame.title = "Root font animation order diagnostic";
    frames.push(frame);
    const loaded = new Promise(resolve => frame.onload = resolve);
    frame.srcdoc = `<!doctype html><meta charset="utf-8"><title>Root font order</title>
      <style>html,body{margin:0;writing-mode:horizontal-tb}
      .child{font-size:11px;line-height:17px}
      html::before{content:"root";display:block;font-size:7px;line-height:9px}
      #rem,#rlh{position:absolute;height:0}#rem{width:100rem}#rlh{width:100rlh}</style>
      <body><div class="child" id="existing"></div><div id="rem"></div><div id="rlh"></div>`;
    document.body.append(frame); await loaded;
    const win = frame.contentWindow, doc = frame.contentDocument, root = doc.documentElement;
    await settle(win);
    const state = () => {
      const style = win.getComputedStyle(root);
      return {fontSize: px(style.fontSize), lineHeight: Number.isFinite(px(style.lineHeight)) ? px(style.lineHeight) : null,
        rem: px(win.getComputedStyle(doc.getElementById("rem")).width)/100,
        rlh: px(win.getComputedStyle(doc.getElementById("rlh")).width)/100};
    };
    const initial = state();
    root.style.fontSize = "23px"; root.style.lineHeight = "37px";
    const configured = state();
    return {frame,win,doc,root,initial,configured,state};
  };
  try {
    if (!document.body) throw new Error("Loaded HTML page with body required");
    for (const scenario of cases) {
      let ctx, effect;
      const row = {...scenario, controls: {}, samples: [], error: null};
      result.cases.push(row);
      try {
        ctx = await frameFor();
        row.initial = ctx.initial; row.configured = ctx.configured;
        row.controls.initialMetrics = ctx.initial.rem > 0 && ctx.initial.rlh > 0;
        row.controls.configuredRoot = close(ctx.configured.fontSize,23) && close(ctx.configured.lineHeight,37);
        row.controls.configuredMetricProxies = close(ctx.configured.rem,23) && close(ctx.configured.rlh,37);
        const property = scenario.target === "root-line" ? "lineHeight" : "fontSize";
        let target = scenario.target === "child-existing-font" ? ctx.doc.getElementById("existing") : ctx.root;
        const pseudo = scenario.target === "root-pseudo-font" ? "::before" : null;
        const initialBase = scenario.unit === "rem" ? ctx.initial.rem : ctx.initial.rlh;
        const ordinaryBase = scenario.unit === "rem" ? 23 : 37;
        row.normativeExpected = scenario.target === "root-font" ? 2*initialBase :
          scenario.target === "root-line" ? 2*(scenario.unit === "rem" ? 23 : ctx.initial.rlh) : 2*ordinaryBase;
        row.disturbance = null;
        if (scenario.history === "em-cancel") {
          const calibration = animate(ctx.root,"fontSize","1em","3em",null);
          const value = px(ctx.win.getComputedStyle(ctx.root).fontSize);
          row.disturbance = {kind: "em-cancel", value, expected: 2*ctx.initial.rem};
          row.controls.emCalibration = close(value,2*ctx.initial.rem);
          calibration.cancel();
        } else if (scenario.history === "comparator-reset") {
          const before = ctx.root.style[property];
          ctx.root.style[property] = `2${scenario.unit}`;
          const value = px(ctx.win.getComputedStyle(ctx.root)[property]);
          row.disturbance = {kind: "comparator-reset", property, value, expected: row.normativeExpected};
          row.controls.ordinaryComparator = close(value,row.normativeExpected);
          ctx.root.style[property] = before;
        }
        row.preconditionRead = null;
        if (scenario.barrier === "root-read") {
          const style = ctx.win.getComputedStyle(ctx.root);
          row.preconditionRead = {fontSize: px(style.fontSize), lineHeight: px(style.lineHeight)};
          row.controls.restoredRootRead = close(row.preconditionRead.fontSize,23) && close(row.preconditionRead.lineHeight,37);
        }
        if (scenario.target === "child-new-font") {
          target = ctx.doc.createElement("div"); target.className = "child";
          ctx.doc.body.append(target);
        }
        effect = animate(target,property,`1${scenario.unit}`,`3${scenario.unit}`,pseudo);
        const take = timing => {
          const raw = ctx.win.getComputedStyle(target,pseudo)[property];
          row.samples.push({timing,raw,value:px(raw)});
        };
        take("first");
        await effect.ready; await settle(ctx.win);
        take("settled");
        row.animation = {currentTime:effect.currentTime,playState:effect.playState,
          progress:effect.effect.getComputedTiming().progress,targetIsRoot:target===ctx.root,pseudoElement:effect.effect.pseudoElement};
        row.controls.pausedMidpoint = effect.currentTime===500 && effect.playState==="paused" && Math.abs(row.animation.progress-0.5)<1e-9;
        row.postStateAfterBothSamples = ctx.state();
      } catch (error) {
        row.error = {name:error.name,message:error.message,stack:error.stack};
      } finally {
        if (effect) effect.cancel();
        if (ctx) ctx.frame.remove();
      }
    }
  } catch (error) {result.errors.push({name:error.name,message:error.message,stack:error.stack});}
  finally {
    for (const animation of animations) animation.cancel();
    for (const frame of frames) frame.remove();
    result.cleanup = frames.every(frame => !frame.isConnected);
  }
  return result;
})())
