() => { document.body.innerHTML = "<pre id=results></pre>";

const cases = [
  {
    "id": "unequal-direct-images",
    "syntax": "<image>",
    "initialValue": "light-dark(linear-gradient(red, red), linear-gradient(blue, blue))",
    "property": "background-image"
  },
  {
    "id": "equivalent-direct-images",
    "syntax": "<image>",
    "initialValue": "light-dark(linear-gradient(red, red), linear-gradient(rgb(255 0 0), rgb(255 0 0)))",
    "property": "background-image"
  },
  {
    "id": "equivalent-color-branches",
    "syntax": "<color>",
    "initialValue": "light-dark(red, rgb(255 0 0))",
    "property": "color"
  },
  {
    "id": "zero-container-product",
    "syntax": "<length>",
    "initialValue": "calc(0 * 1cqw)",
    "property": "width"
  },
  {
    "id": "cancelled-container-terms",
    "syntax": "<length>",
    "initialValue": "calc(1cqw - 1cqw)",
    "property": "width"
  }
];
const observations = cases.map((item, index) => {
  const result = {...item, supported: CSS.supports(item.property, item.initialValue)};
  try {
    CSS.registerProperty({name: `--initial-observation-${index}`, syntax: item.syntax,
                          inherits: false, initialValue: item.initialValue});
    result.registration = "accepted";
  } catch (error) {
    result.registration = "rejected";
    result.exception = error.name;
    result.message = error.message;
  }
  return result;
});
window.initialIndependenceObservations = observations;
document.getElementById("results").textContent = JSON.stringify(observations, null, 2);

return {userAgent:navigator.userAgent, observations:window.initialIndependenceObservations}; }
