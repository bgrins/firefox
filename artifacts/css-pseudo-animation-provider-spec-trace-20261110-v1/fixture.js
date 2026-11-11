
const output = document.querySelector("#output");
const fixtures = document.querySelector("#fixtures");
const button = document.querySelector("#run");
const frame = () => new Promise(resolve => requestAnimationFrame(resolve));

function observe(target, pseudo, effects, phase) {
  const style = getComputedStyle(target, pseudo);
  const values = {
    font: style.fontSize,
    margin: style.marginLeft,
    content: style.content,
    originFont: getComputedStyle(target).fontSize,
  };
  return {
    phase,
    ...values,
    effects: effects.map(animation => ({
      type: animation.constructor.name,
      name: animation.animationName ?? null,
      targetMatches: animation.effect.target === target,
      pseudo: animation.effect.pseudoElement,
      time: animation.currentTime,
      progress: animation.effect.getComputedTiming().progress,
      pending: animation.pending,
      state: animation.playState,
    })),
  };
}

async function compare(scenario, kind, context, reverse, index) {
  const target = document.createElement("div");
  target.id = `provider-${index}`;
  target.className = `target ${context}`;
  target.style.fontSize = context === "ordinary" ? "20px" : "12px";
  target.style.marginLeft = "2em";
  fixtures.append(target);
  const pseudo = context === "ordinary" ? null : "::before";
  const record = { scenario, kind, context, reverse, observations: [] };
  let effects = [];
  let sheet;
  try {
    record.observations.push(observe(target, pseudo, effects, "baseline"));
    const definitions = [
      { name: "provider-font", frames: { fontSize: ["20px", "40px"] }, composite: "replace" },
      { name: `provider-${scenario.toLowerCase()}`, frames: { marginLeft: scenario === "A" ? ["1em", "2em"] : ["10px", "10px"] }, composite: scenario === "A" ? "replace" : "add" },
    ];
    if (reverse) {
      definitions.reverse();
    }
    if (kind === "CSS") {
      sheet = document.createElement("style");
      sheet.textContent = `#${target.id}${pseudo ?? ""} {
        animation-name: ${definitions.map(item => item.name).join(",")};
        animation-duration: 100s;
        animation-timing-function: linear;
        animation-play-state: paused;
        animation-fill-mode: both;
        animation-composition: ${definitions.map(item => item.composite).join(",")};
      }`;
      document.head.append(sheet);
      effects = target.getAnimations().filter(animation => animation.effect.pseudoElement === pseudo);
    } else {
      effects = definitions.map(item => {
        const animation = target.animate(item.frames, {
          duration: 100000,
          easing: "linear",
          fill: "both",
          composite: item.composite,
          pseudoElement: pseudo,
        });
        animation.pause();
        return animation;
      });
    }
    await Promise.all(effects.map(animation => animation.ready));
    for (const animation of effects) {
      animation.currentTime = 50000;
    }
    record.observations.push(observe(target, pseudo, effects, "ready-seek-sync"));
    target.style.color = "rgb(1, 2, 3)";
    record.observations.push(observe(target, pseudo, effects, "after-color-invalidation"));
    await frame();
    record.observations.push(observe(target, pseudo, effects, "next-frame"));
    return record;
  } finally {
    for (const animation of effects) {
      animation.cancel();
    }
    sheet?.remove();
    target.remove();
  }
}

button.addEventListener("click", async () => {
  button.disabled = true;
  output.textContent = "";
  let index = 0;
  try {
    for (const scenario of ["A", "B"]) {
      for (const kind of ["CSS", "WAAPI"]) {
        for (const context of ["ordinary", "generated", "absent"]) {
          for (const reverse of [false, true]) {
            const record = await compare(scenario, kind, context, reverse, index++);
            output.textContent += JSON.stringify(record) + "\n";
          }
        }
      }
    }
  } catch (error) {
    output.textContent += JSON.stringify({ error: String(error), stack: error.stack }) + "\n";
  } finally {
    button.disabled = false;
  }
});
