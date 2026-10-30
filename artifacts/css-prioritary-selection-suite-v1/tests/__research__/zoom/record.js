(() => {
  window.capturePrioritaryZoom = async row => {
    const configResponse = await fetch("/__research__/zoom/CONFIG.json", {cache: "no-store"});
    if (!configResponse.ok) throw new Error("Zoom capture configuration unavailable");
    const config = await configResponse.json();
    const response = await fetch("/__research__/zoom/receive.py", {
      method: "POST", headers: {"Content-Type": "application/json"}, cache: "no-store",
      body: JSON.stringify({version: 1, nonce: config.nonce, role: config.role,
        page: location.pathname, row})
    });
    if (!response.ok || (await response.json()).accepted !== true) {
      throw new Error("Zoom research observation was not retained");
    }
  };
})();
