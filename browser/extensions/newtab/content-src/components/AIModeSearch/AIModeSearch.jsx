/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

import React from "react";
import { connect } from "react-redux";

export class _AIModeSearch extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      query: "",
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleAskClick = this.handleAskClick.bind(this);
  }

  componentDidMount() {
    // Focus the input when component mounts
    if (this.inputRef) {
      this.inputRef.focus();
    }
  }

  handleInputChange(event) {
    this.setState({ query: event.target.value });
  }

  handleKeyDown(event) {
    if (event.key === "Enter" && this.state.query.trim()) {
      this.performSearch();
    }
  }

  handleAskClick() {
    if (this.state.query.trim()) {
      this.performSearch();
    }
  }

  performSearch() {
    // For now, just perform a regular search
    // Later this can be integrated with AI features
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(this.state.query)}`;
    window.location.href = searchUrl;
  }

  render() {
    return (
      <div className="ai-mode-search-container">
        <div className="ai-mode-logo">
          <span className="ai-mode-logo-text">Firefox AI Mode</span>
        </div>
        
        <div className="ai-mode-searchbar">
          <div className="ai-mode-input-container">
            <input
              ref={ref => this.inputRef = ref}
              type="text"
              className="ai-mode-input"
              placeholder="Help me find a new pair of sneakers"
              value={this.state.query}
              onChange={this.handleInputChange}
              onKeyDown={this.handleKeyDown}
            />
            <button 
              className="ai-mode-ask-button"
              onClick={this.handleAskClick}
              disabled={!this.state.query.trim()}
            >
              Ask
            </button>
          </div>
          
          <div className="ai-mode-suggestions">
            <button className="ai-mode-suggestion" onClick={() => this.setState({ query: "Plan a weekend trip" }, () => this.performSearch())}>
              <span className="suggestion-icon">✈️</span>
              <span>Plan a weekend trip</span>
            </button>
            <button className="ai-mode-suggestion" onClick={() => this.setState({ query: "Healthy dinner recipes" }, () => this.performSearch())}>
              <span className="suggestion-icon">🍽️</span>
              <span>Healthy dinner recipes</span>
            </button>
            <button className="ai-mode-suggestion" onClick={() => this.setState({ query: "Learn something new" }, () => this.performSearch())}>
              <span className="suggestion-icon">📚</span>
              <span>Learn something new</span>
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export const AIModeSearch = connect()(_AIModeSearch);