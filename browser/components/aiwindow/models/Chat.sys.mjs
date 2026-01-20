/**
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

import { ToolRoleOpts } from "moz-src:///browser/components/aiwindow/ui/modules/ChatMessage.sys.mjs";
import {
  MODEL_FEATURES,
  openAIEngine,
} from "moz-src:///browser/components/aiwindow/models/Utils.sys.mjs";
import {
  toolsConfig,
  getOpenTabs,
  searchBrowsingHistory,
  GetPageContent,
} from "moz-src:///browser/components/aiwindow/models/Tools.sys.mjs";

const lazy = {};
ChromeUtils.defineESModuleGetters(lazy, {
  MCPServerManager:
    "moz-src:///browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs",
  MCPToolRegistry:
    "moz-src:///browser/components/aiwindow/services/mcp/MCPToolRegistry.sys.mjs",
});

/**
 * Chat
 */
export const Chat = {};

XPCOMUtils.defineLazyPreferenceGetter(
  Chat,
  "modelId",
  "browser.aiwindow.model",
  "qwen3-235b-a22b-instruct-2507-maas"
);

Object.assign(Chat, {
  toolMap: {
    get_open_tabs: getOpenTabs,
    search_browsing_history: searchBrowsingHistory,
    get_page_content: GetPageContent.getPageContent.bind(GetPageContent),
  },

  // MCP infrastructure (lazy-initialized)
  _mcpServerManager: null,
  _mcpToolRegistry: null,
  _mcpInitialized: false,

  /**
   * Initialize MCP infrastructure if not already initialized.
   * This is called lazily on first use.
   *
   * @returns {Promise<void>}
   */
  async _initializeMCP() {
    if (this._mcpInitialized) {
      return;
    }

    try {
      console.log("[Chat] Initializing MCP infrastructure...");

      // Create server manager and tool registry
      this._mcpServerManager = new lazy.MCPServerManager();
      this._mcpToolRegistry = new lazy.MCPToolRegistry(this._mcpServerManager);

      // Note: MCP servers are registered via prefs or programmatically
      // For now, no servers are auto-started. They can be registered
      // separately when needed.

      this._mcpInitialized = true;
      console.log("[Chat] MCP infrastructure initialized");
    } catch (error) {
      console.error("[Chat] Failed to initialize MCP:", error);
      // Don't throw - fall back to built-in tools only
    }
  },

  /**
   * Get all available tools (built-in + MCP).
   *
   * @returns {Promise<Array>} Tool configuration array
   */
  async _getAllToolsConfig() {
    await this._initializeMCP();

    // Start with built-in tools
    const allTools = [...toolsConfig];

    // Add MCP tools if available
    if (this._mcpToolRegistry) {
      try {
        const mcpTools = this._mcpToolRegistry.listAllTools();

        // Convert MCP tool format to OpenAI tool format
        for (const tool of mcpTools) {
          allTools.push({
            type: "function",
            function: {
              name: tool.name,
              description: tool.description || "",
              parameters: tool.inputSchema || { type: "object", properties: {} },
            },
          });
        }

        if (mcpTools.length > 0) {
          console.log(`[Chat] Added ${mcpTools.length} MCP tools to config`);
        }
      } catch (error) {
        console.error("[Chat] Failed to get MCP tools:", error);
      }
    }

    return allTools;
  },

  /**
   * Stream assistant output with tool-call support.
   * Yields assistant text chunks as they arrive. If the model issues tool calls,
   * we execute them locally, append results to the conversation, and continue
   * streaming the model's follow-up answer. Repeats until no more tool calls.
   *
   * @param {ChatConversation} conversation
   * @param {object} [options] - Optional configuration
   * @param {Array} [options.tools] - Custom tools config. If provided, uses these
   *   instead of the default built-in + MCP tools.
   * @param {object} [options.toolMap] - Custom tool implementation map. If provided,
   *   uses this instead of the default toolMap.
   * @yields {string} Assistant text chunks
   */
  async *fetchWithHistory(conversation, options = {}) {
    // Note FXA token fetching disabled for now - this is still in progress
    // We can flip this switch on when more realiable
    const fxAccountToken = await openAIEngine.getFxAccountToken();

    const toolRoleOpts = new ToolRoleOpts(this.modelId);
    const currentTurn = conversation.currentTurnIndex();
    const engineInstance = await openAIEngine.build(MODEL_FEATURES.CHAT);
    const config = engineInstance.getConfig(engineInstance.feature);
    const inferenceParams = config?.parameters || {};

    // Use custom tools if provided, otherwise get default (built-in + MCP)
    const allToolsConfig = options.tools || (await this._getAllToolsConfig());

    // Use custom toolMap if provided
    const activeToolMap = options.toolMap || this.toolMap;

    // Helper to run the model once (streaming) on current convo
    const streamModelResponse = () =>
      engineInstance.runWithGenerator({
        streamOptions: { enabled: true },
        fxAccountToken,
        tool_choice: "auto",
        tools: allToolsConfig,
        args: conversation.getMessagesInOpenAiFormat(),
        ...inferenceParams,
      });

    // Keep calling until the model finishes without requesting tools
    while (true) {
      let pendingToolCalls = null;

      // 1) First pass: stream tokens; capture any toolCalls
      for await (const chunk of streamModelResponse()) {
        // Stream assistant text to the UI
        if (chunk?.text) {
          yield chunk.text;
        }

        // Capture tool calls (do not echo raw tool plumbing to the user)
        if (chunk?.toolCalls?.length) {
          pendingToolCalls = chunk.toolCalls;
        }
      }

      // 2) Watch for tool calls; if none, we are done
      if (!pendingToolCalls || pendingToolCalls.length === 0) {
        return;
      }

      // 3) Build the assistant tool_calls message exactly as expected by the API
      //
      // @todo Bug 2006159 - Implement parallel tool calling
      // Temporarily only include the first tool call due to quality issue
      // with subsequent tool call responses, will include all later once above
      // ticket is resolved.
      const tool_calls = pendingToolCalls.slice(0, 1).map(toolCall => ({
        id: toolCall.id,
        type: "function",
        function: {
          name: toolCall.function.name,
          arguments: toolCall.function.arguments || "{}",
        },
      }));
      conversation.addAssistantMessage("function", { tool_calls });

      // Yield tool call information for UI display
      for (const toolCall of pendingToolCalls.slice(0, 1)) {
        yield {
          type: "tool_call",
          name: toolCall.function.name,
          arguments: toolCall.function.arguments,
        };
      }

      // 4) Execute each tool locally and create a tool message with the result
      // TODO: Temporarily only execute the first tool call, will run all later
      for (const toolCall of pendingToolCalls) {
        const { id, function: functionSpec } = toolCall;
        const name = functionSpec?.name || "";
        let toolParams = {};

        try {
          toolParams = functionSpec?.arguments
            ? JSON.parse(functionSpec.arguments)
            : {};
        } catch {
          const content = {
            tool_call_id: id,
            body: { error: "Invalid JSON arguments" },
          };
          conversation.addToolCallMessage(content, currentTurn, toolRoleOpts);
          continue;
        }

        let result;
        try {
          // Check if it's in the active tool map (built-in or custom)
          const toolFunc = activeToolMap[name];

          if (typeof toolFunc === "function") {
            // Execute tool from toolMap
            result = await toolFunc(toolParams);
          } else if (this._mcpToolRegistry) {
            // Try MCP tool
            console.log(`[Chat] Calling MCP tool: ${name}`);
            const mcpResult = await this._mcpToolRegistry.callTool(
              name,
              toolParams
            );

            // MCP tools return { content: [{type: "text", text: "..."}] }
            // Extract the text for the conversation
            if (mcpResult?.content?.[0]?.text) {
              result = mcpResult.content[0].text;
            } else {
              result = mcpResult;
            }
          } else {
            throw new Error(`No such tool: ${name}`);
          }

          // Create special tool call log message to show in the UI log panel
          const content = { tool_call_id: id, body: result, name };
          conversation.addToolCallMessage(content, currentTurn, toolRoleOpts);

          // Yield tool result for UI display
          yield {
            type: "tool_result",
            name,
            result,
          };
        } catch (e) {
          console.error(`[Chat] Tool execution error for ${name}:`, e);
          result = { error: `Tool execution failed: ${String(e)}` };
          const content = { tool_call_id: id, body: result };
          conversation.addToolCallMessage(content, currentTurn, toolRoleOpts);

          // Yield error result for UI display
          yield {
            type: "tool_result",
            name,
            result,
            error: true,
          };
        }

        // Bug 	2006159 - Implement parallel tool calling, remove after implemented
        break;
      }
    }
  },
});
