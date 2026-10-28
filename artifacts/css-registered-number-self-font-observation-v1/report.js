document.getElementById("probe").addEventListener("load", async event => {
  if (!event.target.contentWindow.location.pathname.endsWith("/observation-only.html")) return;
  let payload;
  try {
    const frame = event.target.contentWindow;
    const observation = frame.observations;
    if (!observation || observation.rows.length !== 4) {
      throw new Error("Missing four-row observation");
    }
    const calibrations = [];
    for (const [id, value, expected] of [["literal-number", "5", "5"], ["true-var-self-cycle", "var(--n,7)", "3"]]) {
      const parent = frame.document.createElement("div");
      parent.style.cssText = "font-size:19px;line-height:23px";
      const target = frame.document.createElement("div");
      target.style.cssText = `--n:${value};font-size:calc(var(--n)*1px);width:calc(var(--n)*1px)`;
      parent.append(target);
      frame.document.body.append(parent);
      const computed = frame.getComputedStyle(target);
      calibrations.push({id, expected, number:computed.getPropertyValue("--n").trim(), fontSize:computed.fontSize, width:computed.width});
      parent.remove();
    }
    payload = {observation, calibrations};
  } catch (error) {
    payload = {error:String(error)};
  }
  await fetch("result", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
});
document.getElementById("probe").src = "observation-only.html";
