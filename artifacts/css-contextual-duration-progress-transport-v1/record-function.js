async function record(kind, trace) {
  const response = await fetch("duration-progress-record.py", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({kind, observation: JSON.parse(trace)})
  });
  assert_true(response.ok, "Private observation record acknowledged");
  const acknowledgement = await response.json();
  assert_equals(acknowledgement.kind, kind, "Recorded observation kind");
  assert_equals(acknowledgement.sampleCount, 4, "Recorded passive samples");
  assert_true(/^[A-Za-z0-9_-]{16,128}$/.test(acknowledgement.run_id), "Owner-bound record identity");
}

