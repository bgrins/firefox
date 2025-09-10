/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const AIModeChatUI = {
  initialized: false,
  
  init() {
    if (this.initialized) {
      return;
    }
    
    this.initialized = true;
    this.setupEventListeners();
    this.adjustInputHeight();
    
    // Listen for messages from parent window (AI Mode)
    window.addEventListener("message", (e) => {
      if (e.data.type === "ai-mode-query") {
        this.handleIncomingQuery(e.data.detail);
      }
    });
    
    console.log("AI Mode Chat UI initialized");
  },
  
  setupEventListeners() {
    const input = document.getElementById("ai-chat-input");
    const sendButton = document.getElementById("ai-chat-send");
    const closeButton = document.getElementById("ai-chat-close");
    
    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
      
      input.addEventListener("input", () => {
        this.adjustInputHeight();
      });
    }
    
    if (sendButton) {
      sendButton.addEventListener("click", () => {
        this.sendMessage();
      });
    }
    
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        // Send message to parent to close the sidebar
        if (window.parent && window.parent !== window) {
          window.parent.postMessage({ type: "close-ai-sidebar" }, "*");
        }
      });
    }
  },
  
  adjustInputHeight() {
    const input = document.getElementById("ai-chat-input");
    if (input) {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 120) + "px";
    }
  },
  
  sendMessage() {
    const input = document.getElementById("ai-chat-input");
    const message = input?.value?.trim();
    
    if (!message) {
      return;
    }
    
    // Add user message to chat
    this.addMessage(message, "user");
    
    // Clear input
    input.value = "";
    this.adjustInputHeight();
    
    // Simulate AI response (placeholder)
    setTimeout(() => {
      this.addMessage("I'm a placeholder AI response. The actual AI integration will be implemented soon.", "assistant");
    }, 1000);
  },
  
  addMessage(text, sender) {
    const messagesContainer = document.getElementById("ai-chat-messages");
    
    // Remove welcome message if it exists
    const welcomeMessage = messagesContainer.querySelector(".ai-welcome-message");
    if (welcomeMessage) {
      welcomeMessage.remove();
    }
    
    if (sender === "user") {
      // Create a message group for user prompt
      const messageGroup = document.createElement("div");
      messageGroup.className = "message-group";
      
      const promptDiv = document.createElement("div");
      promptDiv.className = "message-prompt";
      promptDiv.textContent = text;
      
      messageGroup.appendChild(promptDiv);
      messagesContainer.appendChild(messageGroup);
    } else {
      // Create response with line and content
      const lastGroup = messagesContainer.querySelector(".message-group:last-child");
      
      if (lastGroup) {
        const responseDiv = document.createElement("div");
        responseDiv.className = "message-response";
        
        const lineDiv = document.createElement("div");
        lineDiv.className = "message-line";
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        
        const textDiv = document.createElement("div");
        textDiv.className = "message-text";
        textDiv.textContent = text;
        
        contentDiv.appendChild(textDiv);
        
        // Add suggestions for assistant messages
        if (sender === "assistant") {
          const suggestionsDiv = document.createElement("div");
          suggestionsDiv.className = "ai-chat-suggestions";
          
          const suggestions = [
            { icon: "🔍", text: "Tell me more" },
            { icon: "💡", text: "Give examples" }
          ];
          
          suggestions.forEach(s => {
            const suggestionBtn = document.createElement("button");
            suggestionBtn.className = "ai-chat-suggestion";
            suggestionBtn.innerHTML = `
              <span class="ai-chat-suggestion-icon">${s.icon}</span>
              <span class="ai-chat-suggestion-text">${s.text}</span>
            `;
            suggestionBtn.onclick = () => {
              this.handleSuggestion(s.text);
            };
            suggestionsDiv.appendChild(suggestionBtn);
          });
          
          contentDiv.appendChild(suggestionsDiv);
        }
        
        responseDiv.appendChild(lineDiv);
        responseDiv.appendChild(contentDiv);
        lastGroup.appendChild(responseDiv);
      }
    }
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  },
  
  handleSuggestion(text) {
    const input = document.getElementById("ai-chat-input");
    if (input) {
      input.value = text;
      this.sendMessage();
    }
  },
  
  handleIncomingQuery(detail) {
    if (detail?.query) {
      const input = document.getElementById("ai-chat-input");
      if (input) {
        input.value = detail.query;
        this.adjustInputHeight();
        // Auto-send the message
        this.sendMessage();
      }
    }
  }
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  AIModeChatUI.init();
});