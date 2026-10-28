const cases = [{"id":"literal/fixed-font","mode":"literal","consumption":"fixed-font","name":"--zoom-n-0","raw":"--zoom-raw-0","declarations":"--zoom-n-0:5px"},{"id":"literal/self-font","mode":"literal","consumption":"self-font","name":"--zoom-n-1","raw":"--zoom-raw-1","declarations":"--zoom-n-1:5px"},{"id":"ready-unused-em/fixed-font","mode":"ready-unused-em","consumption":"fixed-font","name":"--zoom-n-2","raw":"--zoom-raw-2","declarations":"--zoom-raw-2:5px;--zoom-n-2:var(--zoom-raw-2,1em)"},{"id":"ready-unused-em/self-font","mode":"ready-unused-em","consumption":"self-font","name":"--zoom-n-3","raw":"--zoom-raw-3","declarations":"--zoom-raw-3:5px;--zoom-n-3:var(--zoom-raw-3,1em)"},{"id":"selected-invalid-em/fixed-font","mode":"selected-invalid-em","consumption":"fixed-font","name":"--zoom-n-4","raw":"--zoom-raw-4","declarations":"--zoom-n-4:var(--zoom-missing-4,1em red)"},{"id":"selected-invalid-em/self-font","mode":"selected-invalid-em","consumption":"self-font","name":"--zoom-n-5","raw":"--zoom-raw-5","declarations":"--zoom-n-5:var(--zoom-missing-5,1em red)"},{"id":"wrong-ready-unused-em/fixed-font","mode":"wrong-ready-unused-em","consumption":"fixed-font","name":"--zoom-n-6","raw":"--zoom-raw-6","declarations":"--zoom-raw-6:red;--zoom-n-6:var(--zoom-raw-6,1em)"},{"id":"wrong-ready-unused-em/self-font","mode":"wrong-ready-unused-em","consumption":"self-font","name":"--zoom-n-7","raw":"--zoom-raw-7","declarations":"--zoom-raw-7:red;--zoom-n-7:var(--zoom-raw-7,1em)"},{"id":"direct-invalid/fixed-font","mode":"direct-invalid","consumption":"fixed-font","name":"--zoom-n-8","raw":"--zoom-raw-8","declarations":"--zoom-n-8:1em red"},{"id":"direct-invalid/self-font","mode":"direct-invalid","consumption":"self-font","name":"--zoom-n-9","raw":"--zoom-raw-9","declarations":"--zoom-n-9:1em red"},{"id":"initial/fixed-font","mode":"initial","consumption":"fixed-font","name":"--zoom-n-10","raw":"--zoom-raw-10","declarations":"--zoom-raw-10:initial;--zoom-n-10:var(--zoom-raw-10,initial)"},{"id":"initial/self-font","mode":"initial","consumption":"self-font","name":"--zoom-n-11","raw":"--zoom-raw-11","declarations":"--zoom-raw-11:initial;--zoom-n-11:var(--zoom-raw-11,initial)"},{"id":"inherit/fixed-font","mode":"inherit","consumption":"fixed-font","name":"--zoom-n-12","raw":"--zoom-raw-12","declarations":"--zoom-raw-12:inherit;--zoom-n-12:inherit"},{"id":"inherit/self-font","mode":"inherit","consumption":"self-font","name":"--zoom-n-13","raw":"--zoom-raw-13","declarations":"--zoom-raw-13:inherit;--zoom-n-13:inherit"},{"id":"unset/fixed-font","mode":"unset","consumption":"fixed-font","name":"--zoom-n-14","raw":"--zoom-raw-14","declarations":"--zoom-raw-14:unset;--zoom-n-14:var(--zoom-raw-14,unset)"},{"id":"unset/self-font","mode":"unset","consumption":"self-font","name":"--zoom-n-15","raw":"--zoom-raw-15","declarations":"--zoom-raw-15:unset;--zoom-n-15:var(--zoom-raw-15,unset)"}];
async function run() {
  let payload;
  try {
    const rows = [];
    for (const item of cases) {
      const registrationErrors = [];
      try { CSS.registerProperty({name:item.name, syntax:"<length>", inherits:false, initialValue:"10px"}); }
      catch (error) { registrationErrors.push(String(error)); }
      const parent = document.createElement("div");
      parent.style.cssText = "font-size:19px;line-height:23px;width:200px;" + item.name + ":20px";
      const target = document.createElement("div");
      target.style.cssText = item.declarations + ";box-sizing:content-box;border:0;padding:0;height:10px;width:var(" + item.name + ");font-size:" + (item.consumption === "fixed-font" ? "20px" : "var(" + item.name + ")");
      parent.append(target); document.body.append(parent);
      const snapshots = [];
      for (let step = 0; step < 2; ++step) {
        target.style.zoom = String([1, 2][step]);
        const parentFontSize = getComputedStyle(parent).fontSize;
        const computed = getComputedStyle(target);
        const actual = {value:computed.getPropertyValue(item.name).trim(), raw:computed.getPropertyValue(item.raw).trim(), fontSize:computed.fontSize, lineHeight:computed.lineHeight, width:computed.width, zoom:computed.zoom};
        const rect = target.getBoundingClientRect();
        actual.rectWidth = String(rect.width); actual.rectHeight = String(rect.height);
        snapshots.push({step, parentCSS:parent.style.cssText, specifiedCSS:target.style.cssText, parentFontSize, actual});
      }
      rows.push({id:item.id, registrationErrors, snapshots}); parent.remove();
    }
    payload = {observation:{userAgent:navigator.userAgent, queryOrder:["parentFontSize","value","raw","fontSize","lineHeight","width","zoom","rectWidth","rectHeight"], rows}};
    document.getElementById("output").textContent = JSON.stringify(payload, null, 2);
  } catch (error) { payload = {error:String(error)}; }
  await fetch("result", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
}
run();
