window.rectangleBenchmarkPromise.then(result => fetch("/result", {method: "POST", body: JSON.stringify(result)}));
