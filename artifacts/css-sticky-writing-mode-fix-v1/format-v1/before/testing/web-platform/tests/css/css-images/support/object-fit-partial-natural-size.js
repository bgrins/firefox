const mutate = document.currentScript.dataset.mutate === "true";
const images = [];
const loaded = [];
for (const dimensions of [
  'width="40"', 'height="40"', 'width="160"', 'height="160"',
  'width="40" height="20"', "",
]) {
  for (const fit of ["none", "scale-down"]) {
    for (const position of [0, 100]) {
      const image = document.createElement("img");
      image.style.objectFit = mutate ? "fill" : fit;
      image.style.objectPosition = `${position}% ${position}%`;
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" ${dimensions}><rect width="100%" height="100%" fill="lime"/></svg>`;
      loaded.push(new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = reject;
      }));
      image.src = `data:image/svg+xml,${encodeURIComponent(svg)}`;
      document.body.append(image);
      images.push({ image, fit });
    }
  }
}
const ready = Promise.all(loaded);
if (mutate) {
  document.documentElement.addEventListener("TestRendered", async () => {
    await ready;
    for (const { image, fit } of images) {
      image.style.objectFit = fit;
    }
    requestAnimationFrame(() => requestAnimationFrame(() => {
      document.documentElement.classList.remove("reftest-wait");
    }));
  }, { once: true });
} else {
  ready.then(() => document.documentElement.classList.remove("reftest-wait"));
}
