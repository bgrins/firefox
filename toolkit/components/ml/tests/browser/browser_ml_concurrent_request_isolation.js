/* Any copyright is dedicated to the Public Domain.
   https://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

/**
 * Test that concurrent ML requests are properly isolated.
 *
 * This test verifies that when one request fails (triggering unhandledrejection
 * in the worker), it doesn't corrupt the response routing for concurrent successful
 * requests. This was a bug where re-throwing in the unhandledrejection handler
 * caused PromiseWorker to reject ALL pending promises.
 */

add_task(async function test_concurrent_request_isolation() {
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

  try {
    // Track whether we got the expected responses
    let failedRequestError = null;
    let successfulRequestResult = null;
    let requestCount = 0;

    // Set up custom mock server that returns error for first request, success for second
    const server = new HttpServer();
    server.registerPathHandler("/v1/chat/completions", (request, response) => {
      info("Received request to /v1/chat/completions");

      let bodyText = "";
      if (request.method === "POST") {
        const stream = request.bodyInputStream;
        const available = stream.available();
        bodyText = NetUtil.readInputStreamToString(stream, available, {
          charset: "UTF-8",
        });
      }

      const body = JSON.parse(bodyText || "{}");
      requestCount++;

      info(`Request ${requestCount}: has messages=${!!body.messages}, messages length=${body.messages?.length || 0}`);

      // First request (failing one) - should have no messages field or empty messages
      if (!body.messages || body.messages.length === 0) {
        info("Returning 400 error for request with no/empty messages");
        response.setStatusLine(request.httpVersion, 400, "Bad Request");
        response.setHeader("Content-Type", "application/json", false);
        response.write(JSON.stringify({
          error: {
            message: "[] is too short - 'messages'",
            type: "invalid_request_error",
          }
        }));
      } else {
        // Successful request
        info("Returning success response for valid request");
        response.setStatusLine(request.httpVersion, 200, "OK");
        response.setHeader("Content-Type", "application/json", false);
        response.write(JSON.stringify({
          id: "test-completion",
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model: "test-model",
          choices: [{
            index: 0,
            message: {
              role: "assistant",
              content: "This is a successful response"
            },
            finish_reason: "stop"
          }]
        }));
      }
    });

    server.start(-1);
    const port = server.identity.primaryPort;

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

      info("Engine created, making two concurrent requests");

      // Make two concurrent requests:
      // 1. One with invalid request (will fail)
      // 2. One with valid request (should succeed)

      const failingRequest = engineInstance.run({
        messages: [{ role: "user", content: "test" }], // Wrong field name - should be 'args'
        // Note: OpenAIPipeline expects 'args', not 'messages'
      }).catch(error => {
        failedRequestError = error;
        info("Failing request caught error as expected: " + error.message);
        return null;
      });

      const successfulRequest = engineInstance.run({
        args: [{ role: "user", content: "test" }], // Correct field name
      }).then(result => {
        successfulRequestResult = result;
        info("Successful request completed");
        return result;
      }).catch(error => {
        info("ERROR: Successful request failed unexpectedly: " + error.message);
        throw error;
      });

      // Wait for both to complete
      await Promise.all([failingRequest, successfulRequest]);

      // Verify the failing request failed
      Assert.ok(
        failedRequestError !== null,
        "The intentionally failing request should have failed"
      );
      Assert.ok(
        failedRequestError.message.includes("is too short"),
        "Failed request should have the expected error message"
      );

      // Verify the successful request succeeded despite the other failure
      Assert.ok(
        successfulRequestResult !== null,
        "The successful request should have completed (not corrupted by the failed request)"
      );
      Assert.ok(
        successfulRequestResult.choices?.[0]?.message?.content,
        "Successful request should have valid response content"
      );
      Assert.equal(
        successfulRequestResult.choices[0].message.content,
        "This is a successful response",
        "Successful request should have the correct response text"
      );

    } finally {
      await new Promise(resolve => server.stop(resolve));
    }
  } finally {
    await EngineProcess.destroyMLEngine();
    await cleanup();
  }

  info("Concurrent request isolation test completed successfully");
});
