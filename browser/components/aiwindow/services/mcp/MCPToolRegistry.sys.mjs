/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Resource limits (fix #15)
const MAX_TOOLS_PER_SERVER = 1000;
const MAX_TOTAL_TOOLS = 10000;

export class MCPToolRegistry {
  constructor(serverManager) {
    this.serverManager = serverManager;
    this.tools = new Map(); // FQN -> tool
    this.serverTools = new Map(); // serverId -> [FQNs]
    this.shortNameIndex = new Map(); // shortName -> [FQNs] (fix #13)
  }

  registerServerTools(serverId, tools) {
    // Fix #19: Validate inputs
    if (!serverId || typeof serverId !== "string") {
      throw new Error("serverId must be a non-empty string");
    }
    if (!Array.isArray(tools)) {
      throw new Error("Tools must be an array");
    }

    // Fix #15: Check resource limits
    if (tools.length > MAX_TOOLS_PER_SERVER) {
      throw new Error(
        `Cannot register ${tools.length} tools (max ${MAX_TOOLS_PER_SERVER} per server)`
      );
    }
    if (this.tools.size + tools.length > MAX_TOTAL_TOOLS) {
      throw new Error(
        `Cannot register tools, would exceed limit of ${MAX_TOTAL_TOOLS} total tools`
      );
    }

    // Fix #18: Clear old tools before registering new ones
    this.unregisterServerTools(serverId);

    const registeredTools = [];

    for (const tool of tools) {
      if (!tool.name) {
        console.warn(`Skipping tool without name from server ${serverId}`);
        continue;
      }

      const fullyQualifiedName = `${serverId}/${tool.name}`;

      if (this.tools.has(fullyQualifiedName)) {
        console.warn(
          `Tool ${fullyQualifiedName} already registered, skipping`
        );
        continue;
      }

      const toolEntry = {
        name: tool.name,
        description: tool.description || "",
        inputSchema: tool.inputSchema || {},
        serverId,
        fullyQualifiedName,
      };

      this.tools.set(fullyQualifiedName, toolEntry);
      registeredTools.push(fullyQualifiedName);

      // Fix #13: Build reverse index for short name lookups
      if (!this.shortNameIndex.has(tool.name)) {
        this.shortNameIndex.set(tool.name, []);
      }
      this.shortNameIndex.get(tool.name).push(fullyQualifiedName);
    }

    if (registeredTools.length > 0) {
      this.serverTools.set(serverId, registeredTools);

      console.log(
        `[MCPToolRegistry] Registered ${registeredTools.length} tools from server ${serverId}`
      );
    }

    return registeredTools;
  }

  unregisterServerTools(serverId) {
    const toolNames = this.serverTools.get(serverId);

    if (!toolNames) {
      return [];
    }

    for (const fqn of toolNames) {
      const tool = this.tools.get(fqn);
      if (tool) {
        // Fix #13: Remove from short name index
        const shortNameList = this.shortNameIndex.get(tool.name);
        if (shortNameList) {
          const index = shortNameList.indexOf(fqn);
          if (index !== -1) {
            shortNameList.splice(index, 1);
          }
          if (shortNameList.length === 0) {
            this.shortNameIndex.delete(tool.name);
          }
        }
      }
      this.tools.delete(fqn);
    }

    this.serverTools.delete(serverId);

    console.log(
      `[MCPToolRegistry] Unregistered ${toolNames.length} tools from server ${serverId}`
    );

    return toolNames;
  }

  async callTool(toolName, args = {}) {
    // Validate input
    if (typeof toolName !== "string" || !toolName) {
      throw new Error("Tool name must be a non-empty string");
    }

    if (!args || typeof args !== "object" || Array.isArray(args)) {
      throw new Error("Tool arguments must be an object");
    }

    let serverId;
    let localToolName;
    let tool;

    if (toolName.includes("/")) {
      const parts = toolName.split("/");
      if (parts.length !== 2 || !parts[0] || !parts[1]) {
        throw new Error(
          `Invalid fully qualified tool name: ${toolName} (expected format: serverId/toolName)`
        );
      }
      [serverId, localToolName] = parts;
      tool = this.tools.get(toolName);
    } else {
      tool = this._findToolByShortName(toolName);

      if (!tool) {
        throw new Error(`Tool not found: ${toolName}`);
      }

      serverId = tool.serverId;
      localToolName = tool.name;
    }

    // Validate against input schema if available
    if (tool && tool.inputSchema) {
      this._validateToolArguments(tool, args);
    }

    const transport = this.serverManager.getTransport(serverId);

    if (!transport) {
      throw new Error(`Server ${serverId} is not running`);
    }

    if (!transport.isConnected()) {
      throw new Error(`Server ${serverId} is not connected`);
    }

    try {
      const result = await transport.request("tools/call", {
        name: localToolName,
        arguments: args,
      });

      // Validate result structure
      if (!result || typeof result !== "object") {
        throw new Error("Tool result must be an object");
      }

      if (!Array.isArray(result.content)) {
        throw new Error("Tool result must have 'content' array");
      }

      return result;
    } catch (error) {
      throw new Error(
        `Tool execution failed (${serverId}/${localToolName}): ${error.message}`
      );
    }
  }

  /**
   * Basic validation of tool arguments against input schema.
   * Checks required fields and basic types.
   *
   * @param {object} tool - Tool definition with inputSchema
   * @param {object} args - Arguments to validate
   * @private
   */
  _validateToolArguments(tool, args) {
    const schema = tool.inputSchema;

    // Check required fields
    if (schema.required && Array.isArray(schema.required)) {
      for (const field of schema.required) {
        if (!(field in args)) {
          throw new Error(
            `Missing required argument '${field}' for tool ${tool.name}`
          );
        }
      }
    }

    // Basic type checking for properties
    if (schema.properties) {
      for (const [key, propSchema] of Object.entries(schema.properties)) {
        if (key in args) {
          const value = args[key];
          const expectedType = propSchema.type;

          // Basic type validation
          if (expectedType === "string" && typeof value !== "string") {
            throw new Error(
              `Argument '${key}' must be a string for tool ${tool.name}`
            );
          } else if (expectedType === "number" && typeof value !== "number") {
            throw new Error(
              `Argument '${key}' must be a number for tool ${tool.name}`
            );
          } else if (expectedType === "boolean" && typeof value !== "boolean") {
            throw new Error(
              `Argument '${key}' must be a boolean for tool ${tool.name}`
            );
          } else if (
            expectedType === "object" &&
            (typeof value !== "object" || value === null)
          ) {
            // Fix #12: null handling
            throw new Error(
              `Argument '${key}' must be an object for tool ${tool.name}`
            );
          } else if (expectedType === "array" && !Array.isArray(value)) {
            throw new Error(
              `Argument '${key}' must be an array for tool ${tool.name}`
            );
          }
        }
      }
    }
  }

  getTool(toolName) {
    // Fix #14: Consistent error handling - return undefined
    if (!toolName) {
      return undefined;
    }

    if (toolName.includes("/")) {
      return this.tools.get(toolName);
    }

    return this._findToolByShortName(toolName);
  }

  getToolSchema(toolName) {
    // Fix #14: Consistent error handling - return undefined
    const tool = this.getTool(toolName);
    return tool ? tool.inputSchema : undefined;
  }

  listAllTools() {
    return Array.from(this.tools.values());
  }

  listServerTools(serverId) {
    const toolNames = this.serverTools.get(serverId);

    if (!toolNames) {
      return [];
    }

    return toolNames.map(name => this.tools.get(name)).filter(Boolean);
  }

  hasTool(toolName) {
    return this.getTool(toolName) !== undefined;
  }

  getToolCount() {
    return this.tools.size;
  }

  getServerToolCount(serverId) {
    const toolNames = this.serverTools.get(serverId);
    return toolNames ? toolNames.length : 0;
  }

  _findToolByShortName(shortName) {
    // Fix #13: Use index for O(1) lookup
    const fqns = this.shortNameIndex.get(shortName);
    if (!fqns || fqns.length === 0) {
      return undefined;
    }
    // Return first match if multiple servers have same tool name
    return this.tools.get(fqns[0]);
  }

  async refreshServerTools(serverId) {
    // Fix #19: Add validation
    const transport = this.serverManager.getTransport(serverId);

    if (!transport) {
      throw new Error(`Server ${serverId} is not running`);
    }

    if (!transport.isConnected()) {
      throw new Error(`Server ${serverId} is not connected`);
    }

    const result = await transport.request("tools/list", {});
    const tools = result.tools || [];

    return this.registerServerTools(serverId, tools);
  }
}
