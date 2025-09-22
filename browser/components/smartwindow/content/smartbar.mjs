import {
  Editor,
  StarterKit,
  Link,
  Placeholder,
} from "chrome://browser/content/smartwindow/tiptap-bundle.js";

export function attachToElement(element, options = {}) {
  const { onKeyDown, onUpdate, onSuggestionSelect, getQueryTypeIcon } = options;

  // Internal state for suggestions
  let currentSuggestions = [];
  let selectedSuggestionIndex = -1;
  let suggestionsContainer = null;
  let currentMentionContext = null; // Track active mention being typed

  // Create suggestions container
  function createSuggestionsContainer() {
    suggestionsContainer = document.createElement("div");
    suggestionsContainer.id = "suggestions-container";
    suggestionsContainer.className = "suggestions-container hidden";

    const suggestionsHeader = document.createElement("div");
    suggestionsHeader.className = "suggestions-header";
    suggestionsHeader.innerHTML = `
      <span class="suggestions-title">Suggestions:</span>
    `;

    const suggestionsList = document.createElement("div");
    suggestionsList.className = "suggestions-list";
    suggestionsList.id = "suggestions-list";

    suggestionsContainer.appendChild(suggestionsHeader);
    suggestionsContainer.appendChild(suggestionsList);

    // Add mouseleave handler to clear selection
    suggestionsContainer.addEventListener("mouseleave", () => {
      if (selectedSuggestionIndex >= 0) {
        selectedSuggestionIndex = -1;
        updateSuggestionSelection();
      }
    });

    return suggestionsContainer;
  }

  // Create wrapper for editor and suggestions
  const wrapper = document.createElement("div");
  wrapper.className = "smartbar-wrapper";

  // Move the element's parent and siblings to wrapper
  const parentNode = element.parentNode;
  parentNode.replaceChild(wrapper, element);
  wrapper.appendChild(element);

  // Create and append suggestions container
  const suggestionsEl = createSuggestionsContainer();
  parentNode.appendChild(suggestionsEl);

  // Create editor instance
  const editor = new Editor({
    element,
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: false,
      }),
      Placeholder.configure({
        placeholder: "Ask, search, or type a URL...",
      }),
    ],
    content: "",
    onUpdate: ({ editor: editorInstance }) => {
      const text = editorInstance.getText();
      // Hide suggestions if input is empty
      if (!text.trim() && suggestionsContainer && !suggestionsContainer.classList.contains("hidden")) {
        hideSuggestions();
      }
      if (onUpdate) {
        onUpdate(text);
      }
    },
    editorProps: {
      handleKeyDown(view, event) {
        // Call the external key handler if provided
        if (onKeyDown) {
          onKeyDown(event);
        }

        // Prevent default Tiptap behavior for certain keys
        const keysToPrevent = ["Enter", "ArrowUp", "ArrowDown", "Escape"];

        if (keysToPrevent.includes(event.key)) {
          // For Enter, only prevent if Shift is not pressed (allow Shift+Enter for newlines)
          if (event.key === "Enter" && event.shiftKey) {
            return false; // Let Tiptap handle Shift+Enter for new lines
          }
          // Prevent Tiptap's default handling
          return true;
        }

        return false;
      },
    },
  });

  // Suggestion management functions
  function createSuggestionButton(suggestion, index) {
    const button = document.createElement("button");
    button.className = `suggestion-button suggestion-${suggestion.type}`;
    button.dataset.index = index;

    // Handle favicon for tabs
    let iconElement;
    if (suggestion.icon && suggestion.icon.startsWith('data:') || suggestion.icon && suggestion.icon.startsWith('http')) {
      iconElement = document.createElement("img");
      iconElement.className = "suggestion-icon suggestion-favicon";
      iconElement.src = suggestion.icon;
      iconElement.onerror = function() {
        this.style.display = 'none';
        const fallback = document.createElement("span");
        fallback.className = "suggestion-icon";
        fallback.textContent = "🔗";
        this.parentNode.replaceChild(fallback, this);
      };
    } else {
      iconElement = document.createElement("span");
      iconElement.className = "suggestion-icon";
      iconElement.textContent = suggestion.icon || (getQueryTypeIcon ? getQueryTypeIcon(suggestion.type) : "🔍");
    }

    const textContainer = document.createElement("div");
    textContainer.className = "suggestion-text-container";

    const text = document.createElement("span");
    text.className = "suggestion-text";
    // For mention suggestions, use label; for regular suggestions use text
    text.textContent = suggestion.label || suggestion.text || suggestion.title || "";

    // Add description if available
    if (suggestion.description) {
      const desc = document.createElement("span");
      desc.className = "suggestion-description";
      desc.textContent = suggestion.description;
      textContainer.appendChild(text);
      textContainer.appendChild(desc);
    } else {
      textContainer.appendChild(text);
    }

    button.appendChild(iconElement);
    button.appendChild(textContainer);

    // Add event listeners
    button.addEventListener("mouseenter", () => {
      selectSuggestion(index);
    });

    button.addEventListener("click", e => {
      e.preventDefault();

      // Check if this is a mention suggestion
      if (currentMentionContext) {
        // Clear the @ text
        editor.chain()
          .focus()
          .deleteRange({ from: currentMentionContext.start, to: currentMentionContext.end })
          .run();

        // Clear mention context
        currentMentionContext = null;
        hideSuggestions();

        // Call the callback to handle the mention selection (add to context)
        if (onSuggestionSelect) {
          onSuggestionSelect(suggestion);
        }
      } else {
        // Regular suggestion - set content
        editor.commands.setContent(suggestion.text);
        if (onSuggestionSelect) {
          onSuggestionSelect(suggestion);
        }
      }
    });

    return button;
  }

  function selectSuggestion(index) {
    selectedSuggestionIndex = index;
    updateSuggestionSelection();
  }

  function updateSuggestionSelection() {
    const suggestionButtons =
      suggestionsContainer.querySelectorAll(".suggestion-button");
    suggestionButtons.forEach((button, index) => {
      button.classList.toggle("selected", index === selectedSuggestionIndex);
    });
  }

  function showSuggestions(
    suggestions,
    title = "Suggestions:",
    isQuickPrompts = false
  ) {
    if (!suggestionsContainer) {
      return;
    }

    suggestionsContainer.classList.remove("hidden");

    if (isQuickPrompts) {
      suggestionsContainer.classList.add("quick-prompts");
      suggestionsContainer.classList.remove("user-edited");
    } else {
      suggestionsContainer.classList.remove("quick-prompts");
      suggestionsContainer.classList.add("user-edited");
    }

    currentSuggestions = suggestions;
    selectedSuggestionIndex = -1;

    // Update header
    const header = suggestionsContainer.querySelector(".suggestions-title");
    if (header) {
      header.textContent = title;
    }

    // Clear and populate suggestions list
    const suggestionsList =
      suggestionsContainer.querySelector(".suggestions-list");
    suggestionsList.innerHTML = "";

    suggestions.forEach((suggestion, index) => {
      const suggestionButton = createSuggestionButton(suggestion, index);
      suggestionsList.appendChild(suggestionButton);
    });
  }

  function showMentionSuggestions(suggestions, mentionContext) {
    if (!suggestionsContainer) {
      return;
    }

    currentMentionContext = mentionContext;
    suggestionsContainer.classList.remove("hidden");
    suggestionsContainer.classList.add("mention-mode");
    suggestionsContainer.classList.remove("quick-prompts", "user-edited");

    currentSuggestions = suggestions;
    selectedSuggestionIndex = -1;

    // Update header for mentions
    const header = suggestionsContainer.querySelector(".suggestions-title");
    if (header) {
      header.textContent = "Mention:";
    }

    // Clear and populate suggestions list
    const suggestionsList = suggestionsContainer.querySelector(".suggestions-list");
    suggestionsList.innerHTML = "";

    suggestions.forEach((suggestion, index) => {
      const suggestionButton = createSuggestionButton(suggestion, index);
      suggestionButton.classList.add("mention-suggestion");
      suggestionsList.appendChild(suggestionButton);
    });
  }

  function hideSuggestions() {
    if (!suggestionsContainer) {
      return;
    }

    suggestionsContainer.classList.add("hidden");
    suggestionsContainer.classList.remove("quick-prompts", "user-edited", "mention-mode");
    currentSuggestions = [];
    selectedSuggestionIndex = -1;
    currentMentionContext = null;
  }

  function navigateSuggestions(direction) {
    if (!currentSuggestions.length) {
      return;
    }

    if (direction === "down") {
      selectedSuggestionIndex = Math.min(
        selectedSuggestionIndex + 1,
        currentSuggestions.length - 1
      );
    } else if (direction === "up") {
      selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
    }

    updateSuggestionSelection();
  }

  function getSelectedSuggestion() {
    return selectedSuggestionIndex >= 0
      ? currentSuggestions[selectedSuggestionIndex]
      : null;
  }

  function hasSuggestions() {
    return !!currentSuggestions.length;
  }

  // Return an object with the editor and helper functions
  return {
    editor, // Expose editor for direct access when needed

    // Helper functions
    focus() {
      editor.commands.focus("end");
    },

    getText() {
      return editor.getText();
    },

    setContent(content) {
      editor.commands.setContent(content);
    },

    clear() {
      editor.commands.setContent("");
      // Hide suggestions when clearing
      hideSuggestions();
      // Refocus after clearing
      editor.commands.focus("end");
    },

    setEditable(editable) {
      editor.setEditable(editable);
    },

    destroy() {
      editor.destroy();
      if (suggestionsContainer) {
        suggestionsContainer.remove();
      }
    },

    // Cursor and selection methods
    getSelection() {
      return editor.state.selection;
    },

    getTextBeforeCursor(length = 50) {
      const { from } = editor.state.selection;
      return editor.state.doc.textBetween(Math.max(0, from - length), from);
    },

    getCursorPosition() {
      return editor.state.selection.from;
    },

    // Mention detection
    detectMention() {
      const textBefore = this.getTextBeforeCursor();
      const mentionMatch = textBefore.match(/@(\w*)$/);
      if (mentionMatch) {
        const from = this.getCursorPosition();
        return {
          query: mentionMatch[1],
          start: from - mentionMatch[0].length,
          end: from,
        };
      }
      return null;
    },


    // Suggestions API
    showSuggestions,
    showMentionSuggestions,
    hideSuggestions,
    navigateSuggestions,
    getSelectedSuggestion,
    hasSuggestions,
    getCurrentMentionContext: () => currentMentionContext,
  };
}
