/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

add_task(async function test_pty_and_interactive_stdin() {
  if (!(await vmDepsPresent())) {
    todo(false, "harness VM deps not present; run setup-deps.sh");
    return;
  }
  for (
    let i = 0;
    !["stopped", "running"].includes(HarnessVM.state) && i < 60;
    i++
  ) {
    // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await startVM();
  const agent = HarnessVM.session().agent;

  // Plain jobs have no controlling terminal; tty jobs do.
  const ttyCheck = "if [ -t 0 ]; then echo is-tty; else echo no-tty; fi";
  const piped = await agent.exec(ttyCheck);
  ok(piped.stdout.includes("no-tty"), "pipe job is not a tty");
  const tty = await agent.exec(ttyCheck, { tty: true });
  ok(tty.stdout.includes("is-tty"), "tty job sees a controlling terminal");

  // Interactive stdin: write to a running cat, then EOF cleanly.
  let streamed = "";
  const { requestId, result } = agent.execStart("cat", {
    interactive: true,
    onOutput: (_stream, text) => {
      streamed += text;
    },
  });
  await agent.input(requestId, "hello interactive\n");
  await TestUtils.waitForCondition(
    () => streamed.includes("hello interactive"),
    "cat echoed the interactive write"
  );
  await agent.input(requestId, "second line\n");
  await TestUtils.waitForCondition(
    () => streamed.includes("second line"),
    "second write arrived"
  );
  await agent.inputEof(requestId);
  const done = await result;
  is(done.exitCode, 0, "interactive job exits cleanly on EOF");
  ok(done.stdout.includes("hello interactive"), "output accumulated");

  await stopVM();
});
