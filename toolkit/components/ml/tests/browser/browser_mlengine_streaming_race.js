/* Any copyright is dedicated to the Public Domain.
   https://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

/**
 * Test for MLEngineParent streaming race condition
 *
 * This test simulates OpenAI-compatible streaming endpoints that send:
 * 1. Multiple SSE chunks with streaming data (each triggers InitProgress)
 * 2. A final chunk with finish_reason (triggers both RunResponse and final InitProgress)
 *
 * The bug: MLEngineParent deletes the request after RunResponse (line 1390),
 * causing the final InitProgress to fail with "Could not resolve response" error.
 */

add_task(async function test_openai_streaming_sequence() {
  const records = [
    {
      featureId: "about-inference",
      taskName: "text-generation",
      modelId: "test-model",
      modelRevision: "main",
      id: crypto.randomUUID(),
    },
  ];
  const { cleanup } = await setup({ records });

  // Track console errors to detect "Could not resolve response" messages
  const consoleErrors = [];
  const originalError = console.error;
  console.error = function (...args) {
    consoleErrors.push(args);
    originalError.apply(console, args);
  };

  try {
    const { server: mockServer, port } = startMockOpenAI({
      echo: "Test response",
    });

    try {
      const engineInstance = await createEngine({
        featureId: "about-inference",
        taskName: "text-generation",
        modelId: "test-model",
        modelRevision: "main",
        apiKey: "test-api-key",
        baseURL: `http://localhost:${port}/v1`,
        backend: "openai",
      });

      info("Engine created, testing streaming inference");

      // Make a streaming inference request
      const chunks = [];
      const generator = engineInstance.runWithGenerator({
        args: [{ role: "user", content: "Hello" }],
        streamOptions: { enabled: true },
      });

      info("Starting to consume generator");
      for await (const chunk of generator) {
        info(`Received chunk: ${JSON.stringify(chunk)}`);
        chunks.push(chunk);
      }

      info(`Received total of ${chunks.length} chunks`);

      // Verify we received some chunks
      Assert.ok(
        chunks.length > 0,
        `Should receive at least one chunk, got ${chunks.length}`
      );

      // Check for "Could not resolve response" errors
      const resolveErrors = consoleErrors.filter(args =>
        args.some(
          arg =>
            typeof arg === "string" &&
            arg.includes("Could not resolve response in the MLEngineParent")
        )
      );

      Assert.equal(
        resolveErrors.length,
        0,
        `Should have no 'Could not resolve response' errors. Found ${resolveErrors.length}: ${JSON.stringify(resolveErrors)}`
      );
    } finally {
      await stopMockOpenAI(mockServer);
    }
  } finally {
    console.error = originalError;
    await EngineProcess.destroyMLEngine();
    await cleanup();
  }

  info("Streaming race condition test completed successfully");
});
