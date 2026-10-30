"use strict";

const fs = require("fs");
const vm = require("vm");
let completion;
let captured;
let destination;
const context = {
  URLSearchParams,
  location: {
    pathname: "/test.html",
    search: "?run=check&nonce=token",
    assign: value => { destination = value; },
  },
  navigator: { userAgent: "Firefox/158.0" },
  CSS: { supports: () => false },
  add_completion_callback: callback => { completion = callback; },
  fetch: async (url, options) => {
    captured = { url, options };
    return { ok: true, json: async () => ({ next: "/next" }) };
  },
};
vm.runInNewContext(fs.readFileSync(process.argv[2], "utf8"), context);
if (captured !== undefined) {
  throw new Error("Transport occurred before completion");
}
completion([{ name: "wrong-value", status: 1, message: "0.75 is not 0.375", stack: null }], { status: 0 })
  .then(() => {
    const body = JSON.parse(captured.options.body);
    if (captured.url !== "/report/token" || body.tests[0].status !== 1 ||
        body.tests[0].message !== "0.75 is not 0.375" || body.supports.typed_duration !== false ||
        destination !== "/next") {
      throw new Error("Reporting changed the observation");
    }
    console.log("Bridge completion-only transport and failure preservation passed");
  });
