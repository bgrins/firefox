document.getElementById("probe").addEventListener("load", async event => {
  if (!event.target.contentWindow.location.pathname.endsWith("/observation-only.html")) return;
  let payload;
  try {
    const observation = event.target.contentWindow.observations;
    if (!observation || !Array.isArray(observation.rows)) throw new Error("Missing breadth observations");
    payload = {observation};
  } catch (error) {
    payload = {error:String(error)};
  }
  await fetch("result", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
});
document.getElementById("probe").src = "observation-only.html";
