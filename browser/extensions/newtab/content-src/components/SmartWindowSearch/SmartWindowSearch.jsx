/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

import React from "react";
import { connect } from "react-redux";

export class _SmartWindowSearch extends React.PureComponent {
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
      <div className="smart-window-search-container">
        <div className="smart-window-logo">
          <span className="smart-window-logo-text">Firefox Smart Window</span>
        </div>
        
        <div className="smart-window-searchbar">
          <div className="smart-window-input-container">
            <input
              ref={ref => this.inputRef = ref}
              type="text"
              className="smart-window-input"
              placeholder="Search in Smart Window..."
              value={this.state.query}
              onChange={this.handleInputChange}
              onKeyDown={this.handleKeyDown}
            />
            <button 
              className="smart-window-ask-button"
              onClick={this.handleAskClick}
              disabled={!this.state.query.trim()}
            >
              Ask
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export const SmartWindowSearch = connect()(_SmartWindowSearch);