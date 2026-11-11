"use strict";

async function runTransitionRoutingCase(mode) {
  const result = { mode, checks: [], observations: [], error: null };
  const check = (name, condition, actual) => {
    result.checks.push({ name, passed: !!condition, actual });
  };
  const style = document.createElement("style");
  style.textContent = `
    .routing-probe { opacity: 0.2 !important; transition: opacity 1000s linear; }
    .routing-probe.to { opacity: 0.8 !important; }
  `;
  const target = document.createElement("div");
  target.className = "routing-probe";
  document.head.append(style);
  document.body.append(target);
  let transition, animation;
  try {
    const initial = getComputedStyle(target).opacity;
    check(
      "initial important author value",
      Math.abs(Number(initial) - 0.2) < 1e-6,
      initial
    );
    target.classList.add("to");
    const created = target.getAnimations();
    const transitions = created.filter(
      a => a instanceof CSSTransition && a.transitionProperty === "opacity"
    );
    check(
      "one CSS opacity transition generated on target",
      transitions.length === 1,
      transitions.length
    );
    if (transitions.length !== 1) {
      return result;
    }
    transition = transitions[0];
    transition.pause();
    transition.currentTime = 500000;
    check(
      "transition held at half duration",
      transition.currentTime === 500000,
      transition.currentTime
    );
    check(
      "transition paused without pending task",
      transition.playState === "paused" && !transition.pending,
      { playState: transition.playState, pending: transition.pending }
    );
    check(
      "transition effect still targets original element",
      transition.effect.target === target &&
        transition.effect.pseudoElement === null,
      {
        sameTarget: transition.effect.target === target,
        pseudo: transition.effect.pseudoElement,
      }
    );

    function observe(phase) {
      const values = [
        getComputedStyle(target).opacity,
        getComputedStyle(target).opacity,
        getComputedStyle(target).opacity,
      ];
      const present = target.getAnimations();
      const row = {
        phase,
        values,
        sameTransition: present.includes(transition),
        transitionTargetMatches: transition.effect.target === target,
        transitionProperty: transition.transitionProperty,
        transitionTime: transition.currentTime,
        transitionProgress: transition.effect.getComputedTiming().progress,
        transitionPlayState: transition.playState,
        transitionPending: transition.pending,
        animationPresent: animation ? present.includes(animation) : false,
        animationTargetMatches: animation
          ? animation.effect.target === target
          : null,
        animationTime: animation ? animation.currentTime : null,
        animationProgress: animation
          ? animation.effect.getComputedTiming().progress
          : null,
        animationPlayState: animation ? animation.playState : null,
        animationPending: animation ? animation.pending : null,
        animationRate: animation ? animation.playbackRate : null,
        animationTiming: animation ? animation.effect.getTiming() : null,
      };
      result.observations.push(row);
      check(
        `${phase}: original transition survives flush`,
        row.sameTransition &&
          row.transitionTargetMatches &&
          row.transitionProperty === "opacity",
        row.sameTransition
      );
      check(
        `${phase}: transition remains held at half sample`,
        row.transitionTime === 500000 &&
          row.transitionProgress === 0.5 &&
          row.transitionPlayState === "paused" &&
          !row.transitionPending,
        {
          time: row.transitionTime,
          progress: row.transitionProgress,
          state: row.transitionPlayState,
          pending: row.transitionPending,
        }
      );
      if (animation && (phase === "during" || phase === "two-frames")) {
        check(
          `${phase}: WAAPI effect is registered on same element`,
          row.animationPresent && row.animationTargetMatches,
          {
            registered: row.animationPresent,
            sameTarget: row.animationTargetMatches,
          }
        );
        check(
          `${phase}: WAAPI animation is paused with positive rate`,
          row.animationPlayState === "paused" &&
            !row.animationPending &&
            row.animationRate === 1,
          {
            state: row.animationPlayState,
            pending: row.animationPending,
            rate: row.animationRate,
          }
        );
        check(
          `${phase}: WAAPI timing reaches requested sampling state`,
          row.animationProgress === (mode === "current-no-fill" ? null : 0.5) &&
            row.animationTiming.fill === "none" &&
            row.animationTime === (mode === "current-no-fill" ? 0 : 500),
          {
            time: row.animationTime,
            progress: row.animationProgress,
            timing: row.animationTiming,
          }
        );
      }
      return row;
    }

    observe("before");
    if (mode !== "transition-only") {
      animation = target.animate(
        { opacity: [0.1, 0.3] },
        {
          duration: 1000,
          fill: "none",
          delay: mode === "current-no-fill" ? 1000 : 0,
        }
      );
      animation.pause();
      animation.currentTime = mode === "current-no-fill" ? 0 : 500;
    }
    observe("during");
    await new Promise(requestAnimationFrame);
    await new Promise(requestAnimationFrame);
    observe("two-frames");
    if (animation) {
      animation.cancel();
    }
    observe("after-cancel");
    if (animation) {
      check(
        "cancelled WAAPI effect is absent",
        !target.getAnimations().includes(animation),
        target.getAnimations().length
      );
    }
    result.expectedValues = {
      before: 0.5,
      during: mode === "active-overlap" ? 0.8 : 0.5,
      "two-frames": mode === "active-overlap" ? 0.8 : 0.5,
      "after-cancel": 0.5,
    };
    result.predictionMatches = result.observations.every(row =>
      row.values.every(
        value =>
          Math.abs(Number(value) - result.expectedValues[row.phase]) < 1e-6
      )
    );
    result.setupPassed = result.checks.every(row => row.passed);
    result.interpretation =
      mode === "current-no-fill"
        ? "probe: non-sampling effect should not choose cascade origin; spec-chain inference"
        : "control";
  } catch (error) {
    result.error = {
      name: error.name,
      message: error.message,
      stack: error.stack,
    };
  } finally {
    if (animation) {
      animation.cancel();
    }
    if (transition) {
      transition.cancel();
    }
    target.remove();
    style.remove();
  }
  return result;
}
